import os
from typing import TypedDict,Annotated
import operator
import asyncio
import psycopg
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)

from langchain_groq import ChatGroq

#from tools.Flight_Tool import Flight_Search
#from mcp_client import tavily_mcp_search
from mcp_client import (
     tavily_mcp_search,
     aviation_mcp_call,
     get_airlines,
     get_airports
)

#from tools.Tavily_Tool import Tavily_Search
from dotenv import load_dotenv
load_dotenv()

db_url = os.getenv("DATABASE_URL")

#LLM
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY")
)

# State
class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_input: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int

# Flight Agent using API
# def Flight_Agent(state: TravelState):
#     query = state["user_input"]
#     flight_data= Flight_Search(query)
    
#     return {
#         "flight_results": flight_data,
#         "messages": [
#             AIMessage(content=f"Flight results fetched")
#         ],
#         "llm_calls": state.get("llm_calls", 0) + 1  # No LLM used in this agent
#     }


# Flight Tool Router Prompt
FLIGHT_AGENT_PROMPT = """
You are a travel flight expert.

User Query:
{query}

Airport Information:
{airport_data}

Airline Information:
{airline_data}

Generate:

1. Likely departure airport
2. Likely arrival airport
3. Airlines serving this route
4. Typical flight duration
5. Estimated airfare range
6. Peak season pricing warning
7. Booking advice

Return concise travel guidance.
"""


# Flight Agent with MCP
def Flight_Agent(state: TravelState):
    print("\nINSIDE FLIGHT AGENT\n")

    query = state["user_input"]

    try:

        airports = asyncio.run(
            aviation_mcp_call(
                "list_airports"
            )
        )

        airlines = asyncio.run(
            aviation_mcp_call(
                "list_airlines"
            )
        )

        prompt = FLIGHT_AGENT_PROMPT.format(
            query=query,
            airport_data=str(airports)[:3000],
            airline_data=str(airlines)[:3000]
        )

        response = llm.invoke([
            SystemMessage(
                content="You are an expert travel flight planner."
            ),
            HumanMessage(content=prompt)
        ])

        flight_data = response.content

    except Exception as e:

        flight_data = f"Flight information unavailable: {str(e)}"

    return {
        "flight_results": flight_data,
        "messages": [
            AIMessage(
                content="Flight recommendations generated"
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


# Hotel Agent
def Hotel_Agent(state: TravelState):
    query = f"Best hotels for {state['user_input']}"
    #hotel_results= Tavily_Search(query)

    hotel_results = asyncio.run(
        tavily_mcp_search(query)
    )
    
    return {
        "hotel_results": hotel_results,
        "messages": [
            AIMessage(content=f"Hotel information fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1  # No LLM used in this agent
    }

# Itinerary Agent
def Itinerary_Agent(state: TravelState):
    
    prompt = f"""
    Create a travel itinerary.
    User Query: 
    {state['user_input']}

    Flight Results:
    {state['flight_results']}

    Hotel Results:
    {state['hotel_results']}
    """

    response =llm.invoke([
        SystemMessage(
            content="You are a expert travel planner"
        ),
        HumanMessage(
            content=prompt
        )
    ])

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

# Final Response Agent
def Final_Agent(state: TravelState):
    
    final_prompt = f"""
    Generate final travel response.

    Flights:
    {state['flight_results']}

    Hotels:
    {state['hotel_results']}

    Itinerary:
    {state['itinerary']}
    """

    response = llm.invoke([
        HumanMessage(content=final_prompt)
    ])

    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


graph = StateGraph(TravelState)

graph.add_node("Flight_Agent", Flight_Agent)
graph.add_node("Hotel_Agent", Hotel_Agent)
graph.add_node("Itinerary_Agent", Itinerary_Agent)
graph.add_node("Final_Agent", Final_Agent)

graph.add_edge(START, "Flight_Agent")
graph.add_edge("Flight_Agent", "Hotel_Agent")
graph.add_edge("Hotel_Agent", "Itinerary_Agent")
graph.add_edge("Itinerary_Agent", "Final_Agent")
graph.add_edge("Final_Agent", END)

# Persistent connection so both CLI and Streamlit can share the compiled app
_conn = psycopg.connect(db_url,autocommit=True)
checkpointer = PostgresSaver(_conn)
checkpointer.setup()

app = graph.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    # config={
    #    "configurable": {
    #        "thread_id": "user_MCP"
    #    }
    # }
    
    # Every Run Starts Fresh
    import uuid
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4())
        }
    }


    user_query = input("Enter your travel query: ")

    result = app.invoke(
        {
            "messages": [
                HumanMessage(content=user_query)
            ],
            "user_input": user_query,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )

    print("\nFinal Travel Response:\n")

    for message in result["messages"]:
            print(message.content)