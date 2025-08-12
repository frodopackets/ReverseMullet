'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { PricingResponseDisplay } from './pricing-response-display'
import { AgentIndicator } from './agent-indicator'
import { AgentLoadingState } from './agent-loading-state'
import { MCPStatusIndicator } from './mcp-status-indicator'
import { generateMockPricingData } from '@/utils/pricing-parser'
import { PricingResponseMetadata } from '@/types/pricing'

export function PricingDemo() {
  const [showDemo, setShowDemo] = useState(false)
  const [demoData, setDemoData] = useState<PricingResponseMetadata | null>(null)
  const [demoStage, setDemoStage] = useState<'analyzing' | 'routing' | 'processing' | 'responding' | 'complete'>('complete')

  const handleShowDemo = () => {
    setDemoData(generateMockPricingData())
    setShowDemo(true)
    // Simulate the loading stages
    setDemoStage('analyzing')
    setTimeout(() => setDemoStage('routing'), 800)
    setTimeout(() => setDemoStage('processing'), 1600)
    setTimeout(() => setDemoStage('responding'), 2400)
    setTimeout(() => setDemoStage('complete'), 3200)
  }

  const handleHideDemo = () => {
    setShowDemo(false)
    setDemoData(null)
    setDemoStage('complete')
  }

  return (
    <Card className="p-4 mb-4 bg-gradient-to-r from-blue-50 via-purple-50 to-green-50 border-blue-200">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="font-semibold text-blue-900">🚀 AI-First AWS Pricing Agent Demo</h3>
          <p className="text-sm text-blue-700">Experience real-time AWS pricing analysis with MCP integration</p>
        </div>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleShowDemo}
            disabled={showDemo}
            className="bg-white hover:bg-blue-50"
          >
            Show Live Demo
          </Button>
          {showDemo && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleHideDemo}
              className="bg-white hover:bg-red-50"
            >
              Hide Demo
            </Button>
          )}
        </div>
      </div>

      {/* Demo Benefits Highlight */}
      {!showDemo && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
          <div className="text-center p-3 bg-white rounded-lg border border-green-200">
            <div className="text-green-600 font-semibold text-lg">✅ Real-Time Data</div>
            <div className="text-xs text-green-700">Live AWS pricing via MCP</div>
          </div>
          <div className="text-center p-3 bg-white rounded-lg border border-blue-200">
            <div className="text-blue-600 font-semibold text-lg">🧠 AI-First</div>
            <div className="text-xs text-blue-700">90% code reduction</div>
          </div>
          <div className="text-center p-3 bg-white rounded-lg border border-purple-200">
            <div className="text-purple-600 font-semibold text-lg">⚡ Intelligent</div>
            <div className="text-xs text-purple-700">Smart optimization</div>
          </div>
        </div>
      )}

      {showDemo && (
        <div className="space-y-4">
          {/* Demo User Query */}
          <div className="flex gap-3 justify-end">
            <div className="max-w-md">
              <div className="px-4 py-2 rounded-lg bg-blue-600 text-white">
                <p className="text-sm">
                  I need cost analysis for a 3-tier web application with EC2, RDS, and S3 for 10,000 users
                </p>
              </div>
              <p className="text-xs text-muted-foreground mt-1 text-right">
                {new Date().toLocaleTimeString()}
              </p>
            </div>
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
              <span className="text-white text-sm">👤</span>
            </div>
          </div>

          {/* Loading States Demo */}
          {demoStage !== 'complete' && (
            <AgentLoadingState stage={demoStage} currentAgent="aws_pricing" />
          )}

          {/* Demo Response */}
          {demoStage === 'complete' && demoData && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                <span className="text-green-600 text-sm">🤖</span>
              </div>
              <div className="max-w-2xl lg:max-w-4xl">
                <div className="px-4 py-3 rounded-lg bg-gradient-to-br from-green-50 to-blue-50 border border-green-200">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-medium text-green-700 bg-green-100 px-2 py-1 rounded">
                      ✅ Real-Time AWS Data
                    </span>
                    <span className="text-xs font-medium text-blue-700 bg-blue-100 px-2 py-1 rounded">
                      🧠 AI Analysis
                    </span>
                  </div>
                  <p className="text-sm leading-relaxed">
                    Based on your 3-tier web application architecture for 10,000 users, here's the comprehensive cost analysis using **real-time AWS pricing data**:
                    
                    **🏗️ Recommended Architecture:**
                    - **2x EC2 t3.medium** instances (web servers) with Auto Scaling
                    - **1x RDS db.t3.small** MySQL database with Multi-AZ
                    - **S3 bucket** for static assets and automated backups
                    - **Application Load Balancer** for high availability
                    - **CloudFront CDN** for global content delivery
                    
                    **💰 Monthly Cost Breakdown (Real-Time Pricing):**
                    - EC2 instances: **$67.32**/month (us-east-1)
                    - RDS database: **$29.21**/month (Multi-AZ)
                    - S3 storage: **$23.50**/month (100GB + requests)
                    - Load Balancer: **$16.20**/month
                    - CloudFront: **$8.50**/month (1TB transfer)
                    
                    **📊 Total: $144.73/month ($1,736.76/year)**
                    
                    **🎯 AI-Identified Optimization Opportunities:**
                    - **Reserved Instances**: Save $24/month (17% reduction)
                    - **S3 Intelligent Tiering**: Save $8/month on storage
                    - **Right-sizing analysis**: Potential $15/month savings
                    
                    **💡 Total Potential Savings: $47/month (32% reduction)**
                  </p>
                  <div className="flex items-center justify-between mt-3 pt-2 border-t border-green-200">
                    <p className="text-xs text-muted-foreground">
                      Response generated in 3.2s using MCP + AI
                    </p>
                    <AgentIndicator 
                      agentType="aws_pricing" 
                      intentAnalysis={{
                        intent: 'architecture_cost_analysis',
                        confidence: 'high'
                      }}
                      size="sm"
                    />
                  </div>
                </div>
                
                {/* Enhanced MCP Status */}
                <div className="mt-3">
                  <MCPStatusIndicator 
                    mcpAvailable={true}
                    dataSource="real-time"
                    confidence="high"
                    responseTime={3.2}
                    agentType="aws_pricing"
                  />
                </div>
                
                {/* Specialized Pricing Response Display */}
                <PricingResponseDisplay metadata={demoData} />
              </div>
            </div>
          )}
        </div>
      )}
    </Card>
  )
}