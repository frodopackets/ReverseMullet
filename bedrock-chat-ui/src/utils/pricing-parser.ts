import { PricingResponseMetadata, CostBreakdown, ServiceCost, OptimizationRecommendation } from '@/types/pricing'

/**
 * Utility functions to parse pricing information from agent responses
 */

export function parsePricingResponse(content: string, agentType?: string): PricingResponseMetadata | undefined {
  if (agentType !== 'aws_pricing') {
    return undefined
  }

  // Try to extract structured pricing data from the response
  const metadata: PricingResponseMetadata = {
    analysisType: 'architecture',
    confidence: 'medium'
  }

  // Extract cost information using regex patterns
  const costBreakdown = extractCostBreakdown(content)
  if (costBreakdown) {
    metadata.costBreakdown = costBreakdown
  }

  // Extract optimization recommendations
  const optimizations = extractOptimizations(content)
  if (optimizations.length > 0) {
    metadata.optimizations = optimizations
  }

  // Extract region information
  const region = extractRegion(content)
  if (region) {
    metadata.region = region
  }

  // Extract assumptions
  const assumptions = extractAssumptions(content)
  if (assumptions.length > 0) {
    metadata.assumptions = assumptions
  }

  // Only return metadata if we found some pricing information
  if (metadata.costBreakdown || metadata.optimizations) {
    return metadata
  }

  return undefined
}

function extractCostBreakdown(content: string): CostBreakdown | undefined {
  const services: ServiceCost[] = []
  let totalMonthlyCost = 0
  let totalAnnualCost = 0

  // Pattern to match service costs like "EC2: $150.00/month"
  const servicePattern = /([A-Za-z0-9\s]+):\s*\$?([\d,]+\.?\d*)\s*\/?\s*(month|monthly|per month)/gi
  let match

  while ((match = servicePattern.exec(content)) !== null) {
    const serviceName = match[1].trim()
    const cost = parseFloat(match[2].replace(/,/g, ''))
    
    if (!isNaN(cost)) {
      services.push({
        serviceName,
        monthlyCost: cost,
        unitPrice: cost, // Simplified - would need more parsing for actual unit prices
        unit: 'month',
        quantity: 1,
        breakdown: {
          compute: serviceName.toLowerCase().includes('ec2') || serviceName.toLowerCase().includes('compute') ? cost : undefined,
          storage: serviceName.toLowerCase().includes('s3') || serviceName.toLowerCase().includes('storage') ? cost : undefined,
          other: cost
        }
      })
      totalMonthlyCost += cost
    }
  }

  // Pattern to match total costs
  const totalPattern = /total.*?:?\s*\$?([\d,]+\.?\d*)\s*\/?\s*(month|monthly|per month)/gi
  const totalMatch = totalPattern.exec(content)
  if (totalMatch) {
    totalMonthlyCost = parseFloat(totalMatch[1].replace(/,/g, ''))
  }

  // Pattern to match annual costs
  const annualPattern = /annual.*?:?\s*\$?([\d,]+\.?\d*)\s*\/?\s*(year|yearly|per year|annually)/gi
  const annualMatch = annualPattern.exec(content)
  if (annualMatch) {
    totalAnnualCost = parseFloat(annualMatch[1].replace(/,/g, ''))
  } else {
    totalAnnualCost = totalMonthlyCost * 12
  }

  if (services.length > 0 || totalMonthlyCost > 0) {
    return {
      totalMonthlyCost,
      totalAnnualCost,
      currency: 'USD',
      services,
      assumptions: [],
      confidence: 'medium',
      lastUpdated: new Date().toISOString()
    }
  }

  return undefined
}

function extractOptimizations(content: string): OptimizationRecommendation[] {
  const optimizations: OptimizationRecommendation[] = []

  // Pattern to match optimization suggestions
  const optimizationPatterns = [
    /reserved instance/gi,
    /spot instance/gi,
    /right.?siz/gi,
    /storage class/gi,
    /region/gi
  ]

  // Look for savings mentions
  const savingsPattern = /save.*?\$?([\d,]+\.?\d*)|savings.*?\$?([\d,]+\.?\d*)/gi
  let savingsMatch

  while ((savingsMatch = savingsPattern.exec(content)) !== null) {
    const savings = parseFloat((savingsMatch[1] || savingsMatch[2]).replace(/,/g, ''))
    
    if (!isNaN(savings)) {
      // Determine optimization type based on context
      let category: OptimizationRecommendation['category'] = 'instance_type'
      let title = 'Cost Optimization Opportunity'
      
      const contextBefore = content.substring(Math.max(0, savingsMatch.index - 100), savingsMatch.index)
      const contextAfter = content.substring(savingsMatch.index, savingsMatch.index + 100)
      const context = contextBefore + contextAfter
      
      if (/reserved/gi.test(context)) {
        category = 'reserved_instances'
        title = 'Reserved Instance Savings'
      } else if (/spot/gi.test(context)) {
        category = 'spot_instances'
        title = 'Spot Instance Savings'
      } else if (/storage/gi.test(context)) {
        category = 'storage_class'
        title = 'Storage Optimization'
      } else if (/region/gi.test(context)) {
        category = 'region'
        title = 'Regional Cost Optimization'
      }

      optimizations.push({
        category,
        title,
        description: `Potential savings identified in the analysis`,
        currentCost: savings * 2, // Estimate current cost
        optimizedCost: savings,
        potentialSavings: savings,
        savingsPercentage: 25, // Default estimate
        implementationEffort: 'medium',
        riskLevel: 'low',
        timeToImplement: '1-2 weeks'
      })
    }
  }

  return optimizations
}

function extractRegion(content: string): string | undefined {
  // Pattern to match AWS regions
  const regionPattern = /(us-east-1|us-west-1|us-west-2|eu-west-1|eu-central-1|ap-southeast-1|ap-northeast-1)/gi
  const match = regionPattern.exec(content)
  return match ? match[1] : undefined
}

function extractAssumptions(content: string): string[] {
  const assumptions: string[] = []
  
  // Look for assumption indicators
  const assumptionPatterns = [
    /assuming/gi,
    /assumption/gi,
    /estimate/gi,
    /approximate/gi
  ]

  // Extract sentences that contain assumption keywords
  const sentences = content.split(/[.!?]+/)
  
  for (const sentence of sentences) {
    for (const pattern of assumptionPatterns) {
      if (pattern.test(sentence)) {
        const cleanSentence = sentence.trim()
        if (cleanSentence.length > 10 && cleanSentence.length < 200) {
          assumptions.push(cleanSentence)
          break
        }
      }
    }
  }

  return assumptions.slice(0, 5) // Limit to 5 assumptions
}

/**
 * Mock function to generate sample pricing data for testing
 */
export function generateMockPricingData(): PricingResponseMetadata {
  return {
    costBreakdown: {
      totalMonthlyCost: 450.75,
      totalAnnualCost: 5409.00,
      currency: 'USD',
      services: [
        {
          serviceName: 'Amazon EC2',
          monthlyCost: 250.00,
          unitPrice: 0.10,
          unit: 'hour',
          quantity: 2500,
          breakdown: {
            compute: 250.00
          }
        },
        {
          serviceName: 'Amazon S3',
          monthlyCost: 75.50,
          unitPrice: 0.023,
          unit: 'GB',
          quantity: 3283,
          breakdown: {
            storage: 75.50
          }
        },
        {
          serviceName: 'Amazon RDS',
          monthlyCost: 125.25,
          unitPrice: 0.17,
          unit: 'hour',
          quantity: 737,
          breakdown: {
            compute: 100.25,
            storage: 25.00
          }
        }
      ],
      assumptions: [
        'Standard On-Demand pricing model',
        'us-east-1 region pricing',
        'No Reserved Instance discounts applied',
        'Average 80% utilization assumed'
      ],
      confidence: 'high',
      lastUpdated: new Date().toISOString()
    },
    optimizations: [
      {
        category: 'reserved_instances',
        title: 'Reserved Instance Savings',
        description: 'Switch to 1-year Reserved Instances for EC2 and RDS',
        currentCost: 375.25,
        optimizedCost: 262.68,
        potentialSavings: 112.57,
        savingsPercentage: 30,
        implementationEffort: 'low',
        riskLevel: 'low',
        timeToImplement: '1 day'
      },
      {
        category: 'storage_class',
        title: 'S3 Storage Class Optimization',
        description: 'Move infrequently accessed data to S3 IA',
        currentCost: 75.50,
        optimizedCost: 45.30,
        potentialSavings: 30.20,
        savingsPercentage: 40,
        implementationEffort: 'medium',
        riskLevel: 'low',
        timeToImplement: '1 week'
      }
    ],
    confidence: 'high',
    analysisType: 'architecture',
    region: 'us-east-1',
    assumptions: [
      'Standard On-Demand pricing model',
      'us-east-1 region pricing',
      'No Reserved Instance discounts applied'
    ]
  }
}