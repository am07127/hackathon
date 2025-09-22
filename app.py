
import streamlit as st
import requests
import json
import time
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="شعور.ai - Unified Knowledge Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern dark theme design
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700;800&family=Amiri:wght@400;700&family=Roboto:wght@400;600&display=swap" rel="stylesheet">
<style>
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #1a1a2e 50%, #16213e 100%);
        color: #e0e6ed;
    }
    
    /* Main content area */
    .main .block-container {
        background: transparent;
        color: #e0e6ed;
    }
    
    .main-header {
        font-size: 4rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4a9eff 0%, #00d4ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-family: 'Noto Sans Arabic', 'Arial Unicode MS', Arial, sans-serif;
        direction: rtl;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .app-name {
        font-size: 4.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4a9eff 0%, #00d4ff 50%, #0ea5e9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        font-family: 'Noto Sans Arabic', 'Amiri', 'Times New Roman', serif;
        direction: rtl;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
        letter-spacing: 2px;
    }
    
    .app-extension {
        font-size: 2rem;
        font-weight: 600;
        color: #4a9eff;
        text-align: center;
        margin-bottom: 1rem;
        font-family: 'Roboto', 'Arial', sans-serif;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #a0a9c0;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    .mode-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #475569;
        color: #e0e6ed;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        transition: transform 0.3s ease;
    }
    
    .mode-card:hover {
        transform: translateY(-5px);
        border: 1px solid #4a9eff;
        box-shadow: 0 12px 35px rgba(74, 158, 255, 0.2);
    }
    
    .stats-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #475569;
        color: #e0e6ed;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border-left: 4px solid #4a9eff;
        margin: 1rem 0;
    }
    
    .chat-container {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid #475569;
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin: 1rem 0;
    }
    
    .source-badge {
        background: linear-gradient(90deg, #4a9eff, #00d4ff);
        color: #0a0e1a;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.25rem;
        display: inline-block;
        font-weight: 600;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #4a9eff 0%, #0ea5e9 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 15px rgba(74, 158, 255, 0.3);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #CC8899 0%, #AA6677 100%);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #4a9eff 0%, #0ea5e9 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(74, 158, 255, 0.4);
        background: linear-gradient(90deg, #0ea5e9 0%, #4a9eff 100%);
    }
    
    .agent-indicator {
        background: #00d4ff;
        color: #0a0e1a;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.7rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid #475569;
        border-radius: 10px;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: #1e293b;
        color: #e0e6ed;
        border: 1px solid #475569;
        border-radius: 10px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4a9eff;
        box-shadow: 0 0 0 2px rgba(74, 158, 255, 0.2);
    }
    
    /* Markdown text styling */
    .stMarkdown {
        color: #e0e6ed;
    }
    
    /* Plotly chart background */
    .js-plotly-plot {
        background: transparent !important;
    }
    
    /* Section headers */
    h1, h2, h3, h4, h5, h6 {
        color: #e0e6ed !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages_team" not in st.session_state:
    st.session_state["messages_team"] = []
if "messages_mcp" not in st.session_state:
    st.session_state["messages_mcp"] = []
if "current_mode" not in st.session_state:
    st.session_state["current_mode"] = "team"
if "query_count" not in st.session_state:
    st.session_state["query_count"] = 0
if "sources_accessed" not in st.session_state:
    st.session_state["sources_accessed"] = set()

FASTAPI_URL = "http://localhost:8080"

def create_hero_section():
    """Create an impressive hero section"""
    st.markdown('<h1 class="app-name">شعور</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-extension">.ai</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Artificial Intelligence • Breaking down data silos • Unifying knowledge • Empowering decisions</p>', unsafe_allow_html=True)
    
    # Key metrics dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>3+</h3>
            <p>Data Sources</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{st.session_state.query_count}</h3>
            <p>Queries Processed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(st.session_state.sources_accessed)}</h3>
            <p>Sources Accessed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>∞</h3>
            <p>Insights Generated</p>
        </div>
        """, unsafe_allow_html=True)

def create_mode_selector():
    """Create an elegant mode selection interface"""
    st.markdown("## 🎯 Choose Your Intelligence Mode")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🤖 Team Intelligence", key="team_mode", use_container_width=True):
            st.session_state.current_mode = "team"
        
        st.markdown("""
        <div class="mode-card">
            <h3>🤖 Multi-Agent Team</h3>
            <p><strong>Collaborative Intelligence</strong></p>
            <ul>
                <li>🎯 Jira Project Specialist</li>
                <li>📚 Confluence Knowledge Expert</li>
                <li>💡 Notion Strategy Advisor</li>
            </ul>
            <p><em>Perfect for comprehensive project insights and strategic planning</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("⚡ MCP Intelligence", key="mcp_mode", use_container_width=True):
            st.session_state.current_mode = "mcp"
        
        st.markdown("""
        <div class="mode-card">
            <h3>⚡ MCP Agent</h3>
            <p><strong>Direct Tool Access</strong></p>
            <ul>
                <li>🔧 Native API Integration</li>
                <li>⚡ Lightning-fast Responses</li>
                <li>🎯 Precision Tool Selection</li>
            </ul>
            <p><em>Ideal for specific queries and rapid data retrieval</em></p>
        </div>
        """, unsafe_allow_html=True)

def display_sources(sources):
    """Display sources in an attractive format"""
    if sources:
        st.markdown("**📊 Sources Consulted:**")
        for source in sources:
            agent_name = source.get('agent', 'Unknown')
            source_list = source.get('sources', [])
            
            # Update accessed sources
            st.session_state.sources_accessed.update(source_list)
            
            st.markdown(f"""
            <div class="source-badge">
                {agent_name}: {len(source_list)} sources
            </div>
            """, unsafe_allow_html=True)

def send_team_query(prompt):
    """Send query to team_chat endpoint"""
    try:
        with st.spinner("🤖 Team agents are collaborating..."):
            response = requests.post(
                f"{FASTAPI_URL}/team_chat",
                json={"message": prompt},
                timeout=300  # Increased to 5 minutes
            )
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data.get("responses", {}).get("team", "No response generated")
                
                
                return ai_response
            else:
                return f"Error: {response.status_code} - {response.text}", []
                
    except requests.exceptions.Timeout:
        return "⏰ Request timed out. The agents are taking longer than expected. Please try a simpler query or try again.", []
    except requests.exceptions.ConnectionError:
        return "🔌 Connection error. Please ensure the FastAPI server is running on localhost:8080", []
    except requests.exceptions.RequestException as e:
        return f"❌ Request error: {str(e)}", []

def send_mcp_query(prompt):
    """Send query to chat endpoint"""
    try:
        with st.spinner("⚡ MCP agents are processing..."):
            response = requests.post(
                f"{FASTAPI_URL}/chat",
                json={"message": prompt},
                timeout=300  # Increased to 5 minutes
            )
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data.get("response", "No response generated")
                return ai_response, []
            else:
                return f"Error: {response.status_code} - {response.text}", []
                
    except requests.exceptions.Timeout:
        return "⏰ Request timed out. The MCP agents are taking longer than expected. Please try a simpler query or try again.", []
    except requests.exceptions.ConnectionError:
        return "🔌 Connection error. Please ensure the FastAPI server is running on localhost:8080", []
    except requests.exceptions.RequestException as e:
        return f"❌ Request error: {str(e)}", []

def create_chat_interface():
    """Create the main chat interface"""
    sources = None
    mode_name = "Team Intelligence" if st.session_state.current_mode == "team" else "MCP Intelligence"
    mode_icon = "🤖" if st.session_state.current_mode == "team" else "⚡"
    
    st.markdown(f"## {mode_icon} {mode_name} Chat")
    
    # Current mode indicator
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1rem;">
        <span class="agent-indicator">ACTIVE: {mode_name.upper()}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Get current messages
    current_messages = st.session_state[f"messages_{st.session_state.current_mode}"]
    
    # Display chat history
    for message in current_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                display_sources(message["sources"])
    
    # Chat input
    if prompt := st.chat_input(f"Ask your question to {mode_name}..."):
        # Add user message
        current_messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Send to appropriate endpoint
        if st.session_state.current_mode == "team":
            ai_response = send_team_query(prompt)
        else:
            ai_response, sources = send_mcp_query(prompt)
        
        # Add AI response
        current_messages.append({
            "role": "assistant", 
            "content": ai_response,
            "sources": sources,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update query count
        st.session_state.query_count += 1
        
        with st.chat_message("assistant"):
            st.markdown(ai_response)
            if sources:
                display_sources(sources)

# Main application flow
def main():
    create_hero_section()
    
    st.markdown("---")
    
    create_mode_selector()
    
    st.markdown("---")
    
    create_chat_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🧠 <strong>شعور.ai</strong> - Powered by Multi-Agent AI Architecture</p>
        <p><em>Artificial Intelligence • Breaking down silos, one query at a time.</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()