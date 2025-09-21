import streamlit as st
import requests
import json
import time
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Unified Knowledge Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, sleek design
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    .mode-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .mode-card:hover {
        transform: translateY(-5px);
    }
    
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .source-badge {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.25rem;
        display: inline-block;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .agent-indicator {
        background: #00ff88;
        color: #000;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.7rem;
        font-weight: bold;
        margin-left: 0.5rem;
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
    st.markdown('<h1 class="main-header">🧠 Unified Knowledge Engine</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Breaking down data silos • Unifying knowledge • Empowering decisions</p>', unsafe_allow_html=True)
    
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
            st.rerun()
        
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
            st.rerun()
        
        st.markdown("""
        <div class="mode-card">
            <h3>⚡ MCP Protocol</h3>
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
                timeout=120  # Increased to 2 minutes
            )
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data.get("responses", {}).get("team", "No response generated")
                sources = response_data.get("sources", [])
                
                return ai_response, sources
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
                timeout=120  # Increased to 2 minutes
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
            ai_response, sources = send_team_query(prompt)
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
        
        st.rerun()

def create_sidebar():
    """Create an informative sidebar"""
    with st.sidebar:
        st.markdown("## 🚀 Platform Overview")
        
        st.markdown("""
        ### 🎯 **Mission**
        Transform scattered organizational knowledge into unified, actionable intelligence.
        
        ### 🔧 **Technology Stack**
        - **FastAPI**: High-performance backend
        - **Multi-Agent Architecture**: Specialized AI agents
        - **MCP Protocol**: Direct tool integration
        - **Vector Databases**: Intelligent knowledge retrieval
        
        ### 📊 **Connected Platforms**
        """)
        
        # Platform status indicators
        platforms = [
            ("Jira", "🟢", "Project Management"),
            ("Confluence", "🟢", "Documentation"),
            ("Notion", "🟢", "Knowledge Base")
        ]
        
        for platform, status, description in platforms:
            st.markdown(f"""
            <div class="stats-card">
                <strong>{status} {platform}</strong><br>
                <small>{description}</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 🔄 **Session Stats**")
        
        if st.session_state.query_count > 0:
            # Create a simple chart
            fig = go.Figure(data=go.Bar(
                x=['Team Chat', 'MCP Chat'],
                y=[len(st.session_state.messages_team), len(st.session_state.messages_mcp)],
                marker_color=['#667eea', '#764ba2']
            ))
            fig.update_layout(
                title="Queries by Mode",
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        if st.button("🔄 Reset Session", use_container_width=True):
            for key in st.session_state.keys():
                if key.startswith('messages_'):
                    st.session_state[key] = []
            st.session_state.query_count = 0
            st.session_state.sources_accessed = set()
            st.rerun()

# Main application flow
def main():
    create_sidebar()
    create_hero_section()
    
    st.markdown("---")
    
    create_mode_selector()
    
    st.markdown("---")
    
    create_chat_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🧠 <strong>Unified Knowledge Engine</strong> - Powered by Multi-Agent AI Architecture</p>
        <p><em>Breaking down silos, one query at a time.</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()