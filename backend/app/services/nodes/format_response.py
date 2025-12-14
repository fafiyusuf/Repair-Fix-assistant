"""
Node 7: Format Response

Formats the final response in clean Markdown for frontend rendering.
Handles both iFixit guides and community fallback sources.
"""

from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ..agent import AgentState

logger = logging.getLogger(__name__)


async def format_response_node(state: "AgentState") -> "AgentState":
    """
    Format final response in clean Markdown.
    
    Ensures proper rendering in the frontend.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with final_response
    """
    state["tool_status"].append("Formatting response...")
    
    if state.get("repair_steps"):
        if state.get("fallback_used"):
            # Format community sources
            response = f"## ⚠️ Community Sources (No Official iFixit Guide Found)\n\n"
            response += f"**Query:** {state['query']}\n\n"
            
            for i, result in enumerate(state["repair_steps"].get("results", []), 1):
                response += f"### {i}. {result.get('title', 'Result')}\n"
                response += f"{result.get('body', '')}\n"
                response += f"[Source]({result.get('href', '')})\n\n"
        else:
            # Format official iFixit guide
            guide = state["repair_steps"]
            response = f"# {guide['title']}\n\n"
            response += f"**Device:** {guide.get('subject', 'N/A')}\n"
            response += f"**Difficulty:** {guide.get('difficulty', 'N/A')}\n"
            response += f"**Time Required:** {guide.get('time_required', 'N/A')}\n\n"
            
            if guide.get("introduction"):
                response += f"## Introduction\n{guide['introduction']}\n\n"
            
            if guide.get("tools"):
                response += f"## Tools Needed\n"
                for tool in guide["tools"]:
                    response += f"- {tool}\n"
                response += "\n"
            
            if guide.get("parts"):
                response += f"## Parts\n"
                for part in guide["parts"]:
                    response += f"- {part}\n"
                response += "\n"
            
            response += f"## Repair Steps\n\n"
            
            for step in guide.get("steps", []):
                response += f"### Step {step['orderby']}: {step['title']}\n\n"
                response += f"{step['text']}\n\n"
                
                for img in step.get("images", []):
                    response += f"![Step {step['orderby']}]({img['url']})\n\n"
    else:
        response = "I couldn't find any repair information for your query. Please try rephrasing or providing more specific device details."
    
    state["final_response"] = response
    state["tool_status"].append("Response ready")
    
    return state
