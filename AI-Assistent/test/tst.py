import json
from typing import Any

menu: list[dict[str, Any]] = []
menu.append({
    "type": "function",
    "function": {
        "name": "disk_hogs",
        "description": "Which folders use the most space.",
        "parameters": {"type": "object", "properties": {}},
    },
})
print(json.dumps(menu, indent=2))



messages = ["system"]
checkpoint = len(messages)
messages.append("user question")
messages.append("assistant tool_call")
print(messages)
del messages[checkpoint:]
print(messages)
