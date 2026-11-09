import json, os, pathlib, tempfile

def read(path):
    return json.loads(pathlib.Path(path).read_text())

def atomic(path, value, uid=None):
    if uid is None: uid=os.getuid()
    path = pathlib.Path(path)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.pending-')
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w') as out:
            json.dump(value, out)
            out.flush(); os.fsync(out.fileno())
        os.chown(tmp, uid, uid)
        os.replace(tmp, path)
        d = os.open(path.parent, os.O_RDONLY); os.fsync(d); os.close(d)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def text_once(path, value, uid=0):
    path = pathlib.Path(path)
    if path.exists():
        if path.read_text() != value: raise ValueError('secret_divergence')
        return
    # Enclosing directory is private; atomic publication never exposes partial data.
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.pending-')
    with os.fdopen(fd, 'w') as f:
        f.write(value); f.flush(); os.fsync(f.fileno())
    os.chmod(tmp, 0o600); os.chown(tmp, uid, uid); os.replace(tmp, path)
