import asyncio, json, os, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Launch the CONTAINER as a stdio MCP server; mount the workspace read-only.
    params = StdioServerParameters(
        command="sudo",
        args=["docker","run","--rm","-i","--network","none",
              "-v","/workspace/plans:/data:ro","data-plane-mcp:test"],
        env={},
    )
    async with stdio_client(params) as (r,w):
        async with ClientSession(r,w) as s:
            await s.initialize()
            tools = await s.list_tools()
            print("TOOLS:", [t.name for t in tools.tools])
            res = await s.call_tool("repo_stats", {"path":"/data"})
            print("repo_stats(/data):", res.content[0].text[:200])
            res2 = await s.call_tool("find_todos", {"path":"/data"})
            print("find_todos count:", len(json.loads(res2.content[0].text)))

asyncio.run(main())
