"""Verify and unpack a current organizer bundle without running its contents."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
RECEIPT = ".test-bundle-receipt.json"


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            value.update(block)
    return value.hexdigest()


def source_name(name):
    """Return one unambiguous, relative archive/receipt path."""
    if not isinstance(name, str):
        raise ValueError("Invalid source path")
    path = PurePosixPath(name)
    if (not path.parts or path.is_absolute() or ".." in path.parts
            or "\\" in name or ":" in name or "\0" in name
            or path.parts[0] == RECEIPT):
        raise ValueError("Unsafe archive or receipt path")
    return path.as_posix()


def local_source(destination, name):
    local = destination.joinpath(*PurePosixPath(name).parts)
    # Refuse links in either a source file or its parents, including links that
    # lead elsewhere inside the same bundle. They are not receipt-owned files.
    if local.is_symlink() or local.resolve() != local:
        raise FileExistsError("A source path contains a symbolic link or redirected directory; choose a new --target")
    return local


def inspect_archive(archive):
    members, files = {}, {}
    for member in archive.infolist():
        name = source_name(member.filename)
        if name in members:
            raise ValueError("Duplicate paths in archive")
        mode = member.external_attr >> 16
        if stat.S_ISLNK(mode):
            raise ValueError("Unsafe archive symbolic link")
        members[name] = member
    file_names = {name for name, member in members.items() if not member.is_dir()}
    for name in members:
        if any(str(parent) in file_names for parent in PurePosixPath(name).parents):
            raise ValueError("Archive file and directory paths conflict")
    if archive.testzip() is not None:
        raise ValueError("Archive integrity check failed")
    for name in sorted(file_names):
        value = hashlib.sha256()
        with archive.open(members[name]) as stream:
            for block in iter(lambda: stream.read(1024*1024), b""):
                value.update(block)
        files[name] = value.hexdigest()
    return members, files


def existing_changes(destination, bundle, archive_sha256, files, members, refresh):
    """Validate every existing source and collision before changing any file."""
    if not destination.exists() or not any(destination.iterdir()):
        if refresh:
            raise FileExistsError("Refresh requires an existing prepared bundle receipt; omit --refresh for a first extraction")
        return "prepared", sorted(files)
    receipt = local_source(destination, RECEIPT)
    if not receipt.is_file():
        raise FileExistsError("Target is not empty and has no matching receipt; choose a new --target. Nothing was overwritten")
    previous = json.loads(receipt.read_text(encoding="utf-8"))
    if not isinstance(previous, dict):
        raise ValueError("Invalid bundle receipt; choose a new --target")
    old_files = previous.get("files")
    if (previous.get("bundle") != bundle or not isinstance(old_files, dict)
            or not isinstance(previous.get("archive_sha256"), str)):
        raise ValueError("Invalid or different bundle receipt; choose a new --target")
    for name, expected in old_files.items():
        if (source_name(name) != name or not isinstance(expected, str)
                or len(expected) != 64 or any(char not in "0123456789abcdef" for char in expected)):
            raise ValueError("Invalid source hash or path in bundle receipt")
    same_archive = previous["archive_sha256"] == archive_sha256
    if not same_archive and not refresh:
        raise FileExistsError("Target belongs to another bundle; choose a new --target or explicitly use --refresh")
    if set(old_files) - set(files):
        raise FileExistsError("The new bundle removes source files; preserve this target and choose a new --target")
    if same_archive and old_files != files:
        raise ValueError("Receipt source list does not match the verified archive; choose a new --target")
    updates = []
    for name, expected in old_files.items():
        local = local_source(destination, name)
        if not local.is_file():
            raise FileExistsError("An extracted source file is missing or changed; preserve your work and choose a new --target")
        actual = digest(local)
        if actual != expected and (not refresh or actual != files[name]):
            raise FileExistsError("An extracted source file changed; preserve your work and choose a new --target")
        if actual != files[name]:
            updates.append(name)
    for name in set(files) - set(old_files):
        top = PurePosixPath(name).parts[0]
        if refresh and (top.startswith(".venv") or top.startswith("venv-")
                        or top.startswith("build-vllm-cu128.")
                        or top in {"venv", "logs", "results", "cache", ".cache"}):
            raise FileExistsError("A new source would enter an environment, log, result or cache directory; choose a new --target")
        local = local_source(destination, name)
        if local.exists():
            raise FileExistsError("A new bundle source collides with an existing file or directory; choose a new --target. Nothing was overwritten")
        updates.append(name)
    directories = {str(parent) for name in members for parent in PurePosixPath(name).parents if str(parent) != "."}
    directories.update(name for name, member in members.items() if member.is_dir())
    for name in directories:
        local = local_source(destination, name)
        if local.exists() and not local.is_dir():
            raise FileExistsError("A bundle directory collides with an existing file; choose a new --target. Nothing was overwritten")
    return ("already_prepared_files_unchanged" if same_archive else "refreshed"), sorted(updates)


def prepare(bundle, target=None, *, repository_root=ROOT, refresh=False):
    root = Path(repository_root).resolve()
    catalogue = json.loads((root/"packages.json").read_text(encoding="utf-8"))
    record = catalogue["packages"].get(bundle)
    if record is None or record["status"] != "current":
        raise ValueError("Choose a current bundle: 4090, h200, runtime, or starter")
    source = (root/record["file"]).resolve()
    if not source.is_relative_to(root) or not source.is_file():
        raise FileNotFoundError("Bundle archive missing inside the cloned test repository")
    if digest(source) != record["sha256"]:
        raise ValueError("Archive checksum mismatch. Fetch the complete repository again before extracting")
    destination = Path(target).expanduser().resolve() if target else root.parent/record["extract_dir"]
    if destination == root or destination.is_relative_to(root):
        raise ValueError("Choose an extraction directory outside the cloned assets repository")
    if destination.exists() and not destination.is_dir():
        raise ValueError("Extraction target exists and is not a directory")
    with zipfile.ZipFile(source) as archive:
        members, files = inspect_archive(archive)
        status, updates = existing_changes(destination, bundle, record["sha256"], files, members, refresh)
        if status != "already_prepared_files_unchanged":
            destination.mkdir(parents=True, mode=0o700, exist_ok=True)
            # Stage on the target filesystem so every source and the receipt can
            # be published with an atomic rename. Validation failures above leave
            # all source files, environments, caches and results untouched.
            with tempfile.TemporaryDirectory(prefix=".test-bundle-stage-", dir=destination) as staging:
                stage = Path(staging)
                for name in updates:
                    member = members[name]
                    output = stage/"sources"/name
                    output.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
                    with archive.open(member) as incoming, output.open("xb") as outgoing:
                        shutil.copyfileobj(incoming, outgoing)
                    output.chmod(0o700 if (member.external_attr >> 16) & 0o111 else 0o600)
                receipt = stage/"receipt.json"
                receipt.write_text(json.dumps({"bundle": bundle, "archive_sha256": record["sha256"], "files": files}, indent=2), encoding="utf-8")
                receipt.chmod(0o600)
                for name in updates:
                    output = destination/name
                    output.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
                    os.replace(stage/"sources"/name, output)
                for name, member in members.items():
                    if member.is_dir():
                        (destination/name).mkdir(parents=True, mode=0o700, exist_ok=True)
                os.replace(receipt, destination/RECEIPT)
    return {"bundle": bundle, "status": status, "extracted_to": str(destination),
        "source_files_updated": len(updates),
        "environment_script": str(destination/"env_open_models.sh") if (destination/"env_open_models.sh").is_file() else None,
        "model_physics_or_api_calls": 0, "existing_results_overwritten": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", choices=("4090", "h200", "runtime", "starter"), default="4090")
    parser.add_argument("--target", type=Path)
    parser.add_argument("--refresh", action="store_true", help="Update receipt-owned source files while preserving environments, caches and results")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(prepare(args.bundle, args.target, refresh=args.refresh), ensure_ascii=False, indent=2))
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        parser.exit(2, "Preparation stopped: "+str(exc)+"\n")


if __name__ == "__main__":
    main()
