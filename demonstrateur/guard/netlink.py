"""Bounded, read-only Linux nftables Netlink requests (UAPI 6.18)."""

import socket
import struct

HEADER = struct.Struct('=IHHII')
NFT = 10 << 8
GET_TABLE, GET_RULE, GET_GENERATION = 1, 7, 16


def fields(data, *, unique=True):
    offset = 0
    seen = set()
    while offset < len(data):
        size, kind = struct.unpack_from('=HH', data, offset)
        kind &= 0x3fff
        if size < 4 or offset + size > len(data) or (unique and kind in seen):
            raise ValueError('malformed_netlink_attribute')
        seen.add(kind)
        yield kind, data[offset + 4:offset + size]
        offset += (size + 3) & ~3
    if offset != len(data):
        raise ValueError('truncated_netlink_attribute')


def string(data):
    if not data.endswith(b'\0') or b'\0' in data[:-1]:
        raise ValueError('invalid_netlink_string')
    return data[:-1].decode('ascii')


def responses(data, sequence, port):
    offset = 0
    while offset < len(data):
        size, kind, flags, seq, pid = HEADER.unpack_from(data, offset)
        if size < HEADER.size or offset + size > len(data) or seq != sequence or pid != port or flags & 0x10:
            raise ValueError('invalid_or_interrupted_netlink_reply')
        yield kind, data[offset + HEADER.size:offset + size]
        offset += (size + 3) & ~3
    if offset != len(data):
        raise ValueError('truncated_netlink_reply')


def request(command, family=0):
    if command not in (GET_TABLE, GET_RULE, GET_GENERATION):
        raise ValueError('netlink_read_operations_only')
    dump = command != GET_GENERATION
    reply = NFT | (command - 1)  # The corresponding NEW object in the reply.
    with socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, 12) as sock:
        sock.bind((0, 0))
        sock.settimeout(0.75)
        port = sock.getsockname()[0]
        seq = 17101 + command
        flags = 0x301 if dump else 1
        sock.sendto(HEADER.pack(20, NFT | command, flags, seq, port) + bytes((family, 0, 0, 0)), (0, 0))
        result = []
        for _ in range(8):
            data, _, received_flags, sender = sock.recvmsg(65536)
            if sender != (0, 0) or received_flags & socket.MSG_TRUNC:
                raise ValueError('invalid_netlink_sender_or_size')
            records = list(responses(data, seq, port))
            for index, (kind, payload) in enumerate(records):
                last = index == len(records) - 1
                if dump and kind == 3 and last and payload == bytes(4):
                    return result
                if kind != reply or len(payload) < 4 or payload[1] != 0:
                    raise ValueError('unexpected_netlink_reply')
                result.append((payload[0], dict(fields(payload[4:]))))
            if not dump and len(result) == 1:
                return result
        raise ValueError('incomplete_netlink_reply')


def generation():
    (_, info), = request(GET_GENERATION)
    return struct.unpack('!I', info[1])[0]


def tables():
    result = {}
    for family, info in request(GET_TABLE):
        key = family, string(info[1])
        if key in result:
            raise ValueError('duplicate_netlink_table')
        result[key] = struct.unpack('!I', info[2])[0]
    return result


def targets():
    result = {}
    for family, info in request(GET_RULE, socket.AF_INET):
        key = string(info[1]), string(info[2]), struct.unpack('!Q', info[3])[0]
        if family != socket.AF_INET or key in result:
            raise ValueError('invalid_netlink_rule_identity')
        matches = []
        for list_kind, expression in fields(info[4], unique=False):
            if list_kind != 1:
                raise ValueError('unknown_netlink_expression_entry')
            expr = dict(fields(expression))
            if string(expr[1]) != 'target':
                continue
            target = dict(fields(expr[2]))
            if set(target) != {1, 2, 3}:
                raise ValueError('unknown_target_attributes')
            matches.append((string(target[1]), struct.unpack('!I', target[2])[0], target[3]))
        result[key] = matches
    return result
