"""
Node 6: Fallback Web Search

Fallback node that searches the web when iFixit doesn't have results.
Only executed if device not found, no guides available, or no guide selected.
"""

from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ..agent import AgentState

logger = logging.getLogger(__name__)


async def fallback_search_node(state: "AgentState") -> "AgentState":
    """
    Fallback web search (only if iFixit fails).
    
    This node is only reached if:
    - No device found, OR
    - No guides available, OR
    - No guide selected
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with repair_steps from community sources
    """
    state["tool_status"].append("Searching community sources as fallback...")
    state["fallback_used"] = True
    
    # Simple DuckDuckGo search (can be replaced with Tavily)
    try:
        from duckduckgo_search import DDGS
        
        ddgs = DDGS()
        results = list(ddgs.text(
            f"{state['query']} repair guide",
            max_results=3
        ))
        
        if results:
            state["repair_steps"] = {
                "source": "community",
                "results": results
            }
            state["tool_status"].append(f"Found {len(results)} community sources")
            logger.info(f"Fallback search returned {len(results)} results")
        else:
            state["repair_steps"] = None
            state["tool_status"].append("No results from fallback search")
            
    except Exception as e:
        logger.error(f"Fallback search failed: {e}")
        state["repair_steps"] = None
        state["tool_status"].append("Fallback search failed")
    
    return state
