'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Send, Bot, User } from 'lucide-react'
import { AgentIndicator } from './agent-indicator'
import { AgentLoadingState } from './agent-loading-state'
import { PricingResponseDisplay } from './pricing-response-display'
import { PricingResponseMetadata } from '@/types/pricing'
import { MessageFormatter } from './message-formatter'

export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  agent_type?: 'router' | 'aws_pricing' | 'general' | 'fallback_error' | 'orchestrator_fallback' | string
  intent_analysis?: {
    intent?: string
    confidence?: 'high' | 'medium' | 'low'
    fallback_applied?: boolean
    error_handled?: boolean
  }
  orchestration_metadata?: {
    context_messages_count?: number
    current_architecture_available?: boolean
    last_agent_used?: string
    context_summary?: string
  }
  pricing_metadata?: PricingResponseMetadata
}

interface SimpleChatInterfaceProps {
  messages: Message[]
  onSendMessage: (message: string) => void
  isLoading: boolean
  loadingStage?: 'analyzing' | 'routing' | 'processing' | 'responding'
  currentAgent?: string
}

export function SimpleChatInterface({
  messages,
  onSendMessage,
  isLoading,
  loadingStage = 'analyzing',
  currentAgent
}: SimpleChatInterfaceProps) {
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
    <Card className="w-full mx-auto bg-card border shadow-lg">
      {/* Header */}
      <div className="border-b bg-muted/50 p-4">
        <div className="flex items-center gap-3">
          <Bot className="h-6 w-6 text-primary" />
          <div>
            <h2 className="font-semibold text-lg">Intelligent AWS Assistant</h2>
            <p className="text-sm text-muted-foreground">
              AI-powered routing • AWS pricing analysis • General knowledge
            </p>
          </div>
        </div>
      </div>

      {/* Messages Area - Made much taller */}
      <div ref={messagesContainerRef} className="h-[600px] overflow-y-auto p-6">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <Bot className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-xl font-semibold mb-2">Welcome to Your Intelligent AWS Assistant</h3>
            <p className="text-muted-foreground mb-4">
              I can help with AWS pricing analysis, cost optimization, and general questions.
            </p>
            <div className="text-sm text-muted-foreground space-y-1">
              <p>• Ask about AWS service costs and pricing</p>
              <p>• Get architecture cost estimates</p>
              <p>• Receive cost optimization recommendations</p>
              <p>• General technical questions and guidance</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div key={message.id} className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {message.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                )}
                <div className={`${
                  message.role === 'user' 
                    ? 'max-w-md lg:max-w-xl text-right' 
                    : message.agent_type === 'aws_pricing' && message.pricing_metadata
                      ? 'max-w-3xl lg:max-w-5xl'
                      : 'max-w-2xl lg:max-w-3xl'
                }`}>
                  <div className={`px-5 py-3 rounded-lg ${
                    message.role === 'user' 
                      ? 'bg-primary text-primary-foreground' 
                      : 'bg-muted'
                  }`}>
                    {message.role === 'user' ? (
                      <p className="text-base leading-relaxed whitespace-pre-wrap">{message.content}</p>
                    ) : (
                      <MessageFormatter content={message.content} className="text-base" />
                    )}
                    <div className={`flex items-center justify-between mt-2 ${
                      message.role === 'user' ? 'flex-row-reverse' : ''
                    }`}>
                      <p className={`text-xs ${
                        message.role === 'user' ? 'text-primary-foreground/70' : 'text-muted-foreground'
                      }`}>
                        {formatTimestamp(message.timestamp)}
                      </p>
                      {message.role === 'assistant' && (
                        <AgentIndicator 
                          agentType={message.agent_type} 
                          intentAnalysis={message.intent_analysis}
                          size="sm"
                        />
                      )}
                    </div>
                  </div>
                  
                  {/* Specialized Pricing Response Display */}
                  {message.role === 'assistant' && message.agent_type === 'aws_pricing' && message.pricing_metadata && (
                    <PricingResponseDisplay metadata={message.pricing_metadata} />
                  )}
                </div>
                {message.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                    <User className="h-4 w-4 text-primary-foreground" />
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <AgentLoadingState stage={loadingStage} currentAgent={currentAgent} />
            )}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area - Made larger */}
      <div className="border-t p-6">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about AWS costs, architecture, or anything else..."
            disabled={isLoading}
            className="flex-1 text-base py-6 px-4"
          />
          <Button type="submit" disabled={!input.trim() || isLoading} className="px-6">
            <Send className="h-5 w-5" />
          </Button>
        </form>
      </div>
    </Card>
  )
}