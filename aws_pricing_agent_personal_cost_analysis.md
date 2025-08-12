# AWS Pricing Agent Solution (Personal Use) Cost Analysis Estimate Report

## Service Overview

AWS Pricing Agent Solution (Personal Use) is a fully managed, serverless service that allows you to This project uses multiple AWS services.. This service follows a pay-as-you-go pricing model, making it cost-effective for various workloads.

## Pricing Model

This cost analysis estimate is based on the following pricing model:
- **ON DEMAND** pricing (pay-as-you-go) unless otherwise specified
- Standard service configurations without reserved capacity or savings plans
- No caching or optimization techniques applied

## Assumptions

- Personal usage: ~500 queries per month
- Single ECS Fargate task for development/testing
- Minimal logging and monitoring
- Light load balancer usage (~2 LCUs)
- Occasional usage pattern, not 24/7 production

## Limitations and Exclusions

- Production-scale redundancy
- Heavy monitoring and alerting
- Multi-region deployment
- Enterprise support costs
- Backup and disaster recovery

## Cost Breakdown

### Unit Pricing Details

| Service | Resource Type | Unit | Price | Free Tier |
|---------|--------------|------|-------|------------|
| Amazon Bedrock (Nova Lite) - Personal | Input Tokens | 1,000 tokens | $0.00006 | No free tier for Amazon Bedrock |
| Amazon Bedrock (Nova Lite) - Personal | Output Tokens | 1,000 tokens | $0.00024 | No free tier for Amazon Bedrock |
| ECS Fargate (Single Task) | Vcpu | vCPU-hour | $0.04048 | No free tier for ECS Fargate |
| ECS Fargate (Single Task) | Memory | GB-hour | $0.004445 | No free tier for ECS Fargate |
| Application Load Balancer (Light Usage) | Alb Hours | ALB-hour | $0.0225 | No free tier for Application Load Balancer |
| Application Load Balancer (Light Usage) | Lcu Hours | LCU-hour | $0.008 | No free tier for Application Load Balancer |
| CloudWatch (Minimal Logging) | Log Ingestion | GB | $0.50 | First 5 GB log ingestion and 5 GB log storage free per month |
| CloudWatch (Minimal Logging) | Log Storage | GB-month | $0.03 | First 5 GB log ingestion and 5 GB log storage free per month |
| CloudWatch (Minimal Logging) | Custom Metrics | metric-month | $0.30 | First 5 GB log ingestion and 5 GB log storage free per month |
| ECR (Container Registry) | Storage | GB-month | $0.10 | 500 MB storage free per month for 12 months |
| Data Transfer (Personal) | Internet Outbound | GB | $0.09 | 1 GB internet outbound free per month |
| Data Transfer (Personal) | Inter Az | GB | $0.01 | 1 GB internet outbound free per month |

### Cost Calculation

| Service | Usage | Calculation | Monthly Cost |
|---------|-------|-------------|-------------|
| Amazon Bedrock (Nova Lite) - Personal | Personal usage: ~500 queries/month with ~30 input tokens + 12 output tokens per query (Input Tokens: 15,000 tokens = 15 × 1K tokens, Output Tokens: 6,000 tokens = 6 × 1K tokens) | $0.00006 × 15 + $0.00024 × 6 = $0.90 + $1.44 = $2.34 | $2.16 |
| ECS Fargate (Single Task) | 1 task × 1 vCPU × 2 GB memory × 730 hours/month for personal development (Vcpu Hours: 1 task × 1 vCPU × 730 hours = 730 vCPU-hours, Memory Hours: 1 task × 2 GB × 730 hours = 1,460 GB-hours) | $0.04048 × 730 vCPU-hours + $0.004445 × 1,460 GB-hours = $29.55 + $6.49 = $36.04 | $36.04 |
| Application Load Balancer (Light Usage) | 1 ALB running 24/7 with ~2 LCUs average (personal usage) (Alb Hours: 730 hours/month, Lcu Hours: 730 hours × 2 LCUs = 1,460 LCU-hours) | $0.0225 × 730 hours + $0.008 × 1,460 LCU-hours = $16.43 + $11.68 = $28.11 | $16.43 |
| CloudWatch (Minimal Logging) | ~1 GB log ingestion, ~1 GB log storage, ~10 custom metrics (Log Ingestion: 1 GB/month (within free tier), Log Storage: 1 GB stored (within free tier), Custom Metrics: 10 metrics) | $0 (free tier) + $0 (free tier) + $0.30 × 10 metrics = $3.00 | $3.50 |
| ECR (Container Registry) | ~1 GB container image storage (Storage: 1 GB stored (0.5 GB over free tier)) | $0.10 × 0.5 GB = $0.05 | $0.05 |
| Data Transfer (Personal) | ~2 GB internet outbound, ~1 GB inter-AZ transfer (Internet Outbound: 2 GB/month (1 GB over free tier), Inter Az: 1 GB/month) | $0.09 × 1 GB + $0.01 × 1 GB = $0.09 + $0.01 = $0.10 | $0.10 |
| **Total** | **All services** | **Sum of all calculations** | **$58.28/month** |

### Free Tier

Free tier information by service:
- **Amazon Bedrock (Nova Lite) - Personal**: No free tier for Amazon Bedrock
- **ECS Fargate (Single Task)**: No free tier for ECS Fargate
- **Application Load Balancer (Light Usage)**: No free tier for Application Load Balancer
- **CloudWatch (Minimal Logging)**: First 5 GB log ingestion and 5 GB log storage free per month
- **ECR (Container Registry)**: 500 MB storage free per month for 12 months
- **Data Transfer (Personal)**: 1 GB internet outbound free per month

## Cost Scaling with Usage

The following table illustrates how cost estimates scale with different usage levels:

| Service | Low Usage | Medium Usage | High Usage |
|---------|-----------|--------------|------------|
| Amazon Bedrock (Nova Lite) - Personal | $1/month | $2/month | $4/month |
| ECS Fargate (Single Task) | $18/month | $36/month | $72/month |
| Application Load Balancer (Light Usage) | $8/month | $16/month | $32/month |
| CloudWatch (Minimal Logging) | $1/month | $3/month | $7/month |
| ECR (Container Registry) | $0/month | $0/month | $0/month |
| Data Transfer (Personal) | $0/month | $0/month | $0/month |

### Key Cost Factors

- **Amazon Bedrock (Nova Lite) - Personal**: Personal usage: ~500 queries/month with ~30 input tokens + 12 output tokens per query
- **ECS Fargate (Single Task)**: 1 task × 1 vCPU × 2 GB memory × 730 hours/month for personal development
- **Application Load Balancer (Light Usage)**: 1 ALB running 24/7 with ~2 LCUs average (personal usage)
- **CloudWatch (Minimal Logging)**: ~1 GB log ingestion, ~1 GB log storage, ~10 custom metrics
- **ECR (Container Registry)**: ~1 GB container image storage
- **Data Transfer (Personal)**: ~2 GB internet outbound, ~1 GB inter-AZ transfer

## Projected Costs Over Time

The following projections show estimated monthly costs over a 12-month period based on different growth patterns:

Base monthly cost calculation:

| Service | Monthly Cost |
|---------|-------------|
| Amazon Bedrock (Nova Lite) - Personal | $2.16 |
| ECS Fargate (Single Task) | $36.04 |
| Application Load Balancer (Light Usage) | $16.43 |
| CloudWatch (Minimal Logging) | $3.50 |
| ECR (Container Registry) | $0.05 |
| Data Transfer (Personal) | $0.10 |
| **Total Monthly Cost** | **$58** |

| Growth Pattern | Month 1 | Month 3 | Month 6 | Month 12 |
|---------------|---------|---------|---------|----------|
| Steady | $58/mo | $58/mo | $58/mo | $58/mo |
| Moderate | $58/mo | $64/mo | $74/mo | $99/mo |
| Rapid | $58/mo | $70/mo | $93/mo | $166/mo |

* Steady: No monthly growth (1.0x)
* Moderate: 5% monthly growth (1.05x)
* Rapid: 10% monthly growth (1.1x)

## Detailed Cost Analysis

### Pricing Model

ON DEMAND


### Exclusions

- Production-scale redundancy
- Heavy monitoring and alerting
- Multi-region deployment
- Enterprise support costs
- Backup and disaster recovery

### Recommendations

#### Immediate Actions

- Start with single ECS task - scale up only when needed
- Use development/testing configuration initially
- Monitor actual token usage and adjust estimates
- Consider using Fargate Spot for even lower costs



## Cost Optimization Recommendations

### Immediate Actions

- Start with single ECS task - scale up only when needed
- Use development/testing configuration initially
- Monitor actual token usage and adjust estimates

### Best Practices

- Regularly review costs with AWS Cost Explorer
- Consider reserved capacity for predictable workloads
- Implement automated scaling based on demand

## Conclusion

By following the recommendations in this report, you can optimize your AWS Pricing Agent Solution (Personal Use) costs while maintaining performance and reliability. Regular monitoring and adjustment of your usage patterns will help ensure cost efficiency as your workload evolves.
