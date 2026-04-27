import streamlit as st
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Drafter", page_icon="📝", layout="wide")

# ── Session state ──────────────────────────────────────────────────────────────
if "document_content" not in st.session_state:
    st.session_state.document_content = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "saved_filename" not in st.session_state:
    st.session_state.saved_filename = None
if "lg_messages" not in st.session_state:
    st.session_state.lg_messages = []

# ── Tools ──────────────────────────────────────────────────────────────────────
@tool
def update(content: str) -> str:
    st.session_state.document_content = content
    return "Document updated successfully."

@tool
def save(filename: str) -> str:
    if not filename.endswith('.txt'):
        filename += ".txt"
    st.session_state.saved_filename = filename
    return f"Document saved successfully to '{filename}'."

tools = [update, save]

# ── Model ──────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_model():
    return ChatGroq(model="llama-3.3-70b-versatile").bind_tools(tools)

# ── LangGraph State ────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    document: str

def our_agent(state: AgentState) -> AgentState:
    model = get_model()

    system_prompt = SystemMessage(content=f"""
You are Drafter, a writing assistant.

Rules:
- Use 'update' tool when modifying document (send FULL updated content)
- Use 'save' tool when user asks to save
- Keep responses concise

Current document:
{state["document"] if state["document"] else "(empty)"}
""")

    response = model.invoke([system_prompt] + list(state["messages"]))
    return {"messages": list(state["messages"]) + [response], "document": state["document"]}

def should_use_tools(state: AgentState):
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
        return "tools"
    return "end"

def should_continue(state: AgentState):
    for msg in reversed(state["messages"]):
        if isinstance(msg, ToolMessage) and "saved successfully" in msg.content.lower():
            return "end"
    return "agent"

@st.cache_resource
def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("agent", our_agent)
    graph.add_node("tools", ToolNode(tools))

    graph.set_entry_point("agent")

    graph.add_conditional_edges("agent", should_use_tools, {
        "tools": "tools",
        "end": END
    })

    graph.add_conditional_edges("tools", should_continue, {
        "agent": "agent",
        "end": END
    })

    return graph.compile()

# ── Agent runner ───────────────────────────────────────────────────────────────
def run_agent(user_input: str):
    app = build_graph()

    user_msg = HumanMessage(content=user_input)
    st.session_state.lg_messages.append(user_msg)

    old_len = len(st.session_state.lg_messages)

    state = {
        "messages": st.session_state.lg_messages,
        "document": st.session_state.document_content
    }

    final_state = app.invoke(state)

    new_messages = final_state["messages"][old_len:]
    st.session_state.lg_messages = final_state["messages"]

    ai_text = ""
    tool_info = []

    for msg in new_messages:
        if isinstance(msg, AIMessage) and msg.content:
            ai_text = msg.content
        if isinstance(msg, ToolMessage):
            tool_info.append(msg.content)

    return ai_text, tool_info

# ── UI ─────────────────────────────────────────────────────────────────────────
st.title("📝 Drafter")

left, right = st.columns([1.2, 1])

# ── Document panel ─────────────────────────────────────────────────────────────
with left:
    st.subheader("Document")

    if st.session_state.document_content:
        st.text_area(
            "Document",
            value=st.session_state.document_content,
            height=400,
            disabled=True
        )
    else:
        st.info("Your document will appear here.")

    st.subheader("Export")

    filename_input = st.text_input(
        "Filename",
        placeholder="document.txt",
        label_visibility="collapsed",
        key="filename_input"
    )

    if st.button("💾 Save"):
        if st.session_state.document_content:
            fname = filename_input.strip() or "document"
            ai_text, tool_info = run_agent(f"Save as {fname}")

            st.session_state.chat_history.append(("user", f"Save as {fname}"))
            if ai_text:
                st.session_state.chat_history.append(("ai", ai_text))
            for t in tool_info:
                st.session_state.chat_history.append(("tool", t))

            st.rerun()
        else:
            st.warning("Nothing to save")

    if st.session_state.document_content:
        st.download_button(
            "⬇ Download",
            data=st.session_state.document_content,
            file_name=st.session_state.saved_filename or "document.txt"
        )

# ── Chat panel ────────────────────────────────────────────────────────────────
with right:
    st.subheader("Chat")

    for role, content in st.session_state.chat_history:
        if role == "user":
            st.markdown(f"**You:** {content}")
        elif role == "ai":
            st.markdown(f"**Drafter:** {content}")
        elif role == "tool":
            st.markdown(f"`{content}`")

    user_input = st.text_input(
        "Message",
        placeholder="What would you like to write?",
        label_visibility="collapsed",
        key="user_input_field"
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button("Send"):
            if user_input.strip():
                ai_text, tool_info = run_agent(user_input.strip())

                st.session_state.chat_history.append(("user", user_input.strip()))
                if ai_text:
                    st.session_state.chat_history.append(("ai", ai_text))
                for t in tool_info:
                    st.session_state.chat_history.append(("tool", t))

                st.rerun()

    with col2:
        if st.button("Clear"):
            st.session_state.chat_history = []
            st.session_state.document_content = ""
            st.session_state.lg_messages = []
            st.session_state.saved_filename = None
            st.rerun()