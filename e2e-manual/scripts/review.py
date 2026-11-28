"""review.py <module> <tool> <json-args>: call one review tool in-memory and print its JSON."""
import importlib, json, sys, anyio
from mcp.shared.memory import create_connected_server_and_client_session
mod, tool, args = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
story = open("story.txt", encoding="utf-8").read()
args = {k: (story if v == "@story" else v) for k, v in args.items()}
async def go():
    srv = importlib.import_module(mod).create_server()
    async with create_connected_server_and_client_session(srv._mcp_server) as c:
        await c.initialize()
        r = await c.call_tool(tool, args)
        print(r.content[0].text)
anyio.run(go)
