import copy
import ipaddress
import json
from pathlib import Path
import struct
import sys
import time
import unittest
import uuid
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'guard'))
import heartbeat
import netlink
import ruleset


def sample(tcp=46701, udp=54651):
    reference = ruleset.policy_contract()['filter']
    doc = [{'metainfo': {'json_schema_version': 1}}]
    for family, table, profile in (
        ('inet', 'thiga_m17', reference),
        ('ip', 'nat', {
            'OUTPUT': {'attributes': {'type': 'nat', 'hook': 'output', 'prio': -100, 'policy': 'accept'}, 'rules': []},
            'DOCKER_OUTPUT': {'attributes': {}, 'rules': []},
            'POSTROUTING': {'attributes': {'type': 'nat', 'hook': 'postrouting', 'prio': 100, 'policy': 'accept'}, 'rules': []},
            'DOCKER_POSTROUTING': {'attributes': {}, 'rules': []},
        }),
    ):
        doc.append({'table': {'family': family, 'name': table, 'handle': len(doc)}})
        for name, chain in profile.items():
            doc.append({'chain': {'family': family, 'table': table, 'name': name, 'handle': len(doc), **chain['attributes']}})
        for name, chain in profile.items():
            for expr in chain['rules']:
                doc.append({'rule': {'family': family, 'table': table, 'chain': name, 'handle': len(doc), 'expr': expr}})
    entries = {}

    def add(chain, expr, target=()):
        handle = len(doc)
        doc.append({'rule': {'family': 'ip', 'table': 'nat', 'chain': chain, 'handle': handle, 'expr': expr}})
        entries['nat', chain, handle] = list(target)

    dns = '127.0.0.11'
    for chain in ('OUTPUT', 'POSTROUTING'):
        add(chain, [ruleset.match('ip', 'daddr', dns), {'counter': None}, {'jump': {'target': 'DOCKER_' + chain}}])
    for protocol, port in (('tcp', tcp), ('udp', udp)):
        address = ipaddress.IPv4Address(dns).packed + bytes(12)
        dnat = struct.pack('=I', 3) + address * 2 + struct.pack('!HH', port, port) + bytes(8)
        snat = struct.pack('=II', 1, 2) + bytes(8) + struct.pack('!HH', 53, 53) + bytes(4)
        for chain, direction, ip_field, port_field, source_port, revision, data in (
            ('DOCKER_OUTPUT', 'DNAT', 'daddr', 'dport', 53, 2, dnat),
            ('DOCKER_POSTROUTING', 'SNAT', 'saddr', 'sport', port, 0, snat),
        ):
            add(chain, [ruleset.match('ip', ip_field, dns), ruleset.match(protocol, port_field, source_port),
                        {'counter': None}, {'xt': {'type': 'target', 'name': direction}}], [(direction, revision, data)])
    return {'nftables': doc}, entries, {(1, 'thiga_m17'): 0, (2, 'nat'): 0}, reference


class GuardTests(unittest.TestCase):
    def test_current_ports_are_not_pinned(self):
        for tcp, udp in ((46701, 54651), (50001, 50002), (49999, 49999)):
            out = ruleset.validate(*sample(tcp, udp))
            self.assertEqual(len(out), 4)
            self.assertEqual(out['DNAT_tcp']['translated_port'], tcp)
            self.assertEqual(out['DNAT_udp']['translated_port'], udp)

    def test_unknown_and_dormant_table(self):
        for extra in ({(2, 'other'): 0}, {(1, 'thiga_m17'): 1}):
            doc, entries, tables, ref = sample()
            with self.assertRaises(ValueError):
                ruleset.validate(doc, entries, {**tables, **extra}, ref)

    def test_opaque_or_partial_dump(self):
        for change in ('missing', 'opaque', 'extra'):
            doc, entries, tables, ref = sample()
            key = next(k for k in entries if k[1] == 'DOCKER_OUTPUT')
            if change == 'missing':
                del entries[key]
            elif change == 'opaque':
                entries[key] = [('DNAT', 255, bytes(48))]
            else:
                entries['nat', 'elsewhere', 999] = []
            with self.assertRaises(ValueError):
                ruleset.validate(doc, entries, tables, ref)

    def test_external_dnat_is_refused(self):
        doc, entries, tables, ref = sample()
        key = next(k for k in entries if k[1] == 'DOCKER_OUTPUT')
        name, rev, data = entries[key][0]
        entries[key] = [(name, rev, data.replace(b'\x7f\x00\x00\x0b', b'\x01\x01\x01\x01'))]
        with self.assertRaisesRegex(ValueError, 'unexpected_nat_translation'):
            ruleset.validate(doc, entries, tables, ref)

    def test_unpaired_ports_are_refused(self):
        doc, entries, tables, ref = sample()
        key = next(k for k in entries if k[1] == 'DOCKER_OUTPUT')
        name, rev, data = entries[key][0]
        entries[key] = [(name, rev, data[:36] + struct.pack('!HH', 51001, 51001) + data[40:])]
        with self.assertRaisesRegex(ValueError, 'unpaired_dns_ports'):
            ruleset.validate(doc, entries, tables, ref)

    def test_filter_order_and_extra_rule_are_refused(self):
        doc, entries, tables, ref = sample()
        for extra_rule in (False, True):
            modified = copy.deepcopy(doc)
            selected = [i for i, r in enumerate(modified['nftables']) if r.get('rule', {}).get('chain') == 'output']
            x, y = selected[:2]
            if extra_rule:
                record = copy.deepcopy(modified['nftables'][x])
                record['rule']['handle'] = 999
                modified['nftables'].append(record)
            else:
                modified['nftables'][x], modified['nftables'][y] = modified['nftables'][y], modified['nftables'][x]
            with self.assertRaisesRegex(ValueError, 'sealed_filter_mismatch'):
                ruleset.validate(modified, entries, tables, ref)

    def test_netlink_refuses_mutation_and_truncated_reply(self):
        with self.assertRaisesRegex(ValueError, 'read_operations_only'):
            netlink.request(6)
        for flags, size in ((0x10, 16), (0, 32)):
            with self.assertRaises(ValueError):
                list(netlink.responses(netlink.HEADER.pack(size, 3, flags, 1, 2), 1, 2))

    def test_readiness_cannot_be_stale_incomplete_or_cross_namespace(self):
        mock_id = {'netns': 'net:[42]', 'boot_id': str(uuid.uuid4())}
        state = {**mock_id, 'monotonic': time.monotonic(), 'generation': str(uuid.uuid4()),
                 'rules_sha256': '0' * 64, 'ruleset_sha256': '1' * 64, 'nat_sha256': '2' * 64,
                 'guard_container': 'abcdefabcdef', 'kernel_generation': 1, 'nat_targets': 4}
        with patch.object(heartbeat, 'identity', return_value=mock_id):
            path = Mock()
            path.read_text.return_value = json.dumps(state)
            self.assertEqual(heartbeat.read_valid(path), state)
            for change in ({'netns': 'net:[12]'}, {'monotonic': time.monotonic() - 4}, {'nat_targets': 3},
                           {'ruleset_sha256': ''}, {'guard_container': 'other'}):
                path.read_text.return_value = json.dumps({**state, **change})
                self.assertIsNone(heartbeat.read_valid(path))


if __name__ == '__main__':
    unittest.main(verbosity=2)
