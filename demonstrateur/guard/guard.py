"""Install and verify the namespace policy before signalling readiness."""
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
import uuid

from heartbeat import identity, read_valid
from netlink import generation
from ruleset import observe, policy_contract

POLICY = Path("/guard/policy.nft")
STATUS = Path("/run/guard/status.json")
TABLE = "thiga_m17"
EXPECTED_CAPABILITIES = 1 << 12  # NET_ADMIN


def nft(*args, input_text=None, check=True):
    return subprocess.run(
        ["nft", *args], input=input_text, capture_output=True,
        text=True, check=check, timeout=1,
    )


def rules_digest():
    # Stateless listing keeps packet counters out of the integrity comparison.
    listing = nft("-s", "list", "table", "inet", TABLE).stdout
    return hashlib.sha256(listing.encode()).hexdigest()


def healthy():
    state = read_valid(STATUS)
    return (state is not None and state["guard_container"] == socket.gethostname()
            and rules_digest() == state["rules_sha256"] and generation() == state["kernel_generation"])


def serve():
    temporary = STATUS.with_suffix(".tmp")
    STATUS.unlink(missing_ok=True)
    temporary.unlink(missing_ok=True)
    stopping = False

    def request_stop(_signum, _frame):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    try:
        capabilities = {
            key: int(value, 16)
            for key, value in (
                line.split(":", 1)
                for line in Path("/proc/self/status").read_text().splitlines()
                if line.startswith(("CapEff:", "CapPrm:", "CapBnd:"))
            )
        }
        if capabilities != dict.fromkeys(
            ("CapEff", "CapPrm", "CapBnd"), EXPECTED_CAPABILITIES
        ):
            raise RuntimeError("unexpected_guard_capabilities")

        reference = policy_contract()
        nft("list", "tables")
        existing = nft("list", "table", "inet", TABLE, check=False).returncode == 0
        policy = POLICY.read_text()
        # If the table exists, replace it in one transaction without a gap.
        transaction = (f"delete table inet {TABLE}\n" if existing else "") + policy
        nft("-c", "-f", "-", input_text=transaction)
        nft("-f", "-", input_text=transaction)
        expected = rules_digest()
        qualified = observe(reference)
        state = {
            **identity(),
            "generation": str(uuid.uuid4()),
            "guard_container": socket.gethostname(),
            "rules_sha256": expected,
            "ruleset_sha256": qualified["ruleset_sha256"],
            "nat_sha256": qualified["nat_sha256"],
            "kernel_generation": qualified["kernel_generation"],
            "nat_targets": 4,
        }
        print(json.dumps({"event": "policy_installed", **state, "nat": qualified["nat"]}), flush=True)

        while not stopping:
            if rules_digest() != expected or generation() != state["kernel_generation"]:
                raise RuntimeError("policy_changed")
            state["monotonic"] = time.monotonic()
            temporary.write_text(json.dumps(state), encoding="utf-8")
            temporary.chmod(0o444)
            os.replace(temporary, STATUS)
            time.sleep(0.4)
    finally:
        # The kernel policy remains installed if the namespace survives.
        STATUS.unlink(missing_ok=True)
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        if sys.argv[1:] == ["health"]:
            sys.exit(0 if healthy() else 1)
        if sys.argv[1:]:
            sys.exit(2)
        serve()
    except Exception as error:
        reason = error.args[0] if (type(error) in (ValueError, RuntimeError) and len(error.args) == 1
                                  and isinstance(error.args[0], str) and error.args[0].isascii()
                                  and error.args[0].replace('_', '').isalnum()) else None
        print(json.dumps({"event": "guard_failed", "type": type(error).__name__, "reason": reason}), flush=True)
        sys.exit(1)
