#!/usr/bin/env python3
"""diskhog.py - Tool 2 of the PC toolkit.

Answers one question: "what is eating my disk?"
It walks through a folder, adds up file sizes, and shows the biggest
folders and the biggest single files.

Usage:
    python3 diskhog.py                  # scans your home folder
    python3 diskhog.py /mnt/hdd1        # scans any folder you give it

It only READS. It never changes or deletes anything.
"""

import os
import sys

# These look like folders but are not real files on disk. Skip them.
SKIP: list[str] = ["/proc", "/sys", "/dev", "/run"]

# Any single file at least this big gets remembered for the "big files" list.
BIG_FILE: int = 100 * 1024 * 1024  # 100 MB


def human(n_bytes: int | float) -> str:
    # Turns 1572864 into "1.5 MB"
    size = float(n_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size = size / 1024
    return f"{size:.1f} TB"


def bar(percent: float, width: int = 20) -> str:
    # Same helper as in sysinfo.py (we copy it for now).
    filled = int(percent / 100 * width)
    return "#" * filled + "-" * (width - filled)


def folder_size(top: str, big_files: list[tuple[int, str]]) -> tuple[int, int]:
    # os.walk visits `top` and every folder inside it, however deep.
    # Each step gives us: the folder's path, its subfolders, its files.
    total_size = 0
    total_files = 0

    for folder, subfolders, files in os.walk(top):
        for name in files:
            full = os.path.join(folder, name)
            try:
                if os.path.islink(full):
                    continue  # a shortcut, not a real file: counting it would lie
                size = os.path.getsize(full)
            except OSError:
                continue  # file vanished or we are not allowed to look
            total_files += 1
            total_size += size
            if size >= BIG_FILE:
                big_files.append((size, full))

    return total_size,total_files


def main() -> None:
    root = os.path.expanduser("~")  # "~" becomes /home/yourname
    if len(sys.argv) > 1:
        root = sys.argv[1]

    if not os.path.isdir(root):
        print(f"{root} is not a folder.")
        return

    print(f"Scanning {root} ... this can take a minute.")

    results: list[tuple[int, str, int]] = []     # one (size, name,total_files) pair per item directly inside root
    big_files: list[tuple[int, str]] = []   # (size, path) for every file over BIG_FILE
    grand_total = 0

    for name in os.listdir(root):
        full = os.path.join(root, name)
        if full in SKIP or os.path.islink(full):
            continue

        if os.path.isdir(full):
            size, total_files = folder_size(full, big_files)
        else:
            total_files = 1
            try:
                size = os.path.getsize(full)
            except OSError:
                continue
            if size >= BIG_FILE:
                big_files.append((size, full))

        results.append((size, name, total_files))
        grand_total = grand_total + size

    # Pairs sort by their first item, so this puts the biggest size first.
    results.sort(reverse=True)
    big_files.sort(reverse=True)

    print()
    print(f"=== BIGGEST ITEMS IN {root} (total {human(grand_total)}) ===")
    for size, name, total_files in results[:15]:
        if grand_total > 0:
            percent = size / grand_total * 100
        else:
            percent = 0
        print(f"  [{bar(percent)}] {percent:4.1f}%  {human(size):>9}  {name:<15} {total_files:>12} Files")

    print()
    print(f"=== SINGLE FILES OVER {human(BIG_FILE)} ===")
    if len(big_files) == 0:
        print("  none")
    for size, path in big_files[:10]:
        print(f"  {human(size):>9}  {path}")

if __name__ == "__main__":
    main