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
from confluence_agent import run_confluence_query, make_confluence_agent
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
    except Exception as ex:
        print(f"Error running data.py: {ex}")

    global client, tools, agent
    try:
        client = MultiServerMCPClient(
            {
                "mcp-atlassian": {
                    "command": "docker",
                    "args": [
                        "run",
                        "-i",
                        "--rm",
                        "-e", "CONFLUENCE_URL",
                        "-e", "CONFLUENCE_USERNAME",
                        "-e", "CONFLUENCE_API_TOKEN",
                        "-e", "JIRA_URL",
                        "-e", "JIRA_USERNAME",
                        "-e", "JIRA_API_TOKEN",
                        "ghcr.io/sooperset/mcp-atlassian:latest"
                    ],
                    "env": {
                        "CONFLUENCE_URL": os.getenv("CONFLUENCE_URL"),
                        "CONFLUENCE_USERNAME": os.getenv("CONFLUENCE_USERNAME"),
                        "CONFLUENCE_API_TOKEN": os.getenv("CONFLUENCE_API_TOKEN"),
                        "JIRA_URL": os.getenv("JIRA_URL"),
                        "JIRA_USERNAME": os.getenv("JIRA_USERNAME"),
                        "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN")
                    },
                    "transport": "stdio",
                },
                "mcp-notion": {
                    "command": "docker",
                    "args": [
                        "run",
                        "-i",
                        "--rm",
                        "-e", "OPENAPI_MCP_HEADERS",
                        "mcp/notion"
                    ],
                    "env": {
                        "OPENAPI_MCP_HEADERS": os.getenv("OPENAPI_MCP_HEADERS")
                        # e.g., '{"Authorization":"Bearer ntn_XXXX...","Notion-Version":"2022-06-28"}'
                    },
                    "transport": "stdio",
                }
            }
        )

        tools = await client.get_tools()
        agent = create_react_agent('gpt-4o', tools=tools)
        print(f"Successfully initialized with {len(tools)} tools")
    except Exception as ex:
        print(ex)


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
        response = await agent.ainvoke(
            {"messages": [HumanMessage(content=chat_input.message)]}
        )
        ai_response_message = response["messages"][-1].content
        print(f"AI message {ai_response_message}")
        return ChatOutput(response=ai_response_message)
    except Exception as ex:
        print(ex)

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
        confluence_agent = make_confluence_agent()

        # Build a team agent
        team_instructions = [
            "You are the lead Project Intelligence Agent, commanding a team of exactly THREE specialized sub-agents. Your mission is to provide comprehensive, synthesized answers by consulting ALL THREE sources—Jira, Confluence, AND Notion.",
            "",
            "Your team consists of:",
            "• Jira Project Management Specialist: Provides real-time project status, task assignments, and work item progress.",
            "• Confluence Knowledge Specialist: Provides technical documentation, procedural guides, and organizational knowledge.",
            "• Notion Knowledge Specialist: Provides high-level strategic plans, roadmaps, and detailed notes.",
            "",
            "CRITICAL DIRECTIVES:",
            "1. ALWAYS Consult ALL THREE Specialists: For every user query, you MUST transfer tasks to ALL THREE agents (Jira, Confluence, AND Notion) to ensure comprehensive coverage. Do not skip any agent.",
            "2. Transfer Tasks Explicitly: Use transfer_task_to_jira_project_management_specialist, transfer_task_to_confluence_knowledge_specialist, AND transfer_task_to_notion_knowledge_specialist for every query.",
            "3. Build Context and Cohesion: Do not simply list information. Build a coherent narrative that connects tasks in Jira to their documentation in Confluence and their strategic purpose in Notion.",
            "4. Provide a Cohesive Summary: Present the synthesized information clearly, using bold keywords, headings, and bullet points.",
            "5. Identify and Resolve Discrepancies: If information from different sources conflicts, highlight the discrepancy and provide context to explain it.",
            "6. Focus on Actionable Insights: Conclude your response with clear, actionable insights or next steps based on ALL THREE sources.",
            "7. Maintain Transparency: Always cite your sources by clearly referencing the application (e.g., 'From Jira,' 'From Confluence,' 'From Notion').",
            "8. Quality Control: Ensure you have gathered information from all three platforms before providing your final synthesis."
        ]
        team_agent = Agent(
            name="Integrated Workspace Assistant",
            role="Team leader coordinating ALL THREE specialized agents (Jira, Confluence, and Notion) to provide comprehensive workspace insights",
            description="You are an expert workspace assistant that coordinates between project management (Jira), technical documentation (Confluence), and knowledge management (Notion) specialists. You MUST consult all three agents for every query to provide comprehensive, actionable insights about projects, tasks, documentation, and organizational processes.",
            model=OpenAIChat(id="gpt-4o"),
            team=[notion_agent, jira_agent, confluence_agent],
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
    uvicorn.run(app, host="0.0.0.0", port=8080)