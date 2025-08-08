'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Send, Sparkles, Heart, Star } from 'lucide-react'

export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
}

interface BubblegumChatInterfaceProps {
  messages: Message[]
  onSendMessage: (message: string) => void
  isLoading: boolean
  selectedKnowledgeBase?: string
}

export function BubblegumChatInterface({
  messages,
  onSendMessage,
  isLoading,
  selectedKnowledgeBase
}: BubblegumChatInterfaceProps) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    if (messagesContainerRef.current) {
      const container = messagesContainerRef.current
      container.scrollTo({
        top: container.scrollHeight,
        behavior: 'smooth'
      })
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim())
      setInput('')
    }
  }

  const formatTimestamp = (timestamp: Date) => {
    // Ensure timestamp is a Date object
    const date = timestamp instanceof Date ? timestamp : new Date(timestamp)
    return date.toLocaleTimeString('en-US', { 
      hour12: true,
      hour: 'numeric',
      minute: '2-digit'
    })
  }

  return (
    <Card className="w-full max-w-4xl mx-auto bg-gradient-to-br from-pink-50 via-purple-50 to-blue-50 border-4 border-pink-300 shadow-2xl shadow-pink-200/50 rounded-3xl overflow-hidden">
      {/* Cute Header */}
      <div className="bg-gradient-to-r from-pink-400 via-purple-400 to-blue-400 p-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-white/20"></div>
        <div className="relative flex items-center justify-center gap-3">
          <Sparkles className="h-6 w-6 text-white animate-pulse" />
          <h2 className="text-white font-bold text-xl tracking-wide" style={{ fontFamily: 'Comic Sans MS, cursive' }}>
            ✨ Magical Knowledge Chat ✨
          </h2>
          <Heart className="h-6 w-6 text-white animate-bounce" />
        </div>
        {selectedKnowledgeBase && (
          <div className="text-center mt-2">
            <span className="bg-white/30 text-white px-3 py-1 rounded-full text-sm font-medium backdrop-blur-sm">
              💖 Connected to: {selectedKnowledgeBase} 💖
            </span>
          </div>
        )}
        {!selectedKnowledgeBase && (
          <div className="text-center mt-2">
            <span className="bg-white/30 text-white px-3 py-1 rounded-full text-sm font-medium backdrop-blur-sm">
              💖 Direct Nova Lite Magic Active! 💖
            </span>
          </div>
        )}
        {/* Floating decorations */}
        <div className="absolute top-2 left-4 text-white/60 animate-bounce" style={{ animationDelay: '0.5s' }}>⭐</div>
        <div className="absolute top-4 right-8 text-white/60 animate-bounce" style={{ animationDelay: '1s' }}>🌟</div>
        <div className="absolute bottom-2 left-8 text-white/60 animate-bounce" style={{ animationDelay: '1.5s' }}>✨</div>
        <div className="absolute bottom-4 right-4 text-white/60 animate-bounce" style={{ animationDelay: '2s' }}>💫</div>
      </div>

      {/* Messages Area */}
      <div ref={messagesContainerRef} className="h-96 overflow-y-auto p-6 bg-gradient-to-b from-pink-25 to-purple-25">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4 animate-bounce">🦄</div>
            <h3 className="text-2xl font-bold text-pink-600 mb-2" style={{ fontFamily: 'Comic Sans MS, cursive' }}>
              Welcome to your magical chat! 
            </h3>
            <p className="text-purple-500 text-lg" style={{ fontFamily: 'Comic Sans MS, cursive' }}>
              Ask me anything and I&apos;ll help you with sparkles! ✨
            </p>
            <div className="flex justify-center gap-4 mt-4 text-2xl">
              <span className="animate-bounce" style={{ animationDelay: '0.1s' }}>🌈</span>
              <span className="animate-bounce" style={{ animationDelay: '0.2s' }}>🎀</span>
              <span className="animate-bounce" style={{ animationDelay: '0.3s' }}>🌸</span>
              <span className="animate-bounce" style={{ animationDelay: '0.4s' }}>🦋</span>
              <span className="animate-bounce" style={{ animationDelay: '0.5s' }}>🌺</span>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl relative ${
                  message.role === 'user' 
                    ? 'bg-gradient-to-r from-pink-400 to-purple-400 text-white shadow-lg shadow-pink-200' 
                    : 'bg-gradient-to-r from-blue-100 to-purple-100 text-purple-800 shadow-lg shadow-blue-200'
                }`}>
                  {/* Message bubble tail */}
                  <div className={`absolute top-3 w-0 h-0 ${
                    message.role === 'user'
                      ? 'right-[-8px] border-l-[8px] border-l-purple-400 border-t-[8px] border-t-transparent border-b-[8px] border-b-transparent'
                      : 'left-[-8px] border-r-[8px] border-r-purple-100 border-t-[8px] border-t-transparent border-b-[8px] border-b-transparent'
                  }`}></div>
                  
                  {/* Avatar */}
                  <div className={`absolute ${
                    message.role === 'user' ? 'right-[-50px] top-0' : 'left-[-50px] top-0'
                  }`}>
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-pink-300 to-purple-300 flex items-center justify-center text-lg shadow-lg">
                      {message.role === 'user' ? '👧' : '🤖'}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <p className="text-sm font-medium leading-relaxed" style={{ fontFamily: 'Comic Sans MS, cursive' }}>
                      {message.content}
                    </p>
                    <div className={`text-xs flex items-center gap-1 ${
                      message.role === 'user' ? 'text-white/80' : 'text-purple-600/80'
                    }`}>
                      <Star className="h-3 w-3" />
                      <span>{formatTimestamp(message.timestamp)}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-xs lg:max-w-md px-4 py-3 rounded-2xl bg-gradient-to-r from-yellow-100 to-pink-100 text-purple-800 shadow-lg shadow-yellow-200 relative">
                  <div className="absolute left-[-8px] top-3 w-0 h-0 border-r-[8px] border-r-pink-100 border-t-[8px] border-t-transparent border-b-[8px] border-b-transparent"></div>
                  <div className="absolute left-[-50px] top-0">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-yellow-300 to-pink-300 flex items-center justify-center text-lg shadow-lg animate-pulse">
                      🤖
                    </div>
                  </div>
                  <div className="flex items-center gap-2" style={{ fontFamily: 'Comic Sans MS, cursive' }}>
                    <span>Thinking with sparkles</span>
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-lg animate-spin">✨</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-gradient-to-r from-pink-100 via-purple-100 to-blue-100 border-t-4 border-pink-200">
        <form onSubmit={handleSubmit} className="flex gap-3 p-4">
          <div className="flex-1 relative">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your magical question here... ✨"
              disabled={isLoading}
              className="w-full bg-white border-3 border-pink-300 rounded-full px-6 py-3 text-purple-800 placeholder:text-purple-400 focus:border-purple-400 focus:ring-4 focus:ring-purple-200 shadow-lg text-lg"
              style={{ fontFamily: 'Comic Sans MS, cursive' }}
            />
            <div className="absolute right-4 top-1/2 transform -translate-y-1/2 text-pink-400">
              💖
            </div>
          </div>
          <Button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="bg-gradient-to-r from-pink-400 to-purple-400 hover:from-pink-500 hover:to-purple-500 text-white px-6 py-3 rounded-full shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 font-bold"
            style={{ fontFamily: 'Comic Sans MS, cursive' }}
          >
            <Send className="h-5 w-5 mr-2" />
            Send! 🚀
          </Button>
        </form>
      </div>
    </Card>
  )
}