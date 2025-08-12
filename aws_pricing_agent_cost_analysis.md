# AWS Pricing Agent Solution Cost Analysis Estimate Report

## Service Overview

AWS Pricing Agent Solution is a fully managed, serverless service that allows you to This project uses multiple AWS services.. This service follows a pay-as-you-go pricing model, making it cost-effective for various workloads.

## Pricing Model

This cost analysis estimate is based on the following pricing model:
- **ON DEMAND** pricing (pay-as-you-go) unless otherwise specified
- Standard service configurations without reserved capacity or savings plans
- No caching or optimization techniques applied

## Assumptions

- Production deployment with 2 ECS Fargate tasks for high availability
- 1 vCPU and 2 GB memory per task configuration
- 24/7 operation (730 hours/month)
- Moderate usage: ~50,000 AI queries per month
- Standard logging and monitoring configuration
- Frontend already deployed on Amplify (existing cost)

## Limitations and Exclusions

- Data transfer costs between regions
- Reserved Instance pricing (using On-Demand only)
- AWS Support costs
- Development and testing environments
- Custom domain and SSL certificate costs (using free ACM)
- Backup and disaster recovery costs

## Cost Breakdown

### Unit Pricing Details

| Service | Resource Type | Unit | Price | Free Tier |
|---------|--------------|------|-------|------------|
| ECS Fargate (Compute) | Vcpu | vCPU-hour | $0.04048 | No free tier for ECS Fargate |
| ECS Fargate (Compute) | Memory | GB-hour | $0.004445 | No free tier for ECS Fargate |
| Application Load Balancer | Alb Hours | ALB-hour | $0.0225 | No free tier for Application Load Balancer |
| Application Load Balancer | Lcu Hours | LCU-hour | $0.008 | No free tier for Application Load Balancer |
| Amazon Bedrock (Nova Lite) | Input Tokens | 1,000 input tokens | $0.00006 | No free tier for Amazon Bedrock |
| Amazon Bedrock (Nova Lite) | Output Tokens | 1,000 output tokens | $0.00024 | No free tier for Amazon Bedrock |
| CloudWatch (Monitoring & Logging) | Log Ingestion | GB | $0.50 | First 5 GB log ingestion and 5 GB log storage free per month |
| CloudWatch (Monitoring & Logging) | Log Storage | GB-month | $0.03 | First 5 GB log ingestion and 5 GB log storage free per month |
| CloudWatch (Monitoring & Logging) | Custom Metrics | metric-month | $0.30 | First 5 GB log ingestion and 5 GB log storage free per month |
| ECR (Container Registry) | Storage | GB-month | $0.10 | 500 MB storage free per month for 12 months |
| Data Transfer | Internet Outbound | GB | $0.09 | 1 GB internet outbound free per month |
| Data Transfer | Inter Az | GB | $0.01 | 1 GB internet outbound free per month |

### Cost Calculation

| Service | Usage | Calculation | Monthly Cost |
|---------|-------|-------------|-------------|
| ECS Fargate (Compute) | 2 tasks × 1 vCPU × 2 GB memory × 730 hours/month (Vcpu Hours: 2 tasks × 1 vCPU × 730 hours = 1,460 vCPU-hours, Memory Hours: 2 tasks × 2 GB × 730 hours = 2,920 GB-hours) | $0.04048 × 1,460 vCPU-hours + $0.004445 × 2,920 GB-hours = $59.10 + $12.98 = $72.08 | $72.08 |
| Application Load Balancer | 1 ALB running 24/7 with ~10 LCUs average usage (Alb Hours: 730 hours/month, Lcu Hours: 730 hours × 10 LCUs = 7,300 LCU-hours) | $0.0225 × 730 hours + $0.008 × 7,300 LCU-hours = $16.43 + $58.40 = $74.83 | $22.04 |
| Amazon Bedrock (Nova Lite) | 500,000 input tokens + 200,000 output tokens per month (Input Tokens: 500,000 tokens = 500 × 1K tokens, Output Tokens: 200,000 tokens = 200 × 1K tokens) | $0.00006 × 500 + $0.00024 × 200 = $30.00 + $48.00 = $78.00 | $78.00 |
| CloudWatch (Monitoring & Logging) | ~5 GB log ingestion, ~5 GB log storage, ~20 custom metrics (Log Ingestion: 5 GB/month, Log Storage: 5 GB stored, Custom Metrics: 20 metrics) | $0.50 × 5 GB + $0.03 × 5 GB + $0.30 × 20 metrics = $2.50 + $0.15 + $6.00 = $8.65 | $8.65 |
| ECR (Container Registry) | ~2 GB container image storage (Storage: 2 GB stored) | $0.10 × 2 GB = $0.20 | $0.20 |
| Data Transfer | ~10 GB internet outbound, ~5 GB inter-AZ transfer (Internet Outbound: 10 GB/month, Inter Az: 5 GB/month) | $0.09 × 10 GB + $0.01 × 5 GB = $0.90 + $0.05 = $0.95 | $0.95 |
| **Total** | **All services** | **Sum of all calculations** | **$181.92/month** |

### Free Tier

Free tier information by service:
- **ECS Fargate (Compute)**: No free tier for ECS Fargate
- **Application Load Balancer**: No free tier for Application Load Balancer
- **Amazon Bedrock (Nova Lite)**: No free tier for Amazon Bedrock
- **CloudWatch (Monitoring & Logging)**: First 5 GB log ingestion and 5 GB log storage free per month
- **ECR (Container Registry)**: 500 MB storage free per month for 12 months
- **Data Transfer**: 1 GB internet outbound free per month

## Cost Scaling with Usage

The following table illustrates how cost estimates scale with different usage levels:

| Service | Low Usage | Medium Usage | High Usage |
|---------|-----------|--------------|------------|
| ECS Fargate (Compute) | $36/month | $72/month | $144/month |
| Application Load Balancer | $11/month | $22/month | $44/month |
| Amazon Bedrock (Nova Lite) | $39/month | $78/month | $156/month |
| CloudWatch (Monitoring & Logging) | $4/month | $8/month | $17/month |
| ECR (Container Registry) | $0/month | $0/month | $0/month |
| Data Transfer | $0/month | $0/month | $1/month |

### Key Cost Factors

- **ECS Fargate (Compute)**: 2 tasks × 1 vCPU × 2 GB memory × 730 hours/month
- **Application Load Balancer**: 1 ALB running 24/7 with ~10 LCUs average usage
- **Amazon Bedrock (Nova Lite)**: 500,000 input tokens + 200,000 output tokens per month
- **CloudWatch (Monitoring & Logging)**: ~5 GB log ingestion, ~5 GB log storage, ~20 custom metrics
- **ECR (Container Registry)**: ~2 GB container image storage
- **Data Transfer**: ~10 GB internet outbound, ~5 GB inter-AZ transfer

## Projected Costs Over Time

The following projections show estimated monthly costs over a 12-month period based on different growth patterns:

Base monthly cost calculation:

| Service | Monthly Cost |
|---------|-------------|
| ECS Fargate (Compute) | $72.08 |
| Application Load Balancer | $22.04 |
| Amazon Bedrock (Nova Lite) | $78.00 |
| CloudWatch (Monitoring & Logging) | $8.65 |
| ECR (Container Registry) | $0.20 |
| Data Transfer | $0.95 |
| **Total Monthly Cost** | **$181** |

| Growth Pattern | Month 1 | Month 3 | Month 6 | Month 12 |
|---------------|---------|---------|---------|----------|
| Steady | $181/mo | $181/mo | $181/mo | $181/mo |
| Moderate | $181/mo | $200/mo | $232/mo | $311/mo |
| Rapid | $181/mo | $220/mo | $292/mo | $519/mo |

* Steady: No monthly growth (1.0x)
* Moderate: 5% monthly growth (1.05x)
* Rapid: 10% monthly growth (1.1x)

## Detailed Cost Analysis

### Pricing Model

ON DEMAND


### Exclusions

- Data transfer costs between regions
- Reserved Instance pricing (using On-Demand only)
- AWS Support costs
- Development and testing environments
- Custom domain and SSL certificate costs (using free ACM)
- Backup and disaster recovery costs

### Recommendations

#### Immediate Actions

- Start with 1 ECS Fargate task and scale to 2 tasks as traffic increases
- Implement response caching to reduce Bedrock token usage
- Monitor CloudWatch costs and optimize log retention policies
- Use Fargate Spot instances for development environments (50% cost savings)



## Cost Optimization Recommendations

### Immediate Actions

- Start with 1 ECS Fargate task and scale to 2 tasks as traffic increases
- Implement response caching to reduce Bedrock token usage
- Monitor CloudWatch costs and optimize log retention policies

### Best Practices

- Regularly review costs with AWS Cost Explorer
- Consider reserved capacity for predictable workloads
- Implement automated scaling based on demand

## Conclusion

By following the recommendations in this report, you can optimize your AWS Pricing Agent Solution costs while maintaining performance and reliability. Regular monitoring and adjustment of your usage patterns will help ensure cost efficiency as your workload evolves.
