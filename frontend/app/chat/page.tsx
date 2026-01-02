'use client'

import { BarChart3, ExternalLink, Loader2, LogOut, Menu, Send, Square, Wrench } from 'lucide-react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import React, { useEffect, useRef, useState } from 'react'
import type { Components } from 'react-markdown'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

import { SessionHistory } from '@/components/SessionHistory'
import { ThemeToggle } from '@/components/ThemeToggle'
import { supabase } from '@/lib/supabase'

interface Message {
  role: 'user' | 'assistant' | 'status'
  content: string
  timestamp: Date
}

// Custom components for ReactMarkdown
const markdownComponents: Components = {
  a: ({ node, children, href, ...props }) => (
    <a 
      href={href} 
      target="_blank" 
      rel="noopener noreferrer" 
      className="inline-flex items-center gap-1 text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 underline decoration-primary-600/30 dark:decoration-primary-400/30 underline-offset-2 hover:decoration-primary-600 dark:hover:decoration-primary-400 transition-colors font-medium"
      {...props}
    >
      {children}
      <ExternalLink className="w-3 h-3 inline-block" />
    </a>
  ),
  code: ({ node, inline, className, children, ...props }: any) => {
    if (inline) {
      return (
        <code 
          className="bg-gray-100 dark:bg-gray-800 text-primary-700 dark:text-primary-300 px-1.5 py-0.5 rounded text-[0.875em] font-mono border border-gray-200 dark:border-gray-700"
          {...props}
        >
          {children}
        </code>
      )
    }
    return (
      <code 
        className={`${className} block bg-gray-900 dark:bg-gray-950 text-gray-100 p-4 rounded-lg overflow-x-auto border border-gray-700 dark:border-gray-800`}
        {...props}
      >
        {children}
      </code>
    )
  },
  p: ({ node, children, ...props }) => (
    <p className="mb-4 leading-relaxed text-gray-700 dark:text-gray-300" {...props}>
      {children}
    </p>
  ),
  ol: ({ node, children, ...props }) => (
    <ol className="list-decimal mb-4 space-y-2 pl-6" {...props}>
      {children}
    </ol>
  ),
  ul: ({ node, children, ...props }) => (
    <ul className="list-disc mb-4 space-y-2 pl-6" {...props}>
      {children}
    </ul>
  ),
  li: ({ node, children, ...props }) => (
    <li className="text-gray-700 dark:text-gray-300 leading-relaxed" {...props}>
      {children}
    </li>
  ),
  h1: ({ node, children, ...props }) => (
    <h1 className="text-2xl font-bold text-gray-900 dark:text-white mt-6 mb-4" {...props}>
      {children}
    </h1>
  ),
  h2: ({ node, children, ...props }) => (
    <h2 className="text-xl font-bold text-gray-900 dark:text-white mt-5 mb-3" {...props}>
      {children}
    </h2>
  ),
  h3: ({ node, children, ...props }) => (
    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mt-4 mb-2" {...props}>
      {children}
    </h3>
  ),
  strong: ({ node, children, ...props }) => (
    <strong className="font-bold text-gray-900 dark:text-white" {...props}>
      {children}
    </strong>
  ),
  blockquote: ({ node, children, ...props }) => (
    <blockquote className="border-l-4 border-primary-500 bg-primary-50 dark:bg-gray-800 pl-4 pr-4 py-2 italic my-4 text-gray-700 dark:text-gray-300 rounded-r" {...props}>
      {children}
    </blockquote>
  ),
  hr: ({ node, ...props }) => (
    <hr className="my-6 border-gray-200 dark:border-gray-700" {...props} />
  ),
}

// Memoized Message Component to prevent unnecessary re-renders during streaming
const MessageContent = React.memo(({ content }: { content: string }) => {
  return (
    <div className="prose max-w-none text-gray-700 dark:text-gray-300">
      <ReactMarkdown 
        remarkPlugins={[remarkGfm]}
        components={markdownComponents}
        key={content.length} // Force re-render when content length changes
      >
        {content}
      </ReactMarkdown>
    </div>
  )
})

MessageContent.displayName = 'MessageContent'

export default function ChatPage() {
  const router = useRouter()
  const searchParams = useSearchParams()

  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingStatus, setLoadingStatus] = useState('')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [user, setUser] = useState<any>(null)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [sessionRefresh, setSessionRefresh] = useState(0) // Trigger for session list refresh

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const abortControllerRef = useRef<AbortController | null>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const streamingMessageRef = useRef<boolean>(false)

  /* ---------------- Auth + Session ---------------- */
  useEffect(() => {
    checkAuth()
    // Check for session ID in URL
    const urlSessionId = searchParams.get('session')
    if (urlSessionId) {
      setSessionId(urlSessionId)
    }
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (sessionId) loadConversationHistory()
  }, [sessionId])

  const checkAuth = async () => {
    const { data } = await supabase.auth.getSession()
    if (!data.session) {
      router.push('/auth/login')
      return
    }
    setUser(data.session.user)
  }

  const loadConversationHistory = async () => {
    if (!sessionId) return
    setLoadingHistory(true)

    try {
      const { data } = await supabase.auth.getSession()
      if (!data.session) return

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/sessions/${sessionId}/messages`,
        {
          headers: {
            Authorization: `Bearer ${data.session.access_token}`,
          },
        }
      )

      if (!res.ok) return

      const json = await res.json()
      const history: Message[] = json.messages.map((m: any) => ({
        role: m.role,
        content: m.content,
        timestamp: new Date(m.created_at),
      }))

      setMessages(history)
    } catch (err) {
      console.error('Load history failed', err)
    } finally {
      setLoadingHistory(false)
    }
  }

  /* ---------------- Helpers ---------------- */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleStop = () => {
    abortControllerRef.current?.abort()
    abortControllerRef.current = null
    setLoading(false)
    setLoadingStatus('')

    setMessages((prev) => [
      ...prev,
      {
        role: 'assistant',
        content: '⚠️ Response cancelled by user.',
        timestamp: new Date(),
      },
    ])
  }

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px'
    }
  }

  /* ---------------- Chat Submit ---------------- */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    // Create session on first message if it doesn't exist
    let currentSessionId = sessionId
    if (!currentSessionId) {
      const { data } = await supabase.auth.getSession()
      if (!data.session) {
        router.push('/auth/login')
        return
      }

      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/sessions`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${data.session.access_token}`,
          },
        })

        const json = await res.json()
        currentSessionId = json.session_id
        setSessionId(currentSessionId)
        // Update URL with session ID
        router.replace(`/chat?session=${currentSessionId}`, { scroll: false })
      } catch (err) {
        console.error('Create session failed', err)
        return
      }
    }

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
    setLoading(true)
    setLoadingStatus('Starting search...')
    streamingMessageRef.current = false // Reset streaming flag

    abortControllerRef.current = new AbortController()

    try {
      const { data } = await supabase.auth.getSession()
      if (!data.session) {
        router.push('/auth/login')
        return
      }

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${data.session.access_token}`,
        },
        body: JSON.stringify({
          message: userMessage.content,
          session_id: currentSessionId,
        }),
        signal: abortControllerRef.current.signal,
      })

      if (!res.body) throw new Error('No stream')

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let assistantText = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        for (const line of chunk.split('\n')) {
          if (!line.startsWith('data: ')) continue

          const payload = JSON.parse(line.slice(6))

          if (payload.type === 'status') {
            setLoadingStatus(payload.content)
          }

          if (payload.type === 'response') {
            assistantText = payload.content
            setLoadingStatus('')
            
            // Update or add the streaming assistant message
            setMessages((prev) => {
              // If we haven't added the streaming message yet, add it
              if (!streamingMessageRef.current) {
                streamingMessageRef.current = true
                return [
                  ...prev,
                  {
                    role: 'assistant',
                    content: assistantText,
                    timestamp: new Date(),
                  },
                ]
              }
              
              // Otherwise, update the last assistant message (the streaming one)
              const lastIndex = prev.length - 1
              if (lastIndex >= 0 && prev[lastIndex].role === 'assistant') {
                return [
                  ...prev.slice(0, lastIndex),
                  {
                    ...prev[lastIndex],
                    content: assistantText,
                  },
                ]
              }
              
              // Fallback: just add the message
              return [
                ...prev,
                {
                  role: 'assistant',
                  content: assistantText,
                  timestamp: new Date(),
                },
              ]
            })
          }
        }
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.error(err)
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: '❌ Something went wrong. Try again.',
            timestamp: new Date(),
          },
        ])
      }
    } finally {
      setLoading(false)
      setLoadingStatus('')
      abortControllerRef.current = null
      
      // Refresh session list to show updated title
      setSessionRefresh(prev => prev + 1)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  /* ---------------- Session Controls ---------------- */
  const handleSessionSelect = async (id: string) => {
    setSessionId(id)
    setMessages([])
    setSidebarOpen(false)
    // Update URL with selected session ID
    router.replace(`/chat?session=${id}`, { scroll: false })
  }

  const handleNewSession = () => {
    setMessages([])
    setSessionId(null) // Clear session ID - new session will be created on first message
    setSidebarOpen(false)
    // Clear URL parameter
    router.replace('/chat', { scroll: false })
  }

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    router.push('/')
  }

  /* ---------------- UI ---------------- */
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-chat-bg">
      {/* Sidebar */}
      <SessionHistory
        currentSessionId={sessionId}
        onSessionSelect={handleSessionSelect}
        onNewSession={handleNewSession}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        refreshTrigger={sessionRefresh}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navigation Bar */}
        <header className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-sidebar-border bg-white dark:bg-sidebar">
          <div className="flex items-center gap-3">
            {/* Mobile menu button */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-sidebar-hover transition-colors"
              aria-label="Open sidebar"
            >
              <Menu className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            </button>

            {/* Logo and Title */}
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary-500 flex items-center justify-center">
                <Wrench className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-lg font-semibold text-gray-900 dark:text-white hidden sm:block">
                Repair Fix Assistant
              </h1>
            </div>
          </div>

          {/* Right side actions */}
          <div className="flex items-center gap-2">
            <ThemeToggle />
            
            <Link 
              href="/dashboard" 
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-sidebar-hover transition-colors"
              title="Dashboard"
            >
              <BarChart3 className="w-5 h-5" />
              <span className="hidden sm:inline text-sm font-medium">Dashboard</span>
            </Link>

            <button 
              onClick={handleSignOut} 
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-sidebar-hover transition-colors"
              title="Sign out"
            >
              <LogOut className="w-5 h-5" />
              <span className="hidden sm:inline text-sm font-medium">Sign Out</span>
            </button>
          </div>
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto scrollbar-thin">
          {messages.length === 0 && !loadingHistory ? (
            /* Empty State */
            <div className="flex flex-col items-center justify-center h-full px-4">
              <div className="w-16 h-16 rounded-2xl bg-primary-500 flex items-center justify-center mb-6">
                <Wrench className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
                How can I help you today?
              </h2>
              <p className="text-gray-500 dark:text-gray-400 text-center max-w-md">
                Describe your device issue and I&apos;ll find the best repair guides from iFixit for you.
              </p>

              {/* Example prompts */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-8 w-full max-w-2xl">
                {[
                  'My iPhone screen is cracked',
                  'MacBook Pro won\'t turn on',
                  'Samsung Galaxy battery drains fast',
                  'Nintendo Switch Joy-Con drift',
                ].map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(prompt)}
                    className="p-4 text-left border border-gray-200 dark:border-sidebar-border rounded-xl hover:bg-gray-50 dark:hover:bg-sidebar-hover transition-colors text-gray-700 dark:text-gray-300 text-sm"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            /* Chat Messages */
            <div className="max-w-3xl mx-auto px-4 py-6">
              {messages.map((m, i) => (
                <div 
                  key={`${i}-${m.timestamp.getTime()}-${m.content.length}`}
                  className={`py-6 ${i !== 0 ? 'border-t border-gray-100 dark:border-sidebar-border' : ''}`}
                >
                  <div className="flex gap-4">
                    {/* Avatar */}
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      m.role === 'user' 
                        ? 'bg-primary-400 text-white' 
                        : 'bg-primary-600 text-white'
                    }`}>
                      {m.role === 'user' ? (
                        <span className="text-sm font-medium">
                          {user?.email?.charAt(0).toUpperCase() || 'U'}
                        </span>
                      ) : (
                        <Wrench className="w-4 h-4" />
                      )}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-900 dark:text-white mb-1 text-sm">
                        {m.role === 'user' ? 'You' : 'Repair Fix Assistant'}
                      </div>
                      {m.role === 'assistant' ? (
                        <MessageContent content={m.content} />
                      ) : (
                        <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{m.content}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}

              {/* Loading Status */}
              {loading && loadingStatus && (
                <div className="py-6 border-t border-gray-100 dark:border-sidebar-border">
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center">
                      <Wrench className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>{loadingStatus}</span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 dark:border-sidebar-border bg-white dark:bg-sidebar p-4">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
            <div className="relative flex items-end bg-gray-100 dark:bg-chat-user rounded-2xl border border-gray-200 dark:border-sidebar-border focus-within:border-primary-500 focus-within:ring-2 focus-within:ring-primary-500/20 transition-all">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => {
                  setInput(e.target.value)
                  adjustTextareaHeight()
                }}
                onKeyDown={handleKeyDown}
                placeholder="Describe your device issue..."
                disabled={loading}
                rows={1}
                className="flex-1 bg-transparent px-4 py-3 resize-none focus:outline-none text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 max-h-[200px]"
              />

              {loading ? (
                <button
                  type="button"
                  onClick={handleStop}
                  className="m-2 p-2 rounded-lg bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors"
                  title="Stop generating"
                >
                  <Square className="w-5 h-5 text-gray-700 dark:text-gray-200" />
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={!input.trim()}
                  className={`m-2 p-2 rounded-lg transition-colors ${
                    input.trim()
                      ? 'bg-primary-500 hover:bg-primary-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-600 text-gray-400 dark:text-gray-500 cursor-not-allowed'
                  }`}
                  title="Send message"
                >
                  <Send className="w-5 h-5" />
                </button>
              )}
            </div>
            <p className="text-xs text-center text-gray-500 dark:text-gray-400 mt-2">
              Powered by iFixit repair guides. Results may vary based on device model.
            </p>
          </form>
        </div>
      </div>
    </div>
  )
}
