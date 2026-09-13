import os
import asyncio

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

Tavily_API_Key = os.getenv("Tavily_API_Key")

client = MultiServerMCPClient(
    {
        "tavily" : {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={Tavily_API_Key}"
        }
    }

)

# tools discovery
#async def main():

#    tools = await client.get_tools()

#    print("\nAvailable MCP Tools:\n")

#    for tool in tools:
#        print(tool.name)



async def main():
    tools = await client.get_tools()

    search_tool = next(
        tool
        for tool in tools
        if tool.name=="tavily_search"        
    )

    result = await search_tool.ainvoke(
        {
            "query": "Best hotels in Delhi"
        }
    )

    print(result)

#asyncio.run(main())


search_tool = None

async def initialize_mcp():
    global search_tool
    if search_tool is not None:
        return

    tools = await client.get_tools()
    print("\nAvailable MCP Tools:")

    for tool in tools:
        print(tool.name)

    search_tool=next(
        tool
        for tool in tools
        if tool.name == "tavily_search"
    )





async def tavily_mcp_search(query: str):
    await initialize_mcp()
    result = search_tool.ainvoke(
        {
            "query": query
        }
    )
    return

if __name__ == "__main__":
    asyncio.run(main())