import json, sys, anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
story = open("story.txt", encoding="utf-8").read()
async def go():
    async with stdio_client(StdioServerParameters(command=sys.argv[1], args=sys.argv[2:])) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            res = await s.call_tool("review_user_story", {"story": story})
            print(res.content[0].text)
anyio.run(go)
