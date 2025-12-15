"""
Node 1: Normalize Query

Converts casual user language to canonical device names for better search results.
Example: "my ps5 fan is loud" -> "PlayStation 5 fan noise"
"""

from typing import TYPE_CHECKING
from langchain_core.messages import HumanMessage
import logging

if TYPE_CHECKING:
    from ..agent import AgentState

logger = logging.getLogger(__name__)


async def normalize_query_node(state: "AgentState") -> "AgentState":
    """
    Normalize user query for better device matching.
    
    Extracts ONLY the canonical device name (no symptoms/issues).
    This device name is IMMUTABLE and used for ALL iFixit API calls.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with ifixit_device (immutable device name)
    """
    from ..agent import get_llm
    
    state["tool_status"].append("Normalizing query...")
    
    llm = get_llm()
    
    prompt = f"""Extract ONLY the device model/name from this repair query.

Query: {state['query']}

CRITICAL RULES:
- Extract ONLY the device name (no symptoms, issues, or problems)
- For laptops, prefer series name over specific model numbers
- Never include words like "Troubleshooting", "Repair", "Won't Work", etc.
- Output must be a clean device category name only

Examples:
- "my ps5 fan is loud" -> "PlayStation 5"
- "iphone 12 battery dying fast" -> "iPhone 12"
- "HP Spectre x360 is slow" -> "HP Spectre x360"
- "dell xps 15 screen flickering" -> "Dell XPS 15"
- "macbook pro 2020 won't turn on" -> "MacBook Pro 2020"

Output ONLY the device name (nothing else):"""
    
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    device_name = response.content.strip()
    
    # Store in immutable field for iFixit API
    state["ifixit_device"] = device_name
    
    # Also update normalized_query for backward compatibility
    state["normalized_query"] = device_name
    
    state["tool_status"].append(f"Device: {device_name}")
    
    logger.info(f"Extracted device name: '{device_name}' from query: '{state['query']}'")
    
    return state
