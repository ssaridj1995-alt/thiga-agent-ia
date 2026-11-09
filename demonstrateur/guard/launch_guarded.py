"""Run WebUI only while its network guard reports a valid generation."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import urllib.request

from heartbeat import read_valid

STATUS = Path("/guard-status/status.json")


def healthy():
    state = read_valid(STATUS)
    if state is None:
        return False
    with urllib.request.urlopen("http://127.0.0.1:8080/health", timeout=2) as response:
        current = read_valid(STATUS)
        return response.status == 200 and current is not None and signal_id(current) == signal_id(state)


def signal_id(state):
    return tuple(state[key] for key in ("generation", "guard_container", "kernel_generation", "ruleset_sha256", "nat_sha256"))


def signal_group(child, signum):
    try:
        os.killpg(child.pid, signum)
    except ProcessLookupError:
        pass


def stop(child):
    signal_group(child, signal.SIGTERM)
    try:
        child.wait(timeout=5)
    except subprocess.TimeoutExpired:
        signal_group(child, signal.SIGKILL)
        child.wait()
    # A child that exited may still have left processes in its group.
    signal_group(child, signal.SIGKILL)


def supervise():
    stopping = False
    child = None
    generation = None

    def request_stop(_signum, _frame):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    os.umask(0o077)
    try:
        while not stopping:
            state = read_valid(STATUS)
            if child is not None:
                if child.poll() is not None:
                    return 1
                if state is None or signal_id(state) != generation:
                    stop(child)
                    child = None
                    print('{"event":"webui_stopped_guard_unavailable"}', flush=True)
                    continue  # Revalidate after waiting for the child to exit.
            elif state is not None:
                prepared = subprocess.run(
                    [sys.executable, "-B", "/app/backend/open_webui/utils/thiga_revocation.py", "prepare"],
                    timeout=12,
                )
                if prepared.returncode != 0:
                    print('{"event":"webui_session_registry_unavailable"}', flush=True)
                    return 1
                password = Path("/webkeys/admin_password").read_text()
                current = read_valid(STATUS)
                if not stopping and current and signal_id(current) == signal_id(state):
                    child = subprocess.Popen(
                        ["/bin/bash", "/app/backend/start.sh"], start_new_session=True,
                        env={**os.environ, "WEBUI_ADMIN_PASSWORD": password},
                    )
                    generation = signal_id(current)
                    print(json.dumps({"event": "webui_started_guard_ready", "generation": current["generation"],
                                      "guard_container": current["guard_container"], "netns": current["netns"],
                                      "ruleset_sha256": current["ruleset_sha256"]}), flush=True)
                del password
            time.sleep(0.2)
        return 0
    finally:
        if child is not None:
            stop(child)


if __name__ == "__main__":
    try:
        if sys.argv[1:] == ["health"]:
            sys.exit(0 if healthy() else 1)
        if sys.argv[1:]:
            sys.exit(2)
        sys.exit(supervise())
    except Exception:
        sys.exit(1)
