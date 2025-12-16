'use client'

import { ThemeToggle } from '@/components/ThemeToggle'
import { supabase } from '@/lib/supabase'
import {
  Activity,
  ArrowLeft,
  Calendar,
  Clock,
  DollarSign,
  Info,
  TrendingUp,
  Zap
} from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

interface UsageStats {
  total_tokens: number
  input_tokens: number
  output_tokens: number
  records: number
  total_cost: number
}

interface DailyUsage {
  date: string
  tokens: number
  requests: number
}

export default function DashboardPage() {
  const router = useRouter()
  const [stats, setStats] = useState<UsageStats | null>(null)
  const [dailyUsage, setDailyUsage] = useState<DailyUsage[]>([])
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState<any>(null)
  const [recentActivity, setRecentActivity] = useState<any[]>([])

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
      // Fetch usage stats from database directly
      const userId = session.user.id

      // Get total usage stats
      const { data: usageData, error: usageError } = await supabase
        .from('usage_stats')
        .select('tokens_used, input_tokens, output_tokens')
        .eq('user_id', userId)

      if (!usageError && usageData) {
        const totalTokens = usageData.reduce((sum, record) => sum + (record.tokens_used || 0), 0)
        const inputTokens = usageData.reduce((sum, record) => sum + (record.input_tokens || 0), 0)
        const outputTokens = usageData.reduce((sum, record) => sum + (record.output_tokens || 0), 0)
        const totalCost = (totalTokens / 1000) * 0.0001 // Gemini 2.5 Flash pricing

        setStats({
          total_tokens: totalTokens,
          input_tokens: inputTokens,
          output_tokens: outputTokens,
          records: usageData.length,
          total_cost: totalCost
        })
      }

      // Get daily usage for last 7 days
      const sevenDaysAgo = new Date()
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)

      const { data: dailyData, error: dailyError } = await supabase
        .from('usage_stats')
        .select('timestamp, tokens_used')
        .eq('user_id', userId)
        .gte('timestamp', sevenDaysAgo.toISOString())
        .order('timestamp', { ascending: true })

      if (!dailyError && dailyData) {
        // Group by date
        const grouped = dailyData.reduce((acc: any, record) => {
          const date = new Date(record.timestamp).toLocaleDateString()
          if (!acc[date]) {
            acc[date] = { tokens: 0, requests: 0 }
          }
          acc[date].tokens += record.tokens_used || 0
          acc[date].requests += 1
          return acc
        }, {})

        const daily = Object.entries(grouped).map(([date, data]: [string, any]) => ({
          date,
          tokens: data.tokens,
          requests: data.requests
        }))

        setDailyUsage(daily)
      }

      // Get recent activity (last 5 requests)
      const { data: activityData, error: activityError } = await supabase
        .from('usage_stats')
        .select('timestamp, tokens_used, input_tokens, output_tokens, session_id')
        .eq('user_id', userId)
        .order('timestamp', { ascending: false })
        .limit(5)

      if (!activityError && activityData) {
        setRecentActivity(activityData)
      }

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

  const avgTokensPerRequest = stats?.records ? Math.round(stats.total_tokens / stats.records) : 0

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
      <div className="container mx-auto max-w-7xl px-4 py-8">
        {/* Primary Stats Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          {/* Total Tokens */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-gray-200 dark:border-gray-700">
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

          {/* Total Requests */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-blue-100 dark:bg-blue-900/20 p-3 rounded-lg">
                <Activity className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {stats?.records || 0}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              API Requests
            </p>
          </div>

          {/* Estimated Cost */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-green-100 dark:bg-green-900/20 p-3 rounded-lg">
                <DollarSign className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              ${stats?.total_cost.toFixed(4) || '0.0000'}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Estimated Cost (USD)
            </p>
          </div>

          {/* Average Tokens */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-purple-100 dark:bg-purple-900/20 p-3 rounded-lg">
                <TrendingUp className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {avgTokensPerRequest.toLocaleString()}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Avg Tokens/Request
            </p>
          </div>
        </div>

        {/* Secondary Stats Row */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Token Breakdown */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Info className="w-5 h-5 text-primary-500" />
              Token Breakdown
            </h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <span className="text-gray-600 dark:text-gray-300 font-medium">Input Tokens</span>
                <span className="text-gray-900 dark:text-white font-bold">
                  {stats?.input_tokens.toLocaleString() || 0}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <span className="text-gray-600 dark:text-gray-300 font-medium">Output Tokens</span>
                <span className="text-gray-900 dark:text-white font-bold">
                  {stats?.output_tokens.toLocaleString() || 0}
                </span>
              </div>
              <div className="pt-3 border-t border-gray-200 dark:border-gray-600">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    Input/Output Ratio
                  </span>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {stats?.input_tokens && stats?.output_tokens 
                      ? (stats.input_tokens / stats.output_tokens).toFixed(2) 
                      : 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5 text-primary-500" />
              Recent Activity
            </h2>
            {recentActivity.length === 0 ? (
              <div className="text-center py-8">
                <Activity className="w-10 h-10 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500 dark:text-gray-400 text-sm">
                  No recent activity
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {recentActivity.map((activity, idx) => (
                  <div
                    key={idx}
                    className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                  >
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-300">
                        {activity.tokens_used.toLocaleString()} tokens
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(activity.timestamp).toLocaleString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        In: {activity.input_tokens || 0}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Out: {activity.output_tokens || 0}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Daily Usage Chart */}
        {dailyUsage.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 mb-8 border border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-primary-500" />
              Last 7 Days Usage
            </h2>
            <div className="space-y-3">
              {dailyUsage.map((day, idx) => {
                const maxTokens = Math.max(...dailyUsage.map(d => d.tokens))
                const percentage = (day.tokens / maxTokens) * 100
                
                return (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-gray-600 dark:text-gray-300 font-medium">
                        {day.date}
                      </span>
                      <span className="text-gray-500 dark:text-gray-400">
                        {day.tokens.toLocaleString()} tokens • {day.requests} requests
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-primary-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Pricing Info Card */}
        <div className="bg-gradient-to-r from-primary-50 to-primary-100 dark:from-primary-950/20 dark:to-primary-900/20 rounded-xl shadow-md p-6 border border-primary-200 dark:border-primary-800">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
            <Info className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            Pricing Information
          </h2>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Model</p>
              <p className="text-sm font-bold text-gray-900 dark:text-white">Gemini 2.5 Flash</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Rate</p>
              <p className="text-sm font-bold text-gray-900 dark:text-white">$0.0001 / 1K tokens</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Data Source</p>
              <p className="text-sm font-bold text-gray-900 dark:text-white">iFixit API (Free)</p>
            </div>
          </div>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-4">
            💡 <strong>Note:</strong> Costs are estimates based on Gemini 2.5 Flash pricing. 
            iFixit API is free. Tavily fallback search (if used) has separate billing.
          </p>
        </div>

        {/* Account Info */}
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
            Account Information
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Email</p>
              <p className="text-sm font-medium text-gray-900 dark:text-white">{user?.email}</p>
            </div>
            <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Member Since</p>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
