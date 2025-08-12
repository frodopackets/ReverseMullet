# AWS Pricing Agent - Example Queries

## 🎯 Overview

This document provides comprehensive examples of queries that work exceptionally well with the AWS Pricing Agent. Each example demonstrates different capabilities and shows you how to get the most accurate and useful cost analysis.

## 🚀 Quick Start Examples

### **Simple Service Pricing**

#### **EC2 Instance Pricing**
```
"What's the monthly cost of a t3.small EC2 instance in us-east-1?"
```
**Expected Response**: Detailed cost breakdown with hourly, monthly, and annual pricing, plus optimization suggestions.

#### **RDS Database Pricing**
```
"RDS pricing for a MySQL database with 100GB storage"
```
**Expected Response**: Database instance costs, storage costs, and backup pricing with configuration recommendations.

#### **S3 Storage Costs**
```
"S3 storage costs for 500GB with standard access patterns"
```
**Expected Response**: Storage class recommendations, request pricing, and data transfer costs.

### **Architecture Cost Analysis**

#### **3-Tier Web Application**
```
"I need pricing for a 3-tier web application with:
- 2 EC2 t3.medium instances for web servers
- 1 RDS MySQL database (db.t3.small)
- S3 bucket for static assets
- Application Load Balancer
Expected traffic: 10,000 users per month"
```
**Expected Response**: Complete architecture cost breakdown, monthly/annual totals, and optimization opportunities.

#### **Microservices Architecture**
```
"Cost analysis for a microservices platform with:
- 5 containerized services on ECS Fargate
- API Gateway for service communication
- DynamoDB for user data
- ElastiCache Redis for caching
- CloudWatch for monitoring
Expected load: 100,000 API calls per day"
```
**Expected Response**: Service-by-service cost analysis with scaling considerations and cost optimization strategies.

## 💡 Advanced Query Examples

### **Multi-Region Deployments**

#### **Global Application**
```
"Compare costs for deploying my web application across:
- us-east-1 (primary region)
- eu-west-1 (European users)
- ap-southeast-1 (Asian users)
Include data transfer costs between regions"
```
**Expected Response**: Regional cost comparison, data transfer pricing, and recommendations for cost-effective global deployment.

#### **Disaster Recovery Setup**
```
"Cost analysis for disaster recovery setup:
- Primary: us-east-1 with full production environment
- DR: us-west-2 with minimal standby resources
- RTO: 4 hours, RPO: 1 hour
Services: EC2, RDS, S3, ELB"
```
**Expected Response**: Primary and DR costs, failover considerations, and cost optimization for DR scenarios.

### **Development Lifecycle Environments**

#### **Complete Development Pipeline**
```
"Cost comparison for three environments:
1. Development: Minimal resources, 8 hours/day usage
2. Staging: Production-like, 12 hours/day usage  
3. Production: High availability, 24/7 operation
Services needed: EC2, RDS, S3, CloudFront"
```
**Expected Response**: Environment-specific cost analysis with usage-based pricing and recommendations for cost-effective development workflows.

#### **CI/CD Pipeline Costs**
```
"What's the cost of running a CI/CD pipeline with:
- CodeBuild for compilation (50 builds/day)
- CodeDeploy for deployment
- ECR for container registry
- Lambda for automated testing
- S3 for artifact storage"
```
**Expected Response**: Build pipeline cost analysis with usage-based pricing and optimization for development teams.

### **Data and Analytics Workloads**

#### **Data Lake Architecture**
```
"Cost analysis for a data lake processing 1TB of data daily:
- S3 for raw data storage (multiple storage classes)
- EMR cluster for data processing
- Redshift for data warehouse
- Kinesis for real-time streaming
- QuickSight for visualization
- Glue for ETL jobs"
```
**Expected Response**: Comprehensive data platform cost analysis with storage optimization and processing cost recommendations.

#### **Machine Learning Pipeline**
```
"ML pipeline cost estimation:
- SageMaker for model training (10 hours/week)
- SageMaker endpoints for inference
- S3 for training data and model artifacts
- Lambda for data preprocessing
- Expected: 1M predictions per month"
```
**Expected Response**: ML workflow cost breakdown with training vs. inference costs and scaling recommendations.

### **Enterprise Applications**

#### **ERP System Migration**
```
"Cost for migrating our ERP system to AWS:
- Current: On-premises with 500 users
- Requirements: High availability, 99.9% uptime
- Database: 2TB with heavy transaction load
- Integration: 20+ external systems
- Compliance: SOX and GDPR requirements"
```
**Expected Response**: Enterprise-grade architecture cost analysis with compliance considerations and migration cost factors.

#### **E-commerce Platform**
```
"High-traffic e-commerce platform cost analysis:
- Peak traffic: 50,000 concurrent users
- Product catalog: 1M items
- Order processing: 10,000 orders/day
- Payment processing integration
- Global CDN for fast loading
- Auto-scaling for traffic spikes"
```
**Expected Response**: Scalable e-commerce architecture with peak load pricing and cost optimization for variable traffic patterns.

## 🎨 Optimization-Focused Queries

### **Cost Reduction Strategies**

#### **Current Infrastructure Optimization**
```
"I'm currently spending $5,000/month on AWS. My setup includes:
- 10 EC2 m5.large instances running 24/7
- RDS MySQL with 500GB storage
- 2TB of S3 storage
- CloudFront CDN
How can I reduce costs while maintaining performance?"
```
**Expected Response**: Detailed optimization recommendations with specific savings amounts and implementation guidance.

#### **Reserved Instance Analysis**
```
"Should I buy Reserved Instances for my stable workload?
- 5 EC2 c5.xlarge instances
- Running 24/7 for at least 2 years
- Current On-Demand cost: $2,500/month
Compare 1-year vs 3-year commitments"
```
**Expected Response**: Reserved Instance savings analysis with break-even calculations and commitment recommendations.

### **Scaling and Growth Planning**

#### **Growth Scenario Planning**
```
"Cost projection for scaling from 1,000 to 100,000 users:
- Current architecture: 2 EC2 instances, 1 RDS
- Expected growth: 10x over 18 months
- Performance requirements: <200ms response time
- Budget constraint: <$10,000/month at full scale"
```
**Expected Response**: Scaling cost analysis with architecture evolution recommendations and budget-conscious growth strategies.

#### **Seasonal Traffic Planning**
```
"Cost analysis for seasonal e-commerce business:
- Normal traffic: 1,000 orders/day
- Holiday peak: 20,000 orders/day (2 months/year)
- Need auto-scaling architecture
- Budget optimization for variable load"
```
**Expected Response**: Variable load cost analysis with auto-scaling recommendations and seasonal cost optimization strategies.

## 🔧 Technical Deep-Dive Queries

### **Performance vs. Cost Trade-offs**

#### **Database Performance Optimization**
```
"Compare costs for different RDS configurations:
1. db.t3.large with General Purpose SSD
2. db.r5.xlarge with Provisioned IOPS
3. Aurora Serverless v2
Workload: 10,000 transactions/hour, 200GB database"
```
**Expected Response**: Performance-cost analysis with recommendations based on workload characteristics.

#### **Compute Optimization**
```
"Compare compute costs for CPU-intensive workload:
1. EC2 c5.4xlarge On-Demand
2. EC2 c5.4xlarge Spot Instances
3. Fargate with CPU optimization
4. Lambda with high memory allocation
Workload: Batch processing, 4 hours/day"
```
**Expected Response**: Compute option comparison with cost-performance analysis and workload-specific recommendations.

### **Compliance and Security Costs**

#### **HIPAA Compliance Architecture**
```
"Cost for HIPAA-compliant healthcare application:
- Encrypted data at rest and in transit
- VPC with private subnets
- WAF for application protection
- CloudTrail for audit logging
- Backup and disaster recovery
- 24/7 monitoring and alerting"
```
**Expected Response**: Compliance-focused architecture cost analysis with security service pricing and regulatory requirements.

#### **Financial Services Compliance**
```
"Cost analysis for financial services platform:
- SOX compliance requirements
- Multi-AZ deployment for high availability
- Dedicated tenancy for sensitive workloads
- Advanced monitoring and logging
- Data retention for 7 years"
```
**Expected Response**: Financial compliance architecture with dedicated infrastructure costs and long-term storage considerations.

## 🌍 Industry-Specific Examples

### **Healthcare and Life Sciences**

#### **Medical Imaging Platform**
```
"Cost for medical imaging platform:
- Storage: 10TB of DICOM images per month
- Processing: AI analysis of medical images
- Compliance: HIPAA, FDA validation
- Users: 500 healthcare professionals
- Uptime requirement: 99.99%"
```

#### **Clinical Trial Management**
```
"Clinical trial data management system:
- Patient data for 10,000 participants
- Real-time data collection and analysis
- Regulatory compliance (21 CFR Part 11)
- Global access from 50 research sites
- 10-year data retention requirement"
```

### **Financial Services**

#### **Trading Platform**
```
"High-frequency trading platform costs:
- Ultra-low latency requirements (<1ms)
- Real-time market data processing
- 100,000 transactions per second capacity
- Disaster recovery with <30 second RTO
- Regulatory compliance and audit trails"
```

#### **Digital Banking Platform**
```
"Digital banking application:
- 1M active users
- Mobile and web applications
- Real-time transaction processing
- Fraud detection and prevention
- PCI DSS compliance
- 24/7 customer support integration"
```

### **Media and Entertainment**

#### **Video Streaming Platform**
```
"Video streaming service cost analysis:
- Content library: 10,000 hours of video
- Concurrent viewers: 50,000 peak
- Global CDN for content delivery
- Multiple video quality options
- Content transcoding and storage
- Analytics and recommendation engine"
```

#### **Gaming Platform**
```
"Multiplayer gaming platform:
- 100,000 concurrent players
- Real-time game state synchronization
- Player matchmaking and lobbies
- Game analytics and telemetry
- In-game purchase processing
- Global deployment for low latency"
```

## 📊 Query Best Practices

### **How to Structure Effective Queries**

#### **Include Key Information**
✅ **Good Structure**:
```
"[Application Type] cost analysis:
- [Specific Requirements]
- [Usage Patterns]
- [Performance Needs]
- [Compliance Requirements]
- [Budget Constraints]"
```

#### **Be Specific About Scale**
✅ **Specific**: "10,000 users, 1M API calls/day, 500GB database"
❌ **Vague**: "Medium-sized application with some users"

#### **Mention Your Constraints**
✅ **Helpful**: "Budget under $2,000/month, must be GDPR compliant"
❌ **Missing**: No constraints mentioned

### **Getting the Most Accurate Results**

#### **Provide Usage Patterns**
- Peak vs. average load
- Seasonal variations
- Geographic distribution
- Growth expectations

#### **Specify Performance Requirements**
- Response time needs
- Availability requirements
- Throughput expectations
- Scalability needs

#### **Include Compliance Needs**
- Regulatory requirements
- Data residency needs
- Security standards
- Audit requirements

## 🎯 Query Categories Summary

### **Simple Queries** (5-10 words)
- Single service pricing
- Basic cost comparisons
- Quick estimates

### **Architecture Queries** (50-100 words)
- Multi-service applications
- Complete system costs
- Integration requirements

### **Optimization Queries** (30-50 words)
- Cost reduction strategies
- Performance vs. cost trade-offs
- Scaling recommendations

### **Complex Queries** (100+ words)
- Enterprise applications
- Compliance requirements
- Multi-region deployments
- Industry-specific needs

## 🚀 Pro Tips for Power Users

### **Advanced Query Techniques**

#### **Scenario Comparison**
```
"Compare three scenarios for my application:
1. Cost-optimized (minimal resources)
2. Performance-optimized (premium resources)
3. Balanced approach (moderate resources)
Show trade-offs for each option"
```

#### **What-If Analysis**
```
"What if my traffic increases by 5x over the next year?
Current setup: [describe current architecture]
Show cost progression at 2x, 3x, and 5x current load"
```

#### **Migration Planning**
```
"Migration cost analysis from on-premises to AWS:
Current: [describe current setup]
Requirements: [list requirements]
Timeline: [migration timeline]
Include migration costs and ongoing operational costs"
```

### **Getting Detailed Breakdowns**

#### **Request Specific Details**
- "Include data transfer costs"
- "Show Reserved Instance savings"
- "Compare storage classes"
- "Include backup and DR costs"

#### **Ask for Alternatives**
- "What are cheaper alternatives?"
- "How can I optimize this further?"
- "What if I use Spot Instances?"
- "Compare with serverless options"

---

## 🎉 Ready to Get Started?

These examples demonstrate the full range of capabilities available with the AWS Pricing Agent. Start with simple queries and gradually explore more complex scenarios as you become familiar with the system.

**Remember**: The agent uses real-time AWS pricing data, so your results will always be current and accurate! 🚀