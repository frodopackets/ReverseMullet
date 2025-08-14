'use client'

import { Badge } from '@/components/ui/badge'
import { Bot, DollarSign, Brain, AlertTriangle, Zap } from 'lucide-react'

interface AgentIndicatorProps {
  agentType?: string
  intentAnalysis?: {
    intent?: string
    confidence?: 'high' | 'medium' | 'low'
    fallback_applied?: boolean
    error_handled?: boolean
  }
  messageContent?: string  // Add to detect data source from message content
  size?: 'sm' | 'md'
  showDescription?: boolean
}

export function AgentIndicator({ agentType, intentAnalysis, messageContent, size = 'sm', showDescription = false }: AgentIndicatorProps) {
  if (!agentType || agentType === 'user') return null
  
  // Detect if this is real-time data vs fallback mode
  const isRealTimeData = messageContent?.includes('Real-time AWS pricing data')
  const isFallbackMode = messageContent?.includes('fallback mode') || messageContent?.includes('Knowledge base estimates')

  const getAgentInfo = (type: string) => {
    switch (type) {
      case 'aws_pricing':
        return {
          label: 'AWS Pricing',
          icon: DollarSign,
          variant: 'default' as const,
          color: 'text-green-600',
          description: 'Cost analysis and optimization'
        }
      case 'router':
        return {
          label: 'Router',
          icon: Brain,
          variant: 'secondary' as const,
          color: 'text-blue-600',
          description: 'Intelligent query routing'
        }
      case 'general':
        return {
          label: 'General',
          icon: Bot,
          variant: 'outline' as const,
          color: 'text-gray-600',
          description: 'General knowledge assistant'
        }
      case 'fallback_error':
      case 'orchestrator_fallback':
      case 'fallback_system':
      case 'parse_error_fallback':
      case 'process_error_fallback':
      case 'timeout_fallback':
        return {
          label: 'Fallback',
          icon: AlertTriangle,
          variant: 'destructive' as const,
          color: 'text-orange-600',
          description: 'Error handling fallback'
        }
      default:
        return {
          label: 'AI Assistant',
          icon: Zap,
          variant: 'outline' as const,
          color: 'text-purple-600',
          description: 'Specialized assistant'
        }
    }
  }

  const agentInfo = getAgentInfo(agentType)
  const Icon = agentInfo.icon
  const confidence = intentAnalysis?.confidence

  return (
    <div className={`flex items-center gap-1 ${showDescription ? 'flex-col items-start' : ''}`}>
      <div className="flex items-center gap-1">
        <Badge variant={agentInfo.variant} className={size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm px-3 py-1'}>
          <Icon className={`${size === 'sm' ? 'h-3 w-3' : 'h-4 w-4'} mr-1`} />
          {agentInfo.label}
        </Badge>
        
        {confidence && confidence !== 'high' && (
          <Badge variant="outline" className={`${size === 'sm' ? 'text-xs px-1.5 py-0.5' : 'text-sm px-2 py-1'} ${
            confidence === 'medium' ? 'border-yellow-300 text-yellow-700' : 'border-red-300 text-red-700'
          }`}>
            {confidence === 'medium' ? '~' : '?'}
          </Badge>
        )}
        
        {/* Data Source Indicator for AWS Pricing Agent */}
        {agentType === 'aws_pricing' && isRealTimeData && (
          <Badge variant="outline" className={`${size === 'sm' ? 'text-xs px-1.5 py-0.5' : 'text-sm px-2 py-1'} border-green-300 text-green-700 bg-green-50`}>
            ⚡ Live
          </Badge>
        )}
        
        {agentType === 'aws_pricing' && isFallbackMode && (
          <Badge variant="outline" className={`${size === 'sm' ? 'text-xs px-1.5 py-0.5' : 'text-sm px-2 py-1'} border-orange-300 text-orange-700 bg-orange-50`}>
            📚 Est
          </Badge>
        )}
        
        {intentAnalysis?.fallback_applied && (
          <Badge variant="outline" className={`${size === 'sm' ? 'text-xs px-1.5 py-0.5' : 'text-sm px-2 py-1'} border-orange-300 text-orange-700`}>
            FB
          </Badge>
        )}
      </div>
      
      {showDescription && agentInfo.description && (
        <p className="text-xs text-muted-foreground mt-1">{agentInfo.description}</p>
      )}
    </div>
  )
}