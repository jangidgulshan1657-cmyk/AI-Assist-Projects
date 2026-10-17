from pathlib import Path
from datetime import datetime

item = Path.home() / "Downloads/Gulshan Resume.png"

info = item.stat()
print(f"Size: {info.st_size} bytes")
print(f"Last modified: {info.st_mtime}")
print(f"Permissions: {oct(info.st_mode)}")
print(datetime.fromtimestamp(1791857375.3410938))
