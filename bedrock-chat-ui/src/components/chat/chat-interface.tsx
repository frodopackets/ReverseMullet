'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Card } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Send, Bot, User, Database } from 'lucide-react'
import { format } from 'date-fns'

export interface Message {
    id: string
    content: string
    role: 'user' | 'assistant'
    timestamp: Date
    knowledgeBase?: string
}

interface ChatInterfaceProps {
    onSendMessage: (message: string) => Promise<void>
    messages: Message[]
    isLoading: boolean
    selectedKnowledgeBase?: string
}

export function ChatInterface({
    onSendMessage,
    messages,
    isLoading,
    selectedKnowledgeBase
}: ChatInterfaceProps) {
    const [input, setInput] = useState('')
    const scrollAreaRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        if (scrollAreaRef.current) {
            scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
        }
    }, [messages])

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!input.trim() || isLoading) return

        const message = input.trim()
        setInput('')
        await onSendMessage(message)
    }

    return (
        <Card className="flex flex-col h-[600px] w-full max-w-4xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b">
                <div className="flex items-center gap-2">
                    <Bot className="h-6 w-6 text-primary" />
                    <h2 className="text-lg font-semibold">Bedrock Knowledge Base Chat</h2>
                </div>
                {selectedKnowledgeBase && (
                    <Badge variant="secondary" className="flex items-center gap-1">
                        <Database className="h-3 w-3" />
                        {selectedKnowledgeBase}
                    </Badge>
                )}
            </div>

            {/* Messages */}
            <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
                <div className="space-y-4">
                    {messages.length === 0 ? (
                        <div className="text-center text-muted-foreground py-8">
                            <Bot className="h-12 w-12 mx-auto mb-4 text-muted-foreground/50" />
                            <p>Start a conversation with your Bedrock Knowledge Base</p>
                            <p className="text-sm mt-2">Ask questions and get intelligent responses</p>
                        </div>
                    ) : (
                        messages.map((message) => (
                            <div
                                key={message.id}
                                className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'
                                    }`}
                            >
                                {message.role === 'assistant' && (
                                    <Avatar className="h-8 w-8 mt-1">
                                        <AvatarFallback className="bg-primary/10 text-primary">
                                            <Bot className="h-4 w-4" />
                                        </AvatarFallback>
                                    </Avatar>
                                )}

                                <div
                                    className={`max-w-[70%] rounded-lg px-4 py-2 ${message.role === 'user'
                                        ? 'bg-primary text-primary-foreground'
                                        : 'bg-muted'
                                        }`}
                                >
                                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                                    <div className="flex items-center justify-between mt-2 gap-2">
                                        <span className={`text-xs ${message.role === 'user' ? 'text-primary-foreground/70' : 'text-muted-foreground'
                                            }`}>
                                            {format(message.timestamp, 'HH:mm')}
                                        </span>
                                        {message.knowledgeBase && (
                                            <Badge variant="outline" className="text-xs">
                                                {message.knowledgeBase}
                                            </Badge>
                                        )}
                                    </div>
                                </div>

                                {message.role === 'user' && (
                                    <Avatar className="h-8 w-8 mt-1">
                                        <AvatarFallback className="bg-secondary text-secondary-foreground">
                                            <User className="h-4 w-4" />
                                        </AvatarFallback>
                                    </Avatar>
                                )}
                            </div>
                        ))
                    )}

                    {isLoading && (
                        <div className="flex gap-3 justify-start">
                            <Avatar className="h-8 w-8 mt-1">
                                <AvatarFallback className="bg-primary/10 text-primary">
                                    <Bot className="h-4 w-4" />
                                </AvatarFallback>
                            </Avatar>
                            <div className="bg-muted rounded-lg px-4 py-2">
                                <div className="flex items-center gap-1">
                                    <div className="flex space-x-1">
                                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                        <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                                    </div>
                                    <span className="text-sm text-muted-foreground ml-2">Thinking...</span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </ScrollArea>

            <Separator />

            {/* Input */}
            <form onSubmit={handleSubmit} className="p-4">
                <div className="flex gap-2">
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask a question about your knowledge base..."
                        disabled={isLoading}
                        className="flex-1"
                    />
                    <Button
                        type="submit"
                        disabled={!input.trim() || isLoading}
                        size="icon"
                    >
                        <Send className="h-4 w-4" />
                    </Button>
                </div>
            </form>
        </Card>
    )
}