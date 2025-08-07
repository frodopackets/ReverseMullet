'use client'

import React from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Crown, Shield, Sword, Castle, Scroll } from 'lucide-react'

export interface KnowledgeBase {
  id: string
  name: string
  description: string
  status: 'active' | 'inactive'
  documentCount: number
}

interface MedievalKnowledgeBaseSelectorProps {
  knowledgeBases: KnowledgeBase[]
  selectedKnowledgeBase?: string
  onSelect: (knowledgeBaseId: string) => void
}

const medievalEmojis = ['🏰', '⚔️', '🛡️', '👑', '🗡️', '🐉']
const medievalTitles = ['Royal Archives', 'Sacred Scrolls', 'Ancient Codex', 'Noble Records', 'Mystic Tomes', 'Dragon Lore']

export function MedievalKnowledgeBaseSelector({
  knowledgeBases,
  selectedKnowledgeBase,
  onSelect
}: MedievalKnowledgeBaseSelectorProps) {
  return (
    <Card className="w-full max-w-4xl mx-auto bg-gradient-to-b from-stone-100 via-slate-100 to-gray-100 border-4 border-stone-600 shadow-2xl shadow-stone-900/50 rounded-none overflow-hidden">
      {/* Medieval Header with Castle Battlements */}
      <div className="bg-gradient-to-r from-stone-800 via-slate-700 to-stone-800 relative overflow-hidden">
        {/* Battlements */}
        <div className="absolute top-0 left-0 right-0 h-4 bg-stone-900 flex">
          {Array.from({ length: 20 }).map((_, i) => (
            <div key={i} className={`flex-1 ${i % 2 === 0 ? 'bg-stone-800' : 'bg-stone-900'}`}></div>
          ))}
        </div>
        
        <div className="pt-6 pb-4 px-6 relative">
          <div className="flex items-center justify-center gap-4">
            <Castle className="h-8 w-8 text-amber-300 animate-pulse" />
            <h3 className="text-stone-100 font-bold text-2xl tracking-wide" style={{ fontFamily: 'serif' }}>
              🏰 Choose Thy Sacred Scrolls 🏰
            </h3>
            <Scroll className="h-8 w-8 text-amber-300 animate-pulse" />
          </div>
          {/* Decorative elements */}
          <div className="absolute top-4 left-6 text-amber-400/60 text-2xl">🗡️</div>
          <div className="absolute top-6 right-8 text-amber-400/60 text-2xl">🛡️</div>
          <div className="absolute bottom-2 left-8 text-amber-400/60 text-xl">⚔️</div>
          <div className="absolute bottom-2 right-6 text-amber-400/60 text-xl">👑</div>
        </div>
      </div>

      {/* Knowledge Bases Grid */}
      <div className="p-6 bg-gradient-to-b from-stone-50 to-slate-50 relative">
        {/* Stone texture overlay */}
        <div className="absolute inset-0 opacity-10 bg-gradient-to-br from-stone-200 via-transparent to-slate-300 pointer-events-none"></div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 relative z-10">
          {knowledgeBases.map((kb, index) => (
            <Button
              key={kb.id}
              variant="ghost"
              className={`h-auto min-h-[160px] p-0 justify-start relative overflow-hidden rounded-lg border-3 transition-all duration-300 transform hover:scale-105 ${
                selectedKnowledgeBase === kb.id 
                  ? 'bg-gradient-to-br from-stone-200 to-slate-200 border-stone-600 shadow-xl shadow-stone-500/50' 
                  : 'bg-gradient-to-br from-stone-50 to-slate-50 border-stone-400 hover:border-stone-500 shadow-lg hover:shadow-xl'
              }`}
              onClick={() => onSelect(kb.id)}
            >
              {/* Stone texture */}
              <div className="absolute inset-0 opacity-20 bg-gradient-to-br from-stone-100 via-transparent to-slate-100"></div>
              
              {/* Medieval scroll corners */}
              <div className={`absolute top-1 left-1 w-3 h-3 ${
                selectedKnowledgeBase === kb.id ? 'bg-stone-500' : 'bg-stone-300'
              } transform rotate-45`}></div>
              <div className={`absolute top-1 right-1 w-3 h-3 ${
                selectedKnowledgeBase === kb.id ? 'bg-stone-500' : 'bg-stone-300'
              } transform rotate-45`}></div>
              <div className={`absolute bottom-1 left-1 w-3 h-3 ${
                selectedKnowledgeBase === kb.id ? 'bg-stone-500' : 'bg-stone-300'
              } transform rotate-45`}></div>
              <div className={`absolute bottom-1 right-1 w-3 h-3 ${
                selectedKnowledgeBase === kb.id ? 'bg-stone-500' : 'bg-stone-300'
              } transform rotate-45`}></div>

              {/* Selection indicator */}
              {selectedKnowledgeBase === kb.id && (
                <div className="absolute top-3 right-3 w-10 h-10 bg-gradient-to-r from-amber-600 to-amber-700 rounded-full flex items-center justify-center shadow-lg border-2 border-amber-400">
                  <Crown className="h-5 w-5 text-amber-200 animate-pulse" />
                </div>
              )}

              <div className="relative w-full h-full p-4 flex flex-col space-y-3 z-10">
                {/* Title */}
                <div className="flex items-center gap-3">
                  <div className="text-3xl">{medievalEmojis[index % medievalEmojis.length]}</div>
                  <div className="flex-1">
                    <h4 className={`font-bold text-lg leading-tight break-words ${
                      selectedKnowledgeBase === kb.id ? 'text-stone-900' : 'text-stone-800'
                    }`} style={{ fontFamily: 'serif' }}>
                      {medievalTitles[index % medievalTitles.length]}
                    </h4>
                    <p className={`text-sm font-medium ${
                      selectedKnowledgeBase === kb.id ? 'text-slate-700' : 'text-slate-600'
                    }`} style={{ fontFamily: 'serif' }}>
                      {kb.name}
                    </p>
                  </div>
                </div>

                {/* Description */}
                <p className={`text-sm leading-relaxed break-words whitespace-normal flex-1 ${
                  selectedKnowledgeBase === kb.id ? 'text-stone-800' : 'text-slate-700'
                }`} style={{ fontFamily: 'serif' }}>
                  {kb.description}
                </p>

                {/* Status and docs */}
                <div className="flex items-center justify-between mt-auto pt-2">
                  <Badge 
                    className={`text-xs font-bold rounded-full px-3 py-1 border-2 ${
                      kb.status === 'active' 
                        ? 'bg-gradient-to-r from-green-400 to-emerald-400 text-green-900 border-green-600 shadow-md' 
                        : 'bg-gradient-to-r from-red-400 to-orange-400 text-red-900 border-red-600 shadow-md'
                    }`}
                    style={{ fontFamily: 'serif' }}
                  >
                    {kb.status === 'active' ? '⚔️ Active' : '🛡️ Sealed'}
                  </Badge>
                  <div className="flex items-center gap-1">
                    <Scroll className={`h-4 w-4 ${
                      selectedKnowledgeBase === kb.id ? 'text-stone-700' : 'text-slate-600'
                    }`} />
                    <span className={`text-sm font-medium ${
                      selectedKnowledgeBase === kb.id ? 'text-stone-700' : 'text-slate-600'
                    }`} style={{ fontFamily: 'serif' }}>
                      {kb.documentCount} scrolls
                    </span>
                  </div>
                </div>
              </div>
            </Button>
          ))}
        </div>

        {/* Bottom message */}
        <div className="text-center mt-6 p-4 bg-gradient-to-r from-stone-100 to-slate-100 rounded-lg border-3 border-stone-500 relative z-10">
          {/* Decorative corners */}
          <div className="absolute top-1 left-1 w-3 h-3 bg-stone-400 transform rotate-45"></div>
          <div className="absolute top-1 right-1 w-3 h-3 bg-stone-400 transform rotate-45"></div>
          <div className="absolute bottom-1 left-1 w-3 h-3 bg-stone-400 transform rotate-45"></div>
          <div className="absolute bottom-1 right-1 w-3 h-3 bg-stone-400 transform rotate-45"></div>
          
          <p className="text-stone-800 font-bold text-lg relative z-10" style={{ fontFamily: 'serif' }}>
            {selectedKnowledgeBase 
              ? `⚔️ Thou hast chosen the ${knowledgeBases.find(kb => kb.id === selectedKnowledgeBase)?.name} scrolls! ⚔️`
              : '🏰 Select thy sacred knowledge scrolls to begin thy quest! 🏰'
            }
          </p>
          <div className="flex justify-center gap-2 mt-2 text-2xl relative z-10">
            <span className="animate-bounce" style={{ animationDelay: '0.1s' }}>🗡️</span>
            <span className="animate-bounce" style={{ animationDelay: '0.2s' }}>⚔️</span>
            <span className="animate-bounce" style={{ animationDelay: '0.3s' }}>🛡️</span>
            <span className="animate-bounce" style={{ animationDelay: '0.4s' }}>👑</span>
            <span className="animate-bounce" style={{ animationDelay: '0.5s' }}>🏰</span>
          </div>
        </div>
      </div>
    </Card>
  )
}