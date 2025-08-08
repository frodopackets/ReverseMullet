'use client'

import { useState } from 'react'
import { SimpleChatInterface, Message } from '@/components/chat/simple-chat-interface'
import { StatusIndicator } from '@/components/chat/status-indicator'
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { Button } from '@/components/ui/button'
import { Terminal, Heart, Crown } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
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
        content: 'Sorry, I encountered an error while processing your request. Please try again.',
        role: 'assistant',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background py-4 px-4">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Navigation Bar */}
        <div className="flex justify-between items-center py-4">
          <div className="flex gap-2">
            <Link href="/terminal">
              <Button variant="outline" size="sm">
                <Terminal className="h-4 w-4 mr-2" />
                Terminal Mode
              </Button>
            </Link>
            <Link href="/bubblegum">
              <Button variant="outline" size="sm" className="border-pink-300 text-pink-600 hover:bg-pink-50">
                <Heart className="h-4 w-4 mr-2" />
                Bubblegum Mode
              </Button>
            </Link>
            <Link href="/medieval">
              <Button variant="outline" size="sm" className="border-stone-500 text-stone-700 hover:bg-stone-50">
                <Crown className="h-4 w-4 mr-2" />
                Medieval Mode
              </Button>
            </Link>
          </div>
          <ThemeToggle />
        </div>
        
        {/* Main Content */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            AWS Bedrock Nova Lite Chat
          </h1>
          <p className="text-muted-foreground mb-4">
            Direct connection to AWS Bedrock Nova Lite model for intelligent conversations
          </p>
          <StatusIndicator isConnected={true} mode="bedrock" />
        </div>

        <SimpleChatInterface
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  )
}