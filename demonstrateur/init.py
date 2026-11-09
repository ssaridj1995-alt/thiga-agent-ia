import fcntl, os, pathlib, secrets
from state import read, atomic, text_once
from settings import NAMES

os.umask(0o077)
for directory, uid in [('/admin',10001),('/webkeys',0),('/state',10001),('/audit',10001)]:
    os.chmod(directory, 0o700); os.chown(directory,uid,uid)
with open('/admin/lock','a') as lock:
    os.chown('/admin/lock',10001,10001)
    fcntl.flock(lock, fcntl.LOCK_EX)
    p = pathlib.Path('/admin/credentials.json')
    if not p.exists():
        # Missing master beside published material is not a new installation.
        if pathlib.Path('/state/service_secret').exists() or pathlib.Path('/webkeys/key').exists():
            raise ValueError('missing_master')
        atomic(p, dict(admin_password=secrets.token_urlsafe(36), webui_secret=secrets.token_urlsafe(48),
                       service_secret=secrets.token_urlsafe(48), passwords={n:secrets.token_urlsafe(36) for n in NAMES}),10001)
    c=read(p)
    text_once('/state/service_secret',c['service_secret'],10001)
    text_once('/webkeys/key',c['webui_secret'])
    text_once('/webkeys/admin_password',c['admin_password'])
print('{"event":"secrets_ready"}')
