// Types for AWS pricing and cost analysis data

export interface ServiceCost {
  serviceName: string
  monthlyCost: number
  unitPrice: number
  unit: string
  quantity: number
  breakdown: {
    compute?: number
    storage?: number
    dataTransfer?: number
    other?: number
  }
}

export interface CostBreakdown {
  totalMonthlyCost: number
  totalAnnualCost: number
  currency: string
  services: ServiceCost[]
  assumptions: string[]
  confidence: 'high' | 'medium' | 'low'
  lastUpdated: string
}

export interface OptimizationRecommendation {
  category: 'instance_type' | 'reserved_instances' | 'spot_instances' | 'storage_class' | 'region'
  title: string
  description: string
  currentCost: number
  optimizedCost: number
  potentialSavings: number
  savingsPercentage: number
  implementationEffort: 'low' | 'medium' | 'high'
  riskLevel: 'low' | 'medium' | 'high'
  timeToImplement: string
}

export interface PricingResponseMetadata {
  costBreakdown?: CostBreakdown
  optimizations?: OptimizationRecommendation[]
  confidence?: 'high' | 'medium' | 'low'
  analysisType?: 'architecture' | 'service_specific' | 'optimization' | 'comparison'
  region?: string
  assumptions?: string[]
}

// Service categorization for display
export type ServiceCategory = 'compute' | 'storage' | 'networking' | 'database' | 'analytics' | 'security' | 'other'

export interface CategorizedService extends ServiceCost {
  category: ServiceCategory
  icon?: string
}