"""
Node 5: Fetch Guide

Fetches detailed repair guide with step-by-step instructions and images.
"""

from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ..agent import AgentState

logger = logging.getLogger(__name__)


async def fetch_guide_node(state: "AgentState") -> "AgentState":
    """
    Fetch detailed repair guide with steps and images.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with repair_steps
    """
    from ..ifixit_tools import get_ifixit_tools
    
    state["tool_status"].append("Fetching repair instructions...")
    
    ifixit = get_ifixit_tools()
    guide_id = state["selected_guide"]["guideid"]
    
    result = await ifixit.fetch_repair_guide(guide_id)
    
    if result:
        state["repair_steps"] = result
        state["tool_status"].append(f"Retrieved {len(result.get('steps', []))} repair steps")
        logger.info(f"Fetched guide {guide_id} with {len(result.get('steps', []))} steps")
    else:
        state["repair_steps"] = None
        state["tool_status"].append("Failed to fetch repair guide")
        logger.error(f"Failed to fetch guide {guide_id}")
    
    return state
