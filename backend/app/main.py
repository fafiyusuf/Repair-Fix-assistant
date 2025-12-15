"""
FastAPI application with SSE streaming for the Repair Fix Assistant.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import asyncio
from datetime import datetime
import uuid

from app.core.config import get_settings
from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.tokens import count_tokens, count_message_tokens
from app.core.context import prepare_context_for_agent, trim_conversation_history
from app.services.agent import agent_graph
import logging
import re

settings = get_settings()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Repair Fix Assistant API",
    description="AI-powered device repair assistant using verified iFixit guides",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    session_id: Optional[str] = None


class ChatSession(BaseModel):
    """Response model for session creation."""
    session_id: str
    created_at: str
    title: Optional[str] = None


def generate_session_title(message: str) -> str:
    """
    Generate a concise, descriptive title from the first user message.
    
    Args:
        message: The first user message
        
    Returns:
        A short, descriptive title (max 50 chars)
    """
    try:
        # Try to use LLM for better title generation
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import SystemMessage, HumanMessage
        
        settings = get_settings()
        if settings.gemini_api_key:
            llm = ChatGoogleGenerativeAI(
                api_key=settings.gemini_api_key,
                model="gemini-2.5-flash",
                temperature=0.3
            )
            
            messages = [
                SystemMessage(content="Generate a concise 3-5 word title for this repair request. Only return the title, nothing else. Examples: 'iPhone 12 Screen Repair', 'MacBook Battery Issue', 'Samsung Galaxy Display'"),
                HumanMessage(content=message)
            ]
            
            response = llm.invoke(messages)
            title = response.content.strip().strip('"').strip("'")
            
            # Ensure it's not too long
            if len(title) > 50:
                title = title[:47] + "..."
            
            return title
    except Exception as e:
        logger.warning(f"Could not generate AI title, using fallback: {e}")
    
    # Fallback to simple title generation
    cleaned = message.strip()
    
    # Remove common filler words
    filler_words = ['my', 'the', 'a', 'an', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'help', 'me', 'with']
    words = cleaned.split()
    
    # Keep important words
    important_words = [w for w in words if w.lower() not in filler_words or len(words) <= 3]
    
    # Reconstruct title
    if important_words:
        title = ' '.join(important_words[:6])  # Max 6 words
    else:
        title = ' '.join(words[:6])
    
    # Capitalize first letter of each word
    title = ' '.join(word.capitalize() for word in title.split())
    
    # Truncate if too long
    if len(title) > 50:
        title = title[:47] + "..."
    
    return title if title else "New Chat"


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Repair Fix Assistant",
        "version": "1.0.0"
    }


@app.get("/api/test")
async def test_endpoint():
    """Test endpoint without authentication."""
    return {
        "message": "Backend is working!",
        "gemini_configured": bool(settings.gemini_api_key),
        "supabase_configured": bool(settings.supabase_url)
    }


@app.post("/api/sessions", response_model=ChatSession)
async def create_session(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Create a new chat session for the authenticated user.
    """
    session_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    
    try:
        # Insert session into database
        db.table("chat_sessions").insert({
            "id": session_id,
            "user_id": user_id,
            "created_at": created_at
        }).execute()

        return ChatSession(session_id=session_id, created_at=created_at)

    except Exception as e:
        # Log full exception with traceback for debugging
        logger.exception("Failed to create chat session for user_id=%s", user_id)
        # Return a generic message but keep details in server logs
        raise HTTPException(status_code=500, detail="Failed to create session (see server logs)")


@app.get("/api/sessions")
async def list_sessions(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    List all chat sessions for the authenticated user.
    """
    try:
        response = db.table("chat_sessions")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        
        return {"sessions": response.data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sessions: {str(e)}")


@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get all messages for a specific session.
    """
    try:
        # Verify session belongs to user
        session = db.table("chat_sessions")\
            .select("*")\
            .eq("id", session_id)\
            .eq("user_id", user_id)\
            .execute()
        
        if not session.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Fetch messages
        messages = db.table("messages")\
            .select("*")\
            .eq("session_id", session_id)\
            .order("created_at")\
            .execute()
        
        return {"messages": messages.data}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")


@app.delete("/api/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Delete a chat session and all its messages.
    """
    try:
        # Verify session belongs to user
        session = db.table("chat_sessions")\
            .select("*")\
            .eq("id", session_id)\
            .eq("user_id", user_id)\
            .execute()
        
        if not session.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Delete session (messages will cascade delete)
        db.table("chat_sessions")\
            .delete()\
            .eq("id", session_id)\
            .execute()
        
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")


async def stream_agent_response(
    user_id: str,
    session_id: str,
    message: str,
    db
):
    """
    Stream agent execution with tool status updates and final response.
    
    Yields Server-Sent Events (SSE) with:
    - Tool execution status
    - Partial responses
    - Final complete response
    """
    
    # Save user message
    user_message_id = str(uuid.uuid4())
    db.table("messages").insert({
        "id": user_message_id,
        "session_id": session_id,
        "role": "user",
        "content": message,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    
    # Update session title if this is the first message
    try:
        # Check if session has messages (other than the one we just added)
        existing_messages = db.table("messages")\
            .select("id")\
            .eq("session_id", session_id)\
            .execute()
        
        logger.info(f"Session {session_id} has {len(existing_messages.data)} message(s)")
        
        if len(existing_messages.data) == 1:  # Only our new message exists
            # Generate title from first message
            logger.info(f"Generating title for first message in session {session_id}")
            title = generate_session_title(message)
            logger.info(f"Generated title: {title}")
            
            # Update session with title
            update_response = db.table("chat_sessions")\
                .update({"title": title, "updated_at": datetime.utcnow().isoformat()})\
                .eq("id", session_id)\
                .execute()
            
            logger.info(f"✅ Successfully set session title to: '{title}' for session {session_id}")
            logger.debug(f"Update response: {update_response.data}")
    except Exception as e:
        logger.error(f"❌ Failed to set session title for session {session_id}: {e}", exc_info=True)
    
    # Load conversation history for context
    try:
        history_response = db.table("messages")\
            .select("role,content")\
            .eq("session_id", session_id)\
            .order("created_at")\
            .execute()
        
        conversation_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history_response.data[:-1]  # Exclude the message we just added
        ]
        
        # Apply context management (trim if too long)
        managed_context = trim_conversation_history(conversation_history)
        
        logger.info(f"Loaded {len(conversation_history)} messages, using {len(managed_context)} after context management")
    except Exception as e:
        logger.error(f"Error loading conversation history: {e}")
        managed_context = []
    
    # Initialize agent state
    initial_state = {
        "user_id": user_id,
        "session_id": session_id,
        "messages": managed_context,  # Use managed context
        "query": message,  # Original user query with symptoms
        "normalized_query": None,  # Deprecated - use ifixit_device
        "ifixit_device": None,  # IMMUTABLE: Canonical device name for iFixit API
        "selected_device": None,
        "available_guides": None,
        "selected_guide": None,
        "repair_steps": None,
        "fallback_used": False,
        "final_response": None,
        "tool_status": []
    }
    
    try:
        # Execute agent graph and stream status updates
        final_state = None
        async for event in agent_graph.astream(initial_state):
            node_name = list(event.keys())[0]
            node_output = event[node_name]
            final_state = node_output
            
            # Stream tool status updates to user
            if "tool_status" in node_output and node_output["tool_status"]:
                latest_status = node_output["tool_status"][-1]
                logger.info(f"Agent status: {latest_status}")
                # Send status update to frontend
                yield f"data: {json.dumps({'type': 'status', 'content': latest_status})}\n\n"
        
        # Send final response when complete
        if final_state and final_state.get("final_response"):
            final_response = final_state["final_response"]
            
            # Save assistant message
            assistant_message_id = str(uuid.uuid4())
            db.table("messages").insert({
                "id": assistant_message_id,
                "session_id": session_id,
                "role": "assistant",
                "content": final_response,
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            
            # Track token usage with accurate counting
            # Count input + output tokens
            input_tokens = count_tokens(message)
            output_tokens = count_tokens(final_response)
            total_tokens = input_tokens + output_tokens
            
            # Try to insert with new columns, fallback to old schema if needed
            try:
                db.table("usage_stats").insert({
                    "user_id": user_id,
                    "session_id": session_id,
                    "tokens_used": total_tokens,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "timestamp": datetime.utcnow().isoformat()
                }).execute()
                logger.info(f"Token usage - Input: {input_tokens}, Output: {output_tokens}, Total: {total_tokens}")
            except Exception as token_error:
                # Fallback: Insert without new columns (for backwards compatibility)
                logger.warning(f"Could not insert with input/output tokens (missing columns?), using total only: {token_error}")
                db.table("usage_stats").insert({
                    "user_id": user_id,
                    "session_id": session_id,
                    "tokens_used": total_tokens,
                    "timestamp": datetime.utcnow().isoformat()
                }).execute()
                logger.info(f"Token usage - Total: {total_tokens} (input/output not tracked)")
            
            # Stream final response word by word for better UX
            words = final_response.split()
            accumulated_text = ""
            
            for i, word in enumerate(words):
                # Add word to accumulated text
                if i == 0:
                    accumulated_text = word
                else:
                    accumulated_text += " " + word
                
                # Send accumulated text
                yield f"data: {json.dumps({'type': 'response', 'content': accumulated_text})}\n\n"
                
                # Small delay for smooth streaming (adjust as needed)
                await asyncio.sleep(0.03)  # 30ms per word
        else:
            # No response generated
            error_msg = "Unable to generate a response. Please try rephrasing your question."
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
        
        # Send completion signal
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        yield f"data: {json.dumps({'type': 'error', 'content': error_message})}\n\n"


@app.post("/api/chat/stream")
async def chat_stream(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Stream chat responses using Server-Sent Events (SSE).
    
    This endpoint:
    1. Validates the session
    2. Executes the agent graph
    3. Streams tool status and responses in real-time
    """
    
    # Create session if not provided
    if not request.session_id:
        session_id = str(uuid.uuid4())
        db.table("chat_sessions").insert({
            "id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    else:
        session_id = request.session_id
        
        # Verify session belongs to user
        session = db.table("chat_sessions")\
            .select("*")\
            .eq("id", session_id)\
            .eq("user_id", user_id)\
            .execute()
        
        if not session.data:
            raise HTTPException(status_code=404, detail="Session not found")
    
    return StreamingResponse(
        stream_agent_response(user_id, session_id, request.message, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/usage")
async def get_usage_stats(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get token usage statistics for the authenticated user.
    """
    try:
        # Get total tokens used
        response = db.table("usage_stats")\
            .select("tokens_used")\
            .eq("user_id", user_id)\
            .execute()
        
        total_tokens = sum(record["tokens_used"] for record in response.data)
        
        return {
            "user_id": user_id,
            "total_tokens": total_tokens,
            "records": len(response.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch usage stats: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
