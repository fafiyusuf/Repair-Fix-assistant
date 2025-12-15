"""
Context management utilities for handling long conversations.

Implements strategies to stay within LLM context limits:
- Trimming old messages
- Summarization (future enhancement)
"""

from typing import List, Dict, Optional
import logging
from app.core.tokens import count_message_tokens

logger = logging.getLogger(__name__)

# Gemini 2.5 Flash has a 1M token context window, but we'll use conservative limits
MAX_CONTEXT_TOKENS = 100000  # 100K tokens for safety
MAX_MESSAGES_TO_KEEP = 50  # Keep last 50 messages max


def trim_conversation_history(
    messages: List[Dict],
    max_tokens: int = MAX_CONTEXT_TOKENS,
    max_messages: int = MAX_MESSAGES_TO_KEEP
) -> List[Dict]:
    """
    Trim conversation history to stay within context limits.
    
    Strategy:
    1. Always keep system messages
    2. Keep the most recent messages up to max_messages
    3. If still over token limit, trim further from the oldest
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        max_tokens: Maximum tokens allowed
        max_messages: Maximum number of messages to keep
        
    Returns:
        Trimmed list of messages
    """
    if not messages:
        return []
    
    # Separate system messages from conversation
    system_messages = [msg for msg in messages if msg.get("role") == "system"]
    conversation_messages = [msg for msg in messages if msg.get("role") != "system"]
    
    # Keep only the most recent max_messages
    if len(conversation_messages) > max_messages:
        logger.info(f"Trimming conversation from {len(conversation_messages)} to {max_messages} messages")
        conversation_messages = conversation_messages[-max_messages:]
    
    # Combine system messages with trimmed conversation
    trimmed_messages = system_messages + conversation_messages
    
    # Check token count
    current_tokens = count_message_tokens(trimmed_messages)
    
    # If still over limit, trim from oldest conversation messages
    while current_tokens > max_tokens and len(conversation_messages) > 1:
        logger.warning(f"Context still at {current_tokens} tokens, removing oldest message")
        conversation_messages.pop(0)  # Remove oldest
        trimmed_messages = system_messages + conversation_messages
        current_tokens = count_message_tokens(trimmed_messages)
    
    if current_tokens > max_tokens:
        logger.error(f"Unable to trim context below {max_tokens} tokens (current: {current_tokens})")
    else:
        logger.info(f"Context managed: {len(trimmed_messages)} messages, {current_tokens} tokens")
    
    return trimmed_messages


def should_summarize(messages: List[Dict], threshold_messages: int = 30) -> bool:
    """
    Determine if conversation history should be summarized.
    
    Args:
        messages: List of messages
        threshold_messages: Number of messages that triggers summarization
        
    Returns:
        True if summarization is recommended
    """
    conversation_messages = [msg for msg in messages if msg.get("role") != "system"]
    return len(conversation_messages) > threshold_messages


def create_context_summary(messages: List[Dict]) -> str:
    """
    Create a summary of older conversation context.
    
    This is a placeholder for future enhancement with LLM-based summarization.
    
    Args:
        messages: Messages to summarize
        
    Returns:
        Summary text
    """
    # Simple summary: count user queries and topics mentioned
    user_messages = [msg for msg in messages if msg.get("role") == "user"]
    
    if not user_messages:
        return "No previous conversation context."
    
    summary = f"Previous conversation summary: User asked {len(user_messages)} questions"
    
    # Extract device mentions (simple keyword extraction)
    devices_mentioned = set()
    common_devices = ["ps5", "playstation", "xbox", "iphone", "macbook", "laptop", "phone"]
    
    for msg in user_messages:
        content_lower = msg.get("content", "").lower()
        for device in common_devices:
            if device in content_lower:
                devices_mentioned.add(device)
    
    if devices_mentioned:
        summary += f" about: {', '.join(devices_mentioned)}"
    
    return summary + "."


def prepare_context_for_agent(
    current_query: str,
    conversation_history: List[Dict],
    include_summary: bool = True
) -> List[Dict]:
    """
    Prepare optimized context for the agent with the current query.
    
    Args:
        current_query: The current user query
        conversation_history: Previous messages
        include_summary: Whether to include a summary of trimmed context
        
    Returns:
        Optimized message list for the agent
    """
    # Trim conversation to manageable size
    trimmed_history = trim_conversation_history(conversation_history)
    
    # If we trimmed a lot and summary is requested, add context summary
    if include_summary and len(conversation_history) > len(trimmed_history) + 10:
        trimmed_count = len(conversation_history) - len(trimmed_history)
        older_messages = conversation_history[:trimmed_count]
        summary = create_context_summary(older_messages)
        
        # Insert summary at the beginning (after system messages)
        system_msgs = [msg for msg in trimmed_history if msg.get("role") == "system"]
        other_msgs = [msg for msg in trimmed_history if msg.get("role") != "system"]
        
        summary_msg = {
            "role": "system",
            "content": f"[Context Summary] {summary}"
        }
        
        trimmed_history = system_msgs + [summary_msg] + other_msgs
    
    # Add current query as the latest message
    trimmed_history.append({
        "role": "user",
        "content": current_query
    })
    
    return trimmed_history
