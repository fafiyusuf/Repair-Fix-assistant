"""
Node 1: Normalize Query

Converts casual user language to canonical device names for better search results.
Example: "my ps5 fan is loud" -> "PlayStation 5 fan noise"
"""

from typing import TYPE_CHECKING
from langchain.schema import HumanMessage
import logging

if TYPE_CHECKING:
    from ..agent import AgentState

logger = logging.getLogger(__name__)


async def normalize_query_node(state: "AgentState") -> "AgentState":
    """
    Normalize user query for better device matching.
    
    Converts casual language to canonical device names.
    Example: "my ps5 fan is loud" -> "PlayStation 5 fan noise"
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with normalized_query
    """
    from ..agent import get_llm
    
    state["tool_status"].append("Normalizing query...")
    
    llm = get_llm()
    
    prompt = f"""Convert this repair query into a clear, searchable device name and issue:
Query: {state['query']}

Output only the normalized query (device model + issue). Be concise.
Example: "PlayStation 5 fan noise" """
    
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    normalized = response.content.strip()
    
    state["normalized_query"] = normalized
    state["tool_status"].append(f"Normalized to: {normalized}")
    
    logger.info(f"Normalized '{state['query']}' -> '{normalized}'")
    
    return state
