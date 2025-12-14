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
from app.services.agent import agent_graph
import logging

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
    
    # Initialize agent state
    initial_state = {
        "user_id": user_id,
        "session_id": session_id,
        "messages": [],
        "query": message,
        "normalized_query": None,
        "selected_device": None,
        "available_guides": None,
        "selected_guide": None,
        "repair_steps": None,
        "fallback_used": False,
        "final_response": None,
        "tool_status": []
    }
    
    try:
        # Stream tool status updates
        async for event in agent_graph.astream(initial_state):
            node_name = list(event.keys())[0]
            node_output = event[node_name]
            
            # Send status updates
            if "tool_status" in node_output and node_output["tool_status"]:
                latest_status = node_output["tool_status"][-1]
                yield f"data: {json.dumps({'type': 'status', 'content': latest_status})}\n\n"
                await asyncio.sleep(0.1)  # Small delay for better UX
            
            # Send final response when available
            if "final_response" in node_output and node_output["final_response"]:
                final_response = node_output["final_response"]
                
                # Save assistant message
                assistant_message_id = str(uuid.uuid4())
                db.table("messages").insert({
                    "id": assistant_message_id,
                    "session_id": session_id,
                    "role": "assistant",
                    "content": final_response,
                    "created_at": datetime.utcnow().isoformat()
                }).execute()
                
                # Track token usage (simplified - should count actual tokens)
                estimated_tokens = len(final_response.split())
                db.table("usage_stats").insert({
                    "user_id": user_id,
                    "session_id": session_id,
                    "tokens_used": estimated_tokens,
                    "timestamp": datetime.utcnow().isoformat()
                }).execute()
                
                # Stream final response
                yield f"data: {json.dumps({'type': 'response', 'content': final_response})}\n\n"
        
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
