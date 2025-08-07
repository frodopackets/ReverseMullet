'use client'

import React from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Sparkles, Heart, Star, Crown } from 'lucide-react'

export interface KnowledgeBase {
  id: string
  name: string
  description: string
  status: 'active' | 'inactive'
  documentCount: number
}

interface BubblegumKnowledgeBaseSelectorProps {
  knowledgeBases: KnowledgeBase[]
  selectedKnowledgeBase?: string
  onSelect: (knowledgeBaseId: string) => void
}

const cuteEmojis = ['🌸', '🦋', '🌈', '🎀', '🌺', '🦄']

export function BubblegumKnowledgeBaseSelector({
  knowledgeBases,
  selectedKnowledgeBase,
  onSelect
}: BubblegumKnowledgeBaseSelectorProps) {
  return (
    <Card className="w-full max-w-4xl mx-auto bg-gradient-to-br from-pink-50 via-purple-50 to-blue-50 border-4 border-pink-300 shadow-2xl shadow-pink-200/50 rounded-3xl overflow-hidden">
      {/* Cute Header */}
      <div className="bg-gradient-to-r from-pink-400 via-purple-400 to-blue-400 p-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-white/20"></div>
        <div className="relative flex items-center justify-center gap-3">
          <Crown className="h-6 w-6 text-white animate-pulse" />
          <h3 className="text-white font-bold text-xl tracking-wide" style={{ fontFamily: 'Comic Sans MS, cursive' }}>
            🌟 Choose Your Magic Library 🌟
          </h3>
          <Sparkles className="h-6 w-6 text-white animate-bounce" />
        </div>
        {/* Floating decorations */}
        <div className="absolute top-2 left-6 text-white/60 animate-bounce" style={{ animationDelay: '0.5s' }}>🌸</div>
        <div className="absolute top-4 right-10 text-white/60 animate-bounce" style={{ animationDelay: '1s' }}>🦋</div>
        <div className="absolute bottom-2 left-10 text-white/60 animate-bounce" style={{ animationDelay: '1.5s' }}>🌈</div>
        <div className="absolute bottom-4 right-6 text-white/60 animate-bounce" style={{ animationDelay: '2s' }}>🎀</div>
      </div>

      {/* Knowledge Bases Grid */}
      <div className="p-6 bg-gradient-to-b from-pink-25 to-purple-25">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {knowledgeBases.map((kb, index) => (
            <Button
              key={kb.id}
              variant="ghost"
              className={`h-auto min-h-[160px] p-0 justify-start relative overflow-hidden rounded-2xl border-3 transition-all duration-300 transform hover:scale-105 ${
                selectedKnowledgeBase === kb.id 
                  ? 'bg-gradient-to-br from-pink-200 to-purple-200 border-pink-400 shadow-xl shadow-pink-300/50' 
                  : 'bg-gradient-to-br from-white to-pink-50 border-pink-200 hover:border-purple-300 shadow-lg hover:shadow-xl'
              }`}
              onClick={() => onSelect(kb.id)}
            >
              {/* Background pattern */}
              <div className="absolute inset-0 opacity-10">
                <div className="absolute top-2 right-2 text-2xl animate-pulse">{cuteEmojis[index % cuteEmojis.length]}</div>
                <div className="absolute bottom-2 left-2 text-lg animate-bounce" style={{ animationDelay: `${index * 0.2}s` }}>✨</div>
              </div>

              {/* Selection indicator */}
              {selectedKnowledgeBase === kb.id && (
                <div className="absolute top-3 right-3 w-8 h-8 bg-gradient-to-r from-pink-400 to-purple-400 rounded-full flex items-center justify-center shadow-lg">
                  <Heart className="h-4 w-4 text-white animate-pulse" />
                </div>
              )}

              <div className="relative w-full h-full p-4 flex flex-col space-y-3">
                {/* Title */}
                <div className="flex items-center gap-2">
                  <div className="text-2xl">{cuteEmojis[index % cuteEmojis.length]}</div>
                  <h4 className={`font-bold text-lg leading-tight break-words flex-1 ${
                    selectedKnowledgeBase === kb.id ? 'text-purple-800' : 'text-pink-700'
                  }`} style={{ fontFamily: 'Comic Sans MS, cursive' }}>
                    {kb.name}
                  </h4>
                </div>

                {/* Description */}
                <p className={`text-sm leading-relaxed break-words whitespace-normal flex-1 ${
                  selectedKnowledgeBase === kb.id ? 'text-purple-700' : 'text-pink-600'
                }`} style={{ fontFamily: 'Comic Sans MS, cursive' }}>
                  {kb.description}
                </p>

                {/* Status and docs */}
                <div className="flex items-center justify-between mt-auto pt-2">
                  <Badge 
                    className={`text-xs font-bold rounded-full px-3 py-1 ${
                      kb.status === 'active' 
                        ? 'bg-gradient-to-r from-green-300 to-emerald-300 text-green-800 shadow-md' 
                        : 'bg-gradient-to-r from-yellow-300 to-orange-300 text-orange-800 shadow-md'
                    }`}
                    style={{ fontFamily: 'Comic Sans MS, cursive' }}
                  >
                    {kb.status === 'active' ? '✨ Active' : '💤 Sleeping'}
                  </Badge>
                  <div className="flex items-center gap-1">
                    <Star className={`h-3 w-3 ${
                      selectedKnowledgeBase === kb.id ? 'text-purple-600' : 'text-pink-500'
                    }`} />
                    <span className={`text-xs font-medium ${
                      selectedKnowledgeBase === kb.id ? 'text-purple-600' : 'text-pink-500'
                    }`} style={{ fontFamily: 'Comic Sans MS, cursive' }}>
                      {kb.documentCount} docs
                    </span>
                  </div>
                </div>
              </div>
            </Button>
          ))}
        </div>

        {/* Bottom message */}
        <div className="text-center mt-6 p-4 bg-gradient-to-r from-pink-100 to-purple-100 rounded-2xl border-2 border-pink-200">
          <p className="text-purple-700 font-medium" style={{ fontFamily: 'Comic Sans MS, cursive' }}>
            {selectedKnowledgeBase 
              ? `🎉 Yay! You picked ${knowledgeBases.find(kb => kb.id === selectedKnowledgeBase)?.name}! 🎉`
              : '💖 Pick a magical library to start chatting! 💖'
            }
          </p>
          <div className="flex justify-center gap-2 mt-2 text-lg">
            <span className="animate-bounce" style={{ animationDelay: '0.1s' }}>🌟</span>
            <span className="animate-bounce" style={{ animationDelay: '0.2s' }}>✨</span>
            <span className="animate-bounce" style={{ animationDelay: '0.3s' }}>💫</span>
            <span className="animate-bounce" style={{ animationDelay: '0.4s' }}>⭐</span>
            <span className="animate-bounce" style={{ animationDelay: '0.5s' }}>🌟</span>
          </div>
        </div>
      </div>
    </Card>
  )
}