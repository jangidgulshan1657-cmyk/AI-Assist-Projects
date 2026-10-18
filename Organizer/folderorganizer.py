"""Organize files in a folder by type."""

import sys
import shutil
from pathlib import Path


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


def categorize(file: Path) -> str:
 
    ext = file.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Other"

def organize(folder: Path, dry_run: bool = True) -> None:
    for item in folder.iterdir():
        if item.is_file():
            if item.name.startswith("."):
                print(f"[Skipped]-> {item}")
                continue
            category = categorize(item)
            dest_folder = folder / category
            dest_path = dest_folder / item.name

            if dry_run:
                if dest_path.exists():
                    print(f"[Skipped]-> File Already Exists {item.name}-> {category}/")
                    continue
                print(f"[DRY RUN]: {item} -> {category}")
            else:
                dest_folder.mkdir(exist_ok= True)
                if dest_path.exists():
                    print(f"[Skipped]-> File Already Exists {item.name}-> {category}/")
                    continue
                shutil.move(str(item),str(dest_path))
                print(f"Moved {item.name} -> {category}/")

if __name__ == "__main__":
    downloads = Path.home() / "Downloads"
    dry_run = "--run" not in sys.argv
    organize(downloads, dry_run)