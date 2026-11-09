"""Check the narrow init privileges and file modes around the M13 initializer."""
import os
from pathlib import Path
import runpy
import stat

EXPECTED_CAPABILITIES = 11  # CHOWN, DAC_OVERRIDE, FOWNER
EXPECTED_PATHS = {
    "/admin": (10001, 0o700),
    "/webkeys": (0, 0o700),
    "/state": (10001, 0o700),
    "/audit": (10001, 0o700),
    "/admin/credentials.json": (10001, 0o600),
    "/state/service_secret": (10001, 0o600),
    "/webkeys/key": (0, 0o600),
    "/webkeys/admin_password": (0, 0o600),
}

capabilities = {
    key: int(value, 16)
    for key, value in (
        line.split(":", 1)
        for line in Path("/proc/self/status").read_text().splitlines()
        if line.startswith(("CapEff:", "CapPrm:", "CapBnd:"))
    )
}
if os.getuid() != 0 or capabilities != dict.fromkeys(
    ("CapEff", "CapPrm", "CapBnd"), EXPECTED_CAPABILITIES
):
    raise SystemExit("unexpected_init_privileges")

runpy.run_path("/app/init.py", run_name="__main__")
for name, (uid, mode) in EXPECTED_PATHS.items():
    entry = Path(name).lstat()
    if stat.S_ISLNK(entry.st_mode) or (
        entry.st_uid, entry.st_gid, stat.S_IMODE(entry.st_mode)
    ) != (uid, uid, mode):
        raise SystemExit("unexpected_init_permissions")
print('{"event":"init_permissions_verified"}', flush=True)
