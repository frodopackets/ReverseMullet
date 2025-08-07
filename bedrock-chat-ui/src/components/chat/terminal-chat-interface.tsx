'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Send, Terminal, User, Bot } from 'lucide-react'

export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
}

interface TerminalChatInterfaceProps {
  messages: Message[]
  onSendMessage: (message: string) => void
  isLoading: boolean
  selectedKnowledgeBase?: string
}

export function TerminalChatInterface({
  messages,
  onSendMessage,
  isLoading,
  selectedKnowledgeBase
}: TerminalChatInterfaceProps) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
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
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <Card className="w-full max-w-4xl mx-auto bg-black border-green-500/30 shadow-lg shadow-green-500/10">
      {/* Terminal Header */}
      <div className="flex items-center gap-2 p-3 border-b border-green-500/30 bg-gray-900">
        <Terminal className="h-4 w-4 text-green-400" />
        <span className="text-green-400 font-mono text-sm">
          bedrock-kb-chat@aws:~$ 
          {selectedKnowledgeBase && (
            <span className="text-green-300 ml-2">
              connected to [{selectedKnowledgeBase}]
            </span>
          )}
        </span>
      </div>

      {/* Messages Area */}
      <div className="h-96 overflow-y-auto p-4 bg-black font-mono text-sm">
        {messages.length === 0 ? (
          <div className="text-green-400/70 text-center py-8">
            <Terminal className="h-12 w-12 mx-auto mb-4 text-green-500/50" />
            <p className="text-green-400">Terminal ready. Type your query below.</p>
            <p className="text-green-400/60 text-xs mt-2">
              {selectedKnowledgeBase 
                ? `Connected to knowledge base: ${selectedKnowledgeBase}`
                : 'No knowledge base selected'
              }
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div key={message.id} className="space-y-1">
                {/* Timestamp and role indicator */}
                <div className="flex items-center gap-2 text-green-500/70 text-xs">
                  <span>[{formatTimestamp(message.timestamp)}]</span>
                  {message.role === 'user' ? (
                    <span className="flex items-center gap-1">
                      <User className="h-3 w-3" />
                      user@terminal
                    </span>
                  ) : (
                    <span className="flex items-center gap-1">
                      <Bot className="h-3 w-3" />
                      bedrock-assistant
                    </span>
                  )}
                </div>
                
                {/* Message content */}
                <div className={`pl-4 border-l-2 ${
                  message.role === 'user' 
                    ? 'border-blue-500/50 text-blue-300' 
                    : 'border-green-500/50 text-green-300'
                }`}>
                  <pre className="whitespace-pre-wrap font-mono text-sm leading-relaxed">
                    {message.content}
                  </pre>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-green-500/70 text-xs">
                  <span>[{formatTimestamp(new Date())}]</span>
                  <span className="flex items-center gap-1">
                    <Bot className="h-3 w-3" />
                    bedrock-assistant
                  </span>
                </div>
                <div className="pl-4 border-l-2 border-green-500/50 text-green-300">
                  <span className="animate-pulse">Processing query...</span>
                  <span className="animate-pulse ml-2">█</span>
                </div>
              </div>
            )}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-green-500/30 bg-gray-900">
        <form onSubmit={handleSubmit} className="flex gap-2 p-3">
          <div className="flex-1 flex items-center gap-2">
            <span className="text-green-400 font-mono text-sm">$</span>
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Enter your query..."
              disabled={isLoading}
              className="flex-1 bg-black border-green-500/30 text-green-300 placeholder:text-green-500/50 font-mono focus:border-green-400 focus:ring-green-400/20"
            />
          </div>
          <Button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="bg-green-600 hover:bg-green-700 text-black font-mono"
          >
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </Card>
  )
}