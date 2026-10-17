#!/usr/bin/env python3
"""watcher.py - Tool 3 of the PC toolkit.

Watches a folder. When a NEW file shows up, it waits until the file has
finished downloading, then sorts it into a subfolder by type.

Safe by default: it only PRINTS what it would do.
Add --run to really move files.

Usage:
    python3 watcher.py                   # watch ~/Downloads, dry-run
    python3 watcher.py --run             # watch ~/Downloads, really move
    python3 watcher.py /some/folder      # watch another folder

Stop it with Ctrl+C.
"""

import shutil
import sys
import time
from pathlib import Path

CHECK_EVERY = 2  # seconds between looks at the folder

# Browsers write to names like these while a download is still running.
UNFINISHED = [".crdownload", ".part", ".tmp", ".download", ".opdownload"]

# folder name -> the file endings that belong in it
CATEGORIES = {
    "Pictures": [".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".odt"],
    "Videos": [".mp4", ".mkv", ".webm", ".mov"],
    "Music": [".mp3", ".flac", ".wav", ".ogg"],
    "Archives": [".zip", ".tar", ".gz", ".xz", ".7z", ".rar"],
    "Disk Images": [".iso", ".img"],
    "Code": [".py", ".js", ".json", ".html", ".css", ".sh"],
    "Installers": [".rpm", ".deb", ".appimage"],
}


def category_for(item):
    # item.suffix is the file ending, e.g. "photo.PNG" -> ".PNG"
    ending = item.suffix.lower()
    for folder_name, endings in CATEGORIES.items():
        if ending in endings:
            return folder_name
    return "Other"


def should_skip(item):
    if item.name.startswith("."):
        return True  # hidden file
    if item.is_symlink() or not item.is_file():
        return True  # folders, shortcuts, broken links
    if item.suffix.lower() in UNFINISHED:
        return True  # download still in progress
    return False


def stamp():
    return time.strftime("%H:%M:%S")


def handle(item, folder, dry_run):
    target_dir = folder / category_for(item)
    target = target_dir / item.name

    if target.exists():
        print(f"{stamp()}  SKIP   {item.name}  (already a file with that name in {target_dir.name}/)")
        return

    if dry_run:
        print(f"{stamp()}  WOULD MOVE  {item.name}  ->  {target_dir.name}/")
        return

    try:
        target_dir.mkdir(exist_ok=True)
        shutil.move(str(item), str(target))
    except OSError as error:
        print(f"{stamp()}  ERROR  {item.name}: {error}")
        return
    print(f"{stamp()}  MOVED  {item.name}  ->  {target_dir.name}/")


def main():
    args = sys.argv[1:]

    dry_run = True
    if "--run" in args:
        dry_run = False
        args.remove("--run")

    folder = Path.home() / "Downloads"
    if len(args) > 0:
        folder = Path(args[0]).expanduser()

    if not folder.is_dir():
        print(f"{folder} is not a folder.")
        return

    last_sizes = {}  # file name -> its size when we last looked
    done = set()     # names we already handled (or chose to ignore)

    # Files that are already here when we start are not "new". Ignore them.
    for item in folder.iterdir():
        done.add(item.name)

    if dry_run:
        mode = "DRY-RUN, nothing will be moved"
    else:
        mode = "LIVE, new files will be moved"
    print(f"Watching {folder}  [{mode}]  Ctrl+C to stop.")

    try:
        while True:
            present = set()

            for item in folder.iterdir():
                present.add(item.name)

                if item.name in done or should_skip(item):
                    continue

                try:
                    size = item.stat().st_size
                except OSError:
                    continue  # file vanished between listing and checking

                # Same size as last look = nothing is writing to it any more.
                if last_sizes.get(item.name) == size:
                    handle(item, folder, dry_run)
                    done.add(item.name)
                else:
                    last_sizes[item.name] = size

            # Forget files that disappeared, so a later file with the
            # same name counts as new again.
            for name in list(done):
                if name not in present:
                    done.remove(name)
            for name in list(last_sizes):
                if name not in present:
                    del last_sizes[name]

            time.sleep(CHECK_EVERY)

    except KeyboardInterrupt:
        print("\nStopped.")


main()