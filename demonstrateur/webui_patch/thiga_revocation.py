"""Standalone single-worker revocation store. A missing or rolled-back member denies access."""

import hashlib
import os
import re
import secrets
import sqlite3
import sys
import tempfile
import threading
import time
from contextlib import closing
from pathlib import Path


class Revocations:
    def __init__(self, path: Path):
        self.path = path
        self.checkpoint = path.with_suffix(path.suffix + '.state')
        self.lock = threading.RLock()

    def _connect(self):
        if self.path.is_symlink() or not self.path.is_file():
            raise ValueError('revocation registry unavailable')
        return sqlite3.connect(self.path.as_uri() + '?mode=rw', uri=True, timeout=4)

    def _write_checkpoint(self, epoch):
        fd, name = tempfile.mkstemp(dir=self.path.parent, prefix='.revocation-')
        pending = Path(name)
        try:
            with os.fdopen(fd, 'w', encoding='ascii') as stream:
                stream.write(epoch + '\n')
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(pending, self.checkpoint)
            if os.name == 'posix':
                directory = os.open(self.path.parent, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
        finally:
            pending.unlink(missing_ok=True)

    def _check(self, db):
        if self.checkpoint.is_symlink() or not self.checkpoint.is_file():
            raise ValueError('revocation checkpoint unavailable')
        with self.checkpoint.open(encoding='ascii') as stream:
            epoch = stream.read(66)
        if not re.fullmatch(r'[a-f0-9]{64}\n', epoch):
            raise ValueError('invalid revocation checkpoint')
        if db.execute('SELECT epoch FROM registry WHERE id = 1').fetchone() != (epoch.rstrip(),):
            raise ValueError('revocation checkpoint mismatch')

    def prepare(self, app_db: Path):
        """Create once, before first WebUI startup. Require a valid pair on any later startup."""
        with self.lock:
            if not any(os.path.lexists(path) for path in (self.path, self.checkpoint, app_db)):
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                os.close(fd)
                epoch = secrets.token_hex(32)
                with closing(self._connect()) as db, db:
                    db.execute(
                        'CREATE TABLE revoked (fingerprint TEXT PRIMARY KEY, expires INTEGER) WITHOUT ROWID'
                    )
                    db.execute('CREATE INDEX revoked_expiry ON revoked(expires)')
                    db.execute('CREATE TABLE registry (id INTEGER PRIMARY KEY CHECK (id = 1), epoch TEXT NOT NULL)')
                    db.execute('INSERT INTO registry VALUES (1, ?)', (epoch,))
                self._write_checkpoint(epoch)
            with closing(self._connect()) as db:
                self._check(db)

    @staticmethod
    def _key(jti: str):
        if not isinstance(jti, str) or not 0 < len(jti) <= 128:
            raise ValueError('invalid session identifier')
        return hashlib.sha256(jti.encode('utf-8')).hexdigest()

    def revoked(self, jti: str, now=None):
        key = self._key(jti)
        now = int(time.time()) if now is None else now
        with self.lock, closing(self._connect()) as db, db:
            self._check(db)
            return db.execute(
                'SELECT 1 FROM revoked WHERE fingerprint = ? AND (expires IS NULL OR expires > ?)',
                (key, now),
            ).fetchone() is not None

    def revoke(self, jti: str, expires, now=None):
        key = self._key(jti)
        now = int(time.time()) if now is None else now
        if expires is not None and type(expires) is not int:
            raise ValueError('invalid session expiration')
        epoch = secrets.token_hex(32)
        with self.lock:
            with closing(self._connect()) as db, db:
                self._check(db)
                db.execute('DELETE FROM revoked WHERE expires <= ?', (now,))
                if expires is None or expires > now:
                    db.execute(
                        'INSERT OR IGNORE INTO revoked(fingerprint, expires) VALUES (?, ?)',
                        (key, expires),
                    )
                db.execute('UPDATE registry SET epoch = ? WHERE id = 1', (epoch,))
            # A crash between the commit and this rename leaves a mismatch, so access remains closed.
            self._write_checkpoint(epoch)


if __name__ == '__main__':
    data = Path('/app/backend/data')
    try:
        if sys.argv[1:] != ['prepare']:
            sys.exit(2)
        Revocations(data / 'thiga_session_revocations.sqlite3').prepare(data / 'webui.db')
    except (OSError, sqlite3.Error, ValueError):
        sys.exit(1)
