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

#    for tools in tools:
#        print(tools.name)

async def main():

    tools = await client.get_tools()

    search_tool = next(
        tools
        for tools in tools
        if tools.name=="tavily_search"        
    )

    result = await search_tool.ainvoke(
        {
            "query": "Best hotels in Delhi"
        }
    )

    print(result)

asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())