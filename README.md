# Repair Fix Assistant 🔧

AI-powered device repair assistant using verified iFixit guides. Built with Next.js, FastAPI, LangGraph, and Supabase.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

- **Official iFixit Guides**: Always prioritizes verified repair documentation
- **Real-time Streaming**: Watch as the AI searches and retrieves repair steps live
- **No Hallucinations**: Deterministic tools-first approach prevents AI fabrication
- **User Authentication**: Secure login/signup with Supabase Auth
- **Usage Analytics**: Track token consumption and chat history
- **Responsive UI**: Beautiful, mobile-friendly interface with dark mode support

## 🏗️ Architecture

### Frontend
- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **Supabase Auth Client**
- **React Markdown** for rendering repair guides
- **SSE** for real-time streaming

### Backend
- **FastAPI** (Python 3.11+)
- **LangGraph** for agent orchestration
- **Google Gemini 2.0 Flash** for LLM (OpenAI GPT-4 also supported)
- **Supabase** for PostgreSQL database
- **Server-Sent Events** for streaming responses

### Database
- **Supabase PostgreSQL**
  - User management (Auth)
  - Chat sessions and messages
  - Usage analytics
  - LangGraph checkpoints

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Supabase** account ([create free account](https://supabase.com))
- **Google Gemini** API key ([get free key](https://ai.google.dev/)) or **OpenAI** API key
- **VPN** (required for iFixit API access in some regions)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd IFix-AI
```

### 2. Set Up Supabase

1. Create a new project at [supabase.com](https://supabase.com)
2. Enable Email/Password authentication in Authentication settings
3. Run the database schema:
   - Go to SQL Editor in Supabase dashboard
   - Copy and execute the contents of `supabase/schema.sql`
4. Note your:
   - Project URL
   - Anon/Public key
   - Service role key (keep secret!)

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

Edit `.env` with your credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# LLM Provider (Gemini 2.0 Flash recommended)
GEMINI_API_KEY=your-gemini-api-key
# OR
# OPENAI_API_KEY=your-openai-api-key

# Optional: for web search fallback
TAVILY_API_KEY=your-tavily-api-key

ENVIRONMENT=development
LOG_LEVEL=INFO
```

Start the backend server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📖 Usage

1. **Sign Up**: Create an account at `http://localhost:3000/auth/signup`
2. **Sign In**: Log in at `http://localhost:3000/auth/login`
3. **Start Chatting**: Describe your device issue (e.g., "my PS5 fan is loud")
4. **View Analytics**: Check your usage stats at `http://localhost:3000/dashboard`

## 🔧 How It Works

### LangGraph Agent Flow

The agent follows a deterministic 7-node state machine:

```
1. Normalize Query
   ↓
2. Search Device (iFixit)
   ↓
3. List Guides
   ↓
4. Select Best Guide
   ↓
5. Fetch Repair Guide
   ↓
7. Format Response
```

If any step fails, it routes to:

```
6. Fallback Web Search (DuckDuckGo/Tavily)
   ↓
7. Format Response
```

### API Response Cleanup

All iFixit API responses are cleaned before being passed to the LLM:
- Removes author metadata, revision history, and comments
- Extracts only: step order, step text, and image URLs
- Prevents the LLM from learning irrelevant information

### Authentication Flow

1. User signs up/logs in via Supabase Auth
2. Frontend receives JWT token
3. JWT is sent with every API request in `Authorization` header
4. Backend verifies JWT and extracts `user_id`
5. All database operations are scoped to authenticated user

## 📁 Project Structure

```
IFix-AI/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes (future expansion)
│   │   ├── core/         # Config, auth, database
│   │   ├── services/     # Agent and tools
│   │   └── main.py       # FastAPI app
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── auth/         # Login/signup pages
│   │   ├── chat/         # Chat interface
│   │   ├── dashboard/    # Analytics dashboard
│   │   └── page.tsx      # Home page
│   ├── lib/              # Supabase client
│   ├── components/       # Reusable components (future)
│   ├── package.json
│   └── .env.local.example
└── supabase/
    └── schema.sql        # Database schema
```

## 🔒 Security Features

- ✅ JWT verification on all protected endpoints
- ✅ Row Level Security (RLS) on all database tables
- ✅ Service role key kept server-side only
- ✅ Password hashing via Supabase Auth
- ✅ CORS configured for frontend origin
- ✅ User data isolation

## 🚢 Deployment

### Backend (Railway/Render/Fly.io)

1. Set environment variables in hosting platform
2. Deploy from `backend/` directory
3. Update `NEXT_PUBLIC_API_URL` in frontend

### Frontend (Vercel)

1. Connect repository to Vercel
2. Set root directory to `frontend/`
3. Add environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `NEXT_PUBLIC_API_URL`
4. Deploy

### Database (Supabase)

Already hosted - no additional deployment needed!

## 🧪 Testing

Example queries to try:

- "my iPhone 13 screen is cracked"
- "PS5 overheating issue"
- "MacBook Pro 2020 battery replacement"
- "Nintendo Switch won't charge"
- "Samsung Galaxy S21 camera not working"

## 📊 Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.11+ |
| AI/Agent | LangGraph, Google Gemini 2.0 Flash |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth (JWT) |
| Tools | iFixit API, DuckDuckGo/Tavily |
| Streaming | Server-Sent Events (SSE) |

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [iFixit](https://www.ifixit.com) for their excellent API and repair guides
- [LangChain](https://langchain.com) and [LangGraph](https://langchain-ai.github.io/langgraph/) for agent orchestration
- [Supabase](https://supabase.com) for authentication and database
- [FastAPI](https://fastapi.tiangolo.com) for the backend framework

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Check the [documentation](./docs)
- Review the SRS document included in the repository

---

**Built with ❤️ using verified iFixit guides**
