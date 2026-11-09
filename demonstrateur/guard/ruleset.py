"""Validate the entire live ruleset before issuing a readiness signal."""

import hashlib
import ipaddress
import json
from pathlib import Path
import struct
import subprocess

from heartbeat import identity
from netlink import generation, tables, targets

ROOT = Path(__file__).resolve().parent
DNS = '127.0.0.11'


def require(condition, code):
    if not condition:
        raise ValueError(code)


def match(protocol, field, value):
    return {'match': {'op': '==', 'left': {'payload': {'protocol': protocol, 'field': field}}, 'right': value}}


def nat_range(revision, data):
    if revision == 0:
        require(len(data) == 24 and data[20:] == bytes(4) and struct.unpack_from('=I', data)[0] == 1, 'nat_range_v0')
        flags, = struct.unpack_from('=I', data, 4)
        addresses = data[8:12], data[12:16]
        ports = struct.unpack_from('!HH', data, 16)
    elif revision in (1, 2):
        require(len(data) == {1: 40, 2: 48}[revision] and not any(data[8:20] + data[24:36] + data[40:]), 'nat_range_v1_v2')
        flags, = struct.unpack_from('=I', data)
        addresses = data[4:8], data[20:24]
        ports = struct.unpack_from('!HH', data, 36)
    else:
        raise ValueError('unknown_nat_revision')
    return flags, tuple(str(ipaddress.IPv4Address(addr)) for addr in addresses), ports


def ruleset_index(document):
    metadata = 0
    result = {}
    handles = set()
    for item in document['nftables']:
        require(len(item) == 1, 'ambiguous_ruleset_item')
        kind, obj = next(iter(item.items()))
        if kind == 'metainfo':
            metadata += 1
            require(obj['json_schema_version'] == 1, 'unexpected_nft_json_schema')
            continue
        if kind == 'table':
            key = obj['family'], obj['name']
            require(set(obj) == {'family', 'name', 'handle'} and key not in result, 'unexpected_table_attributes')
            result[key] = {}
            continue
        chains = result[obj['family'], obj['table']]
        if kind == 'chain':
            name = obj['name']
            attrs = {k: v for k, v in obj.items() if k not in ('family', 'table', 'name', 'handle')}
            require(name not in chains, 'duplicate_chain')
            chains[name] = {'attributes': attrs, 'rules': []}
        elif kind == 'rule':
            key = obj['family'], obj['table'], obj['handle']
            require(set(obj) == {'family', 'table', 'chain', 'handle', 'expr'} and key not in handles, 'unexpected_rule_attributes')
            handles.add(key)
            chains[obj['chain']]['rules'].append((obj['handle'], obj['expr']))
        else:
            raise ValueError('unknown_ruleset_object')
    require(metadata == 1, 'missing_or_duplicate_ruleset_metadata')
    return result


def validate(document, observed_targets, kernel_tables, expected_filter):
    live = ruleset_index(document)
    require(set(live) == {('inet', 'thiga_m17'), ('ip', 'nat')}
            and kernel_tables == {(1, 'thiga_m17'): 0, (2, 'nat'): 0}, 'unexpected_or_inactive_table')
    installed = live['inet', 'thiga_m17']
    actual_filter = {name: {'attributes': row['attributes'], 'rules': [expr for _, expr in row['rules']]}
                     for name, row in installed.items()}
    require(actual_filter == expected_filter, 'sealed_filter_mismatch')
    nat = live['ip', 'nat']
    require({name: row['attributes'] for name, row in nat.items()} == {
        'OUTPUT': {'type': 'nat', 'hook': 'output', 'prio': -100, 'policy': 'accept'},
        'POSTROUTING': {'type': 'nat', 'hook': 'postrouting', 'prio': 100, 'policy': 'accept'},
        'DOCKER_OUTPUT': {}, 'DOCKER_POSTROUTING': {},
    }, 'unexpected_nat_chains')
    handles = {('nat', name, handle) for name, row in nat.items() for handle, _ in row['rules']}
    require(len(handles) == 6 and set(observed_targets) == handles, 'incomplete_or_unmatched_nat_rules')
    for chain in ('OUTPUT', 'POSTROUTING'):
        (handle, expr), = nat[chain]['rules']
        require(expr == [match('ip', 'daddr', DNS), {'counter': None}, {'jump': {'target': 'DOCKER_' + chain}}]
                and not observed_targets['nat', chain, handle], 'unexpected_nat_jump')
    translations = {}
    for chain, direction in (('DOCKER_OUTPUT', 'DNAT'), ('DOCKER_POSTROUTING', 'SNAT')):
        outgoing = direction == 'DNAT'
        ip_field, port_field = ('daddr', 'dport') if outgoing else ('saddr', 'sport')
        require(len(nat[chain]['rules']) == 2, 'unexpected_nat_rule_count')
        for handle, expr in nat[chain]['rules']:
            condition = expr[1]['match']
            protocol = condition['left']['payload']['protocol']
            input_port = condition['right']
            require(protocol in ('tcp', 'udp') and (direction, protocol) not in translations
                    and type(input_port) is int and 1 <= input_port <= 65535 and (not outgoing or input_port == 53)
                    and expr == [match('ip', ip_field, DNS), match(protocol, port_field, input_port), {'counter': None},
                                 {'xt': {'type': 'target', 'name': direction}}], 'unexpected_nat_condition')
            (name, revision, data), = observed_targets['nat', chain, handle]
            flags, addresses, ports = nat_range(revision, data)
            require(name == direction and flags == (3 if outgoing else 2)
                    and addresses == ((DNS, DNS) if outgoing else ('0.0.0.0', '0.0.0.0')) and ports[0] == ports[1]
                    and (ports[0] > 1023 if outgoing else ports[0] == 53), 'unexpected_nat_translation')
            translations[direction, protocol] = {
                'chain': chain, 'handle': handle, 'input_port': input_port, 'translated_port': ports[0],
                'input_address': DNS, 'translated_address': DNS, 'maps_address': outgoing,
                'revision': revision, 'flags': flags, 'target_info_hex': data.hex(),
            }
    for protocol in ('tcp', 'udp'):
        require(translations['DNAT', protocol]['translated_port'] == translations['SNAT', protocol]['input_port'],
                'unpaired_dns_ports')
    return {f'{direction}_{proto}': value for (direction, proto), value in sorted(translations.items())}


def policy_contract():
    reference = json.loads((ROOT / 'policy.expected.json').read_text(encoding='utf-8'))
    require(hashlib.sha256((ROOT / 'policy.nft').read_bytes()).hexdigest() == reference['policy_sha256'],
            'bundled_policy_digest_mismatch')
    return reference


def observe(reference):
    before = identity(), generation()
    raw = subprocess.run(['nft', '-j', '-a', '-s', '-n', 'list', 'ruleset'], check=True,
                         capture_output=True, timeout=1).stdout
    current_tables, current_targets = tables(), targets()
    require(before == (identity(), generation()), 'ruleset_generation_changed_during_capture')
    document = json.loads(raw)
    nat = validate(document, current_targets, current_tables, reference['filter'])
    return {'ruleset_sha256': hashlib.sha256(raw).hexdigest(), 'nat_sha256': hashlib.sha256(
            json.dumps(nat, sort_keys=True).encode()).hexdigest(), 'kernel_generation': before[1], 'nat': nat,
            **before[0]}


if __name__ == '__main__':
    print(json.dumps(observe(policy_contract()), sort_keys=True))
