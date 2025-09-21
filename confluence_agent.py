# agents/confluence_agent.py

from phi.knowledge.csv import CSVKnowledgeBase
from phi.vectordb.pgvector import PgVector
from phi.agent import Agent
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in the environment or .env file")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def make_confluence_agent():
    knowledge_base = CSVKnowledgeBase(
        path="knoccs_confluence.csv",
        vector_db=PgVector(
            table_name="csv_documents_confluence",
            db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
        ),
    )
    agent = Agent(
        name="Confluence Knowledge Specialist",
        role="Expert technical documentation and procedural knowledge specialist focused on Confluence-based organizational information",
        description="You are a specialized Confluence documentation expert that excels at finding technical documentation, procedural guides, organizational knowledge, and process information stored in Confluence. You provide detailed technical context and procedural guidance for projects and organizational processes.",
        knowledge=knowledge_base,
        search_knowledge=True,
        instructions=[
            "You are the Confluence specialist on a multi-agent team providing comprehensive workspace intelligence",
            "Search the Confluence knowledge base thoroughly for technical documentation, procedures, and organizational information relevant to the user's query",
            "Focus specifically on technical documentation, process guides, organizational procedures, and implementation details",
            "Provide detailed, contextual answers based on the Confluence documentation found",
            "When referencing information, always mention the specific Confluence page or space title where the information was found",
            "If multiple relevant Confluence documents exist, synthesize information from all sources",
            "Always include clear source references in your responses with 'From Confluence:' prefix",
            "Focus on providing actionable technical insights and procedural guidance",
            "If the query relates to technical features, implementation procedures, or organizational processes, provide comprehensive details from Confluence",
            "When Confluence information is incomplete, clearly state what additional technical context might be needed",
            "Coordinate with your Jira and Notion specialist teammates to provide complete cross-platform insights"
        ],
        markdown=True,
        show_tool_calls=True,
        add_datetime_to_instructions=True
    )
    agent.knowledge.load(recreate=True)
    return agent

def run_confluence_query(query: str):
    agent = make_confluence_agent()
    # returns a RunResponse object
    response = agent.run(query, stream=False)
    return response


myresponse = run_confluence_query("What is the most recent update on knoccs?")
print(myresponse)