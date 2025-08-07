'use client'

import React from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Database, CheckCircle, Circle } from 'lucide-react'

export interface KnowledgeBase {
  id: string
  name: string
  description: string
  status: 'active' | 'inactive'
  documentCount: number
}

interface TerminalKnowledgeBaseSelectorProps {
  knowledgeBases: KnowledgeBase[]
  selectedKnowledgeBase?: string
  onSelect: (knowledgeBaseId: string) => void
}

export function TerminalKnowledgeBaseSelector({
  knowledgeBases,
  selectedKnowledgeBase,
  onSelect
}: TerminalKnowledgeBaseSelectorProps) {
  return (
    <Card className="w-full max-w-4xl mx-auto bg-black border-green-500/30 shadow-lg shadow-green-500/10">
      {/* Terminal Header */}
      <div className="flex items-center gap-2 p-3 border-b border-green-500/30 bg-gray-900">
        <Database className="h-4 w-4 text-green-400" />
        <span className="text-green-400 font-mono text-sm">
          kb-config@bedrock:~$ ls -la knowledge-bases/
        </span>
      </div>

      {/* Knowledge Bases List */}
      <div className="p-4 bg-black font-mono text-sm space-y-2">
        <div className="text-green-500/70 text-xs mb-4">
          total {knowledgeBases.length} knowledge bases available
        </div>
        
        {knowledgeBases.map((kb, index) => (
          <Button
            key={kb.id}
            variant="ghost"
            className={`w-full justify-start p-3 h-auto font-mono text-left hover:bg-green-500/10 ${
              selectedKnowledgeBase === kb.id 
                ? 'bg-green-500/20 border border-green-500/50' 
                : 'hover:bg-gray-900/50'
            }`}
            onClick={() => onSelect(kb.id)}
          >
            <div className="w-full space-y-2">
              {/* File listing style header */}
              <div className="flex items-center gap-3 text-xs">
                <span className="text-green-500/70">
                  {String(index + 1).padStart(2, '0')}
                </span>
                <span className={`${
                  selectedKnowledgeBase === kb.id ? 'text-green-300' : 'text-green-500/70'
                }`}>
                  {kb.status === 'active' ? 'drwxr-xr-x' : 'dr--r--r--'}
                </span>
                <span className={`${
                  selectedKnowledgeBase === kb.id ? 'text-green-300' : 'text-green-500/70'
                }`}>
                  root bedrock
                </span>
                <span className={`${
                  selectedKnowledgeBase === kb.id ? 'text-green-300' : 'text-green-500/70'
                }`}>
                  {kb.documentCount.toString().padStart(4, ' ')}
                </span>
                <span className={`${
                  selectedKnowledgeBase === kb.id ? 'text-green-300' : 'text-green-500/70'
                }`}>
                  Dec 25 12:00
                </span>
                <div className="flex items-center gap-2">
                  {selectedKnowledgeBase === kb.id ? (
                    <CheckCircle className="h-3 w-3 text-green-400" />
                  ) : (
                    <Circle className="h-3 w-3 text-green-500/50" />
                  )}
                  <span className={`font-bold ${
                    selectedKnowledgeBase === kb.id ? 'text-green-300' : 'text-green-400'
                  }`}>
                    {kb.name.toLowerCase().replace(/\s+/g, '-')}
                  </span>
                </div>
              </div>

              {/* Description */}
              <div className={`pl-12 text-xs ${
                selectedKnowledgeBase === kb.id ? 'text-green-300/80' : 'text-green-500/60'
              }`}>
                # {kb.description}
              </div>

              {/* Status and docs count */}
              <div className="pl-12 flex items-center gap-3">
                <Badge 
                  variant="outline"
                  className={`text-xs font-mono border ${
                    kb.status === 'active' 
                      ? 'border-green-500/50 text-green-400 bg-green-500/10' 
                      : 'border-yellow-500/50 text-yellow-400 bg-yellow-500/10'
                  }`}
                >
                  {kb.status.toUpperCase()}
                </Badge>
                <span className={`text-xs ${
                  selectedKnowledgeBase === kb.id ? 'text-green-300/70' : 'text-green-500/50'
                }`}>
                  [{kb.documentCount} documents]
                </span>
              </div>
            </div>
          </Button>
        ))}

        {/* Terminal prompt */}
        <div className="pt-4 border-t border-green-500/20 mt-4">
          <div className="flex items-center gap-2 text-green-400 text-xs">
            <span>$</span>
            <span className="text-green-500/70">
              {selectedKnowledgeBase 
                ? `selected: ${knowledgeBases.find(kb => kb.id === selectedKnowledgeBase)?.name.toLowerCase().replace(/\s+/g, '-')}`
                : 'no knowledge base selected'
              }
            </span>
          </div>
        </div>
      </div>
    </Card>
  )
}