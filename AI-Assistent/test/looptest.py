def fake_llm(messages):
    # first time: LLM asks for TWO tools. after tool results: plain answer.
    if messages[-1]["role"] == "user":
        return {"content": "", "tool_calls": [
            {"id": "c1", "function": {"name": "system_info"}},
            {"id": "c2", "function": {"name": "network"}},
        ]}
    return {"content": "RAM is fine, network is idle."}

messages = [
    {"role": "system", "content": "You are Jarvis"},
    {"role": "user", "content": "how is my pc?"},
]

for step in range(5):
    reply = fake_llm(messages)
    calls = reply.get("tool_calls")

    assistant = {"role": "assistant", "content": reply.get("content") or ""}
    if calls:
        assistant["tool_calls"] = calls
    messages.append(assistant)
    print(f"--- step {step}: LLM replied ---")

    if not calls:
        print("FINAL ANSWER:", assistant["content"])
        break

    for call in calls:
        name = call["function"]["name"]
        messages.append({"role": "tool", "tool_call_id": call["id"],
                         "content": f"<output of {name}>"})

for m in messages:
    print(m)