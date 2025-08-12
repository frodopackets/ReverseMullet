'use client'

import { Badge } from '@/components/ui/badge'
import { Wifi, WifiOff } from 'lucide-react'

interface StatusIndicatorProps {
  isConnected: boolean
  mode: 'mock' | 'bedrock' | 'router'
}

export function StatusIndicator({ isConnected, mode }: StatusIndicatorProps) {
  return (
    <div className="flex items-center gap-2 text-sm">
      <div className="flex items-center gap-1">
        {isConnected ? (
          <Wifi className="h-4 w-4 text-primary" />
        ) : (
          <WifiOff className="h-4 w-4 text-destructive" />
        )}
        <span className={isConnected ? 'text-primary' : 'text-destructive'}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>
      <Badge variant={mode === 'mock' ? 'secondary' : 'default'}>
        {mode === 'mock' ? 'Mock Mode' : mode === 'router' ? 'Intelligent Router' : 'Bedrock'}
      </Badge>
    </div>
  )
}