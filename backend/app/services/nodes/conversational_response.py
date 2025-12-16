"""
Conversational Response Node

Handles follow-up questions and general conversation without needing to fetch new repair guides.
This node is used when the user asks clarifying questions about existing repair information.
"""

import re
from typing import TYPE_CHECKING
from langchain_core.messages import HumanMessage, SystemMessage
import logging

if TYPE_CHECKING:
    from ..agent import AgentState

logger = logging.getLogger(__name__)


def _fix_markdown_formatting(text: str) -> str:
    """
    Post-process text to fix common markdown formatting issues.
    Converts asterisk lists to proper dash lists and ensures proper spacing.
    """
    # Replace asterisk bullets with dash bullets
    # Match lines starting with * followed by space
    text = re.sub(r'^\* ', '- ', text, flags=re.MULTILINE)
    
    # Ensure blank line before lists (if not already present)
    text = re.sub(r'([^\n])\n(- )', r'\1\n\n\2', text)
    
    # Ensure blank line after lists (if not already present)
    text = re.sub(r'(- [^\n]+)\n([^\n-])', r'\1\n\n\2', text)
    
    # Fix multiple consecutive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text


def _is_followup_question(state: "AgentState") -> bool:
    """
    Determine if the user's query is a follow-up question about existing repair info
    or a general conversational query (greetings, casual conversation).
    
    Returns:
        True if this is a follow-up/conversational query, False if it's a new repair request
    """
    query = state.get("query", "").lower().strip()
    messages = state.get("messages", [])
    
    # Greetings and casual conversation patterns (should NOT go to iFixit)
    greeting_patterns = [
        "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
        "greetings", "howdy", "what's up", "whats up", "sup",
        "how are you", "how r u", "how do you do",
        "thanks", "thank you", "appreciate", "great job",
        "bye", "goodbye", "see you", "later",
        "who are you", "what can you do", "what do you do",
        "help me", "can you help", "i need help",
        "what is this", "what's this", "whats this"
    ]
    
    # Check if query is a greeting or casual conversation
    if any(pattern in query for pattern in greeting_patterns):
        return True
    
    # Check if query is very short (likely greeting or simple question)
    words = query.split()
    if len(words) <= 3 and not any(repair_keyword in query for repair_keyword in 
                                     ["fix", "repair", "broken", "replace", "screen", "battery"]):
        return True
    
    # Check if we have conversation history with repair information
    has_repair_context = any(
        msg.get("role") == "assistant" and len(msg.get("content", "")) > 200
        for msg in messages
    )
    
    if not has_repair_context:
        # No repair context, but could still be a greeting/casual query
        return False
    
    # Keywords that indicate follow-up questions
    followup_indicators = [
        "what about", "how do i", "can you explain", "why", "when",
        "what is", "what are", "which", "where", "tell me more",
        "clarify", "confused", "don't understand", "what does",
        "in step", "the step", "this step", "that part",
        "alternative", "instead", "easier way", "different",
        "tool", "part", "where to buy", "how much",
        "skip", "necessary", "optional", "important"
    ]
    
    return any(indicator in query for indicator in followup_indicators)


async def conversational_response_node(state: "AgentState") -> "AgentState":
    """
    Generate conversational responses to follow-up questions using LLM.
    
    This node is invoked when users ask questions about existing repair information
    rather than requesting new repair guides.
    
    Args:
        state: Current agent state with conversation history
        
    Returns:
        Updated state with conversational response
    """
    from ..agent import get_llm
    
    state["tool_status"].append("Understanding your question...")
    
    query = state.get("query", "")
    messages = state.get("messages", [])
    
    # Build conversation context
    context_messages = []
    
    # Add system prompt
    system_prompt = """You are a friendly and knowledgeable repair assistant. You help users with device repairs by:

1. Responding warmly to greetings and casual conversation
2. Answering follow-up questions about repair procedures
3. Clarifying specific steps in repair guides
4. Explaining tools, parts, and techniques
5. Providing helpful tips and alternatives
6. Offering encouragement and support

Always be:
- Friendly and conversational
- Clear and concise
- Helpful and supportive
- Practical and specific

When handling greetings:
- Respond warmly and introduce yourself briefly
- Let them know you can help with device repairs
- Suggest they can ask about fixing phones, laptops, tablets, or other devices
- Keep it short and inviting

When answering questions:
- Reference previous repair information when relevant
- Use emojis sparingly for a friendly tone (1-2 per response)
- Break down complex topics into simple steps
- Suggest helpful follow-up questions
- Encourage the user to ask for more help if needed

**CRITICAL FORMATTING RULES:**
- NEVER use asterisks (*) for bullet points - ALWAYS use dashes (-)
- For bullet points, use: `- Item` (dash + space + text)
- For numbered lists, use: `1. Item` (number + period + space + text)
- Add a blank line before every list
- Add a blank line after every list
- Use proper line breaks between paragraphs
- Use `**bold**` for emphasis (double asterisks around text)
- Each list item MUST be on its own line
- DO NOT use `* Item` - it's WRONG, use `- Item` instead

Example of CORRECT formatting:
```
That's a great question! 🧺

The repair procedures vary depending on several factors:

- **Top-loaders vs. Front-loaders**: These have very different internal layouts
- **Different Brands**: Each manufacturer has unique designs
- **Age of Machine**: Older models are simpler than modern ones

To give you the best advice, I need to know your specific model.
```

Example of WRONG formatting (DO NOT DO THIS):
```
* Top-loaders vs. Front-loaders: Different layouts
* Different Brands: Unique designs
```

To give you the best advice, I need to know your specific model.
```

Keep responses focused and well-formatted. Use proper Markdown syntax consistently."""

    context_messages.append(SystemMessage(content=system_prompt))
    
    # Add conversation history
    for msg in messages[-6:]:  # Last 6 messages for context
        if msg.get("role") == "user":
            context_messages.append(HumanMessage(content=msg["content"]))
        elif msg.get("role") == "assistant":
            # Summarize long repair guides to save tokens
            content = msg["content"]
            if len(content) > 1000:
                content = content[:1000] + "\n\n[... repair guide continues ...]"
            context_messages.append(SystemMessage(content=f"Previous response: {content}"))
    
    # Add current question
    context_messages.append(HumanMessage(content=query))
    
    try:
        llm = get_llm()
        state["tool_status"].append("Generating answer...")
        
        response = await llm.ainvoke(context_messages)
        
        # Get response content and fix markdown formatting
        response_text = response.content
        
        # Apply markdown formatting fixes
        response_text = _fix_markdown_formatting(response_text)
        
        # Check if this was a greeting
        query_lower = query.lower()
        is_greeting = any(pattern in query_lower for pattern in 
                         ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"])
        
        if is_greeting:
            response_text += "\n\n---\n\n🔧 **Ready to help!** Tell me about the device you need to repair (e.g., \"My iPhone 12 screen is cracked\")."
        else:
            response_text += "\n\n---\n\n💬 **Still have questions?** Feel free to ask me anything else!"
        
        state["final_response"] = response_text
        state["tool_status"].append("Response ready")
        
        logger.info(f"Generated conversational response for: {query[:50]}...")
        
    except Exception as e:
        logger.error(f"Error generating conversational response: {e}")
        state["final_response"] = (
            "I'd be happy to help with that! However, I'm having trouble processing your question right now. "
            "Could you rephrase it, or would you like to start a new repair search? 🔧"
        )
        state["tool_status"].append("Response ready")
    
    return state
