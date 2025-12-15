'use client'

import { ThemeToggle } from '@/components/ThemeToggle'
import { supabase } from '@/lib/supabase'
import { ArrowLeft, BarChart3, MessageSquare, Zap } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

interface UsageStats {
  total_tokens: number
  records: number
}

export default function DashboardPage() {
  const router = useRouter()
  const [stats, setStats] = useState<UsageStats | null>(null)
  const [sessions, setSessions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) {
      router.push('/auth/login')
      return
    }

    setUser(session.user)

    try {
      // Fetch usage stats
      const statsResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/usage`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })
      const statsData = await statsResponse.json()
      setStats(statsData)

      // Fetch sessions
      const sessionsResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/sessions`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })
      const sessionsData = await sessionsResponse.json()
      setSessions(sessionsData.sessions || [])
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading analytics...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              href="/chat"
              className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-primary-500 dark:hover:text-primary-400 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Chat</span>
            </Link>
          </div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">
            Usage Analytics
          </h1>
          <ThemeToggle />
        </div>
      </header>

      {/* Content */}
      <div className="container mx-auto max-w-6xl px-4 py-8">
        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-primary-100 dark:bg-primary-900/20 p-3 rounded-lg">
                <Zap className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {stats?.total_tokens.toLocaleString() || 0}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Total Tokens Used
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-primary-200 dark:bg-primary-800/20 p-3 rounded-lg">
                <MessageSquare className="w-6 h-6 text-primary-700 dark:text-primary-300" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {sessions.length}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Chat Sessions
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-primary-300 dark:bg-primary-700/20 p-3 rounded-lg">
                <BarChart3 className="w-6 h-6 text-primary-800 dark:text-primary-200" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {stats?.records || 0}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              API Requests
            </p>
          </div>
        </div>

        {/* Sessions List */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Recent Sessions
          </h2>
          
          {sessions.length === 0 ? (
            <div className="text-center py-12">
              <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600 dark:text-gray-400">
                No sessions yet. Start chatting to see your history here!
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {sessions.slice(0, 10).map((session) => (
                <div
                  key={session.id}
                  className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      Session {session.id.slice(0, 8)}...
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {new Date(session.created_at).toLocaleString()}
                    </p>
                  </div>
                  <Link
                    href={`/chat?session=${session.id}`}
                    className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm"
                  >
                    View
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* User Info */}
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Account Information
          </h2>
          <div className="space-y-2">
            <p className="text-gray-600 dark:text-gray-400">
              <span className="font-semibold">Email:</span> {user?.email}
            </p>
            <p className="text-gray-600 dark:text-gray-400">
              <span className="font-semibold">User ID:</span> {user?.id}
            </p>
            <p className="text-gray-600 dark:text-gray-400">
              <span className="font-semibold">Joined:</span>{' '}
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
