"""Small cross-platform advisory file lock.

The persistent fleet has several worker processes and one supervisor.  They
share a usage ledger, a quota directory, and a merged proof-attempt ledger.
Writes are read-modify-write, so they must be serialized across processes.

Only the standard library is used: ``msvcrt`` on Windows and ``fcntl`` on
POSIX.  A lock is a byte in a sidecar file; the data file itself is still
written with an atomic ``os.replace``.
"""
from __future__ import annotations

import os
import time


class FileLockTimeout(TimeoutError):
    pass


class FileLock:
    def __init__(self, path: str, timeout: float = 20.0,
                 poll: float = 0.05):
        self.path = path
        self.timeout = max(0.1, float(timeout))
        self.poll = max(0.01, float(poll))
        self.fd: int | None = None

    def __enter__(self) -> "FileLock":
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        self.fd = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o600)
        deadline = time.time() + self.timeout
        while True:
            try:
                if os.name == "nt":
                    import msvcrt

                    if os.fstat(self.fd).st_size == 0:
                        os.write(self.fd, b"\0")
                    os.lseek(self.fd, 0, os.SEEK_SET)
                    msvcrt.locking(self.fd, msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except OSError as exc:
                if time.time() >= deadline:
                    os.close(self.fd)
                    self.fd = None
                    raise FileLockTimeout(
                        f"could not lock {self.path} within "
                        f"{self.timeout:.1f}s") from exc
                time.sleep(self.poll)

    def __exit__(self, *_exc) -> None:
        if self.fd is None:
            return
        try:
            if os.name == "nt":
                import msvcrt

                os.lseek(self.fd, 0, os.SEEK_SET)
                msvcrt.locking(self.fd, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.fd, fcntl.LOCK_UN)
        except OSError:
            pass
        finally:
            os.close(self.fd)
            self.fd = None
