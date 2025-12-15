'use client'

import { supabase } from '@/lib/supabase'
import { MessageSquare, Plus, Trash2, X } from 'lucide-react'
import { useEffect, useState } from 'react'

interface Session {
  id: string
  title?: string
  created_at: string
  updated_at: string
}

interface SessionHistoryProps {
  currentSessionId: string | null
  onSessionSelect: (sessionId: string) => void
  onNewSession: () => void
  isOpen?: boolean
  onClose?: () => void
  refreshTrigger?: number // Add this to trigger reload from parent
}

export function SessionHistory({ currentSessionId, onSessionSelect, onNewSession, isOpen = false, onClose, refreshTrigger }: SessionHistoryProps) {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSessions()
  }, [refreshTrigger]) // Reload when refreshTrigger changes

  const loadSessions = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) return

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/sessions`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setSessions(data.sessions || [])
      }
    } catch (error) {
      console.error('Failed to load sessions:', error)
    } finally {
      setLoading(false)
    }
  }

  const deleteSession = async (sessionId: string) => {
    if (!confirm('Delete this conversation?')) return

    const { data: { session } } = await supabase.auth.getSession()
    if (!session) return

    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })
      
      await loadSessions()
      
      // If deleted current session, create new one
      if (sessionId === currentSessionId) {
        onNewSession()
      }
    } catch (error) {
      console.error('Failed to delete session:', error)
    }
  }

  return (
    <>
      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-40 w-72 bg-white dark:bg-sidebar border-r border-gray-200 dark:border-sidebar-border 
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static
      `}>
        <div className="flex flex-col h-full">
          {/* Header with close button for mobile */}
          <div className="p-4 border-b border-gray-200 dark:border-sidebar-border">
            <div className="flex items-center justify-between mb-4 lg:hidden">
              <span className="text-sm font-medium text-gray-900 dark:text-white">History</span>
              <button
                onClick={onClose}
                className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-sidebar-hover transition-colors"
              >
                <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
              </button>
            </div>
            <button
              onClick={onNewSession}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-xl transition-all shadow-md font-medium"
            >
              <Plus className="w-5 h-5" />
              New Conversation
            </button>
          </div>

          {/* Sessions list */}
          <div className="flex-1 overflow-y-auto p-4 scrollbar-thin">
            <h3 className="text-xs font-bold text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wider px-2">
              Recent Chats
            </h3>
            
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mx-auto"></div>
              </div>
            ) : sessions.length === 0 ? (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No conversations yet</p>
              </div>
            ) : (
              <div className="space-y-1.5">
                {sessions.map((session) => (
                  <div
                    key={session.id}
                    className={`
                      group flex items-center gap-2 p-3 rounded-xl cursor-pointer transition-all
                      ${session.id === currentSessionId 
                        ? 'bg-primary-50 dark:bg-primary-600/20 border-2 border-primary-200 dark:border-primary-700 shadow-sm' 
                        : 'hover:bg-gray-50 dark:hover:bg-sidebar-hover border-2 border-transparent'
                      }
                    `}
                  >
                    <div 
                      onClick={() => onSessionSelect(session.id)}
                      className="flex-1 min-w-0"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <MessageSquare className="w-4 h-4 text-gray-500 dark:text-gray-400 flex-shrink-0" />
                        <span className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {session.title || 'New Chat'}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(session.created_at).toLocaleDateString(undefined, { 
                          month: 'short', 
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        deleteSession(session.id)
                      }}
                      className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-all"
                      title="Delete conversation"
                    >
                      <Trash2 className="w-4 h-4 text-red-600 dark:text-red-400" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
        />
      )}
    </>
  )
}
