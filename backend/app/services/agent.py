"""
LangGraph Agent for Repair Fix Assistant.

This module implements the deterministic state machine with 7 nodes:
1. Normalize Query
2. Search Device (iFixit)
3. List Guides (iFixit)
4. Select Best Guide
5. Fetch Repair Guide (iFixit)
6. Fallback Web Search (conditional)
7. Response Formatter

Each node is implemented in a separate file under app/services/nodes/
"""

from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import get_settings

# Import all node functions
from app.services.nodes.normalize_query import normalize_query_node
from app.services.nodes.search_device import search_device_node
from app.services.nodes.list_guides import list_guides_node
from app.services.nodes.select_guide import select_guide_node
from app.services.nodes.fetch_guide import fetch_guide_node
from app.services.nodes.fallback_search import fallback_search_node
from app.services.nodes.format_response import format_response_node
from app.services.nodes.conversational_response import conversational_response_node, _is_followup_question

import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class AgentState(TypedDict):
    """State maintained throughout the agent execution."""
    user_id: str
    session_id: str
    messages: List[Dict]
    query: str  # Original user query with symptoms/issues
    normalized_query: Optional[str]  # Full normalized query (deprecated - use ifixit_device)
    ifixit_device: Optional[str]  # IMMUTABLE: Canonical device name for iFixit API only
    selected_device: Optional[Dict]
    available_guides: Optional[List[Dict]]
    selected_guide: Optional[Dict]
    repair_steps: Optional[Dict]
    fallback_used: bool
    final_response: Optional[str]
    tool_status: List[str]  # For streaming status updates


def get_llm():
    """Get configured LLM instance. Uses Gemini 2.0 Flash."""
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured. Please set it in your .env file")
    
    return ChatGoogleGenerativeAI(
        api_key=settings.gemini_api_key,
        model="gemini-2.5-flash",
        temperature=0.1
    )


def should_use_fallback(state: AgentState) -> str:
    """
    Routing function to determine if fallback is needed.
    
    Returns:
        "fallback" if iFixit failed at any step
        "format" if we have valid iFixit data
    """
    if state.get("selected_device") is None:
        return "fallback"
    
    if state.get("available_guides") is None or len(state.get("available_guides", [])) == 0:
        return "fallback"
    
    if state.get("selected_guide") is None:
        return "fallback"
    
    return "format"


def route_initial_query(state: AgentState) -> str:
    """
    Routing function to determine if query is a follow-up question or new repair request.
    
    Returns:
        "conversational" if this is a follow-up question
        "normalize" if this is a new repair request
    """
    if _is_followup_question(state):
        logger.info("Detected follow-up question - using conversational response")
        return "conversational"
    
    logger.info("New repair request - starting full workflow")
    return "normalize"


def create_agent_graph() -> StateGraph:
    """
    Create the LangGraph state machine.
    
    Flow:
    User Input -> [Route] -> Conversational Response (for follow-ups)
                     |
                     └-> Normalize -> Search Device -> List Guides -> Select Guide -> Fetch Guide -> Format
                                           ↓ (fail)        ↓ (fail)      ↓ (fail)
                                                → Fallback Search → Format
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes (imported from separate files)
    workflow.add_node("conversational_response", conversational_response_node)
    workflow.add_node("normalize_query", normalize_query_node)
    workflow.add_node("search_device", search_device_node)
    workflow.add_node("list_guides", list_guides_node)
    workflow.add_node("select_guide", select_guide_node)
    workflow.add_node("fetch_guide", fetch_guide_node)
    workflow.add_node("fallback_search", fallback_search_node)
    workflow.add_node("format_response", format_response_node)
    
    # Define entry point with routing
    workflow.add_conditional_edges(
        "__start__",
        route_initial_query,
        {
            "conversational": "conversational_response",
            "normalize": "normalize_query"
        }
    )
    
    # Define edges for repair workflow
    workflow.add_edge("normalize_query", "search_device")
    workflow.add_edge("search_device", "list_guides")
    workflow.add_edge("list_guides", "select_guide")
    
    # Conditional routing after select_guide
    workflow.add_conditional_edges(
        "select_guide",
        should_use_fallback,
        {
            "fallback": "fallback_search",
            "format": "fetch_guide"
        }
    )
    workflow.add_edge("fetch_guide", "format_response")
    workflow.add_edge("fallback_search", "format_response")
    workflow.add_edge("format_response", END)
    workflow.add_edge("conversational_response", END)
    
    return workflow.compile()


# Create compiled graph instance
agent_graph = create_agent_graph()

