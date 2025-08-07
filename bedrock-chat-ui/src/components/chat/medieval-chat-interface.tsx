'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Send, Crown, Shield, Sword } from 'lucide-react'

export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
}

interface MedievalChatInterfaceProps {
  messages: Message[]
  onSendMessage: (message: string) => void
  isLoading: boolean
  selectedKnowledgeBase?: string
}

export function MedievalChatInterface({
  messages,
  onSendMessage,
  isLoading,
  selectedKnowledgeBase
}: MedievalChatInterfaceProps) {
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
    return timestamp.toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <Card className="w-full max-w-4xl mx-auto bg-gradient-to-b from-amber-50 via-orange-50 to-red-50 border-4 border-amber-600 shadow-2xl shadow-amber-900/50 rounded-none relative overflow-hidden">
      {/* Medieval Header with Castle Battlements */}
      <div className="bg-gradient-to-r from-amber-800 via-yellow-700 to-amber-800 relative overflow-hidden">
        {/* Battlements */}
        <div className="absolute top-0 left-0 right-0 h-4 bg-amber-900 flex">
          {Array.from({ length: 20 }).map((_, i) => (
            <div key={i} className={`flex-1 ${i % 2 === 0 ? 'bg-amber-800' : 'bg-amber-900'}`}></div>
          ))}
        </div>
        
        <div className="pt-6 pb-4 px-6 relative">
          <div className="flex items-center justify-center gap-4 mb-2">
            <Crown className="h-8 w-8 text-yellow-300 animate-pulse" />
            <h2 className="text-yellow-100 font-bold text-2xl tracking-wide text-center" style={{ fontFamily: 'serif' }}>
              ⚔️ Royal Knowledge Sanctum ⚔️
            </h2>
            <Shield className="h-8 w-8 text-yellow-300 animate-pulse" />
          </div>
          {selectedKnowledgeBase && (
            <div className="text-center">
              <span className="bg-amber-900/50 text-yellow-200 px-4 py-1 rounded-full text-sm font-medium backdrop-blur-sm border border-yellow-600">
                🏰 Consulting the {selectedKnowledgeBase} Scrolls 🏰
              </span>
            </div>
          )}
          {/* Decorative elements */}
          <div className="absolute top-4 left-4 text-yellow-400/60 text-2xl">🗡️</div>
          <div className="absolute top-6 right-6 text-yellow-400/60 text-2xl">🛡️</div>
          <div className="absolute bottom-2 left-8 text-yellow-400/60 text-xl">⚔️</div>
          <div className="absolute bottom-2 right-8 text-yellow-400/60 text-xl">🏰</div>
        </div>
      </div>

      {/* Messages Area */}
      <div ref={messagesContainerRef} className="h-96 overflow-y-auto p-6 bg-gradient-to-b from-amber-25 to-orange-25 relative">
        {/* Parchment texture overlay */}
        <div className="absolute inset-0 opacity-10 bg-gradient-to-br from-amber-200 via-transparent to-amber-300 pointer-events-none"></div>
        
        {messages.length === 0 ? (
          <div className="text-center py-12 relative z-10">
            <div className="text-6xl mb-4 animate-bounce">🐉</div>
            <h3 className="text-2xl font-bold text-amber-800 mb-2" style={{ fontFamily: 'serif' }}>
              Hail and Well Met, Noble Seeker!
            </h3>
            <p className="text-amber-700 text-lg mb-4" style={{ fontFamily: 'serif' }}>
              The ancient scrolls await thy queries. Speak, and wisdom shall be thine!
            </p>
            <div className="flex justify-center gap-4 mt-4 text-3xl">
              <span className="animate-bounce" style={{ animationDelay: '0.1s' }}>🏰</span>
              <span className="animate-bounce" style={{ animationDelay: '0.2s' }}>⚔️</span>
              <span className="animate-bounce" style={{ animationDelay: '0.3s' }}>🛡️</span>
              <span className="animate-bounce" style={{ animationDelay: '0.4s' }}>🗡️</span>
              <span className="animate-bounce" style={{ animationDelay: '0.5s' }}>👑</span>
            </div>
          </div>
        ) : (
          <div className="space-y-6 relative z-10">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs lg:max-w-md px-4 py-3 relative ${
                  message.role === 'user' 
                    ? 'bg-gradient-to-br from-blue-800 to-blue-900 text-yellow-100 shadow-lg shadow-blue-900/50 border-2 border-blue-600' 
                    : 'bg-gradient-to-br from-amber-100 to-orange-100 text-amber-900 shadow-lg shadow-amber-500/50 border-2 border-amber-400'
                } rounded-lg`}>
                  
                  {/* Medieval scroll corners */}
                  <div className={`absolute -top-1 -left-1 w-3 h-3 ${
                    message.role === 'user' ? 'bg-blue-700' : 'bg-amber-200'
                  } transform rotate-45`}></div>
                  <div className={`absolute -top-1 -right-1 w-3 h-3 ${
                    message.role === 'user' ? 'bg-blue-700' : 'bg-amber-200'
                  } transform rotate-45`}></div>
                  <div className={`absolute -bottom-1 -left-1 w-3 h-3 ${
                    message.role === 'user' ? 'bg-blue-700' : 'bg-amber-200'
                  } transform rotate-45`}></div>
                  <div className={`absolute -bottom-1 -right-1 w-3 h-3 ${
                    message.role === 'user' ? 'bg-blue-700' : 'bg-amber-200'
                  } transform rotate-45`}></div>

                  {/* Avatar */}
                  <div className={`absolute ${
                    message.role === 'user' ? 'right-[-50px] top-0' : 'left-[-50px] top-0'
                  }`}>
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center text-xl shadow-lg border-2 ${
                      message.role === 'user' 
                        ? 'bg-gradient-to-br from-blue-600 to-blue-800 border-blue-400' 
                        : 'bg-gradient-to-br from-amber-400 to-amber-600 border-amber-300'
                    }`}>
                      {message.role === 'user' ? '🤴' : '🧙‍♂️'}
                    </div>
                  </div>

                  <div className="space-y-2 relative z-10">
                    <div className={`flex items-center gap-2 mb-2 ${
                      message.role === 'user' ? 'text-yellow-200' : 'text-amber-700'
                    }`}>
                      {message.role === 'user' ? (
                        <>
                          <Sword className="h-4 w-4" />
                          <span className="font-bold text-sm" style={{ fontFamily: 'serif' }}>Noble Seeker</span>
                        </>
                      ) : (
                        <>
                          <Crown className="h-4 w-4" />
                          <span className="font-bold text-sm" style={{ fontFamily: 'serif' }}>Royal Sage</span>
                        </>
                      )}
                    </div>
                    <p className="text-sm leading-relaxed" style={{ fontFamily: 'serif' }}>
                      {message.content}
                    </p>
                    <div className={`text-xs flex items-center gap-1 mt-2 ${
                      message.role === 'user' ? 'text-yellow-300/80' : 'text-amber-600/80'
                    }`}>
                      <Shield className="h-3 w-3" />
                      <span>{formatTimestamp(message.timestamp)}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-xs lg:max-w-md px-4 py-3 bg-gradient-to-br from-purple-100 to-purple-200 text-purple-800 shadow-lg shadow-purple-300/50 border-2 border-purple-400 rounded-lg relative">
                  {/* Scroll corners */}
                  <div className="absolute -top-1 -left-1 w-3 h-3 bg-purple-200 transform rotate-45"></div>
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-purple-200 transform rotate-45"></div>
                  <div className="absolute -bottom-1 -left-1 w-3 h-3 bg-purple-200 transform rotate-45"></div>
                  <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-purple-200 transform rotate-45"></div>
                  
                  <div className="absolute left-[-50px] top-0">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-400 to-purple-600 border-2 border-purple-300 flex items-center justify-center text-xl shadow-lg animate-pulse">
                      🧙‍♂️
                    </div>
                  </div>
                  <div className="flex items-center gap-2 relative z-10" style={{ fontFamily: 'serif' }}>
                    <Crown className="h-4 w-4 text-purple-600" />
                    <span className="font-bold">The Royal Sage consults the ancient scrolls</span>
                    <div className="flex gap-1 ml-2">
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-2xl animate-spin">✨</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-gradient-to-r from-amber-200 via-yellow-200 to-amber-200 border-t-4 border-amber-600 relative">
        {/* Decorative border */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-amber-600 via-yellow-500 to-amber-600"></div>
        
        <form onSubmit={handleSubmit} className="flex gap-3 p-4">
          <div className="flex-1 relative">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Speak thy query to the Royal Sage... ⚔️"
              disabled={isLoading}
              className="w-full bg-amber-50 border-3 border-amber-500 rounded-lg px-6 py-3 text-amber-900 placeholder:text-amber-600 focus:border-amber-700 focus:ring-4 focus:ring-amber-300 shadow-lg text-lg"
              style={{ fontFamily: 'serif' }}
            />
            <div className="absolute right-4 top-1/2 transform -translate-y-1/2 text-amber-600">
              🏰
            </div>
          </div>
          <Button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-700 hover:to-amber-800 text-yellow-100 px-6 py-3 rounded-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 font-bold border-2 border-amber-500"
            style={{ fontFamily: 'serif' }}
          >
            <Send className="h-5 w-5 mr-2" />
            Send Forth! ⚔️
          </Button>
        </form>
      </div>
    </Card>
  )
}