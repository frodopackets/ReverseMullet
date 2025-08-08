'use client'

import { useState } from 'react'
import { BubblegumChatInterface, Message } from '@/components/chat/bubblegum-chat-interface'
import { StatusIndicator } from '@/components/chat/status-indicator'
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { Sparkles, ArrowLeft, Heart, Star, Terminal, Crown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function BubblegumPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      content,
      role: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Send message to API endpoint
      const apiUrl = process.env.NEXT_PUBLIC_API_URL
      const endpoint = apiUrl ? `${apiUrl}/chat` : '/api/chat'
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: content }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response from API')
      }

      const assistantMessage = await response.json()
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Failed to send message:', error)
      // Add error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        content: 'Oops! Something went wrong with the magic! ✨ Please try again! 💖',
        role: 'assistant',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 via-purple-100 to-blue-100 py-4 px-4 relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-10 left-10 text-4xl animate-bounce text-pink-300/30" style={{ animationDelay: '0s' }}>🌸</div>
        <div className="absolute top-20 right-20 text-3xl animate-bounce text-purple-300/30" style={{ animationDelay: '0.5s' }}>🦋</div>
        <div className="absolute bottom-20 left-20 text-5xl animate-bounce text-blue-300/30" style={{ animationDelay: '1s' }}>🌈</div>
        <div className="absolute bottom-10 right-10 text-3xl animate-bounce text-pink-300/30" style={{ animationDelay: '1.5s' }}>🎀</div>
        <div className="absolute top-1/2 left-5 text-2xl animate-bounce text-purple-300/30" style={{ animationDelay: '2s' }}>✨</div>
        <div className="absolute top-1/3 right-5 text-4xl animate-bounce text-pink-300/30" style={{ animationDelay: '2.5s' }}>🌺</div>
      </div>

      <div className="max-w-6xl mx-auto space-y-6 relative z-10">
        {/* Navigation Bar */}
        <div className="flex justify-between items-center py-4">
          <div className="flex gap-2">
            <Link href="/">
              <Button 
                variant="outline" 
                size="sm" 
                className="border-3 border-pink-300 text-pink-600 hover:bg-pink-100 rounded-full shadow-lg font-bold"
                style={{ fontFamily: 'Comic Sans MS, cursive' }}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Normal
              </Button>
            </Link>
            <Link href="/terminal">
              <Button 
                variant="outline" 
                size="sm" 
                className="border-3 border-green-300 text-green-600 hover:bg-green-100 rounded-full shadow-lg font-bold"
                style={{ fontFamily: 'Comic Sans MS, cursive' }}
              >
                <Terminal className="h-4 w-4 mr-2" />
                Terminal
              </Button>
            </Link>
            <Link href="/medieval">
              <Button 
                variant="outline" 
                size="sm" 
                className="border-3 border-stone-300 text-stone-600 hover:bg-stone-100 rounded-full shadow-lg font-bold"
                style={{ fontFamily: 'Comic Sans MS, cursive' }}
              >
                <Crown className="h-4 w-4 mr-2" />
                Medieval
              </Button>
            </Link>
          </div>
          <ThemeToggle />
        </div>
        
        {/* Main Content */}
        <div className="text-center mb-8">
          
          {/* Main title */}
          <div className="flex items-center justify-center gap-4 mb-4">
            <Sparkles className="h-10 w-10 text-pink-500 animate-spin" />
            <h1 className="text-5xl font-bold bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 bg-clip-text text-transparent" style={{ fontFamily: 'Comic Sans MS, cursive' }}>
              Magical Bubblegum Chat
            </h1>
            <Heart className="h-10 w-10 text-pink-500 animate-pulse" />
          </div>
          
          <p className="text-2xl text-purple-600 mb-4 font-bold" style={{ fontFamily: 'Comic Sans MS, cursive' }}>
            🦄 Direct connection to Nova Lite magic! 🦄
          </p>
          
          <div className="flex items-center justify-center gap-6 mb-4">
            <StatusIndicator isConnected={true} mode="bedrock" />
            <div className="bg-gradient-to-r from-pink-200 to-purple-200 px-4 py-2 rounded-full border-2 border-pink-300 shadow-lg">
              <span className="text-purple-700 font-bold text-sm" style={{ fontFamily: 'Comic Sans MS, cursive' }}>
                ✨ Nova Lite Magic Activated! ✨
              </span>
            </div>
          </div>

          {/* Animated stars */}
          <div className="flex justify-center gap-4 text-3xl">
            <Star className="text-pink-400 animate-pulse" style={{ animationDelay: '0s' }} />
            <Star className="text-purple-400 animate-pulse" style={{ animationDelay: '0.2s' }} />
            <Star className="text-blue-400 animate-pulse" style={{ animationDelay: '0.4s' }} />
            <Star className="text-pink-400 animate-pulse" style={{ animationDelay: '0.6s' }} />
            <Star className="text-purple-400 animate-pulse" style={{ animationDelay: '0.8s' }} />
          </div>
        </div>

        <BubblegumChatInterface
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  )
}