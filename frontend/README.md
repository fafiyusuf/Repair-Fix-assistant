# Frontend - Repair Fix Assistant

Next.js 14 frontend for the Repair Fix Assistant with Server-Sent Events streaming.

## 🚀 Quick Start

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Installation

1. **Install dependencies:**

```bash
npm install
# or
yarn install
```

2. **Set up environment variables:**

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. **Run the development server:**

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📁 Project Structure

```
frontend/
├── app/
│   ├── auth/
│   │   ├── login/        # Login page
│   │   └── signup/       # Signup page
│   ├── chat/             # Chat interface
│   ├── dashboard/        # Usage analytics
│   ├── globals.css       # Global styles
│   ├── layout.tsx        # Root layout
│   └── page.tsx          # Home page
├── components/           # Reusable components (future)
├── lib/
│   └── supabase.ts       # Supabase client
├── public/               # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## 🎨 Pages

### Home Page (`/`)

Landing page with:
- Hero section
- Feature highlights
- CTA buttons for login/signup
- Tech stack information

### Authentication

#### Login (`/auth/login`)

- Email/password authentication
- Form validation
- Error handling
- Redirect to chat on success

#### Signup (`/auth/signup`)

- User registration
- Password confirmation
- Email verification (if enabled)
- Success state with redirect

### Chat Interface (`/chat`)

Protected route with:
- Real-time message streaming
- Markdown rendering for repair guides
- Status updates during tool execution
- Auto-scroll to latest message
- Session management

**Features:**
- ✅ Server-Sent Events (SSE) streaming
- ✅ React Markdown with GitHub Flavored Markdown
- ✅ Image rendering from iFixit
- ✅ Loading states
- ✅ Error handling

### Dashboard (`/dashboard`)

Analytics page showing:
- Total tokens used
- Number of chat sessions
- API request count
- Recent session history
- Account information

## 🔐 Authentication Flow

1. User signs up/logs in via Supabase Auth
2. Session is stored in browser
3. JWT token is automatically sent with API requests
4. Protected routes check for valid session
5. Redirect to login if unauthenticated

### Protected Route Pattern

```typescript
useEffect(() => {
  const checkAuth = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) {
      router.push('/auth/login')
    }
  }
  checkAuth()
}, [])
```

## 📡 API Integration

### Creating a Session

```typescript
const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/sessions`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${session.access_token}`
  }
})
const data = await response.json()
```

### Streaming Chat Responses

```typescript
const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat/stream`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${session.access_token}`
  },
  body: JSON.stringify({
    message: userInput,
    session_id: sessionId
  })
})

const reader = response.body?.getReader()
const decoder = new TextDecoder()

while (true) {
  const { done, value } = await reader.read()
  if (done) break
  
  const chunk = decoder.decode(value)
  // Process SSE events...
}
```

### SSE Event Types

| Event Type | Description |
|------------|-------------|
| `status` | Tool execution updates (e.g., "Searching iFixit...") |
| `response` | Final formatted repair guide |
| `error` | Error messages |
| `done` | Stream completion signal |

## 🎨 Styling

### Tailwind CSS

The project uses Tailwind CSS with:
- Custom color palette (primary blues)
- Dark mode support
- Responsive breakpoints
- Custom utility classes

### Markdown Styling

Custom markdown styles in `globals.css`:

```css
.markdown h1 { /* Heading styles */ }
.markdown p { /* Paragraph styles */ }
.markdown img { /* Image styles */ }
```

### Component Patterns

```typescript
// Button
<button className="px-6 py-3 bg-blue-600 text-white rounded-lg 
  hover:bg-blue-700 transition-colors">
  Click Me
</button>

// Card
<div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
  Content
</div>

// Input
<input className="w-full px-4 py-3 border border-gray-300 
  dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500" />
```

## 🔧 Configuration

### Next.js Config

```javascript
// next.config.js
const nextConfig = {
  images: {
    domains: ['guide-images.cdn.ifixit.com', 'www.ifixit.com'],
  },
}
```

### TypeScript Config

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

### Tailwind Config

```javascript
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: { /* Custom palette */ }
      }
    }
  }
}
```

## 📦 Dependencies

### Core

- `next`: 14.1.0
- `react`: 18
- `react-dom`: 18
- `typescript`: 5

### Authentication

- `@supabase/supabase-js`: ^2.39.3
- `@supabase/auth-helpers-nextjs`: ^0.9.0

### UI

- `tailwindcss`: ^3.3.0
- `lucide-react`: ^0.312.0 (icons)
- `react-markdown`: ^9.0.1
- `remark-gfm`: ^4.0.0 (GitHub Flavored Markdown)

## 🚀 Build & Deploy

### Build for Production

```bash
npm run build
npm start
```

### Deploy to Vercel

1. **Connect Repository:**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository

2. **Configure Project:**
   - Root Directory: `frontend`
   - Framework Preset: Next.js

3. **Set Environment Variables:**
   ```
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```

4. **Deploy:**
   - Click "Deploy"
   - Vercel will automatically build and deploy

### Deploy to Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Build
npm run build

# Deploy
netlify deploy --prod
```

## 🧪 Testing

### Manual Testing Checklist

- [ ] Sign up with new account
- [ ] Log in with existing account
- [ ] Submit a chat message
- [ ] Verify streaming status updates appear
- [ ] Verify final response renders markdown correctly
- [ ] Check images load from iFixit
- [ ] Navigate to dashboard
- [ ] Verify token count updates
- [ ] Sign out successfully

### Example Test Queries

```
"my iPhone 13 screen is cracked"
"PS5 overheating"
"MacBook Pro 2020 battery replacement"
"Nintendo Switch won't charge"
```

## 🎯 Performance Optimization

### Image Optimization

```typescript
import Image from 'next/image'

<Image 
  src={imageUrl} 
  alt="Repair step"
  width={800}
  height={600}
  loading="lazy"
/>
```

### Code Splitting

Next.js automatically code-splits by route. For dynamic imports:

```typescript
import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <p>Loading...</p>,
})
```

### Caching

```typescript
// Revalidate every hour
export const revalidate = 3600
```

## 🐛 Troubleshooting

### "Cannot find module" errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### CORS errors

- Ensure backend CORS is configured for your frontend URL
- Check that `NEXT_PUBLIC_API_URL` is correct

### Supabase connection issues

- Verify `NEXT_PUBLIC_SUPABASE_URL` is correct
- Check that anon key is valid
- Ensure RLS policies are set up correctly

### SSE stream not working

- Check browser console for errors
- Verify backend is streaming correctly (`curl` test)
- Ensure `Content-Type: text/event-stream` header is present

## 🔐 Security Best Practices

### Environment Variables

- ✅ Use `NEXT_PUBLIC_` prefix for client-side variables
- ❌ Never expose service role key in frontend
- ✅ Use `.env.local` for local development
- ✅ Set production variables in hosting platform

### Authentication

- ✅ Always check session before API calls
- ✅ Redirect to login if unauthenticated
- ✅ Use HttpOnly cookies (handled by Supabase)
- ✅ Implement CSRF protection (built-in)

## 📱 Responsive Design

Breakpoints:

```css
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
```

Example:

```typescript
<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
  {/* 1 column on mobile, 3 on tablet+ */}
</div>
```

## 🎨 Dark Mode

Dark mode is enabled by default with Tailwind:

```typescript
<div className="bg-white dark:bg-gray-800">
  <p className="text-gray-900 dark:text-white">Content</p>
</div>
```

## 🤝 Contributing

See main [README.md](../README.md) for contribution guidelines.

## 📧 Support

For frontend-specific issues, include:
- Browser and version
- Console errors
- Network tab screenshots (if API-related)

---

**Built with Next.js 14 + TypeScript**
