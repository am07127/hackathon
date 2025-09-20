import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from fastapi.middleware.cors import CORSMiddleware

from notion_agent import run_notion_query, make_notion_agent
from jira_agent import run_jira_query, make_jira_agent
from phi.agent import Agent
from phi.model.openai import OpenAIChat


load_dotenv()

# Ensure OpenAI API key is available globally
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in the environment or .env file")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY  # make sure LangChain/LangGraph can see it

app = FastAPI()

# global variables
client = None
tools = []
agent = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    # Run the data.py script to refresh notion_pages.csv
    import runpy
    try:
        runpy.run_path("data.py")
        print("Successfully ran data.py to refresh Notion pages")
    except Exception as ex:
        print(f"Error running data.py: {ex}")

    # Skip MCP client setup for Railway deployment
    # Railway doesn't support Docker containers, so we'll only use team_chat
    print("Railway deployment: Using team_chat endpoint only (no MCP containers)")
    
    global client, tools, agent
    client = None
    tools = []
    agent = None


class ChatInput(BaseModel):
    message: str


from typing import List, Dict, Any

class SourceInfo(BaseModel):
    agent: str
    sources: List[str]

class TeamChatOutput(BaseModel):
    responses: Dict[str, str]
    sources: List[SourceInfo]

class ChatOutput(BaseModel):
    response: str


@app.post("/chat", response_model=ChatOutput)
async def chat_endpoint(chat_input: ChatInput):
    try:
        if agent is None:
            # Redirect to team_chat since MCP agent is not available on Railway
            team_response = await team_chat_endpoint(chat_input)
            return ChatOutput(response=team_response.responses.get("team", "No response available"))
        
        response = await agent.ainvoke(
            {"messages": [HumanMessage(content=chat_input.message)]}
        )
        ai_response_message = response["messages"][-1].content
        print(f"AI message {ai_response_message}")
        return ChatOutput(response=ai_response_message)
    except Exception as ex:
        print(f"Error in chat endpoint: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))

# --- New Team Chat Endpoint ---

# --- Multi-Agent Team Implementation ---
from phi.agent import Agent as PhiAgent

import importlib


@app.post("/team_chat", response_model=TeamChatOutput)
async def team_chat_endpoint(chat_input: ChatInput):
    try:
        # Instantiate individual agents
        notion_agent = make_notion_agent()
        jira_agent = make_jira_agent()

        # Build a team agent
        team_instructions = [
            "You are leading a team of specialized agents to provide comprehensive answers combining project management and knowledge base information",
            "Coordinate between the Notion Knowledge Specialist and Jira Project Management Specialist to provide complete responses",
            "When the user asks about projects, tasks, or work items, consult the Jira specialist for current status and the Notion specialist for relevant documentation",
            "For strategic questions, roadmaps, or procedures, prioritize the Notion specialist while getting context from Jira about current implementation status",
            "Always provide a synthesis of information from both sources when relevant",
            "Include sources and references from both systems in your final response",
            "Use clear formatting with headers, bullet points, and tables when presenting information",
            "If information from one system contradicts the other, highlight the discrepancy and explain the context",
            "Prioritize actionable insights and next steps in your responses",
            "When information is incomplete from one source, explicitly leverage the other source to fill gaps"
        ]
        team_agent = Agent(
            name="Integrated Workspace Assistant",
            role="Team leader coordinating specialized agents to provide comprehensive workspace insights",
            description="You are an expert workspace assistant that coordinates between project management (Jira) and knowledge management (Notion) specialists to provide comprehensive, actionable insights about projects, tasks, documentation, and organizational processes.",
            model=OpenAIChat(id="gpt-4o"),
            team=[notion_agent, jira_agent],
            instructions=team_instructions,
            markdown=True,
            show_tool_calls=True,
            add_history_to_messages=True,
            num_history_responses=3,
            add_datetime_to_instructions=True,
            prevent_hallucinations=True,
            add_transfer_instructions=True
        )

        # Run the team agent and capture the response
        response = team_agent.run(chat_input.message, stream=False)

        # Extract content
        content = response.content

        print(f"Team agent response: {content}")

        # Optionally extract other fields like tools used, context, etc.
        # e.g., response.messages, response.context, etc.
        sources = []
        if hasattr(response, 'context') and response.context is not None:
            # If context contains source info, extract
            # This is illustrative; you’ll need to adapt depending how your agents/tooling store source info
            for ctx in response.context:
                # If ctx has a “source” or similar field
                src = getattr(ctx, "source", None)
                if src:
                    sources.append(src)

        # Return structured output
        return TeamChatOutput(responses={"team": str(content)}, sources=sources)

    except Exception as ex:
        # For debugging/logging
        print("Error in /team_chat:", ex)
        raise HTTPException(status_code=500, detail=str(ex))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)