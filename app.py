import streamlit as st
import os
from typing import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, START, END
from pypdf import PdfReader

# --- 1. SETTINGS FOR 2026 STABILITY ---
# Gemini 3 Flash is the 2026 production-ready standard
MODEL_NAME = "gemini-2.5-flash"


class AgentState(TypedDict):
    raw_text: str
    academic_audit: str
    market_trends: str
    final_syllabus: str
    next_step: str


# --- 2. WORKER NODES (SLAVES) ---

def academic_auditor(state: AgentState):
    """Slave 1: Analyzes current syllabus for Vision 2030 alignment."""
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=st.session_state.google_key
    )
    prompt = f"Identify core learning outcomes from this text: {state['raw_text']}"
    response = llm.invoke(prompt)
    return {"academic_audit": response.content, "next_step": "scout"}


def market_scout(state: AgentState):
    """Slave 2: Uses Tavily to find 2026 labor market needs."""
    # FIX: Explicitly pass the API key to the tool constructor
    search = TavilySearchResults(tavily_api_key=st.session_state.tavily_key)
    query = f"Labor market gaps in Egypt/Saudi 2026 for skills: {state['academic_audit']}"
    search_results = search.invoke(query)

    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=st.session_state.google_key
    )
    analysis = llm.invoke(f"Based on: {search_results}, list 5 must-have modern skills.")
    return {"market_trends": analysis.content, "next_step": "localizer"}


def localization_expert(state: AgentState):
    """Slave 3: Refactors syllabus into Arabic and Egyptian Dialect."""
    llm = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=st.session_state.google_key
    )
    prompt = (
        f"Merge old objectives ({state['academic_audit']}) with new trends ({state['market_trends']}). "
        "Task 1: Rewrite the syllabus in professional Modern Standard Arabic. "
        "Task 2: End with a 'Dean's Summary' in Egyptian Dialect explaining how this supports "
        "Vision 2030 Goal 4: Building Human Capital."
    )
    response = llm.invoke(prompt)
    return {"final_syllabus": response.content, "next_step": "end"}


# --- 3. MASTER ROUTER & GRAPH ---

def orchestrator(state: AgentState):
    return state["next_step"]


workflow = StateGraph(AgentState)
workflow.add_node("auditor", academic_auditor)
workflow.add_node("scout", market_scout)
workflow.add_node("localizer", localization_expert)

workflow.add_edge(START, "auditor")
workflow.add_conditional_edges("auditor", orchestrator, {"scout": "scout"})
workflow.add_conditional_edges("scout", orchestrator, {"localizer": "localizer"})
workflow.add_conditional_edges("localizer", orchestrator, {"end": END})

app_graph = workflow.compile()

# --- 4. STREAMLIT INTERFACE ---
st.title("🎓 Vision 2030 Syllabus Modernizer")

with st.sidebar:
    st.header("🔑 API Credentials")
    st.session_state.google_key = st.text_input("Google AI Studio Key", type="password")
    st.session_state.tavily_key = st.text_input("Tavily API Key", type="password")

uploaded_file = st.file_uploader("Upload Old Syllabus (PDF)", type="pdf")

if st.button("🚀 Refactor Now") and uploaded_file:
    if not st.session_state.google_key or not st.session_state.tavily_key:
        st.error("Missing API Keys!")
    else:
        reader = PdfReader(uploaded_file)
        text = " ".join([p.extract_text() for p in reader.pages])

        with st.status("Master Agent (The Dean) is orchestrating workers..."):
            result = app_graph.invoke({"raw_text": text, "next_step": ""})
            st.success("Syllabus Modernized!")
            st.divider()
            st.markdown(result["final_syllabus"])