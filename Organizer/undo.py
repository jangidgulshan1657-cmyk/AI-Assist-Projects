"""Undo folderorganizer: move files back up into Downloads."""

import shutil
from pathlib import Path

downloads = Path.home() / "Downloads"
CATEGORY_NAMES = ["Images", "Documents", "Archives", "Audio", "Video", "Installers", "Other"]

for name in CATEGORY_NAMES:
    folder = downloads / name
    if not folder.is_dir():
        continue
    for item in folder.iterdir():
        target = downloads / item.name
        if target.exists():
            print(f"SKIPPED (name clash): {item}")
            continue
        shutil.move(str(item), str(target))
        print(f"Restored {item.name}")
    if not any(folder.iterdir()):
        folder.rmdir()