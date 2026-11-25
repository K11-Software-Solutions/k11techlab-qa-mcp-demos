# Scripts used during the live runs

| Script | Purpose |
|---|---|
| [`run.sh`](run.sh) | Runs one headless `claude -p` session with a plugin loaded from a folder. Only the read-only QA tools are allowed, so the live run can review, parse and explore but never write files. Saves a stream-json log. |
| [`summarise.py`](summarise.py) | Prints a stream-json log as text: plugin load, tool calls, results, final reply and cost. |
| [`runs2md.py`](runs2md.py) | Turns a stream-json log into the Markdown records in `*/live-runs/`, replacing local paths with `%USERPROFILE%`. |
| [`handshake.py`](handshake.py) | Starts an MCP server over stdio the way a plugin's `.mcp.json` would, then lists its tools. This proved the Selenium server itself worked while Claude Code still showed it as "failed". |

Example:

```bash
bash run.sh <path to plugin repo> selenium-qa selenium-qa <empty workdir> out.jsonl \
  "/selenium-qa:story-to-test https://example.com As a shopper, I want checkout to be fast and easy."
python summarise.py out.jsonl
python handshake.py uvx k11-selenium-qa-mcp
```
