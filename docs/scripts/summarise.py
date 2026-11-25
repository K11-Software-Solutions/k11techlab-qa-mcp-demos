"""Summarise a claude -p stream-json log: plugin load, tool calls, denials, final reply, cost."""
import json
import sys

events = [json.loads(line) for line in open(sys.argv[1], encoding="utf-8") if line.strip().startswith("{")]
for e in events:
    if e.get("type") == "system" and e.get("subtype") == "init":
        plugins = [p.get("name") for p in e.get("plugins", [])]
        mcp = [(s.get("name"), s.get("status")) for s in e.get("mcp_servers", [])]
        cmds = [c for c in e.get("slash_commands", []) if "story" in c]
        print("init: plugins", plugins, "| mcp", mcp, "| commands", cmds, "| model", e.get("model"))
    elif e.get("type") == "assistant":
        for b in e["message"].get("content", []):
            if b.get("type") == "tool_use":
                args = json.dumps(b.get("input", {}))[:160]
                print(f"TOOL  {b['name']}  {args}")
    elif e.get("type") == "user":
        for b in e["message"].get("content", []) if isinstance(e["message"].get("content"), list) else []:
            if b.get("type") == "tool_result":
                text = b.get("content")
                if isinstance(text, list):
                    text = " ".join(x.get("text", "") for x in text if isinstance(x, dict))
                flag = "ERROR " if b.get("is_error") else ""
                print(f"  -> {flag}{str(text)[:300]!r}")
    elif e.get("type") == "result":
        print("\nFINAL REPLY:\n" + (e.get("result") or "")[:2500])
        print(f"\nturns {e.get('num_turns')}, cost ${e.get('total_cost_usd') or 0:.4f}, "
              f"denials {[d.get('tool_name') for d in e.get('permission_denials', [])]}, error {e.get('is_error')}")
