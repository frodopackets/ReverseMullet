'use client'

import { useState } from 'react'
import { MedievalChatInterface, Message } from '@/components/chat/medieval-chat-interface'
import { StatusIndicator } from '@/components/chat/status-indicator'
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { Crown, ArrowLeft, Shield, Sword, Castle, Terminal, Heart } from 'lucide-react'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function MedievalPage() {
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
      // Transform the response to be more medieval
      const medievalResponse = {
        ...assistantMessage,
        content: transformToMedieval(assistantMessage.content)
      }
      setMessages(prev => [...prev, medievalResponse])
    } catch (error) {
      console.error('Failed to send message:', error)
      // Add error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        content: 'Alas! The ancient scrolls are temporarily sealed by dark magic! Pray try again, noble seeker. ⚔️',
        role: 'assistant',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const transformToMedieval = (content: string): string => {
    // Add medieval flair to responses
    const medievalPrefixes = [
      'Hark! ',
      'Verily, ',
      'By my troth, ',
      'Forsooth, ',
      'Prithee know that ',
      'Hear me well, noble seeker: ',
    ]
    
    const medievalSuffixes = [
      ' May this wisdom serve thee well! ⚔️',
      ' Thus speaks the ancient lore! 🏰',
      ' So it is written in the sacred scrolls! 📜',
      ' By royal decree, this knowledge is thine! 👑',
      ' May fortune favor thy quest! 🛡️',
    ]

    const prefix = medievalPrefixes[Math.floor(Math.random() * medievalPrefixes.length)]
    const suffix = medievalSuffixes[Math.floor(Math.random() * medievalSuffixes.length)]
    
    return prefix + content + suffix
  }



  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-100 via-slate-100 to-gray-100 py-4 px-4 relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-10 left-10 text-6xl animate-bounce text-stone-300/20" style={{ animationDelay: '0s' }}>🏰</div>
        <div className="absolute top-20 right-20 text-5xl animate-bounce text-stone-300/20" style={{ animationDelay: '0.5s' }}>⚔️</div>
        <div className="absolute bottom-20 left-20 text-7xl animate-bounce text-stone-300/20" style={{ animationDelay: '1s' }}>🐉</div>
        <div className="absolute bottom-10 right-10 text-4xl animate-bounce text-stone-300/20" style={{ animationDelay: '1.5s' }}>🛡️</div>
        <div className="absolute top-1/2 left-5 text-3xl animate-bounce text-stone-300/20" style={{ animationDelay: '2s' }}>👑</div>
        <div className="absolute top-1/3 right-5 text-5xl animate-bounce text-stone-300/20" style={{ animationDelay: '2.5s' }}>🗡️</div>
      </div>

      <div className="max-w-6xl mx-auto space-y-6 relative z-10">
        {/* Navigation Bar */}
        <div className="flex justify-between items-center py-4">
          <div className="flex gap-2">
            <Link href="/">
              <Button 
                variant="outline" 
                size="sm" 
                className="border-3 border-stone-600 text-stone-800 hover:bg-stone-100 rounded-lg shadow-lg font-bold"
                style={{ fontFamily: 'serif' }}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Return to Main Hall
              </Button>
            </Link>
            <Link href="/terminal">
              <Button 
                variant="outline" 
                size="sm" 
                className="border-3 border-green-600 text-green-700 hover:bg-green-100 rounded-lg shadow-lg font-bold"
                style={{ fontFamily: 'serif' }}
              >
                <Terminal className="h-4 w-4 mr-2" />
                Terminal
              </Button>
            </Link>
            <Link href="/bubblegum">
              <Button 
                variant="outline" 
                size="sm" 
                className="border-3 border-pink-600 text-pink-700 hover:bg-pink-100 rounded-lg shadow-lg font-bold"
                style={{ fontFamily: 'serif' }}
              >
                <Heart className="h-4 w-4 mr-2" />
                Bubblegum
              </Button>
            </Link>
          </div>
          <ThemeToggle />
        </div>
        
        {/* Main Content */}
        <div className="text-center mb-8">
          
          {/* Main title */}
          <div className="flex items-center justify-center gap-4 mb-4">
            <Castle className="h-12 w-12 text-stone-700 animate-pulse" />
            <h1 className="text-6xl font-bold bg-gradient-to-r from-stone-700 via-slate-600 to-stone-700 bg-clip-text text-transparent" style={{ fontFamily: 'serif' }}>
              Medieval Nova Lite Realm
            </h1>
            <Crown className="h-12 w-12 text-stone-700 animate-pulse" />
          </div>
          
          <p className="text-3xl text-stone-800 mb-4 font-bold" style={{ fontFamily: 'serif' }}>
            🏰 Where Nova Lite's Wisdom Serves Noble Seekers 🏰
          </p>
          
          <div className="flex items-center justify-center gap-6 mb-4">
            <StatusIndicator isConnected={true} mode="bedrock" />
            <div className="bg-gradient-to-r from-stone-200 to-slate-200 px-4 py-2 rounded-lg border-3 border-stone-500 shadow-lg">
              <span className="text-stone-800 font-bold text-sm" style={{ fontFamily: 'serif' }}>
                ⚔️ Nova Lite Royal Court Activated! ⚔️
              </span>
            </div>
          </div>

          {/* Animated medieval elements */}
          <div className="flex justify-center gap-4 text-4xl">
            <Shield className="text-stone-600 animate-pulse" style={{ animationDelay: '0s' }} />
            <Sword className="text-stone-600 animate-pulse" style={{ animationDelay: '0.2s' }} />
            <Crown className="text-amber-600 animate-pulse" style={{ animationDelay: '0.4s' }} />
            <Castle className="text-stone-600 animate-pulse" style={{ animationDelay: '0.6s' }} />
            <Shield className="text-stone-600 animate-pulse" style={{ animationDelay: '0.8s' }} />
          </div>
        </div>

        <MedievalChatInterface
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  )
}