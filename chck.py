#!/usr/bin/env python3
import hashlib
import json
import pathlib
import argparse
import datetime


def get_checksum(file: pathlib.Path, limit=None) -> str:
    hash = hashlib.sha256()
    size = limit if limit else file.stat().st_size
    blocksize = 4096 if size > 4096 else 1
    blocks_sizes = size // blocksize * [blocksize]
    blocks_sizes.append(size % blocksize)
    with file.open("rb") as f:
        for block in blocks_sizes:
            hash.update(f.read(block))
    return hash.hexdigest()


def check_file(file: pathlib.Path, ignore_mtime: bool, files_history: dict) -> dict:
    filepath = str(file)
    if not file.is_file():
        return {
            "status": "ignored (not a file)",
            "size": "-",
            "checksum": "-",
            "mtime": "-",
        }
    stat = file.stat()
    size = stat.st_size
    mtime = stat.st_mtime
    if filepath in files_history and files_history[filepath]["status"] != "removed":
        if ignore_mtime and files_history[filepath]["mtime"] == mtime:
            new_history = files_history[filepath]
            new_history["status"] = "ignored (mtime unchanged)"
            return files_history[filepath]
        checksum = get_checksum(file)
        if files_history[filepath]["checksum"] == checksum:
            status = "unchanged"
        elif files_history[filepath]["checksum"] == get_checksum(
            file, limit=files_history[filepath]["size"]
        ):
            status = "changed (appended to)"
        else:
            status = "changed (modified)"
    else:
        checksum = get_checksum(file)
        status = "new"
    return {
        "size": size,
        "checksum": checksum,
        "status": status,
        "mtime": mtime,
    }


def main(
    directory: str, history_file: str, glob: str, ignore_mtime: bool, verbose: bool
):
    files = {}
    try:
        with open(history_file, "r") as f:
            files_history = json.loads(f.read())
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        files_history = {}
    if verbose:
        print(f"{'STATUS':<26}{'SIZE':<10}{'CHECKSUM':<65}PATH")
    for file in pathlib.Path(directory).glob(glob):
        result = check_file(file, ignore_mtime, files_history)
        if verbose:
            print(
                f"{result['status']:<26}{result['size']:<10}{result['checksum']:<65}{str(file)}"
            )
        files[str(file)] = result
    for file in files_history.keys():
        if file not in files and files_history[file]["status"] != "removed":
            files[str(file)] = {"status": "removed"}
            if verbose:
                print(f"{'removed':<26}{'-':<10}{'-':<65}{str(file)}")
    try:
        history_path = pathlib.Path(history_file)
        history_path.rename(
            history_path.with_suffix(
                f".bak-{str(datetime.datetime.now()).replace(' ', '-')}"
            )
        )
    except FileNotFoundError:
        pass
    with open(history_file, "w+") as f:
        f.write(json.dumps(files, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Checks files for changes since last run"
    )
    parser.add_argument("DIRECTORY", help="directory path")
    parser.add_argument("HISTORY_FILE", help="history file path")
    parser.add_argument("-g", "--glob", help="files glob pattern", default="*")
    parser.add_argument(
        "-m",
        "--mtime",
        help="ignore files whose mtime hasn't changed",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="show files during processing",
        action="store_true",
    )
    args = parser.parse_args()
    main(args.DIRECTORY, args.HISTORY_FILE, args.glob, args.mtime, args.verbose)
