"""
Node 7: Format Response

Formats the final response in clean Markdown for frontend rendering.
Handles both iFixit guides and community fallback sources.
Includes conversational elements and follow-up suggestions.
"""

from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ..agent import AgentState

logger = logging.getLogger(__name__)


def _get_conversational_intro(state: "AgentState") -> str:
    """Generate a friendly conversational introduction based on the query."""
    query = state.get("query", "")
    
    # Check if this is a follow-up question
    messages = state.get("messages", [])
    is_followup = len(messages) > 2  # More than just the current exchange
    
    if is_followup:
        intros = [
            "Sure! Let me help you with that. ",
            "Great question! Here's what I found: ",
            "I'm happy to help with that. ",
            "Let me explain that for you. ",
        ]
    else:
        intros = [
            "I found the perfect repair guide for you! ",
            "Great news! I found an official iFixit guide for your device. ",
            "I've got you covered! Here's the repair information you need: ",
            "Perfect! I found exactly what you're looking for. ",
        ]
    
    # Simple selection based on query length
    return intros[len(query) % len(intros)]


def _get_follow_up_suggestions(state: "AgentState") -> str:
    """Generate helpful follow-up suggestions based on the repair context."""
    guide = state.get("repair_steps", {})
    
    if not guide or state.get("fallback_used"):
        return "\n\n---\n\n💬 **Need more help?** Feel free to ask me:\n" \
               "- For alternative repair methods\n" \
               "- About specific tools or parts\n" \
               "- For troubleshooting tips\n" \
               "- To search for a different device or issue"
    
    suggestions = "\n\n---\n\n💬 **What else can I help you with?**\n\n"
    
    # Add contextual suggestions
    difficulty = guide.get("difficulty", "").lower()
    
    if "difficult" in difficulty or "hard" in difficulty:
        suggestions += "- Need tips to make this repair easier?\n"
    
    if guide.get("tools"):
        suggestions += "- Questions about any of the required tools?\n"
    
    if guide.get("parts"):
        suggestions += "- Want to know where to buy these parts?\n"
    
    suggestions += "- Need clarification on any specific step?\n"
    suggestions += "- Want to see alternatives or similar repairs?\n"
    suggestions += "- Looking for preventive maintenance tips?\n"
    
    return suggestions


def _get_conversational_closing(state: "AgentState") -> str:
    """Add a friendly closing message."""
    closings = [
        "\n\nI'm here if you have any questions about these steps! Just ask. 😊",
        "\n\nFeel free to ask if you need clarification on any step! I'm here to help. 🔧",
        "\n\nLet me know if you need more details about anything! Happy to assist. 👍",
        "\n\nDon't hesitate to ask if something isn't clear! I'm here for you. ✨",
    ]
    
    query = state.get("query", "")
    return closings[len(query) % len(closings)]


async def format_response_node(state: "AgentState") -> "AgentState":
    """
    Format final response in clean Markdown with conversational elements.
    
    Ensures proper rendering in the frontend and encourages follow-up conversation.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with final_response
    """
    state["tool_status"].append("Formatting response...")
    
    # Start with conversational intro
    response = _get_conversational_intro(state)
    
    if state.get("repair_steps"):
        if state.get("fallback_used"):
            # Format community sources
            response += f"\n\n## ⚠️ Community Resources\n\n"
            response += f"I couldn't find an official iFixit guide for **{state['query']}**, but here are some helpful community resources:\n\n"
            
            for i, result in enumerate(state["repair_steps"].get("results", []), 1):
                response += f"### {i}. {result.get('title', 'Result')}\n"
                response += f"{result.get('body', '')}\n"
                response += f"🔗 [Read more]({result.get('href', '')})\n\n"
        else:
            # Format official iFixit guide
            guide = state["repair_steps"]
            response += f"\n\n# 🔧 {guide['title']}\n\n"
            
            # Add metadata in a friendly way
            metadata = []
            if guide.get("subject"):
                metadata.append(f"**Device:** {guide['subject']}")
            if guide.get("difficulty"):
                difficulty = guide['difficulty']
                emoji = "🟢" if "easy" in difficulty.lower() else "🟡" if "moderate" in difficulty.lower() else "🔴"
                metadata.append(f"**Difficulty:** {emoji} {difficulty}")
            if guide.get("time_required"):
                metadata.append(f"**Time:** ⏱️ {guide['time_required']}")
            
            if metadata:
                response += " | ".join(metadata) + "\n\n"
            
            if guide.get("introduction"):
                response += f"## 📋 Overview\n{guide['introduction']}\n\n"
            
            if guide.get("tools"):
                response += f"## 🛠️ Tools You'll Need\n"
                for tool in guide["tools"]:
                    response += f"- {tool}\n"
                response += "\n"
            
            if guide.get("parts"):
                response += f"## 📦 Required Parts\n"
                for part in guide["parts"]:
                    response += f"- {part}\n"
                response += "\n"
            
            response += f"## 📝 Step-by-Step Instructions\n\n"
            
            for step in guide.get("steps", []):
                response += f"### Step {step['orderby']}: {step['title']}\n\n"
                response += f"{step['text']}\n\n"
                
                for img in step.get("images", []):
                    response += f"![Step {step['orderby']}]({img['url']})\n\n"
    else:
        response = "I couldn't find specific repair information for your query. "
        response += "Could you provide more details about:\n"
        response += "- The exact device model (e.g., 'iPhone 12 Pro')\n"
        response += "- The specific issue or part you want to repair (e.g., 'screen replacement', 'battery')\n\n"
        response += "I'm here to help you find the right repair guide! 🔍"
    
    # Add follow-up suggestions
    response += _get_follow_up_suggestions(state)
    
    # Add conversational closing if we have a guide
    if state.get("repair_steps") and not state.get("fallback_used"):
        response += _get_conversational_closing(state)
    
    state["final_response"] = response
    state["tool_status"].append("Response ready")
    
    return state
