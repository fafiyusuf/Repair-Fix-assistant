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
    
    Uses ONLY the immutable ifixit_device name (no symptoms/issues).
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with selected_device
    """
    from ..ifixit_tools import get_ifixit_tools
    
    state["tool_status"].append("Searching iFixit for device...")
    
    # CRITICAL: Use only the immutable device name for iFixit API
    device_name = state.get("ifixit_device")
    
    if not device_name:
        logger.error("No ifixit_device in state - normalization failed")
        state["selected_device"] = None
        return state
    
    ifixit = get_ifixit_tools()
    result = await ifixit.search_devices(device_name)
    
    if result and result.get("devices"):
        # Select the first (most relevant) device
        state["selected_device"] = result["devices"][0]
        state["tool_status"].append(f"Found device: {state['selected_device']['title']}")
        logger.info(f"Device found: {state['selected_device']['title']}")
    else:
        state["selected_device"] = None
        state["tool_status"].append("No device found on iFixit")
        logger.warning(f"No device found for: {device_name}")
    
    return state
