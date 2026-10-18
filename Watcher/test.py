from pathlib import Path
from datetime import datetime
import shutil

# Returns the path (e.g. "/usr/bin/notify-send") or None if not found
HAS_NOTIFY = shutil.which("notify-send") is not None
print(f"{HAS_NOTIFY}")

item = Path.home() / "Downloads/Music/CD(MP3_320K).mp3"

info = item.stat()
print(f"Size: {info.st_size} bytes")
print(f"Last modified: {info.st_mtime}")
print(f"Permissions: {oct(info.st_mode)}")
print(datetime.fromtimestamp(1791857375.3410938))


