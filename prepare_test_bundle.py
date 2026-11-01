"""Verify and unpack a current organizer bundle without running its contents."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import zipfile

ROOT = Path(__file__).resolve().parent
RECEIPT = ".test-bundle-receipt.json"


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            value.update(block)
    return value.hexdigest()


def prepare(bundle, target=None, *, repository_root=ROOT):
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
    if destination.exists() and any(destination.iterdir()):
        receipt = destination/RECEIPT
        if not receipt.is_file():
            raise FileExistsError("Target is not empty and has no matching receipt; choose a new --target. Nothing was overwritten")
        previous = json.loads(receipt.read_text(encoding="utf-8"))
        if previous.get("archive_sha256") != record["sha256"]:
            raise FileExistsError("Target belongs to another bundle; choose a new --target")
        for name, expected in previous["files"].items():
            local = destination/name
            if not local.is_file() or digest(local) != expected:
                raise FileExistsError("An extracted source file changed; preserve your work and choose a new --target")
        status = "already_prepared_files_unchanged"
    else:
        with zipfile.ZipFile(source) as archive:
            members = archive.infolist()
            if len({member.filename for member in members}) != len(members):
                raise ValueError("Duplicate paths in archive")
            for member in members:
                path = PurePosixPath(member.filename)
                mode = member.external_attr >> 16
                if (path.is_absolute() or ".." in path.parts or "\\" in member.filename
                        or ":" in member.filename or stat.S_ISLNK(mode)):
                    raise ValueError("Unsafe archive path or symbolic link")
            if archive.testzip() is not None:
                raise ValueError("Archive integrity check failed")
            destination.mkdir(parents=True, mode=0o700, exist_ok=True)
            files = {}
            for member in members:
                output = destination/member.filename
                if member.is_dir():
                    output.mkdir(parents=True, mode=0o700, exist_ok=True)
                    continue
                output.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
                with archive.open(member) as incoming, output.open("xb") as outgoing:
                    shutil.copyfileobj(incoming, outgoing)
                output.chmod(0o700 if (member.external_attr >> 16) & 0o111 else 0o600)
                files[member.filename] = digest(output)
        with (destination/RECEIPT).open("x", encoding="utf-8") as stream:
            json.dump({"bundle": bundle, "archive_sha256": record["sha256"], "files": files}, stream, indent=2)
        status = "prepared"
    return {"bundle": bundle, "status": status, "extracted_to": str(destination),
        "environment_script": str(destination/"env_open_models.sh") if (destination/"env_open_models.sh").is_file() else None,
        "model_physics_or_api_calls": 0, "existing_results_overwritten": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", choices=("4090", "h200", "runtime", "starter"), default="4090")
    parser.add_argument("--target", type=Path)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(prepare(args.bundle, args.target), ensure_ascii=False, indent=2))
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        parser.exit(2, "Preparation stopped: "+str(exc)+"\n")


if __name__ == "__main__":
    main()
