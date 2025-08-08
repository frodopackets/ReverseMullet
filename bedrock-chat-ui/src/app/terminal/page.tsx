'use client'

import { useState } from 'react'
import { TerminalChatInterface, Message } from '@/components/chat/terminal-chat-interface'
import { StatusIndicator } from '@/components/chat/status-indicator'
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { Terminal, ArrowLeft, Heart, Crown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function TerminalPage() {
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
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://r2r3oacvc3.execute-api.us-east-1.amazonaws.com/dev'
      const endpoint = `${apiUrl}/chat`
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
      // Convert timestamp string back to Date object
      const messageWithDateTimestamp = {
        ...assistantMessage,
        timestamp: new Date(assistantMessage.timestamp)
      }
      setMessages(prev => [...prev, messageWithDateTimestamp])
    } catch (error) {
      console.error('Failed to send message:', error)
      // Add error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        content: 'ERROR: Connection to Nova Lite failed. Please try again.',
        role: 'assistant',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-black py-4 px-4">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Navigation Bar */}
        <div className="flex justify-between items-center py-4">
          <div className="flex gap-2">
            <Link href="/">
              <Button variant="outline" size="sm" className="border-green-500/30 text-green-400 hover:bg-green-500/10">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to UI Mode
              </Button>
            </Link>
            <Link href="/bubblegum">
              <Button variant="outline" size="sm" className="border-pink-300 text-pink-400 hover:bg-pink-500/10">
                <Heart className="h-4 w-4 mr-2" />
                Bubblegum
              </Button>
            </Link>
            <Link href="/medieval">
              <Button variant="outline" size="sm" className="border-stone-500 text-stone-400 hover:bg-stone-500/10">
                <Crown className="h-4 w-4 mr-2" />
                Medieval
              </Button>
            </Link>
          </div>
          <ThemeToggle />
        </div>
        
        {/* Main Content */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Terminal className="h-8 w-8 text-green-400" />
            <h1 className="text-3xl font-bold text-green-400 font-mono">
              bedrock-nova-lite-terminal
            </h1>
          </div>
          <p className="text-green-500/70 mb-4 font-mono text-sm">
            AWS Bedrock Nova Lite Terminal Interface v1.0.0
          </p>
          <div className="flex items-center justify-center gap-4">
            <StatusIndicator isConnected={true} mode="bedrock" />
            <span className="text-green-500/60 font-mono text-xs">
              [NOVA LITE] - Direct Bedrock connection active
            </span>
          </div>
        </div>

        <TerminalChatInterface
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  )
}