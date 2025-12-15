"""
Token counting utilities for accurate usage tracking.

Uses tiktoken for precise token counting compatible with LLM models.
"""

import tiktoken
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Default encoding for most models (GPT-3.5, GPT-4, Gemini uses similar tokenization)
DEFAULT_ENCODING = "cl100k_base"


def count_tokens(text: str, encoding_name: str = DEFAULT_ENCODING) -> int:
    """
    Count the number of tokens in a text string.
    
    Args:
        text: The text to count tokens for
        encoding_name: The encoding to use (default: cl100k_base for GPT-4/Gemini)
        
    Returns:
        Number of tokens in the text
    """
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(text))
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        # Fallback to word count estimation (1 token ≈ 0.75 words)
        return int(len(text.split()) * 1.33)


def count_message_tokens(messages: List[Dict[str, str]], encoding_name: str = DEFAULT_ENCODING) -> int:
    """
    Count tokens in a list of messages (chat format).
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        encoding_name: The encoding to use
        
    Returns:
        Total number of tokens including message formatting overhead
    """
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = 0
        
        for message in messages:
            # Count tokens for message formatting
            num_tokens += 4  # Every message has formatting overhead
            
            for key, value in message.items():
                if isinstance(value, str):
                    num_tokens += len(encoding.encode(value))
                    
        num_tokens += 2  # Every completion/reply has additional overhead
        
        return num_tokens
    except Exception as e:
        logger.error(f"Error counting message tokens: {e}")
        # Fallback estimation
        total_text = " ".join(msg.get("content", "") for msg in messages)
        return int(len(total_text.split()) * 1.33)


def estimate_cost(tokens: int, model: str = "gemini-2.5-flash") -> float:
    """
    Estimate the cost of token usage based on the model.
    
    Args:
        tokens: Number of tokens used
        model: Model name (e.g., "gemini-2.5-flash", "gpt-4")
        
    Returns:
        Estimated cost in USD
    """
    # Pricing per 1K tokens (approximate as of Dec 2025)
    pricing = {
        "gemini-2.5-flash": 0.0001,  # Very cheap
        "gemini-pro": 0.0005,
        "gpt-3.5-turbo": 0.002,
        "gpt-4": 0.03,
    }
    
    cost_per_1k = pricing.get(model, 0.0001)
    return (tokens / 1000.0) * cost_per_1k
