"""Upload a locally saved Application through the account library's exact sync API."""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import struct
import tempfile
import zipfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from . import account_credentials
from .account import AccountError, AccountSession, account_server, binding_from, valid_id
from .recording import MAIN_TEMPLATE, ActionSession, _lock_record

_ARCHIVE_LIMIT = 64 * 1024 * 1024
_APPLICATION_FILES = ("app.json", f"{MAIN_TEMPLATE}.json")
_STAGING_PREFIX = ".aivane-save-"
_BAD_RECEIPT = "The library returned an unexpected upload receipt."
_WRONG_BINDING = "This upload belongs to a different account server, account, tenant or workspace."


def _modified_utf8(utf16: bytes) -> bytes:
    # Java writeUTF encodes UTF-16 units, including NUL and each half of a surrogate pair.
    encoded = bytearray()
    for (unit,) in struct.iter_unpack(">H", utf16):
        if 0 < unit < 0x80:
            encoded.append(unit)
        elif unit < 0x800:
            encoded.extend((0xC0 | (unit >> 6), 0x80 | (unit & 0x3F)))
        else:
            encoded.extend((0xE0 | (unit >> 12), 0x80 | ((unit >> 6) & 0x3F), 0x80 | (unit & 0x3F)))
    return struct.pack(">H", len(encoded)) + encoded


def tree_digest(package: zipfile.ZipFile) -> str:
    tree = hashlib.sha256()
    files = [entry for entry in package.infolist() if not entry.is_dir()]
    # Java's TreeMap orders strings by UTF-16 code unit.
    for entry in sorted(files, key=lambda item: item.filename.encode("utf-16-be")):
        content = hashlib.sha256()
        with package.open(entry) as handle:
            for block in iter(lambda: handle.read(64 * 1024), b""):
                content.update(block)
        tree.update(_modified_utf8(entry.filename.encode("utf-16-be")))
        tree.update(struct.pack(">Q", entry.file_size))
        tree.update(content.digest())
    return tree.hexdigest()


def _package_descriptor(data: bytes) -> dict:
    return {"sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}


def _read_package(handle) -> bytes:
    data = handle.read(_ARCHIVE_LIMIT + 1)
    if len(data) > _ARCHIVE_LIMIT:
        raise AccountError("The saved ZIP exceeds the 64 MiB library upload limit.")
    return data


@dataclass(frozen=True)
class UploadReceipt:
    automation_id: str
    revision_id: str
    change_seq: int | None


class PendingUpload:
    def __init__(self, path: Path, entry: dict, data: bytes):
        self.path = path
        self.entry = entry
        self.data = data

    def upload(self) -> UploadReceipt:
        session = AccountSession.load()
        if session is None:
            raise AccountError("Signed out. Run `agent-android sign-in --url ACCOUNT_SERVER`.")
        # A new device session is allowed after reauthentication. The owner and workspace are pinned.
        owner = {key: value for key, value in session.binding.items() if key != "deviceSessionId"}
        previous_binding = self.entry["binding"]
        if previous_binding is not None:
            previous_owner = {key: value for key, value in previous_binding.items() if key != "deviceSessionId"}
            if self.entry["server"] != session.server or previous_owner != owner:
                raise AccountError(_WRONG_BINDING)
        self.entry.update(server=session.server, binding=session.binding)
        account_credentials.write_private_json(self.path, self.entry)

        session = session.renew()
        api = session.api()
        automation_id = self.entry["automationId"]
        request = self.entry["request"]
        revision = request["revisionId"]
        requests_path = f"/api/library/upload-requests/{request['clientRequestId']}"
        automation_path = f"/api/library/automations/{automation_id}"
        revisions_path = f"{automation_path}/revisions"

        if previous_binding is not None:
            outcome = api.request("GET", requests_path)
            if outcome.get("status") == "committed":
                return self._commit_receipt(outcome.get("result"))
            if outcome.get("status") not in ("not-found", "pending"):
                raise AccountError(_BAD_RECEIPT)

        prepared = api.request("POST", revisions_path, request)
        parts = prepared.get("requiredParts")
        if parts not in ([], ["package"]) or prepared.get("missingImages") != []:
            raise AccountError("The library requested unsupported upload parts.")
        if prepared.get("state") == "already_synced" and parts == []:
            outcome = api.request("GET", requests_path)
            if outcome.get("status") == "committed":
                return self._commit_receipt(outcome.get("result"))
            if outcome.get("status") not in ("not-found", "pending"):
                raise AccountError(_BAD_RECEIPT)
            current = api.request("GET", f"{automation_path}/sync-head")
            if binding_from(current) != session.binding:
                raise AccountError(_WRONG_BINDING)
            head = current.get("head")
            if current.get("headRevisionId") != revision:
                raise AccountError("The library head changed (SYNC_CONFLICT).")
            if (
                not isinstance(head, dict) or head != prepared.get("head") or current.get("state") != "active"
                or head.get("revisionId") != revision or head.get("treeDigest") != request["digest"]
                or head.get("package") != request["package"]
                or head.get("representation") != "exact"
            ):
                raise AccountError(_BAD_RECEIPT)
            return UploadReceipt(automation_id, revision, None)
        if prepared.get("state") != "pending":
            raise AccountError(_BAD_RECEIPT)
        if parts:
            api.request("PUT", f"{revisions_path}/{revision}/package", self.data, sha256=request["package"]["sha256"])
        return self._commit_receipt(api.request("POST", f"{revisions_path}/{revision}/commit", {}))

    def _commit_receipt(self, result: dict | None) -> UploadReceipt:
        if isinstance(result, dict):
            head = result.get("head")
            sequence = result.get("changeSeq")
            if (
                isinstance(head, dict) and head.get("revisionId") == self.entry["request"]["revisionId"]
                and type(sequence) is int and sequence > 0
            ):
                return UploadReceipt(self.entry["automationId"], head["revisionId"], sequence)
        raise AccountError(_BAD_RECEIPT)


def _load_entry(path: Path, source: list[str], targets: list[str]) -> dict | None:
    try:
        entry = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except ValueError:
        raise AccountError("Could not read the upload journal.") from None
    try:
        if entry["source"] != source:
            raise AccountError("This output belongs to a different recording session.")
        if "targets" in entry:
            staging = entry["staging"]
            if entry["targets"] != targets or not staging.startswith(_STAGING_PREFIX) or Path(staging).name != staging:
                raise ValueError
        request = entry["request"]
        if not all(valid_id(value) for value in (entry["automationId"], request["clientRequestId"], request["revisionId"])):
            raise ValueError
        if request["parentRevisionId"] is not None or request["definitionFormat"] != "exact-v1":
            raise ValueError
        if entry["binding"] is not None:
            binding_from(entry["binding"])
            account_server(entry["server"])
    except (AttributeError, KeyError, TypeError, ValueError):
        raise AccountError("Could not read the upload journal.") from None
    return entry


def _require_absent(directory: Path, zip_path: Path) -> None:
    for path in (directory, zip_path):
        if os.path.lexists(path):
            raise FileExistsError(f"The save output already exists: {path}")


def _publish_application(staging: Path, directory: Path, zip_path: Path) -> None:
    staged_directory = staging / directory.name
    if staged_directory.is_dir():
        _require_absent(directory, zip_path)
        staged_directory.rename(directory)
    if staging.is_dir():
        (staging / zip_path.name).unlink(missing_ok=True)
        staging.rmdir()


def _publish_zip(data: bytes, zip_path: Path, entry: dict) -> None:
    # The journal owns this temporary path, even if a process died while copying to it.
    temporary = zip_path.with_name(f".aivane-upload-{entry['automationId']}.tmp")
    temporary.unlink(missing_ok=True)
    try:
        with temporary.open("xb") as package:
            shutil.copyfileobj(io.BytesIO(data), package)
        temporary.replace(zip_path)
    finally:
        temporary.unlink(missing_ok=True)


def _rebuild_package(directory: Path, entry: dict, journal: Path) -> bytes:
    metadata = entry.get("zipEntries")
    request = entry["request"]
    with tempfile.TemporaryFile() as output:
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name in _APPLICATION_FILES:
                path = directory / name
                if metadata is None:
                    archive.write(path, name)
                    continue
                # Keep the original ZIP header fields even if the file timestamps changed.
                saved = metadata[name]
                info = zipfile.ZipInfo(name, tuple(saved["dateTime"]))
                info.create_system = saved["createSystem"]
                info.external_attr = saved["externalAttr"]
                info.compress_type = zipfile.ZIP_DEFLATED
                with path.open("rb") as original:
                    info.file_size = os.fstat(original.fileno()).st_size
                    with archive.open(info, "w") as bundled:
                        shutil.copyfileobj(original, bundled)
        output.seek(0)
        data = _read_package(output)
        descriptor = _package_descriptor(data)
        if descriptor == request["package"]:
            return data
        # Older journals did not preserve the ZIP headers. An unbound request has never
        # been sent, so it can use rebuilt bytes if the Application contents still match.
        if metadata is None and entry["binding"] is None:
            with zipfile.ZipFile(output) as archive:
                if tree_digest(archive) == request["digest"]:
                    request["package"] = descriptor
                    account_credentials.write_private_json(journal, entry)
                    return data
    raise AccountError("Could not recreate the original ZIP from the saved Application directory.")


def _resume_saved(directory: Path, zip_path: Path, journal: Path, entry: dict) -> bytes:
    if "staging" in entry:
        _publish_application(directory.parent / entry["staging"], directory, zip_path)
    if not directory.is_dir():
        raise AccountError("The journaled Application directory is missing.")
    try:
        with zip_path.open("rb") as original:
            data = _read_package(original)
    except (FileNotFoundError, AccountError):
        pass
    else:
        if _package_descriptor(data) == entry["request"]["package"]:
            return data
    data = _rebuild_package(directory, entry, journal)
    _publish_zip(data, zip_path, entry)
    return data


def _new_entry(source: list[str], data: bytes) -> dict:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            digest = tree_digest(archive)
            name = json.loads(archive.read("app.json"))["applicationName"]
            metadata = {
                info.filename: {"dateTime": info.date_time, "createSystem": info.create_system, "externalAttr": info.external_attr}
                for info in archive.infolist()
            }
    except (ValueError, KeyError, TypeError, zipfile.BadZipFile):
        raise AccountError("Could not read the saved Application ZIP.") from None
    return {
        "source": source,
        "server": None,
        "binding": None,
        "automationId": str(uuid4()),
        "zipEntries": metadata,
        "request": {
            "clientRequestId": str(uuid4()),
            "revisionId": str(uuid4()),
            "parentRevisionId": None,
            "definitionFormat": "exact-v1",
            "name": name,
            "digest": digest,
            "package": _package_descriptor(data),
        },
    }


@contextmanager
def pending_upload(session: ActionSession, directory: Path):
    directory = directory.expanduser().resolve()
    zip_path = directory.with_name(directory.name + ".zip")
    source = [session.path.parent.name, session.name]
    targets = [os.path.normcase(path) for path in (directory, zip_path)]
    key = hashlib.sha256(os.fsencode(targets[0])).hexdigest()
    journal = account_credentials.state_directory() / "uploads" / f"{key}.json"
    journal.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    # The permanent lock file serializes retries. The journal can be atomically replaced under it.
    with journal.with_suffix(".lock").open("a+b") as lock:
        _lock_record(lock)
        entry = _load_entry(journal, source, targets)
        if entry is not None:
            data = _resume_saved(directory, zip_path, journal, entry)
            yield PendingUpload(journal, entry, data), None
            return

        _require_absent(directory, zip_path)
        directory.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=_STAGING_PREFIX, dir=directory.parent))
        try:
            staged_zip = session.save(staging / directory.name)
            try:
                with staged_zip.open("rb") as original:
                    data = _read_package(original)
                entry = _new_entry(source, data)
            except AccountError:
                _require_absent(directory, zip_path)
                staged_zip.with_suffix("").rename(directory)
                staged_zip.rename(zip_path)
                raise
            _require_absent(directory, zip_path)
            entry.update(targets=targets, staging=staging.name)
            account_credentials.write_private_json(journal, entry)
            _publish_application(staging, directory, zip_path)
        finally:
            if not journal.exists():
                shutil.rmtree(staging)
        _publish_zip(data, zip_path, entry)
        yield PendingUpload(journal, entry, data), zip_path
