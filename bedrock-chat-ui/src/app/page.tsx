'use client'

import { useState, useEffect } from 'react'
import { ChatInterface, Message } from '@/components/chat/chat-interface'
import { KnowledgeBaseSelector, KnowledgeBase } from '@/components/chat/knowledge-base-selector'
import { StatusIndicator } from '@/components/chat/status-indicator'
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { Button } from '@/components/ui/button'
import { sendMessage, getKnowledgeBases } from '@/lib/mock-api'
import { Terminal, Heart, Crown } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [selectedKnowledgeBase, setSelectedKnowledgeBase] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    // Load knowledge bases on component mount
    const loadKnowledgeBases = async () => {
      try {
        const kbs = await getKnowledgeBases()
        setKnowledgeBases(kbs)
        // Auto-select the first active knowledge base
        const firstActive = kbs.find(kb => kb.status === 'active')
        if (firstActive) {
          setSelectedKnowledgeBase(firstActive.id)
        }
      } catch (error) {
        console.error('Failed to load knowledge bases:', error)
      }
    }

    loadKnowledgeBases()
  }, [])

  const handleSendMessage = async (content: string) => {
    if (!selectedKnowledgeBase) {
      alert('Please select a knowledge base first')
      return
    }

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
      // Get AI response
      const assistantMessage = await sendMessage(content, selectedKnowledgeBase)
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

  const handleKnowledgeBaseSelect = (knowledgeBaseId: string) => {
    setSelectedKnowledgeBase(knowledgeBaseId)
    // Clear messages when switching knowledge bases
    setMessages([])
  }

  const selectedKB = knowledgeBases.find(kb => kb.id === selectedKnowledgeBase)

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
            Bedrock Knowledge Base Chat
          </h1>
          <p className="text-muted-foreground mb-4">
            Connect with your AWS Bedrock Knowledge Bases and get intelligent responses
          </p>
          <StatusIndicator isConnected={true} mode="mock" />
        </div>

        <ChatInterface
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          selectedKnowledgeBase={selectedKB?.name}
        />

        <KnowledgeBaseSelector
          knowledgeBases={knowledgeBases}
          selectedKnowledgeBase={selectedKnowledgeBase}
          onSelect={handleKnowledgeBaseSelect}
        />
      </div>
    </div>
  )
}