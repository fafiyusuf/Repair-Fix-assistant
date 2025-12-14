"""
Node 2: Search Device

Searches iFixit API for the device based on normalized query.
"""

from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ..agent import AgentState

logger = logging.getLogger(__name__)


async def search_device_node(state: "AgentState") -> "AgentState":
    """
    Search for device on iFixit.
    
    Uses the normalized query to find the canonical device.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with selected_device
    """
    from ..ifixit_tools import get_ifixit_tools
    
    state["tool_status"].append("Searching iFixit for device...")
    
    ifixit = get_ifixit_tools()
    result = await ifixit.search_devices(state["normalized_query"])
    
    if result and result.get("devices"):
        # Select the first (most relevant) device
        state["selected_device"] = result["devices"][0]
        state["tool_status"].append(f"Found device: {state['selected_device']['title']}")
        logger.info(f"Device found: {state['selected_device']['title']}")
    else:
        state["selected_device"] = None
        state["tool_status"].append("No device found on iFixit")
        logger.warning(f"No device found for: {state['normalized_query']}")
    
    return state
