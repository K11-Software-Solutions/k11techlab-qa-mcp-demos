"""Turn a `claude -p --output-format stream-json` log into a readable Markdown record."""
import json, re, sys
src, dst, title, cmd = sys.argv[1:5]
SEP = r'(?:\\\\|\\|/)+'  # one or more of: escaped backslash, backslash, slash


def scrub(s):
    """Replace local home-folder and scratchpad paths so the record can be shared."""
    s = re.sub(r'[A-Za-z]:' + SEP + 'Users' + SEP + r'[^\\/"\s]+', '%USERPROFILE%', s)
    s = re.sub(r'/c/Users/[^/"\s]+', '%USERPROFILE%', s)
    s = re.sub(r'(?i)' + SEP + 'AppData' + SEP + 'Local' + SEP + 'Temp' + SEP + 'claude' + SEP
               + r'[0-9a-f]+' + SEP + r'[0-9a-f-]+' + SEP + 'scratchpad', '/<scratchpad>', s)
    return s
ev = [json.loads(l) for l in open(src, encoding='utf-8') if l.strip().startswith('{')]
out = [f"# {title}\n", "## Command\n", "```powershell", cmd, "```\n"]
for e in ev:
    if e.get('type') == 'system' and e.get('subtype') == 'init':
        qa = [f"`{s['name']}` = {s['status']}" for s in e.get('mcp_servers', []) if 'qa' in s.get('name','')]
        out += ["## Session start\n", f"- Model: `{e.get('model')}`", f"- QA MCP server at start: {', '.join(qa) or 'not listed'}",
                f"- Slash command loaded: {', '.join('`/'+c+'`' for c in e.get('slash_commands', []) if 'story' in c)}\n", "## Tool calls\n"]
    elif e.get('type') == 'assistant':
        for b in e['message'].get('content', []):
            if b.get('type') == 'tool_use' and b['name'] != 'ToolSearch':
                out += [f"### `{b['name'].split('__')[-1]}`\n", "Input:\n", "```json", scrub(json.dumps(b.get('input', {}), indent=2)), "```\n"]
    elif e.get('type') == 'user' and isinstance(e['message'].get('content'), list):
        for b in e['message']['content']:
            if b.get('type') == 'tool_result':
                t = b.get('content')
                if isinstance(t, list): t = ' '.join(x.get('text', '') for x in t if isinstance(x, dict))
                t = str(t).strip()
                if not t: continue
                if len(t) > 6000: t = t[:6000] + '\n... (truncated)'
                out += ["Output:\n", "```json", scrub(t), "```\n"]
    elif e.get('type') == 'result':
        out += ["## Final reply from the agent\n", scrub(e.get('result') or ''), "",
                "## Run stats\n", f"- Turns: {e.get('num_turns')}", f"- Cost: ${e.get('total_cost_usd') or 0:.2f}",
                f"- Duration: {round((e.get('duration_ms') or 0)/1000)} s", f"- Errors: {e.get('is_error')}\n"]
open(dst, 'w', encoding='utf-8').write('\n'.join(out))
