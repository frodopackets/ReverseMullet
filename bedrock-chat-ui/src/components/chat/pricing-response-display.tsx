'use client'

import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown, 
  Server, 
  Database, 
  Network, 
  Shield, 
  BarChart3,
  HardDrive,
  AlertCircle,
  CheckCircle,
  Clock,
  Target
} from 'lucide-react'
import { PricingResponseMetadata, ServiceCost, OptimizationRecommendation, ServiceCategory } from '@/types/pricing'

interface PricingResponseDisplayProps {
  metadata: PricingResponseMetadata
}

export function PricingResponseDisplay({ metadata }: PricingResponseDisplayProps) {
  if (!metadata.costBreakdown && !metadata.optimizations) {
    return null
  }

  const getCategoryIcon = (category: ServiceCategory) => {
    switch (category) {
      case 'compute': return Server
      case 'storage': return HardDrive
      case 'networking': return Network
      case 'database': return Database
      case 'analytics': return BarChart3
      case 'security': return Shield
      default: return Server
    }
  }

  const categorizeService = (serviceName: string): ServiceCategory => {
    const name = serviceName.toLowerCase()
    if (name.includes('ec2') || name.includes('lambda') || name.includes('fargate') || name.includes('compute')) {
      return 'compute'
    }
    if (name.includes('s3') || name.includes('ebs') || name.includes('storage') || name.includes('glacier')) {
      return 'storage'
    }
    if (name.includes('vpc') || name.includes('cloudfront') || name.includes('route53') || name.includes('elb')) {
      return 'networking'
    }
    if (name.includes('rds') || name.includes('dynamodb') || name.includes('redshift') || name.includes('database')) {
      return 'database'
    }
    if (name.includes('analytics') || name.includes('kinesis') || name.includes('emr') || name.includes('athena')) {
      return 'analytics'
    }
    if (name.includes('iam') || name.includes('kms') || name.includes('security') || name.includes('waf')) {
      return 'security'
    }
    return 'other'
  }

  const formatCurrency = (amount: number, currency = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount)
  }

  const getEffortColor = (effort: string) => {
    switch (effort) {
      case 'low': return 'text-green-600 bg-green-50 border-green-200'
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'high': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-600'
      case 'medium': return 'text-yellow-600'
      case 'high': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  return (
    <div className="space-y-4 mt-3">
      {/* Cost Breakdown Section */}
      {metadata.costBreakdown && (
        <Card className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
          <div className="flex items-center gap-2 mb-3">
            <DollarSign className="h-5 w-5 text-blue-600" />
            <h3 className="font-semibold text-blue-900">Cost Analysis</h3>
            <Badge variant="outline" className={`ml-auto ${
              metadata.costBreakdown.confidence === 'high' ? 'border-green-300 text-green-700' :
              metadata.costBreakdown.confidence === 'medium' ? 'border-yellow-300 text-yellow-700' :
              'border-red-300 text-red-700'
            }`}>
              {metadata.costBreakdown.confidence} confidence
            </Badge>
          </div>

          {/* Total Costs */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="text-center p-3 bg-white rounded-lg border">
              <p className="text-sm text-gray-600">Monthly Cost</p>
              <p className="text-2xl font-bold text-blue-600">
                {formatCurrency(metadata.costBreakdown.totalMonthlyCost, metadata.costBreakdown.currency)}
              </p>
            </div>
            <div className="text-center p-3 bg-white rounded-lg border">
              <p className="text-sm text-gray-600">Annual Cost</p>
              <p className="text-2xl font-bold text-blue-600">
                {formatCurrency(metadata.costBreakdown.totalAnnualCost, metadata.costBreakdown.currency)}
              </p>
            </div>
          </div>

          {/* Service Breakdown */}
          {metadata.costBreakdown.services.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Service Breakdown</h4>
              <div className="space-y-2">
                {metadata.costBreakdown.services.map((service, index) => {
                  const category = categorizeService(service.serviceName)
                  const CategoryIcon = getCategoryIcon(category)
                  
                  return (
                    <div key={index} className="flex items-center justify-between p-3 bg-white rounded-lg border">
                      <div className="flex items-center gap-3">
                        <CategoryIcon className="h-4 w-4 text-gray-500" />
                        <div>
                          <p className="font-medium text-sm">{service.serviceName}</p>
                          <p className="text-xs text-gray-500">
                            {service.quantity} {service.unit} × {formatCurrency(service.unitPrice)}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-sm">
                          {formatCurrency(service.monthlyCost)}
                        </p>
                        <Badge variant="secondary" className="text-xs">
                          {category}
                        </Badge>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Assumptions */}
          {metadata.costBreakdown.assumptions.length > 0 && (
            <div className="mt-4 pt-3 border-t">
              <h4 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                <AlertCircle className="h-4 w-4" />
                Assumptions
              </h4>
              <ul className="text-sm text-gray-600 space-y-1">
                {metadata.costBreakdown.assumptions.map((assumption, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-gray-400 mt-1">•</span>
                    <span>{assumption}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </Card>
      )}

      {/* Optimization Recommendations */}
      {metadata.optimizations && metadata.optimizations.length > 0 && (
        <Card className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="h-5 w-5 text-green-600" />
            <h3 className="font-semibold text-green-900">Cost Optimization Opportunities</h3>
          </div>

          <div className="space-y-3">
            {metadata.optimizations.map((optimization, index) => (
              <div key={index} className="p-3 bg-white rounded-lg border">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h4 className="font-medium text-sm text-gray-900">{optimization.title}</h4>
                    <p className="text-xs text-gray-600 mt-1">{optimization.description}</p>
                  </div>
                  <Badge variant="outline" className="ml-2">
                    {optimization.category.replace('_', ' ')}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-4 mt-3">
                  <div className="text-center p-2 bg-red-50 rounded border-red-100 border">
                    <p className="text-xs text-red-600">Current</p>
                    <p className="font-semibold text-red-700">
                      {formatCurrency(optimization.currentCost)}
                    </p>
                  </div>
                  <div className="text-center p-2 bg-green-50 rounded border-green-100 border">
                    <p className="text-xs text-green-600">Optimized</p>
                    <p className="font-semibold text-green-700">
                      {formatCurrency(optimization.optimizedCost)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center justify-between mt-3 pt-2 border-t">
                  <div className="flex items-center gap-4 text-xs">
                    <div className="flex items-center gap-1">
                      <TrendingDown className="h-3 w-3 text-green-600" />
                      <span className="font-medium text-green-700">
                        {formatCurrency(optimization.potentialSavings)} ({optimization.savingsPercentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3 text-gray-500" />
                      <span className="text-gray-600">{optimization.timeToImplement}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className={`text-xs ${getEffortColor(optimization.implementationEffort)}`}>
                      {optimization.implementationEffort} effort
                    </Badge>
                    <Badge variant="outline" className={`text-xs ${getRiskColor(optimization.riskLevel)}`}>
                      {optimization.riskLevel} risk
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Analysis Metadata */}
      {(metadata.region || metadata.analysisType) && (
        <div className="flex items-center gap-2 text-xs text-gray-500">
          {metadata.region && (
            <Badge variant="outline" className="text-xs">
              Region: {metadata.region}
            </Badge>
          )}
          {metadata.analysisType && (
            <Badge variant="outline" className="text-xs">
              Analysis: {metadata.analysisType.replace('_', ' ')}
            </Badge>
          )}
          <span className="ml-auto">
            Updated: {new Date().toLocaleTimeString()}
          </span>
        </div>
      )}
    </div>
  )
}