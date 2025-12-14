# Backend - Repair Fix Assistant API

FastAPI backend with LangGraph agent for the Repair Fix Assistant.

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip
- Virtual environment (recommended)

### Installation

1. **Create and activate virtual environment:**

```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# LLM Provider (choose one)
OPENAI_API_KEY=your-openai-api-key
# OR
# GEMINI_API_KEY=your-gemini-api-key

# Optional: Web search fallback
TAVILY_API_KEY=your-tavily-api-key

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

4. **Run the server:**

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔌 API Endpoints

### Authentication Required

All endpoints except `/` require a valid Supabase JWT token in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

### Endpoints

#### Health Check

```http
GET /
```

Returns server status.

#### Create Chat Session

```http
POST /api/sessions
```

Creates a new chat session for the authenticated user.

**Response:**
```json
{
  "session_id": "uuid",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### List Sessions

```http
GET /api/sessions
```

Lists all chat sessions for the authenticated user.

#### Get Session Messages

```http
GET /api/sessions/{session_id}/messages
```

Retrieves all messages for a specific session.

#### Stream Chat Response

```http
POST /api/chat/stream
```

Streams AI responses using Server-Sent Events (SSE).

**Request Body:**
```json
{
  "message": "my PS5 fan is loud",
  "session_id": "uuid"  // optional, creates new if not provided
}
```

**Response:** SSE stream with events:
- `type: "status"` - Tool execution updates
- `type: "response"` - Final formatted response
- `type: "error"` - Error messages
- `type: "done"` - Stream completion

#### Get Usage Statistics

```http
GET /api/usage
```

Returns token usage statistics for the authenticated user.

**Response:**
```json
{
  "user_id": "uuid",
  "total_tokens": 12345,
  "records": 42
}
```

## 🤖 LangGraph Agent

### Node Architecture

The agent consists of 7 deterministic nodes:

1. **normalize_query**: Converts user input to searchable format
2. **search_device**: Searches iFixit for the device
3. **list_guides**: Retrieves available repair guides
4. **select_guide**: Chooses the most relevant guide
5. **fetch_guide**: Gets detailed repair instructions
6. **fallback_search**: DuckDuckGo/Tavily search (if iFixit fails)
7. **format_response**: Formats output as Markdown

### State Management

Agent state is maintained throughout execution:

```python
{
  "user_id": str,
  "session_id": str,
  "messages": List[Dict],
  "query": str,
  "normalized_query": Optional[str],
  "selected_device": Optional[Dict],
  "available_guides": Optional[List[Dict]],
  "selected_guide": Optional[Dict],
  "repair_steps": Optional[Dict],
  "fallback_used": bool,
  "final_response": Optional[str],
  "tool_status": List[str]
}
```

### Response Cleanup

All iFixit API responses are cleaned before being passed to the LLM:

- ✅ Keeps: step order, step text, image URLs, tools, parts
- ❌ Removes: author info, revisions, comments, metadata, scores

## 🔧 Configuration

### LLM Selection

The agent automatically selects the LLM based on available API keys:

- If `OPENAI_API_KEY` is set → uses GPT-4 Turbo
- Else if `GEMINI_API_KEY` is set → uses Gemini Pro
- Else → raises error

### Token Limits

Configure in `app/core/config.py`:

```python
max_tokens_per_response: int = 2000
max_conversation_length: int = 20
```

## 🗄️ Database Schema

The backend expects the following Supabase tables:

- `chat_sessions`: User chat sessions
- `messages`: Chat messages
- `usage_stats`: Token usage tracking
- `langgraph_checkpoints`: Agent state persistence

Run `supabase/schema.sql` in your Supabase SQL editor to create these tables.

## 🔐 Security

### JWT Verification

The `verify_supabase_jwt()` function validates tokens on every protected endpoint:

```python
from app.core.auth import get_current_user

@app.get("/protected")
async def protected_route(user_id: str = Depends(get_current_user)):
    # user_id is guaranteed to be valid
    pass
```

### CORS Configuration

CORS is configured for the frontend origin:

```python
allow_origins=["http://localhost:3000"]  # Update for production
```

## 📊 Logging

Logs are written to stdout with configurable level:

```python
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🧪 Testing

### Test iFixit API Connection

```bash
python -c "
from app.services.ifixit_tools import get_ifixit_tools
import asyncio

async def test():
    tools = get_ifixit_tools()
    result = await tools.search_devices('PlayStation 5')
    print(result)

asyncio.run(test())
"
```

### Test LLM Connection

```bash
python -c "
from app.services.agent import get_llm
import asyncio

async def test():
    llm = get_llm()
    response = await llm.ainvoke('Hello!')
    print(response.content)

asyncio.run(test())
"
```

## 🚢 Deployment

### Environment Variables (Production)

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-production-service-role-key
OPENAI_API_KEY=your-production-openai-key
ENVIRONMENT=production
LOG_LEVEL=WARNING
```

### Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

### Fly.io Deployment

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
fly deploy
```

## 🐛 Troubleshooting

### "No LLM API key configured"

- Ensure either `OPENAI_API_KEY` or `GEMINI_API_KEY` is set in `.env`

### "Failed to connect to Supabase"

- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are correct
- Check network connectivity

### "iFixit API returns no results"

- Ensure you're connected via VPN if required
- Try different search queries
- Check iFixit API status

### CORS errors

- Update `allow_origins` in `app/main.py` to include your frontend URL

## 📝 Project Structure

```
backend/
├── app/
│   ├── api/              # API routes (future expansion)
│   ├── core/
│   │   ├── config.py     # Settings and configuration
│   │   ├── auth.py       # JWT verification
│   │   └── database.py   # Supabase client
│   ├── services/
│   │   ├── agent.py      # LangGraph agent
│   │   └── ifixit_tools.py  # iFixit API wrappers
│   └── main.py           # FastAPI application
├── requirements.txt      # Python dependencies
└── .env.example          # Environment template
```

## 🤝 Contributing

See the main [README.md](../README.md) for contribution guidelines.

## 📧 Support

For backend-specific issues, please include:
- Python version
- Error logs from console
- Request/response details (if applicable)

---

**Built with FastAPI + LangGraph**
