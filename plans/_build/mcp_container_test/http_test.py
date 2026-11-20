import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
async def main():
    async with streamablehttp_client("http://127.0.0.1:12055/mcp") as (r,w,_):
        async with ClientSession(r,w) as s:
            await s.initialize()
            t=await s.list_tools(); print("HTTP TOOLS:", [x.name for x in t.tools])
            res=await s.call_tool("repo_stats",{"path":"/data"})
            print("HTTP repo_stats:", res.content[0].text[:120])
asyncio.run(main())
