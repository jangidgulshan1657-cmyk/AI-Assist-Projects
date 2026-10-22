from pathlib import Path

here = Path("/home/gulshan/Desktop/AI-Assist-Projects/AI- Assistent/jarvis.py")
print(here.parent)
print(here.parent.parent)
print(here.parent.parent / "Linux" / "sysinfo.py")
print((here.parent.parent / "Linux" / "sysinfo.py").exists())