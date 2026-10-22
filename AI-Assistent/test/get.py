call_good = {"function": {"name": "network"}}
call_bad = {}

print(call_good.get("function", {}).get("name", ""))
print(call_bad.get("function", {}).get("name", ""))
print(repr(call_bad.get("function", {}).get("name", "")))

import sys
print(sys.executable)
