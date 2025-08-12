'use client'

import { Bot, DollarSign, Brain, Zap, Database, Cloud, TrendingUp, CheckCircle } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

interface AgentLoadingStateProps {
  stage?: 'analyzing' | 'routing' | 'processing' | 'responding'
  currentAgent?: string
}

export function AgentLoadingState({ stage = 'analyzing', currentAgent }: AgentLoadingStateProps) {
  const getStageInfo = (currentStage: string) => {
    switch (currentStage) {
      case 'analyzing':
        return {
          label: 'Analyzing your query...',
          description: 'Understanding your requirements and identifying key services',
          icon: Brain,
          color: 'text-blue-600',
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200'
        }
      case 'routing':
        return {
          label: 'Selecting specialized agent...',
          description: currentAgent === 'aws_pricing' ? 'Routing to AWS Pricing Agent for cost analysis' : 'Determining best agent for your query',
          icon: Zap,
          color: 'text-purple-600',
          bgColor: 'bg-purple-50',
          borderColor: 'border-purple-200'
        }
      case 'processing':
        if (currentAgent === 'aws_pricing') {
          return {
            label: 'Accessing real-time AWS pricing data...',
            description: 'Connecting to AWS Labs MCP server for current pricing information',
            icon: Database,
            color: 'text-green-600',
            bgColor: 'bg-green-50',
            borderColor: 'border-green-200'
          }
        }
        return {
          label: 'Processing your request...',
          description: 'Analyzing and preparing comprehensive response',
          icon: Bot,
          color: 'text-gray-600',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200'
        }
      case 'responding':
        return {
          label: 'Generating intelligent response...',
          description: currentAgent === 'aws_pricing' ? 'Creating cost analysis with optimization recommendations' : 'Preparing detailed response',
          icon: currentAgent === 'aws_pricing' ? TrendingUp : Bot,
          color: currentAgent === 'aws_pricing' ? 'text-emerald-600' : 'text-gray-600',
          bgColor: currentAgent === 'aws_pricing' ? 'bg-emerald-50' : 'bg-gray-50',
          borderColor: currentAgent === 'aws_pricing' ? 'border-emerald-200' : 'border-gray-200'
        }
      default:
        return {
          label: 'Processing...',
          description: 'Working on your request',
          icon: Bot,
          color: 'text-gray-600',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200'
        }
    }
  }

  const stageInfo = getStageInfo(stage)
  const Icon = stageInfo.icon

  return (
    <div className="flex gap-3 justify-start">
      <div className={`w-10 h-10 rounded-full ${stageInfo.bgColor} ${stageInfo.borderColor} border-2 flex items-center justify-center flex-shrink-0`}>
        <Icon className={`h-5 w-5 ${stageInfo.color} animate-pulse`} />
      </div>
      <div className={`${stageInfo.bgColor} ${stageInfo.borderColor} border px-4 py-3 rounded-lg max-w-md`}>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-medium">{stageInfo.label}</span>
          {currentAgent === 'aws_pricing' && stage === 'processing' && (
            <Badge variant="outline" className="text-xs bg-white">
              <Cloud className="h-3 w-3 mr-1" />
              MCP Server
            </Badge>
          )}
        </div>
        <p className="text-xs text-muted-foreground mb-2">{stageInfo.description}</p>
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            <div className={`w-2 h-2 ${stageInfo.color.replace('text-', 'bg-')}/60 rounded-full animate-bounce`} style={{ animationDelay: '0s' }}></div>
            <div className={`w-2 h-2 ${stageInfo.color.replace('text-', 'bg-')}/60 rounded-full animate-bounce`} style={{ animationDelay: '0.1s' }}></div>
            <div className={`w-2 h-2 ${stageInfo.color.replace('text-', 'bg-')}/60 rounded-full animate-bounce`} style={{ animationDelay: '0.2s' }}></div>
          </div>
          {currentAgent && (
            <Badge variant="secondary" className="text-xs ml-auto">
              {currentAgent === 'aws_pricing' ? 'AWS Pricing Agent' : 'General Agent'}
            </Badge>
          )}
        </div>
      </div>
    </div>
  )
}