import os
import json
import math
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from datetime import datetime

load_dotenv()

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="NexusAI Agent",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        display: block !important;
        transform: none !important;
        min-width: 250px !important;
    }
</style>
""", unsafe_allow_html=True)

# ---- CUSTOM CSS ----
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        background: linear-gradient(135deg, #f0fff4 0%, #e8f8f0 30%, #f0f8ff 60%, #f5f0ff 100%);
        color: #111111 !important;
        min-height: 100vh;
    }

    /* Force all text to be dark and readable */
    p, span, div, label, li, td, th {
        color: #111111 !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* Streamlit default text */
    .stMarkdown p {
        color: #111111 !important;
        font-size: 1rem !important;
        line-height: 1.7 !important;
    }

    /* Streamlit warnings and info */
    .stAlert p {
        color: #111111 !important;
    }

    /* Sidebar text */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {
        color: #111111 !important;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e8f8f0 0%, #f0fff4 100%) !important;
        border-right: 1px solid rgba(0,180,90,0.2) !important;
    }

    /* Animated background orbs */
    .stApp::before {
        content: '';
        position: fixed;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background:
            radial-gradient(ellipse at 20% 20%, rgba(0,200,100,0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(0,180,255,0.06) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(0,200,100,0.04) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }

    /* Header */
    .nexus-header {
        background: linear-gradient(135deg,
            rgba(0,200,100,0.08) 0%,
            rgba(0,180,255,0.06) 50%,
            rgba(0,200,100,0.04) 100%);
        border: 1px solid rgba(0,180,90,0.3);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow:
            0 0 40px rgba(0,255,128,0.1),
            0 0 80px rgba(0,255,128,0.05),
            inset 0 1px 0 rgba(255,255,255,0.05);
    }
    .nexus-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg,
            transparent, rgba(0,255,128,0.8), rgba(0,200,255,0.8), transparent);
    }
    .nexus-header::after {
        content: '';
        position: absolute;
        top: -50%; right: -10%;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(0,255,128,0.08) 0%, transparent 70%);
        pointer-events: none;
    }
    .nexus-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(0,255,128,0.1);
        border: 1px solid rgba(0,255,128,0.3);
        border-radius: 999px;
        padding: 0.2rem 0.8rem;
        font-size: 0.65rem;
        color: #00ff80;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    .nexus-title {
        font-family: 'Orbitron', monospace;
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00a855, #0090cc, #00a855);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 0.05em;
        line-height: 1.1;
        animation: shine 3s linear infinite,
                   fadeIn 0.5s ease-in;
        opacity: 0;
        animation-fill-mode: forwards;
    }
    @keyframes shine {
        0% { background-position: 0% center; }
        100% { background-position: 200% center; }
    }
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(-10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    .nexus-sub {
        font-family: 'Inter', sans-serif;
        color: #2a6a4a;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        letter-spacing: 0.05em;
    }
    .nexus-stats {
        display: flex;
        gap: 1.5rem;
        margin-top: 1.2rem;
        flex-wrap: wrap;
    }
    .nexus-stat {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        color: #2a6a4a;
        letter-spacing: 0.05em;
    }
    .nexus-stat-dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        background: #00ff80;
        box-shadow: 0 0 6px #00ff80;
        animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.8); }
    }

    /* Input */
    .stTextInput > div > div > input {
        background: #ffffff !important;
        border: 1px solid rgba(0,180,90,0.4) !important;
        border-radius: 12px !important;
        color: #0a2a1a !important;
        padding: 0.9rem 1.2rem !important;
        font-size: 0.95rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s !important;
        box-shadow: 0 0 0 0 rgba(0,255,128,0) !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(0,255,128,0.8) !important;
        box-shadow: 0 0 20px rgba(0,255,128,0.15),
                    0 0 0 3px rgba(0,255,128,0.08) !important;
        background: rgba(0,255,128,0.05) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: rgba(0,150,70,0.35) !important;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #00a855, #0090cc) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        font-size: 0.9rem !important;
        width: 100% !important;
        letter-spacing: 0.05em !important;
        box-shadow: 0 4px 20px rgba(0,255,128,0.3),
                    0 0 40px rgba(0,255,128,0.1) !important;
        transition: all 0.3s !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(0,255,128,0.5),
                    0 0 60px rgba(0,255,128,0.2) !important;
    }

    /* Step cards */
    .step-card {
        border-radius: 14px;
        padding: 1rem 1.3rem;
        margin-bottom: 0.7rem;
        position: relative;
        overflow: hidden;
    }
    .step-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
    }
    .step-action {
        background: linear-gradient(135deg,
            rgba(0,200,100,0.08), rgba(0,200,100,0.03));
        border: 1px solid rgba(0,180,90,0.25);
        box-shadow: 0 4px 20px rgba(0,180,90,0.08);
    
    }
    .step-action::before {
        background: linear-gradient(90deg, transparent, rgba(0,255,128,0.5), transparent);
    }
    .step-observation {
        background: linear-gradient(135deg,
            rgba(0,200,255,0.08), rgba(0,200,255,0.03));
        border: 1px solid rgba(0,200,255,0.25);
        box-shadow: 0 4px 20px rgba(0,200,255,0.05);
    }
    .step-observation::before {
        background: linear-gradient(90deg, transparent, rgba(0,200,255,0.5), transparent);
    }
    .step-label {
        font-family: 'Orbitron', monospace;
        font-size: 0.6rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .step-label-action { color: #00ff80; }
    .step-label-obs { color: #00c8ff; }
    .step-content {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        line-height: 1.6;
        color: rgba(224,255,224,0.8);
    }
    .step-tool-tag {
        display: inline-block;
        background: rgba(0,255,128,0.1);
        border: 1px solid rgba(0,255,128,0.3);
        color: #00ff80;
        padding: 0.1rem 0.5rem;
        border-radius: 4px;
        font-size: 0.7rem;
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        margin-right: 0.4rem;
    }
    .step-tool-tag-blue {
        background: rgba(0,200,255,0.1);
        border-color: rgba(0,200,255,0.3);
        color: #00c8ff;
    }

    /* Answer card */
    .answer-card {
        background: linear-gradient(135deg,
            rgba(0,200,100,0.08) 0%,
            rgba(0,180,255,0.06) 50%,
            rgba(0,200,100,0.04) 100%);
        border: 1px solid rgba(0,180,90,0.4);
        border-radius: 18px;
        padding: 1.8rem 2rem;
        margin: 1.5rem 0;
        position: relative;
        overflow: hidden;
        box-shadow:
            0 8px 40px rgba(0,255,128,0.1),
            0 0 80px rgba(0,255,128,0.05),
            inset 0 1px 0 rgba(255,255,255,0.05);
    }
    .answer-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg,
            transparent, rgba(0,255,128,0.8), rgba(0,200,255,0.8), transparent);
    }
    .answer-label {
        font-family: 'Orbitron', monospace;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #00ff80;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .answer-text {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: #e0ffe0;
        line-height: 1.8;
    }

    /* User message */
    .user-card {
        background: #ffffff;
        border: 1px solid rgba(0,180,90,0.2);
        border-left: 3px solid #00a855;
        border-radius: 12px;
        padding: 1rem 1.3rem;
        margin-bottom: 1rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        color: #111111;
    }
    .user-label {
        font-family: 'Orbitron', monospace;
        font-size: 0.6rem;
        color: #00a855;
        letter-spacing: 0.15em;
        margin-bottom: 0.4rem;
    }

    /* Tool badges */
    .tools-used-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 1rem 0;
        align-items: center;
    }
    .tools-label {
        font-family: 'Orbitron', monospace;
        font-size: 0.6rem;
        color: rgba(0,255,128,0.5);
        letter-spacing: 0.1em;
        margin-right: 0.3rem;
    }
    .tool-chip {
        background: linear-gradient(135deg, rgba(0,255,128,0.1), rgba(0,200,255,0.1));
        border: 1px solid rgba(0,255,128,0.3);
        color: #00ff80;
        padding: 0.2rem 0.7rem;
        border-radius: 999px;
        font-family: 'Orbitron', monospace;
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        box-shadow: 0 0 10px rgba(0,255,128,0.1);
    }

    /* Sidebar tools */
    .sidebar-header {
        font-family: 'Orbitron', monospace;
        font-size: 0.7rem;
        font-weight: 700;
        color: #00ff80;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 1rem;
        text-shadow: 0 0 10px rgba(0,255,128,0.5);
    }
    .sidebar-tool-card {
        background: #ffffff;
        border: 1px solid rgba(0,180,90,0.2);
        box-shadow: 0 2px 8px rgba(0,180,90,0.08);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s;
    }
    .sidebar-tool-name {
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        color: #00a855;
        margin-bottom: 0.2rem;
    }
    .sidebar-tool-desc {
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        color: #555555;
    }
    .sidebar-query {
        font-family: 'Inter', sans-serif;
        font-size: 0.72rem;
        color: #444444;
        padding: 0.3rem 0;
        border-bottom: 1px solid rgba(0,180,90,0.1);
    }
    .sidebar-session {
        font-family: 'Inter', sans-serif;
        font-size: 0.68rem;
        color: #666666;
        line-height: 1.8;
    }

    /* Section headers */
    .section-header {
        font-family: 'Orbitron', monospace;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #00a855;
        margin: 1.2rem 0 0.6rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-header::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(0,255,128,0.3), transparent);
    }

    .step-content {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        line-height: 1.6;
        color: #2a4a3a;
    }
    .answer-text {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: #0a2a1a;
        line-height: 1.8;
    }
    hr { border-color: rgba(0,180,90,0.1) !important; }
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(0,180,90,0.3);
        border-radius: 2px;
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(0,255,128,0.3);
        border-radius: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ---- GROQ CLIENT ----
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ---- TOOLS ----
def web_search(query: str) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        if not results:
            return "No results found."
        output = ""
        for r in results:
            output += f"Title: {r['title']}\nSummary: {r['body']}\nURL: {r['href']}\n\n"
        return output
    except Exception as e:
        return f"Search failed: {str(e)}"

def calculate(expression: str) -> str:
    try:
        allowed = {
            "__builtins__": {},
            "math": math,
            "abs": abs, "round": round,
            "min": min, "max": max,
            "sum": sum, "pow": pow
        }
        result = eval(expression, allowed)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"

def get_current_datetime() -> str:
    now = datetime.now()
    return f"Current date and time: {now.strftime('%A, %B %d, %Y at %H:%M:%S')}"

def get_word_count(text: str) -> str:
    words = len(text.split())
    chars = len(text)
    return f"Word count: {words} words, {chars} characters"

# ---- TOOL DEFINITIONS ----
tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information, news, facts, or any topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate mathematical expressions and calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Mathematical expression to evaluate"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Get the current date and time",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_word_count",
            "description": "Count words and characters in text",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to count"}
                },
                "required": ["text"]
            }
        }
    }
]

# ---- TOOL EXECUTOR ----
def execute_tool(tool_name: str, tool_args: dict) -> str:
    if tool_name == "web_search":
        return web_search(tool_args.get("query", ""))
    elif tool_name == "calculate":
        return calculate(tool_args.get("expression", ""))
    elif tool_name == "get_current_datetime":
        return get_current_datetime()
    elif tool_name == "get_word_count":
        return get_word_count(tool_args.get("text", ""))
    return f"Unknown tool: {tool_name}"

# ---- AGENT ----
def run_agent(user_question: str):
    messages = [
        {
            "role": "system",
            "content": """You are NexusAI, a powerful autonomous agent with access to tools.
Always use tools when you need current information or calculations.
Think step by step and use the most appropriate tool for each task."""
        },
        {"role": "user", "content": user_question}
    ]

    steps = []
    tools_used = []
    max_iterations = 5
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                steps.append({
                    "type": "action",
                    "tool": tool_name,
                    "input": tool_args
                })

                if tool_name not in tools_used:
                    tools_used.append(tool_name)

                result = execute_tool(tool_name, tool_args)

                steps.append({
                    "type": "observation",
                    "tool": tool_name,
                    "result": result
                })

                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        else:
            final_answer = message.content
            steps.append({"type": "answer", "content": final_answer})
            return final_answer, steps, tools_used

    return "Task could not be completed.", steps, tools_used

# ---- SESSION STATE ----
if "history" not in st.session_state:
    st.session_state.history = []

# ---- SIDEBAR ----
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">⚡ NexusAI Tools</div>
    """, unsafe_allow_html=True)

    tools_info = [
        ("🔍", "Web Search", "Real-time internet search"),
        ("🧮", "Calculator", "Math & expressions"),
        ("🕐", "Date & Time", "Current timestamp"),
        ("📝", "Word Counter", "Text analysis"),
    ]

    for icon, name, desc in tools_info:
        st.markdown(f"""
        <div class="sidebar-tool-card">
            <div class="sidebar-tool-name">{icon} {name}</div>
            <div class="sidebar-tool-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="sidebar-header" style="font-size:0.62rem">
    💡 Try These
    </div>
    """, unsafe_allow_html=True)

    queries = [
        "Latest AI breakthroughs?",
        "What is √(256) × 18?",
        "Current date and time?",
        "Search Python best practices",
    ]
    for q in queries:
        st.markdown(f'<div class="sidebar-query">→ {q}</div>', unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🗑️ Clear Session"):
        st.session_state.history = []
        st.rerun()

    now = datetime.now()
    st.markdown(f"""
    <div class="sidebar-session">
    SESSION ACTIVE<br>
    MESSAGES: {len(st.session_state.history)}<br>
    MODEL: llama-3.1-8b<br>
    ENGINE: Groq<br>
    TIME: {now.strftime('%H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

# ---- MAIN AREA ----
st.markdown("""
<div class="nexus-header">
    <div class="nexus-badge">
        <span style="color:#00a855">●</span> SYSTEM ONLINE
    </div>
    <div class="nexus-title">NEXUS AI</div>
    <div class="nexus-sub">
        Autonomous Intelligence Engine · Real-Time Tools · LLaMA 3.1 · Groq
    </div>
    <div class="nexus-stats">
        <div class="nexus-stat">
            <div class="nexus-stat-dot"></div>
            4 TOOLS ACTIVE
        </div>
        <div class="nexus-stat">
            <div class="nexus-stat-dot" style="background:#0090cc;box-shadow:0 0 6px #0090cc"></div>
            GROQ ENGINE
        </div>
        <div class="nexus-stat">
            <div class="nexus-stat-dot"></div>
            <span id="live-clock">Loading...</span>
        </div>
    </div>
</div>

<script>
function updateClock() {
    const now = new Date();
    const formatted = now.getFullYear() + '-' +
        String(now.getMonth()+1).padStart(2,'0') + '-' +
        String(now.getDate()).padStart(2,'0') + ' ' +
        String(now.getHours()).padStart(2,'0') + ':' +
        String(now.getMinutes()).padStart(2,'0') + ':' +
        String(now.getSeconds()).padStart(2,'0');
    const el = document.getElementById('live-clock');
    if(el) el.textContent = formatted;
}
updateClock();
setInterval(updateClock, 1000);
</script>
""", unsafe_allow_html=True)

# ---- CHAT HISTORY ----
for msg in st.session_state.history:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="user-card">
            <div class="user-label">▶ USER QUERY</div>
            {msg['content']}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="answer-card">
            <div class="answer-label">⚡ NEXUS RESPONSE</div>
            <div class="answer-text">{msg['content']}</div>
        </div>
        """, unsafe_allow_html=True)

# ---- INPUT ----
st.markdown("""
<div class="section-header">▶ Query Input</div>
""", unsafe_allow_html=True)

question = st.text_input(
    label="q",
    placeholder="Enter your query — I'll think, search, and respond...",
    label_visibility="collapsed"
)

ask = st.button("⚡ EXECUTE QUERY")

if ask:
    if question.strip() == "":
        st.warning("Please enter a query.")
    else:
        st.session_state.history.append({
            "role": "user",
            "content": question
        })

        st.markdown(f"""
        <div class="user-card">
            <div class="user-label">▶ USER QUERY</div>
            {question}
        </div>
        """, unsafe_allow_html=True)

        progress_bar = st.progress(0, text="⚡ Initializing NexusAI...")
        progress_bar.progress(10, text="🔍 Analyzing query...")
        import time as t
        t.sleep(0.3)
        progress_bar.progress(30, text="🧠 Selecting tools...")
        t.sleep(0.3)
        progress_bar.progress(50, text="⚡ Executing tools...")
        answer, steps, tools_used = run_agent(question)
        progress_bar.progress(80, text="✍️ Generating response...")
        t.sleep(0.2)
        progress_bar.progress(100, text="✅ Complete!")
        t.sleep(0.3)
        progress_bar.empty()

        # Execution trace
        if steps:
            st.markdown("""
            <div class="section-header">🔬 Execution Trace</div>
            """, unsafe_allow_html=True)

            for step in steps:
                if step["type"] == "action":
                    st.markdown(f"""
                    <div class="step-card step-action">
                        <div class="step-label step-label-action">
                            ⚡ Tool Activation
                            <span class="step-tool-tag">{step['tool'].upper()}</span>
                        </div>
                        <div class="step-content">
                            Input: {json.dumps(step['input'])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                elif step["type"] == "observation":
                    result_preview = step['result'][:400].replace('\n', ' ')
                    st.markdown(f"""
                    <div class="step-card step-observation">
                        <div class="step-label step-label-obs">
                            👁️ Tool Output
                            <span class="step-tool-tag step-tool-tag-blue">{step['tool'].upper()}</span>
                        </div>
                        <div class="step-content">{result_preview}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # Tools used
        if tools_used:
            chips = "".join([f'<span class="tool-chip">⚡ {t}</span>' for t in tools_used])
            st.markdown(f"""
            <div class="tools-used-row">
                <span class="tools-label">TOOLS USED:</span>
                {chips}
            </div>
            """, unsafe_allow_html=True)

        # Final answer
        st.markdown(f"""
        <div class="answer-card">
            <div class="answer-label">⚡ NEXUS RESPONSE</div>
            <div class="answer-text">{answer}</div>
        </div>
        """, unsafe_allow_html=True)

        st.session_state.history.append({
            "role": "assistant",
            "content": answer
        })