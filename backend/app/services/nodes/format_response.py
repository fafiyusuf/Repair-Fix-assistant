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


# -------------------------------------------------------------------
# Conversational helpers
# -------------------------------------------------------------------

def _get_conversational_intro(state: "AgentState") -> str:
    """Generate a friendly conversational introduction."""
    query = state.get("query", "")
    messages = state.get("messages", [])

    is_followup = len(messages) > 2

    if is_followup:
        intros = [
            "Sure! Let me help you with that.\n\n",
            "Great question! Here's what I found:\n\n",
            "I'm happy to help with that.\n\n",
            "Let me explain this step by step.\n\n",
        ]
    else:
        intros = [
            "I found the perfect repair guide for you!\n\n",
            "Great news! I found an official iFixit guide for your device.\n\n",
            "I've got you covered! Here's the repair information you need:\n\n",
            "Perfect! I found exactly what you're looking for.\n\n",
        ]

    return intros[len(query) % len(intros)]


def _get_follow_up_suggestions(state: "AgentState") -> str:
    """Generate helpful follow-up suggestions."""
    guide = state.get("repair_steps", {})

    if not guide or state.get("fallback_used"):
        return (
            "\n\n---\n\n"
            "💬 **Need more help?**\n\n"
            "- Alternative repair methods\n"
            "- Required tools or replacement parts\n"
            "- Troubleshooting tips\n"
            "- Searching for a different device or issue\n"
        )

    suggestions = "\n\n---\n\n💬 **What else can I help you with?**\n\n"

    difficulty = guide.get("difficulty", "").lower()

    if "hard" in difficulty or "difficult" in difficulty:
        suggestions += "- Tips to make this repair easier\n"

    if guide.get("tools"):
        suggestions += "- Questions about the required tools\n"

    if guide.get("parts"):
        suggestions += "- Where to buy the replacement parts\n"

    suggestions += (
        "- Clarification on any step\n"
        "- Alternative or similar repairs\n"
        "- Preventive maintenance tips\n"
    )

    return suggestions


def _get_conversational_closing(state: "AgentState") -> str:
    """Add a friendly closing message."""
    closings = [
        "\n\n💡 I'm here if you have any questions about these steps!",
        "\n\n🔧 Feel free to ask if you need clarification on any step.",
        "\n\n👍 Let me know if you'd like more details!",
        "\n\n✨ Don't hesitate to ask if something isn't clear.",
    ]

    query = state.get("query", "")
    return closings[len(query) % len(closings)]


# -------------------------------------------------------------------
# Main formatting node
# -------------------------------------------------------------------

async def format_response_node(state: "AgentState") -> "AgentState":
    """
    Format final response in clean Markdown with conversational elements.
    """
    state["tool_status"].append("Formatting response...")

    response = _get_conversational_intro(state)

    # ---------------------------------------------------------------
    # If repair steps exist
    # ---------------------------------------------------------------
    if state.get("repair_steps"):

        # -----------------------------
        # Community / fallback sources
        # -----------------------------
        if state.get("fallback_used"):
            response += (
                "## ⚠️ Community Resources\n\n"
                f"I couldn't find an official iFixit guide for "
                f"**{state.get('query', 'this issue')}**, "
                "but here are some helpful community resources:\n\n"
            )

            for i, result in enumerate(
                state["repair_steps"].get("results", []), start=1
            ):
                response += (
                    f"### {i}. {result.get('title', 'Resource')}\n\n"
                    f"{result.get('body', '').strip()}\n\n"
                    f"🔗 [Read more]({result.get('href', '#')})\n\n"
                )

        # -----------------------------
        # Official iFixit guide
        # -----------------------------
        else:
            guide = state["repair_steps"]

            response += f"# 🔧 {guide.get('title', 'Repair Guide')}\n\n"

            # Metadata row
            metadata = []

            if guide.get("subject"):
                metadata.append(f"**Device:** {guide['subject']}")

            if guide.get("difficulty"):
                diff = guide["difficulty"]
                emoji = (
                    "🟢" if "easy" in diff.lower()
                    else "🟡" if "moderate" in diff.lower()
                    else "🔴"
                )
                metadata.append(f"**Difficulty:** {emoji} {diff}")

            if guide.get("time_required"):
                metadata.append(f"**Time:** ⏱️ {guide['time_required']}")

            if metadata:
                response += " | ".join(metadata) + "\n\n"

            # Overview
            if guide.get("introduction"):
                response += "## 📋 Overview\n\n"
                response += f"{guide['introduction']}\n\n"

            # Tools
            if guide.get("tools"):
                response += "## 🛠️ Tools You'll Need\n\n"
                for tool in guide["tools"]:
                    response += f"- {tool}\n"
                response += "\n"

            # Parts
            if guide.get("parts"):
                response += "## 📦 Required Parts\n\n"
                for part in guide["parts"]:
                    response += f"- {part}\n"
                response += "\n"

            # Steps
            response += "## 📝 Step-by-Step Instructions\n\n"

            for step in guide.get("steps", []):
                response += (
                    f"### Step {step.get('orderby')}: "
                    f"{step.get('title', '')}\n\n"
                    f"{step.get('text', '').strip()}\n\n"
                )

                for img in step.get("images", []):
                    response += (
                        f"![Step {step.get('orderby')}]"
                        f"({img.get('url')})\n\n"
                    )

    # ---------------------------------------------------------------
    # No results at all
    # ---------------------------------------------------------------
    else:
        response = (
            "❌ **I couldn't find a repair guide for this request.**\n\n"
            "Please provide:\n\n"
            "- The exact device model (e.g., *PlayStation 5 Digital Edition*)\n"
            "- The specific issue or part (e.g., *fan replacement*, *HDMI port*)\n\n"
            "🔍 I'm ready to help once I have more details!"
        )

    # Follow-up section
    response += _get_follow_up_suggestions(state)

    # Friendly closing
    if state.get("repair_steps") and not state.get("fallback_used"):
        response += _get_conversational_closing(state)

    state["final_response"] = response
    state["tool_status"].append("Response ready")

    return state
