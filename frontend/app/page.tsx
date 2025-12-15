import { BookOpen, Shield, Wrench, Zap } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          {/* Logo */}
          <div className="flex justify-center mb-8">
            <div className="bg-primary-500 p-4 rounded-full">
              <Wrench className="w-16 h-16 text-white" />
            </div>
          </div>

          {/* Hero Section */}
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-6">
            Repair Fix Assistant
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-12 max-w-2xl mx-auto">
            AI-powered device repair assistant using verified iFixit guides. 
            Get step-by-step repair instructions with images, powered by LangGraph.
          </p>

          {/* CTA Buttons */}
          <div className="flex gap-4 justify-center mb-16">
            <Link 
              href="/auth/login"
              className="px-8 py-3 bg-primary-500 text-white rounded-lg font-semibold hover:bg-primary-600 transition-colors"
            >
              Sign In
            </Link>
            <Link 
              href="/auth/signup"
              className="px-8 py-3 bg-white text-primary-600 border-2 border-primary-500 rounded-lg font-semibold hover:bg-primary-50 transition-colors"
            >
              Sign Up
            </Link>
          </div>

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-8 mt-16">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <BookOpen className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">
                Official iFixit Guides
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Always prioritizes verified repair documentation from iFixit
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <Zap className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">
                Real-time Streaming
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Watch as the AI searches and retrieves repair steps live
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg">
              <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <Shield className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">
                No Hallucinations
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Deterministic tools-first approach prevents AI fabrication
              </p>
            </div>
          </div>

          {/* Tech Stack */}
          <div className="mt-16 p-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
            <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
              Powered By
            </h2>
            <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-600 dark:text-gray-400">
              <span className="px-4 py-2 bg-primary-50 dark:bg-gray-700 rounded-full">Next.js</span>
              <span className="px-4 py-2 bg-primary-50 dark:bg-gray-700 rounded-full">FastAPI</span>
              <span className="px-4 py-2 bg-primary-50 dark:bg-gray-700 rounded-full">LangGraph</span>
              <span className="px-4 py-2 bg-primary-50 dark:bg-gray-700 rounded-full">Supabase</span>
              <span className="px-4 py-2 bg-primary-50 dark:bg-gray-700 rounded-full">OpenAI/Gemini</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
