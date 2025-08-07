'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Database, Check } from 'lucide-react'

export interface KnowledgeBase {
  id: string
  name: string
  description: string
  status: 'active' | 'inactive'
  documentCount: number
}

interface KnowledgeBaseSelectorProps {
  knowledgeBases: KnowledgeBase[]
  selectedKnowledgeBase?: string
  onSelect: (knowledgeBaseId: string) => void
}

export function KnowledgeBaseSelector({
  knowledgeBases,
  selectedKnowledgeBase,
  onSelect
}: KnowledgeBaseSelectorProps) {
  return (
    <Card className="p-4 w-full max-w-4xl mx-auto">
      <div className="flex items-center gap-2 mb-3">
        <Database className="h-4 w-4 text-primary" />
        <h3 className="text-base font-semibold">Knowledge Base Settings</h3>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {knowledgeBases.map((kb) => (
          <Button
            key={kb.id}
            variant={selectedKnowledgeBase === kb.id ? "default" : "outline"}
            className="h-auto min-h-[140px] p-4 justify-start relative"
            onClick={() => onSelect(kb.id)}
          >
            <div className="flex flex-col w-full text-left space-y-2 h-full">
              <div className="flex items-start justify-between w-full gap-2">
                <span className={`font-medium text-sm leading-tight break-words flex-1 ${
                  selectedKnowledgeBase === kb.id 
                    ? 'text-primary-foreground' 
                    : 'text-foreground'
                }`}>
                  {kb.name}
                </span>
                {selectedKnowledgeBase === kb.id && (
                  <Check className="h-4 w-4 flex-shrink-0 text-primary-foreground" />
                )}
              </div>
              <p className={`text-xs leading-relaxed text-left break-words whitespace-normal flex-1 ${
                selectedKnowledgeBase === kb.id 
                  ? 'text-primary-foreground/80' 
                  : 'text-muted-foreground'
              }`}>
                {kb.description}
              </p>
              <div className="flex items-center gap-2 mt-auto pt-1">
                <Badge 
                  variant={kb.status === 'active' ? 'default' : 'secondary'}
                  className="text-xs"
                >
                  {kb.status}
                </Badge>
                <span className={`text-xs ${
                  selectedKnowledgeBase === kb.id 
                    ? 'text-primary-foreground/70' 
                    : 'text-muted-foreground'
                }`}>
                  {kb.documentCount} docs
                </span>
              </div>
            </div>
          </Button>
        ))}
      </div>
    </Card>
  )
}