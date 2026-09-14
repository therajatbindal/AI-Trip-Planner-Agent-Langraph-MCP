import os
import asyncio

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

Tavily_API_Key = os.getenv("Tavily_API_Key")
AVIATION_STACK_API_KEY = os.getenv("AviationStack_Key")

client = MultiServerMCPClient(
    {
        "tavily" : {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={Tavily_API_Key}"
        },

         "aviationstack" :{
                    "transport": "stdio",
                    "command": r"C:\Users\hp\OneDrive\Desktop\NewLearning_RB\AI-Trip-Planner-Agent-Langraph-MCP\aviationstack-mcp\.venv\Scripts\python.exe",
                    "args": [
                        "-m",
                        "aviationstack_mcp",
                        "mcp",
                        "run"
                    ],
                    "env": {
                        "AVIATION_STACK_API_KEY": AVIATION_STACK_API_KEY
                    }
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

# Find the Tavily Search tool from Tavily's MCP Server
# search_tool = None

# async def initialize_mcp():
#     global search_tool
#     if search_tool is not None:
#         return

#     tools = await client.get_tools()
#     print("\nAvailable MCP Tools:")

#     for tool in tools:
#         print(tool.name)

#     search_tool=next(
#         tool
#         for tool in tools
#         if tool.name == "tavily_search"
#     )

# Find the Respective tools from Repsective MCP servers
search_tool = None
aviation_tools = {}

async def initialize_mcp():

    global search_tool
    global aviation_tools

    if search_tool is not None and aviation_tools:
        return

    tools = await client.get_tools()

    print("\nAvailable MCP Tools\n")

    for tool in tools:
        print(tool.name)

    search_tool = next(
        tool
        for tool in tools
        if tool.name == "tavily_search"
    )

    aviation_tools = {
        tool.name : tool
        for tool in tools
        if tool.name != "tavily_search"
    }

async def tavily_mcp_search(query: str):
    await initialize_mcp()
    result = await search_tool.ainvoke(
        {
            "query": query
        }
    )
    return result

async def aviation_mcp_call(
        tool_name: str,
        tool_args: dict = None
):

    tools = await client.get_tools()

    tool = next(
         t for t in tools
        if t.name == tool_name
    )

    result = await tool.ainvoke(
        tool_args or {}
    )

    return result



async def get_airports():

    await initialize_mcp()

    tool = aviation_tools.get("list_airports")

    if not tool:
        return "Airport tool unavailable"

    result = await tool.ainvoke({})

    return result

async def get_airlines():

    await initialize_mcp()

    tool = aviation_tools.get("list_airlines")

    if not tool:
        return "Airline tool unavailable"

    result = await tool.ainvoke({})

    return result

if __name__ == "__main__":
    asyncio.run(main())