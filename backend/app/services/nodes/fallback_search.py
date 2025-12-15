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
    
    Tries Tavily first (paid, reliable), then DuckDuckGo as last resort.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with repair_steps from community sources
    """
    state["tool_status"].append("Searching community sources as fallback...")
    state["fallback_used"] = True
    
    results = None
    
    # Try Tavily first (paid, reliable API)
    try:
        from ...core.config import get_settings
        
        settings = get_settings()
        
        if settings.tavily_api_key:
            from tavily import TavilyClient
            
            state["tool_status"].append("Searching with Tavily AI...")
            tavily = TavilyClient(api_key=settings.tavily_api_key)
            
            response = tavily.search(
                query=f"{state['query']} repair guide",
                max_results=3,
                search_depth="basic"
            )
            
            if response and response.get("results"):
                # Format Tavily results
                results = [
                    {
                        "title": r.get("title", ""),
                        "href": r.get("url", ""),
                        "body": r.get("content", "")
                    }
                    for r in response["results"]
                ]
                
                state["repair_steps"] = {
                    "source": "tavily",
                    "results": results
                }
                state["tool_status"].append(f"Found {len(results)} results from Tavily")
                logger.info(f"Tavily search returned {len(results)} results")
                return state
        else:
            logger.info("Tavily API key not configured, falling back to DuckDuckGo")
            state["tool_status"].append("Tavily not configured, trying DuckDuckGo...")
            
    except Exception as e:
        logger.warning(f"Tavily search failed: {e}")
        state["tool_status"].append("Tavily failed, trying DuckDuckGo...")
    
    # Try DuckDuckGo as last resort (free but rate-limited)
    try:
        from duckduckgo_search import DDGS
        
        state["tool_status"].append("Trying DuckDuckGo search...")
        ddgs = DDGS()
        results = list(ddgs.text(
            f"{state['query']} repair guide",
            max_results=3
        ))
        
        if results:
            state["repair_steps"] = {
                "source": "duckduckgo",
                "results": results
            }
            state["tool_status"].append(f"Found {len(results)} results from DuckDuckGo")
            logger.info(f"DuckDuckGo search returned {len(results)} results")
            return state
            
    except Exception as e:
        logger.error(f"DuckDuckGo search failed: {e}")
        state["tool_status"].append("All fallback searches failed")
    
    # No results from any source
    state["repair_steps"] = None
    state["tool_status"].append("No community sources found")
    
    return state
