import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

AVIATION_STACK_API_KEY = os.getenv("AviationStack_Key")

client = MultiServerMCPClient(
    {
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


import asyncio

async def main():

    tools = await client.get_tools()

    print("\nAvailable Tools:\n")

    for tool in tools:
        print(tool.name)

asyncio.run(main())