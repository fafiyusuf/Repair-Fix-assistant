# 🚀 Quick Setup Guide

Complete setup instructions for the Repair Fix Assistant.

## Prerequisites Checklist

- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] Git installed
- [ ] Supabase account created
- [ ] OpenAI or Gemini API key obtained
- [ ] VPN available (for iFixit API)

## Step-by-Step Setup

### 1. Supabase Setup (10 minutes)

1. Go to [supabase.com](https://supabase.com) and create an account
2. Click "New Project"
3. Fill in project details:
   - Name: `repair-fix-assistant`
   - Database Password: (generate a strong password)
   - Region: (choose closest to you)
4. Wait for project to be created (~2 minutes)
5. Go to **Settings** → **API**
   - Copy `Project URL` → Save as `SUPABASE_URL`
   - Copy `anon/public` key → Save as `SUPABASE_ANON_KEY`
   - Copy `service_role` key → Save as `SUPABASE_SERVICE_ROLE_KEY` (keep secret!)
6. Go to **Authentication** → **Providers**
   - Enable "Email" provider
   - Disable "Confirm email" for easier testing (optional)
7. Go to **SQL Editor**
   - Click "New query"
   - Copy entire contents of `supabase/schema.sql`
   - Paste and click "Run"
   - Verify all tables were created (check Table Editor)

### 2. Backend Setup (5 minutes)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

Edit `backend/.env`:

```env
SUPABASE_URL=https://xxxxxxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbG...your-service-role-key

# Choose ONE:
OPENAI_API_KEY=sk-...your-openai-key
# OR
# GEMINI_API_KEY=...your-gemini-key

ENVIRONMENT=development
LOG_LEVEL=INFO
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Test it: Open http://localhost:8000 in your browser
You should see: `{"status":"healthy","service":"Repair Fix Assistant","version":"1.0.0"}`

### 3. Frontend Setup (5 minutes)

Open a new terminal:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local
```

Edit `frontend/.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbG...your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the frontend:

```bash
npm run dev
```

You should see:
```
ready - started server on 0.0.0.0:3000
```

Open http://localhost:3000 in your browser

### 4. First Test (5 minutes)

1. **Sign Up:**
   - Click "Sign Up" on the home page
   - Enter email: `test@example.com`
   - Enter password: `password123`
   - Click "Sign Up"
   - You should be redirected to `/chat`

2. **Test Chat:**
   - Type: `my iPhone 13 screen is cracked`
   - Click "Send"
   - Watch for status updates:
     - ✅ "Normalizing query..."
     - ✅ "Searching iFixit for device..."
     - ✅ "Found device: iPhone 13"
     - ✅ "Fetching available repair guides..."
     - ✅ "Found X repair guides"
     - ✅ "Selecting most relevant guide..."
     - ✅ "Fetching repair instructions..."
     - ✅ "Formatting response..."
   - Final response should show repair guide with images

3. **Check Analytics:**
   - Click "Analytics" button in header
   - Verify token count increased
   - See your chat session listed

## Troubleshooting

### Backend won't start

**Error: "No LLM API key configured"**
- Solution: Add `OPENAI_API_KEY` or `GEMINI_API_KEY` to `backend/.env`

**Error: "Connection to Supabase failed"**
- Solution: Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are correct
- Check you're using the **service role key**, not the anon key

### Frontend won't start

**Error: "Module not found"**
- Solution: Delete `node_modules` and run `npm install` again

**Error: "Invalid Supabase configuration"**
- Solution: Verify `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` in `frontend/.env.local`

### Chat not working

**No response after sending message**
- Check backend terminal for errors
- Verify backend is running on port 8000
- Check browser console for CORS errors
- Ensure `NEXT_PUBLIC_API_URL` is `http://localhost:8000` (no trailing slash)

**"No device found on iFixit"**
- Connect to VPN (iFixit API may be blocked in some regions)
- Try a different device name (e.g., "PlayStation 5", "iPhone 14")

**Authentication errors**
- Clear browser cookies and localStorage
- Sign out and sign in again
- Check Supabase dashboard → Authentication → Users (should see your user)

## Production Deployment

### Backend (Railway)

1. Create account at [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Set root directory: `backend`
5. Add environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `OPENAI_API_KEY` or `GEMINI_API_KEY`
   - `ENVIRONMENT=production`
6. Deploy
7. Copy the deployment URL (e.g., `https://your-app.railway.app`)

### Frontend (Vercel)

1. Create account at [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - Root Directory: `frontend`
   - Framework Preset: Next.js
5. Add environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `NEXT_PUBLIC_API_URL=https://your-app.railway.app`
6. Deploy
7. Update backend CORS to allow your Vercel URL

## Security Checklist

Before going to production:

- [ ] Change all default passwords
- [ ] Enable email confirmation in Supabase Auth
- [ ] Set strong password requirements
- [ ] Update CORS origins in backend
- [ ] Use environment-specific API keys
- [ ] Enable Supabase RLS policies
- [ ] Set up monitoring and logging
- [ ] Configure rate limiting
- [ ] Enable HTTPS (automatic on Vercel/Railway)

## Next Steps

- [ ] Customize the UI (colors, branding)
- [ ] Add more chat features (edit messages, delete sessions)
- [ ] Implement conversation summarization for long chats
- [ ] Add support for uploading device photos
- [ ] Set up error monitoring (Sentry)
- [ ] Add analytics (PostHog, Mixpanel)
- [ ] Implement user feedback mechanism
- [ ] Add FAQ/help section

## Support

If you get stuck:

1. Check the error messages carefully
2. Review the README files:
   - Main: `README.md`
   - Backend: `backend/README.md`
   - Frontend: `frontend/README.md`
3. Check the SRS document for architecture details
4. Open an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - Your environment (OS, Python/Node version)

---

**Happy coding! 🔧**
