'use client'

import { useState } from 'react'
import { SimpleChatInterface, Message } from '@/components/chat/simple-chat-interface'
import { StatusIndicator } from '@/components/chat/status-indicator'
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { Button } from '@/components/ui/button'
import { Terminal, Heart, Crown, LogOut, User } from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '@/contexts/auth-context'
import { parsePricingResponse } from '@/utils/pricing-parser'
import { API_CONFIG, API_ENDPOINTS } from '@/config/api'

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [loadingStage, setLoadingStage] = useState<'analyzing' | 'routing' | 'processing' | 'responding'>('analyzing')
  const [currentAgent, setCurrentAgent] = useState<string>()
  const { user, signOut, getAuthToken } = useAuth()

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
    setLoadingStage('analyzing')
    setCurrentAgent(undefined)

    try {
      // Simulate loading stages for better UX
      setTimeout(() => setLoadingStage('routing'), 500)
      setTimeout(() => setLoadingStage('processing'), 1000)
      setTimeout(() => setLoadingStage('responding'), 2000)

      // Get API URL from configuration
      const apiUrl = API_CONFIG.getApiUrl()
      console.log('Using API URL:', apiUrl)
      
      const endpoint = `${apiUrl}${API_ENDPOINTS.ROUTER_CHAT}`
      console.log('Making request to:', endpoint)
      
      // For ALB authentication, we use cookies instead of Authorization headers
      // The ALB handles authentication and passes user info to the backend
      const fetchOptions: RequestInit = {
        method: 'POST',
        credentials: 'include', // Important: Include cookies for ALB session
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: content }),
      }

      // For Amplify mode, add Authorization header
      if (process.env.NEXT_PUBLIC_AUTH_MODE === 'amplify') {
        const authToken = await getAuthToken()
        if (authToken) {
          (fetchOptions.headers as Record<string, string>)['Authorization'] = `Bearer ${authToken}`
        }
      }

      const response = await fetch(endpoint, fetchOptions)

      if (!response.ok) {
        throw new Error('Failed to get response from API')
      }

      const assistantMessage = await response.json()
      
      // Set current agent based on response
      if (assistantMessage.agent_type) {
        setCurrentAgent(assistantMessage.agent_type)
      }
      
      // Parse pricing metadata if this is a pricing response
      const pricingMetadata = parsePricingResponse(assistantMessage.content, assistantMessage.agent_type)
      
      // Convert timestamp string back to Date object and ensure all fields are present
      const messageWithDateTimestamp: Message = {
        ...assistantMessage,
        timestamp: new Date(assistantMessage.timestamp),
        agent_type: assistantMessage.agent_type,
        intent_analysis: assistantMessage.intent_analysis,
        orchestration_metadata: assistantMessage.orchestration_metadata,
        pricing_metadata: pricingMetadata
      }
      setMessages(prev => [...prev, messageWithDateTimestamp])
    } catch (error) {
      console.error('Failed to send message:', error)
      
      // Generate context-aware error message
      const isPricingQuery = content.toLowerCase().includes('cost') || 
                           content.toLowerCase().includes('price') || 
                           content.toLowerCase().includes('pricing') ||
                           content.toLowerCase().includes('budget')
      
      let errorContent = 'I apologize, but I encountered an error while processing your request.'
      
      if (isPricingQuery) {
        errorContent += `

**For AWS Pricing Questions:**
Since you appear to be asking about AWS costs, here are some alternatives while I resolve this issue:

1. **AWS Calculator** - Visit https://calculator.aws/ for official pricing
2. **Try rephrasing** - Be more specific about the AWS services you're interested in
3. **Try again** - This may be a temporary connectivity issue

**Example queries that work well:**
- "What's the monthly cost of a t3.small EC2 instance?"
- "RDS pricing for MySQL database"
- "S3 storage costs for 100GB"

Please try your question again!`
      } else {
        errorContent += `

**What you can try:**
1. **Rephrase your question** - Try asking in a different way
2. **Be more specific** - Include more details about what you need
3. **Try again** - This may be a temporary system issue

**I can help with:**
- AWS service questions and best practices
- Cost analysis and pricing information  
- Architecture recommendations
- Technical guidance

Please try your question again!`
      }
      
      // Add enhanced error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        content: errorContent,
        role: 'assistant',
        timestamp: new Date(),
        agent_type: 'enhanced_error_handler',
        intent_analysis: {
          intent: isPricingQuery ? 'aws_pricing_error' : 'system_error',
          confidence: 'high',
          error_handled: true
        }
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      setLoadingStage('analyzing')
      setCurrentAgent(undefined)
    }
  }

  return (
    <div className="min-h-screen bg-background py-4 px-4">
      <div className="max-w-7xl mx-auto space-y-4">
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
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <User className="h-4 w-4" />
              <span>{user?.email || user?.username}</span>
            </div>
            <Button variant="outline" size="sm" onClick={signOut}>
              <LogOut className="h-4 w-4 mr-2" />
              Sign Out
            </Button>
            <ThemeToggle />
          </div>
        </div>
        
        {/* Compact Header */}
        <div className="text-center mb-4">
          <h1 className="text-2xl font-bold text-foreground mb-1">
            AI-First AWS Pricing Agent
          </h1>
          <p className="text-sm text-muted-foreground mb-2">
            Real-time AWS pricing data via MCP integration
          </p>
          <div className="flex items-center justify-center gap-3">
            <StatusIndicator isConnected={true} mode="router" />
            <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
              ✅ Real-Time Data
            </span>
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
              🧠 AI-First
            </span>
            <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
              ⚡ MCP Integration
            </span>
          </div>
        </div>
        
        <SimpleChatInterface
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          loadingStage={loadingStage}
          currentAgent={currentAgent}
        />
      </div>
    </div>
  )
}