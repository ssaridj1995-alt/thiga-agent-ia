"""Shared contract for a fresh guard signal in the current boot and namespace."""
import json
import os
from pathlib import Path
import re
import time
import uuid


def identity():
    return {
        "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
        "netns": os.readlink("/proc/self/ns/net"),
    }


def read_valid(path):
    try:
        state = json.loads(path.read_text())
        if not all(state[key] == value for key, value in identity().items()):
            return None
        if not 0 <= time.monotonic() - state["monotonic"] < 2:
            return None
        if str(uuid.UUID(state["generation"])) != state["generation"]:
            return None
        if not all(re.fullmatch(r"[0-9a-f]{64}", state[key]) for key in
                   ("rules_sha256", "ruleset_sha256", "nat_sha256")):
            return None
        if (state["nat_targets"] != 4 or not re.fullmatch(r"[0-9a-f]{12}", state["guard_container"])
                or type(state["kernel_generation"]) is not int or not 0 <= state["kernel_generation"] < 2**32):
            return None
        return state
    except (OSError, KeyError, TypeError, ValueError, AttributeError):
        return None
