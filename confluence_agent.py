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

# Global variable to cache the knowledge base
_confluence_knowledge_base = None
_knowledge_base_loaded = False

def get_confluence_knowledge_base():
    """
    Singleton function to get or create the Confluence knowledge base.
    This ensures the knowledge base is only loaded once per application lifecycle.
    """
    global _confluence_knowledge_base, _knowledge_base_loaded
    
    if _confluence_knowledge_base is None:
        print("Initializing Confluence knowledge base for the first time...")
        _confluence_knowledge_base = CSVKnowledgeBase(
            path="knoccs_confluence.csv",
            vector_db=PgVector(
                table_name="csv_documents_confluence",
                db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
            ),
        )
        
        # Load the knowledge base only once
        if not _knowledge_base_loaded:
            try:
                print("Loading Confluence knowledge base...")
                _confluence_knowledge_base.load(recreate=False)
                _knowledge_base_loaded = True
                print("Confluence knowledge base loaded successfully!")
            except Exception as e:
                print(f"Error loading Confluence knowledge base: {e}")
                print("Attempting to recreate knowledge base...")
                _confluence_knowledge_base.load(recreate=True)
                _knowledge_base_loaded = True
                print("Confluence knowledge base recreated successfully!")
    else:
        print("Using existing Confluence knowledge base instance")
    
    return _confluence_knowledge_base

def make_confluence_agent():
    """
    Creates a Confluence agent using the singleton knowledge base.
    This function can be called multiple times without reloading the knowledge base.
    """
    knowledge_base = get_confluence_knowledge_base()
    
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
    
    return agent

def reset_confluence_knowledge_base():
    """
    Utility function to reset the knowledge base (useful for development/testing).
    Call this if you want to force a reload of the knowledge base.
    """
    global _confluence_knowledge_base, _knowledge_base_loaded
    print("Resetting Confluence knowledge base...")
    _confluence_knowledge_base = None
    _knowledge_base_loaded = False

def is_confluence_knowledge_base_loaded():
    """
    Check if the Confluence knowledge base has been loaded.
    """
    return _knowledge_base_loaded

# Optional: Advanced singleton with threading support
import threading

class ConfluenceKnowledgeBaseSingleton:
    """
    Thread-safe singleton class for Confluence knowledge base.
    Use this if you're running in a multi-threaded environment.
    """
    _instance = None
    _lock = threading.Lock()
    _loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_knowledge_base(self):
        if not hasattr(self, 'knowledge_base') or not self._loaded:
            with self._lock:
                if not hasattr(self, 'knowledge_base') or not self._loaded:
                    print("Initializing thread-safe Confluence knowledge base...")
                    self.knowledge_base = CSVKnowledgeBase(
                        path="knoccs_confluence.csv",
                        vector_db=PgVector(
                            table_name="csv_documents_confluence",
                            db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
                        ),
                    )
                    try:
                        print("Loading Confluence knowledge base (thread-safe)...")
                        self.knowledge_base.load(recreate=False)
                        self._loaded = True
                        print("Confluence knowledge base loaded successfully!")
                    except Exception as e:
                        print(f"Error loading knowledge base: {e}")
                        print("Attempting to recreate...")
                        self.knowledge_base.load(recreate=True)
                        self._loaded = True
                        print("Confluence knowledge base recreated successfully!")
        
        return self.knowledge_base
    
    def reset(self):
        with self._lock:
            if hasattr(self, 'knowledge_base'):
                delattr(self, 'knowledge_base')
            self._loaded = False
            print("Thread-safe Confluence knowledge base reset")

# Alternative function using the thread-safe singleton
def make_confluence_agent_threadsafe():
    """
    Creates a Confluence agent using the thread-safe singleton knowledge base.
    """
    singleton = ConfluenceKnowledgeBaseSingleton()
    knowledge_base = singleton.get_knowledge_base()
    
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
    
    return agent