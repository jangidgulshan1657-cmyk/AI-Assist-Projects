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
import subprocess
import shutil
import sys
import time
from pathlib import Path

Log_dic = Path.home()/".local/share/pc-toolkit"
Log_file = Log_dic/"watcher.log"

HAS_NOTIFY = shutil.which("notify-send") is not None

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
    "Fonts": [".ttf", ".otf", ".woff", ".woff2", ".eot"],
    "E-Books": [".epub", ".mobi", ".azw", ".azw3", ".djvu", ".cbr", ".cbz"],
    "Torrents": [".torrent"],
    "Data": [".csv", ".tsv", ".parquet", ".sql", ".sqlite", ".db", ".feather"],
    "Design": [".psd", ".ai", ".eps", ".xcf", ".sketch", ".fig", ".kra"],
    "ROMs": [".nes", ".sfc", ".smc", ".gba", ".gbc", ".nds", ".n64", ".z64"]
}

def log(message):
    print(message)
    try:
        Log_dic.mkdir(parents=True,exist_ok= True)
        with open(Log_file,'a',encoding="utf-8") as f:
            f.write(message + "\n")
            f.flush()
    except OSError as err:
        print(f"Error in opening the file-- {err}")


def notify(title,message):
    if not HAS_NOTIFY:
        return
    try:
        subprocess.run(
            ["notify-send",title,message],
            check= False,
            stderr=subprocess.DEVNULL
            )
    except OSError as e:
        pass

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
    return time.strftime("%Y-%m-%d %H:%M:%S")


def handle(item, folder, dry_run):
    target_dir = folder / category_for(item)
    target = target_dir / item.name

    if target.exists():
        log(f"{stamp()}  SKIP   {item.name}  (already a file with that name in {target_dir.name}/)")
        return "skipped"

    if dry_run:
        log(f"{stamp()}  WOULD MOVE  {item.name}  ->  {target_dir.name}/")
        return "moved"

    try:
        target_dir.mkdir(exist_ok=True)
        shutil.move(str(item), str(target))
    except OSError as error:
        log(f"{stamp()}  ERROR  {item.name}: {error}")
        return "error"
    log(f"{stamp()}  MOVED  {item.name}  ->  {target_dir.name}/")
    notify("File Organized",f"MOVED  {item.name}  ->  {target_dir.name}/")
    return "moved"


def main():
    args = sys.argv[1:]

    # 1. Handle --run flag
    dry_run = True
    if "--run" in args:
        dry_run = False
        args.remove("--run")

    # 2. Handle --every <seconds>
    check_every = 2  # default value
    if "--every" in args:
        idx = args.index("--every")
        try:
            check_every = int(args[idx + 1])
            # Remove both '--every' and its number so they aren't confused for a folder path
            del args[idx:idx + 2]
        except (IndexError, ValueError):
            print("Error: --every requires a numeric value (e.g., --every 5)")
            return

    
    if len(args) > 0:
        folder = Path(args[0]).expanduser().resolve()
    else:
        folder = Path.home() / "Downloads"

    if not folder.is_dir():
        print(f"{folder} is not a folder.")
        return

    last_sizes = {}  # file name -> its size when we last looked
    done = set()     # names we already handled (or chose to ignore)

    # Files that are already here when we start are not "new". Ignore them.
    for item in folder.iterdir():
        done.add(item.name)
    
    print(f"Dry run: {dry_run}")
    print(f"Check interval: {check_every}s")
    print(f"Target folder: {folder}")

    if dry_run:
        mode = "DRY-RUN, nothing will be moved"
    else:
        mode = "LIVE, new files will be moved"
    print(f"\nWatching {folder}  [{mode}]  Ctrl+C to stop.")

    skipped_count = 0
    moved_count = 0

    try:
        while True:
            present = set()

            for item in folder.iterdir():
                present.add(item.name)
                if item.name in done:
                    continue
                if should_skip(item):
                    skipped_count += 1
                    continue
                try:
                    size = item.stat().st_size
                except OSError:
                    continue  # file vanished between listing and checking

                # Same size as last look = nothing is writing to it any more.
                if last_sizes.get(item.name) == size:
                    status = handle(item, folder, dry_run)
                    if status == "moved":
                        moved_count += 1
                    elif status == "skipped":
                        skipped_count +=1
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

            time.sleep(check_every)

    except KeyboardInterrupt:
        prefix = "Would have " if dry_run else ""
        print("\n----Stopped----")
        print(f"{prefix}Moved {moved_count} {prefix} Skipped {skipped_count}")

main()