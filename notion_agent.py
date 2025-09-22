# agents/notion_agent.py

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
_notion_knowledge_base = None
_knowledge_base_loaded = False

def get_notion_knowledge_base():
    """
    Singleton function to get or create the Notion knowledge base.
    This ensures the knowledge base is only loaded once per application lifecycle.
    """
    global _notion_knowledge_base, _knowledge_base_loaded
    
    if _notion_knowledge_base is None:
        print("Initializing Notion knowledge base for the first time...")
        _notion_knowledge_base = CSVKnowledgeBase(
            path="notion_pages.csv",
            vector_db=PgVector(
                table_name="csv_documents",
                db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
            ),
        )
        
        # Load the knowledge base only once
        if not _knowledge_base_loaded:
            try:
                print("Loading Notion knowledge base...")
                _notion_knowledge_base.load(recreate=False)
                _knowledge_base_loaded = True
                print("Notion knowledge base loaded successfully!")
            except Exception as e:
                print(f"Error loading Notion knowledge base: {e}")
                print("Attempting to recreate knowledge base...")
                _notion_knowledge_base.load(recreate=True)
                _knowledge_base_loaded = True
                print("Notion knowledge base recreated successfully!")
    else:
        print("Using existing Notion knowledge base instance")
    
    return _notion_knowledge_base

def make_notion_agent():
    """
    Creates a Notion agent using the singleton knowledge base.
    This function can be called multiple times without reloading the knowledge base.
    """
    knowledge_base = get_notion_knowledge_base()
    
    agent = Agent(
        name="Notion Knowledge Specialist",
        role="Expert knowledge retrieval specialist focused on organizational documentation, procedures, and information stored in Notion databases",
        description="You are a specialized knowledge assistant that excels at searching through Notion databases to find relevant documentation, procedures, guidelines, feature roadmaps, and organizational information. You have deep expertise in understanding context and providing comprehensive answers from knowledge bases.",
        knowledge=knowledge_base,
        search_knowledge=True,
        instructions=[
            "Search the Notion knowledge base thoroughly for information relevant to the user's query",
            "Provide detailed, contextual answers based on the documentation found",
            "When referencing information, mention the specific page or database title where the information was found",
            "If multiple relevant documents exist, synthesize information from all sources",
            "Always include source references in your responses",
            "Focus on providing actionable insights and clear explanations",
            "If the query relates to features, roadmaps, or procedures, provide comprehensive details",
            "When information is incomplete, clearly state what additional context might be needed"
        ],
        markdown=True,
        show_tool_calls=True,
        add_datetime_to_instructions=True
    )
    
    return agent

def run_notion_query(query: str):
    """
    Runs a query against the Notion agent.
    Uses the singleton knowledge base for efficiency.
    """
    agent = make_notion_agent()
    # returns a RunResponse object
    response = agent.run(query, stream=False)
    return response

def reset_notion_knowledge_base():
    """
    Utility function to reset the knowledge base (useful for development/testing).
    Call this if you want to force a reload of the knowledge base.
    """
    global _notion_knowledge_base, _knowledge_base_loaded
    print("Resetting Notion knowledge base...")
    _notion_knowledge_base = None
    _knowledge_base_loaded = False

def is_notion_knowledge_base_loaded():
    """
    Check if the Notion knowledge base has been loaded.
    """
    return _knowledge_base_loaded

# Optional: Advanced singleton with threading support
import threading

class NotionKnowledgeBaseSingleton:
    """
    Thread-safe singleton class for Notion knowledge base.
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
                    print("Initializing thread-safe Notion knowledge base...")
                    self.knowledge_base = CSVKnowledgeBase(
                        path="notion_pages.csv",
                        vector_db=PgVector(
                            table_name="csv_documents",
                            db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
                        ),
                    )
                    try:
                        print("Loading Notion knowledge base (thread-safe)...")
                        self.knowledge_base.load(recreate=False)
                        self._loaded = True
                        print("Notion knowledge base loaded successfully!")
                    except Exception as e:
                        print(f"Error loading knowledge base: {e}")
                        print("Attempting to recreate...")
                        self.knowledge_base.load(recreate=True)
                        self._loaded = True
                        print("Notion knowledge base recreated successfully!")
        
        return self.knowledge_base
    
    def reset(self):
        with self._lock:
            if hasattr(self, 'knowledge_base'):
                delattr(self, 'knowledge_base')
            self._loaded = False
            print("Thread-safe Notion knowledge base reset")

# Alternative function using the thread-safe singleton
def make_notion_agent_threadsafe():
    """
    Creates a Notion agent using the thread-safe singleton knowledge base.
    """
    singleton = NotionKnowledgeBaseSingleton()
    knowledge_base = singleton.get_knowledge_base()
    
    agent = Agent(
        name="Notion Knowledge Specialist",
        role="Expert knowledge retrieval specialist focused on organizational documentation, procedures, and information stored in Notion databases",
        description="You are a specialized knowledge assistant that excels at searching through Notion databases to find relevant documentation, procedures, guidelines, feature roadmaps, and organizational information. You have deep expertise in understanding context and providing comprehensive answers from knowledge bases.",
        knowledge=knowledge_base,
        search_knowledge=True,
        instructions=[
            "Search the Notion knowledge base thoroughly for information relevant to the user's query",
            "Provide detailed, contextual answers based on the documentation found",
            "When referencing information, mention the specific page or database title where the information was found",
            "If multiple relevant documents exist, synthesize information from all sources",
            "Always include source references in your responses",
            "Focus on providing actionable insights and clear explanations",
            "If the query relates to features, roadmaps, or procedures, provide comprehensive details",
            "When information is incomplete, clearly state what additional context might be needed"
        ],
        markdown=True,
        show_tool_calls=True,
        add_datetime_to_instructions=True
    )
    
    return agent