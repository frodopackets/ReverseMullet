'use client'

import { useState, useEffect } from 'react'
import { TerminalChatInterface, Message } from '@/components/chat/terminal-chat-interface'
import { TerminalKnowledgeBaseSelector, KnowledgeBase } from '@/components/chat/terminal-knowledge-base-selector'
import { StatusIndicator } from '@/components/chat/status-indicator'
import { ThemeToggle } from '@/components/ui/theme-toggle'
import { sendMessage, getKnowledgeBases } from '@/lib/mock-api'
import { Terminal, ArrowLeft, Heart, Crown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function TerminalPage() {
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
        content: 'ERROR: Connection to knowledge base failed. Please try again.',
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
              bedrock-kb-terminal
            </h1>
          </div>
          <p className="text-green-500/70 mb-4 font-mono text-sm">
            AWS Bedrock Knowledge Base Terminal Interface v1.0.0
          </p>
          <div className="flex items-center justify-center gap-4">
            <StatusIndicator isConnected={true} mode="mock" />
            <span className="text-green-500/60 font-mono text-xs">
              [MOCK MODE] - Simulated responses enabled
            </span>
          </div>
        </div>

        <TerminalChatInterface
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          selectedKnowledgeBase={selectedKB?.name}
        />

        <TerminalKnowledgeBaseSelector
          knowledgeBases={knowledgeBases}
          selectedKnowledgeBase={selectedKnowledgeBase}
          onSelect={handleKnowledgeBaseSelect}
        />
      </div>
    </div>
  )
}