# Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                                 │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │  Landing     │  │  Auth Pages  │  │  Protected Routes        │ │
│  │  Page        │  │  (Login/     │  │  ┌────────┐ ┌─────────┐ │ │
│  │              │  │   Signup)    │  │  │  Chat  │ │Dashboard│ │ │
│  │  Next.js 14  │  │              │  │  │        │ │         │ │ │
│  └──────────────┘  └──────────────┘  │  └────────┘ └─────────┘ │ │
│                                       │      ↓           ↓       │ │
│                                       │   SSE Stream   REST API  │ │
│                                       └──────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ HTTPS (JWT in headers)
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                      FASTAPI BACKEND                                 │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    API Endpoints                                │ │
│  │  /api/sessions  /api/chat/stream  /api/usage                  │ │
│  └────────────┬───────────────────────────────────────────────────┘ │
│               │                                                      │
│  ┌────────────▼───────────────┐    ┌───────────────────────────┐  │
│  │   Authentication           │    │   Database Client         │  │
│  │   - JWT Verification       │    │   - Supabase Client       │  │
│  │   - User Extraction        │    │   - Query Builder         │  │
│  └────────────────────────────┘    └───────────────────────────┘  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      LANGGRAPH AGENT                            │ │
│  │                                                                  │ │
│  │   ┌──────────────┐      ┌──────────────┐      ┌─────────────┐ │ │
│  │   │ 1. Normalize │─────▶│ 2. Search    │─────▶│ 3. List     │ │ │
│  │   │    Query     │      │    Device    │      │    Guides   │ │ │
│  │   └──────────────┘      └──────────────┘      └──────┬──────┘ │ │
│  │                                                       │         │ │
│  │                         ┌─────────────────────────────┘         │ │
│  │                         │                                       │ │
│  │   ┌─────────────┐      ┌▼──────────────┐      ┌─────────────┐ │ │
│  │   │ 7. Format   │◀─────│ 4. Select     │─────▶│ 5. Fetch    │ │ │
│  │   │    Response │      │    Guide      │      │    Guide    │ │ │
│  │   └─────────────┘      └───────────────┘      └─────────────┘ │ │
│  │         ▲                      │                               │ │
│  │         │                      │ (if iFixit fails)             │ │
│  │         │              ┌───────▼───────────┐                   │ │
│  │         └──────────────│ 6. Fallback       │                   │ │
│  │                        │    Web Search     │                   │ │
│  │                        └───────────────────┘                   │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      iFixit Tools                               │ │
│  │  - search_devices()    - list_guides()    - fetch_guide()     │ │
│  │  - cleanup_search()    - cleanup_guides() - cleanup_guide()   │ │
│  └────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
    ┌───────────────┐  ┌──────────────┐  ┌─────────────┐
    │   Supabase    │  │  iFixit API  │  │ OpenAI/     │
    │   PostgreSQL  │  │              │  │ Gemini API  │
    │               │  │  (Tools)     │  │             │
    │  ┌─────────┐  │  └──────────────┘  └─────────────┘
    │  │Sessions │  │
    │  │Messages │  │
    │  │Usage    │  │
    │  │Checkpts │  │
    │  └─────────┘  │
    │               │
    │  Auth (JWT)   │
    └───────────────┘
```

## Data Flow

### 1. Authentication Flow

```
User Sign Up/Login
       │
       ▼
Supabase Auth
       │
       ▼
JWT Token Generated
       │
       ▼
Token Stored in Browser
       │
       ▼
Token Sent with Each Request
       │
       ▼
Backend Verifies JWT
       │
       ▼
User ID Extracted
       │
       ▼
Database Operations Scoped to User
```

### 2. Chat Request Flow

```
User Types Message
       │
       ▼
Frontend: Create/Get Session ID
       │
       ▼
Frontend: POST /api/chat/stream
       │
       ▼
Backend: Verify JWT → Extract User ID
       │
       ▼
Backend: Save User Message to DB
       │
       ▼
Backend: Initialize Agent State
       │
       ▼
┌──────────────────────────────────────────┐
│      LangGraph Agent Execution           │
│                                          │
│  1. Normalize: "PS5 fan loud"           │
│     → "PlayStation 5 fan noise"          │
│                                          │
│  2. Search Device on iFixit              │
│     → Found: "PlayStation 5"             │
│                                          │
│  3. List Guides for PlayStation 5        │
│     → Found: 15 guides                   │
│                                          │
│  4. Select Best Guide                    │
│     → Selected: "Fan Replacement"        │
│                                          │
│  5. Fetch Detailed Guide                 │
│     → Retrieved: 12 steps with images    │
│                                          │
│  7. Format as Markdown                   │
│     → Ready to stream                    │
└──────────────────────────────────────────┘
       │
       ▼
Backend: Stream Events via SSE
       │
       ├─▶ status: "Searching iFixit..."
       ├─▶ status: "Found device..."
       ├─▶ status: "Fetching guides..."
       └─▶ response: "# Fan Replacement..."
       │
       ▼
Frontend: Process SSE Events
       │
       ├─▶ Show status bubbles
       └─▶ Render final markdown
       │
       ▼
Backend: Save Assistant Message
       │
       ▼
Backend: Track Token Usage
       │
       ▼
Stream Complete
```

### 3. Fallback Flow (if iFixit fails)

```
Device Not Found
       │
       ▼
Agent Routes to Fallback Node
       │
       ▼
DuckDuckGo/Tavily Search
       │
       ▼
Community Results Retrieved
       │
       ▼
Format with "⚠️ Community Sources" Label
       │
       ▼
Stream to User
```

## Technology Stack Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
├─────────────────────────────────────────────────────────────┤
│  Framework       │  Next.js 14 (App Router)                 │
│  Language        │  TypeScript                              │
│  Styling         │  Tailwind CSS                            │
│  Icons           │  Lucide React                            │
│  Markdown        │  React Markdown + remark-gfm            │
│  Auth Client     │  @supabase/supabase-js                  │
│  Streaming       │  Native Fetch API (SSE)                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                               │
├─────────────────────────────────────────────────────────────┤
│  Framework       │  FastAPI                                 │
│  Language        │  Python 3.11+                            │
│  Agent           │  LangGraph                               │
│  LLM             │  LangChain + OpenAI/Gemini              │
│  Database        │  Supabase (psycopg2/asyncpg)           │
│  HTTP Client     │  httpx (async)                          │
│  Auth            │  python-jose (JWT)                       │
│  Streaming       │  FastAPI StreamingResponse (SSE)        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    DATABASE & AUTH                           │
├─────────────────────────────────────────────────────────────┤
│  Database        │  PostgreSQL (Supabase)                   │
│  Auth            │  Supabase Auth (JWT)                     │
│  Storage         │  4 Tables + RLS Policies                 │
│  Hosting         │  Supabase Cloud                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL APIS                             │
├─────────────────────────────────────────────────────────────┤
│  Primary Tool    │  iFixit API (HTTPS)                      │
│  Fallback Search │  DuckDuckGo Search / Tavily             │
│  LLM Provider    │  OpenAI API / Google Gemini            │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      PRODUCTION                              │
└─────────────────────────────────────────────────────────────┘

    ┌───────────────┐
    │   Vercel      │  (Frontend Hosting)
    │               │  - Next.js app
    │   Edge CDN    │  - Static assets
    │   Auto SSL    │  - Auto HTTPS
    └───────┬───────┘
            │
            │ HTTPS
            │
    ┌───────▼───────┐
    │   Railway     │  (Backend Hosting)
    │   /or/        │  - FastAPI app
    │   Render      │  - Python runtime
    │   /or/        │  - Auto SSL
    │   Fly.io      │  - Container deploy
    └───────┬───────┘
            │
            │ PostgreSQL
            │
    ┌───────▼───────┐
    │   Supabase    │  (Database & Auth)
    │               │  - PostgreSQL
    │   Global      │  - Auth service
    │   Edge        │  - Auto backups
    │   Network     │  - RLS policies
    └───────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                           │
└─────────────────────────────────────────────────────────────┘

Frontend
    │
    ├─▶ Anon Key (Public) ──────────────────┐
    │                                        │
    └─▶ JWT Token (from Supabase Auth) ─────┤
                                             │
                                             ▼
Backend                              ┌──────────────┐
    │                                │ JWT Verify   │
    ├─▶ Service Role Key (Secret)   │ Middleware   │
    │                                └──────────────┘
    └─▶ CORS (whitelist frontend)           │
                                             ▼
Database                             ┌──────────────┐
    │                                │ User ID      │
    ├─▶ Row Level Security (RLS)    │ Extraction   │
    │                                └──────────────┘
    ├─▶ User-scoped queries                 │
    │                                       ▼
    └─▶ Encrypted at rest           ┌──────────────┐
                                     │ DB Operation │
                                     │ (Scoped)     │
                                     └──────────────┘
```

---

**Legend:**
- `─▶` : Data flow direction
- `│` : Vertical connection
- `▼` : Downward flow
- `◀─` : Return flow
