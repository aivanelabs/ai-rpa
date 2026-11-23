"""Local storage for the account credential, separate from phone configuration."""
from __future__ import annotations

import ctypes
import json
import os
import stat
import tempfile
from pathlib import Path

CREDENTIAL_TARGET = "AIVane/agent-android/account"
ERROR_NOT_FOUND = 1168


def state_directory() -> Path:
    return Path.home() / ".aivane" / "agent-android"


def _credential_file() -> Path:
    return state_directory() / "account" / "session.json"


def write_private_json(path: Path, value: dict) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def load() -> dict | None:
    if os.name == "nt":
        raw = _windows_credential("read")
        return None if raw is None else json.loads(raw)
    try:
        fd = os.open(_credential_file(), os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return None
    with os.fdopen(fd, "r", encoding="utf-8") as handle:
        info = os.fstat(handle.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise OSError("Account credential file must be user-only")
        return json.load(handle)


def save(value: dict) -> None:
    if os.name == "nt":
        _windows_credential("write", json.dumps(value).encode("utf-8"))
    else:
        path = _credential_file()
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = path.parent.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise OSError("Account credential directory must be user-only")
        write_private_json(path, value)


def clear() -> None:
    if os.name == "nt":
        _windows_credential("delete")
    else:
        _credential_file().unlink(missing_ok=True)


def _windows_credential(operation: str, data: bytes = b"") -> bytes | None:
    from ctypes import wintypes

    class Credential(ctypes.Structure):
        _fields_ = [
            ("Flags", wintypes.DWORD),
            ("Type", wintypes.DWORD),
            ("TargetName", wintypes.LPWSTR),
            ("Comment", wintypes.LPWSTR),
            ("LastWritten", wintypes.FILETIME),
            ("CredentialBlobSize", wintypes.DWORD),
            ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
            ("Persist", wintypes.DWORD),
            ("AttributeCount", wintypes.DWORD),
            ("Attributes", ctypes.c_void_p),
            ("TargetAlias", wintypes.LPWSTR),
            ("UserName", wintypes.LPWSTR),
        ]

    api = ctypes.WinDLL("Advapi32", use_last_error=True)
    generic = 1  # CRED_TYPE_GENERIC
    if operation == "read":
        pointer = ctypes.POINTER(Credential)()
        api.CredReadW.argtypes = [
            wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
            ctypes.POINTER(ctypes.POINTER(Credential)),
        ]
        api.CredFree.argtypes = [ctypes.c_void_p]
        api.CredFree.restype = None
        if api.CredReadW(CREDENTIAL_TARGET, generic, 0, ctypes.byref(pointer)):
            try:
                return ctypes.string_at(pointer.contents.CredentialBlob, pointer.contents.CredentialBlobSize)
            finally:
                api.CredFree(pointer)
    elif operation == "write":
        blob = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
        item = Credential(
            Type=generic, TargetName=CREDENTIAL_TARGET, CredentialBlob=blob,
            CredentialBlobSize=len(data), Persist=2,  # CRED_PERSIST_LOCAL_MACHINE
        )
        api.CredWriteW.argtypes = [ctypes.POINTER(Credential), wintypes.DWORD]
        if api.CredWriteW(ctypes.byref(item), 0):
            return None
    else:
        api.CredDeleteW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD]
        if api.CredDeleteW(CREDENTIAL_TARGET, generic, 0):
            return None
    error = ctypes.get_last_error()
    if operation != "write" and error == ERROR_NOT_FOUND:
        return None
    raise ctypes.WinError(error)
