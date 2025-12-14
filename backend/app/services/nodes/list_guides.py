"""
Node 3: List Guides

Retrieves all available repair guides for the selected device.
"""

from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ..agent import AgentState

logger = logging.getLogger(__name__)


async def list_guides_node(state: "AgentState") -> "AgentState":
    """
    List available repair guides for the device.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with available_guides
    """
    from ..ifixit_tools import get_ifixit_tools
    
    state["tool_status"].append("Fetching available repair guides...")
    
    ifixit = get_ifixit_tools()
    device_title = state["selected_device"]["title"]
    
    result = await ifixit.list_guides(device_title)
    
    if result and result.get("guides"):
        state["available_guides"] = result["guides"]
        state["tool_status"].append(f"Found {len(result['guides'])} repair guides")
        logger.info(f"Found {len(result['guides'])} guides for {device_title}")
    else:
        state["available_guides"] = None
        state["tool_status"].append("No repair guides available")
        logger.warning(f"No guides found for: {device_title}")
    
    return state
