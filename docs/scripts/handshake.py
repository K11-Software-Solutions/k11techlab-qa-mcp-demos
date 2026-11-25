"""Start an MCP server over stdio exactly as a plugin's .mcp.json would, and list its tools."""
import asyncio
import shutil
import sys
import time

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main(command: str, *args: str) -> None:
    print("resolved:", shutil.which(command))
    start = time.time()
    params = StdioServerParameters(command=command, args=list(args))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as s:
            info = await s.initialize()
            tools = sorted(t.name for t in (await s.list_tools()).tools)
            print(f"{info.serverInfo.name} {info.serverInfo.version} in {time.time() - start:.1f}s: {tools}")


asyncio.run(main(*sys.argv[1:]))
