'use client'

import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { 
  Cloud, 
  Database, 
  CheckCircle, 
  AlertCircle, 
  XCircle, 
  Zap,
  TrendingUp,
  Shield,
  Clock
} from 'lucide-react'

interface MCPStatusIndicatorProps {
  mcpAvailable?: boolean
  dataSource?: 'real-time' | 'knowledge-base' | 'cached'
  confidence?: 'high' | 'medium' | 'low'
  responseTime?: number
  agentType?: string
  className?: string
}

export function MCPStatusIndicator({ 
  mcpAvailable = true, 
  dataSource = 'real-time',
  confidence = 'high',
  responseTime,
  agentType,
  className = ''
}: MCPStatusIndicatorProps) {
  
  const getDataSourceInfo = () => {
    switch (dataSource) {
      case 'real-time':
        return {
          label: 'Real-Time AWS Data',
          description: 'Live pricing from AWS Labs MCP server',
          icon: Database,
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200'
        }
      case 'cached':
        return {
          label: 'Cached Data',
          description: 'Recent pricing data from cache',
          icon: Zap,
          color: 'text-blue-600',
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200'
        }
      case 'knowledge-base':
        return {
          label: 'AI Knowledge Base',
          description: 'Estimated pricing - verify with AWS',
          icon: AlertCircle,
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200'
        }
      default:
        return {
          label: 'Unknown Source',
          description: 'Data source not specified',
          icon: XCircle,
          color: 'text-gray-600',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200'
        }
    }
  }

  const getConfidenceInfo = () => {
    switch (confidence) {
      case 'high':
        return {
          label: 'High Confidence',
          color: 'text-green-700 bg-green-100 border-green-300',
          icon: CheckCircle
        }
      case 'medium':
        return {
          label: 'Medium Confidence',
          color: 'text-yellow-700 bg-yellow-100 border-yellow-300',
          icon: AlertCircle
        }
      case 'low':
        return {
          label: 'Low Confidence',
          color: 'text-red-700 bg-red-100 border-red-300',
          icon: XCircle
        }
      default:
        return {
          label: 'Unknown',
          color: 'text-gray-700 bg-gray-100 border-gray-300',
          icon: AlertCircle
        }
    }
  }

  const sourceInfo = getDataSourceInfo()
  const confidenceInfo = getConfidenceInfo()
  const SourceIcon = sourceInfo.icon
  const ConfidenceIcon = confidenceInfo.icon

  return (
    <Card className={`p-3 ${sourceInfo.bgColor} ${sourceInfo.borderColor} border ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <SourceIcon className={`h-4 w-4 ${sourceInfo.color}`} />
          <span className="text-sm font-medium">{sourceInfo.label}</span>
          {!mcpAvailable && (
            <Badge variant="outline" className="text-xs text-red-600 border-red-300">
              MCP Unavailable
            </Badge>
          )}
        </div>
        <Badge variant="outline" className={`text-xs ${confidenceInfo.color}`}>
          <ConfidenceIcon className="h-3 w-3 mr-1" />
          {confidenceInfo.label}
        </Badge>
      </div>
      
      <p className="text-xs text-muted-foreground mb-2">{sourceInfo.description}</p>
      
      <div className="flex items-center gap-4 text-xs">
        {agentType && (
          <div className="flex items-center gap-1">
            <TrendingUp className="h-3 w-3 text-gray-500" />
            <span className="text-gray-600">
              {agentType === 'aws_pricing' ? 'AWS Pricing Agent' : 'General Agent'}
            </span>
          </div>
        )}
        
        {responseTime && (
          <div className="flex items-center gap-1">
            <Clock className="h-3 w-3 text-gray-500" />
            <span className="text-gray-600">{responseTime.toFixed(1)}s</span>
          </div>
        )}
        
        {mcpAvailable && dataSource === 'real-time' && (
          <div className="flex items-center gap-1">
            <Shield className="h-3 w-3 text-green-500" />
            <span className="text-green-600">Official AWS Data</span>
          </div>
        )}
      </div>
      
      {!mcpAvailable && (
        <div className="mt-2 pt-2 border-t border-yellow-200">
          <p className="text-xs text-yellow-700">
            <strong>Note:</strong> MCP server unavailable. Using AI knowledge base. 
            Verify pricing with <a href="https://calculator.aws/" target="_blank" rel="noopener noreferrer" className="underline">AWS Calculator</a>.
          </p>
        </div>
      )}
    </Card>
  )
}