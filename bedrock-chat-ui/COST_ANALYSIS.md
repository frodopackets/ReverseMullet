# AWS Pricing Agent - Cost Analysis & Optimization

## 💰 Updated Cost Breakdown (API Gateway + ECS Fargate)

Based on your personal usage patterns, here's the realistic monthly cost breakdown:

### **Personal Usage Scenario (~500 queries/month)**

| **Component** | **Monthly Cost** | **% of Total** | **Notes** |
|---------------|------------------|----------------|-----------|
| **ECS Fargate (1 task)** | $36.04 | 62% | 1 vCPU, 2GB RAM, 24/7 |
| **API Gateway** | $3.50 | 6% | ~500 requests/month |
| **CloudWatch** | $3.50 | 6% | Minimal logging |
| **Amazon Bedrock** | $2.16 | 4% | Nova Lite tokens |
| **Internal ALB** | $16.43 | 28% | For ECS integration |
| **ECR + Data Transfer** | $0.15 | <1% | Container storage |
| **TOTAL** | **$58.28/month** | **100%** | |

## 🎯 Cost Optimization Options

### **Option 1: Current Configuration (Recommended for Testing)**
- **Cost**: $58/month
- **Reliability**: High (24/7 availability)
- **Features**: Full monitoring, auto-scaling ready

### **Option 2: Scheduled Scaling (Work Hours Only)**
- **Cost**: ~$35/month (40% savings)
- **Schedule**: Run 12 hours/day (8 AM - 8 PM)
- **Trade-off**: Not available outside work hours

### **Option 3: Fargate Spot (Maximum Savings)**
- **Cost**: ~$30/month (48% savings)
- **Risk**: Potential interruptions (rare)
- **Best for**: Development/testing

### **Option 4: Hybrid Approach**
- **Cost**: ~$25/month (57% savings)
- **Configuration**: Spot + Scheduled scaling
- **Best for**: Personal development use

## 📊 Cost Comparison: Lambda vs ECS Fargate

| **Aspect** | **Lambda (Previous)** | **ECS Fargate (New)** |
|------------|----------------------|----------------------|
| **Base Cost** | $0/month | $36/month |
| **Per Request** | $0.0000002/request | $0/request |
| **500 requests** | $0.10/month | $0/month |
| **Cold Starts** | Yes (2-5 seconds) | No |
| **MCP Support** | Limited | Full support |
| **Scaling** | Automatic | Configurable |
| **Monitoring** | Basic | Advanced |
| **Total Cost** | ~$45/month* | $58/month |

*Lambda total includes API Gateway, Bedrock, and other services

## 🚀 Deployment Configurations

### **Development Configuration** (`terraform.tfvars`)
```hcl
# Personal development setup
ecs_desired_count = 1
ecs_min_capacity  = 1
ecs_max_capacity  = 2
enable_scheduled_scaling = false
enable_fargate_spot = false
log_retention_days = 7
```

### **Cost-Optimized Configuration**
```hcl
# Maximum cost savings
ecs_desired_count = 1
ecs_min_capacity  = 0  # Can scale to zero
ecs_max_capacity  = 2
enable_scheduled_scaling = true
enable_fargate_spot = true
log_retention_days = 3
```

### **Production Configuration**
```hcl
# High availability setup
ecs_desired_count = 2
ecs_min_capacity  = 2
ecs_max_capacity  = 4
enable_scheduled_scaling = false
enable_fargate_spot = false
log_retention_days = 30
```

## 📈 Scaling Cost Projections

| **Usage Level** | **Queries/Month** | **Bedrock Cost** | **Total Cost** |
|-----------------|-------------------|------------------|----------------|
| **Personal** | 500 | $2.16 | $58/month |
| **Light Business** | 2,000 | $8.64 | $65/month |
| **Medium Business** | 10,000 | $43.20 | $100/month |
| **Heavy Business** | 50,000 | $216.00 | $275/month |

## 🛠️ How to Enable Cost Optimizations

### **1. Enable Scheduled Scaling**
```bash
# Edit terraform.tfvars
enable_scheduled_scaling = true
scale_down_schedule = "cron(0 22 * * ? *)"  # 6 PM EST
scale_up_schedule = "cron(0 14 * * ? *)"    # 10 AM EST

# Apply changes
cd terraform
terraform apply
```

### **2. Enable Fargate Spot**
```bash
# Edit terraform.tfvars
enable_fargate_spot = true

# Apply changes
cd terraform
terraform apply
```

### **3. Reduce Log Retention**
```bash
# Edit terraform.tfvars
log_retention_days = 3  # Instead of 7

# Apply changes
cd terraform
terraform apply
```

## 💡 Cost Monitoring & Alerts

### **Set Up Billing Alerts**
1. Go to AWS Billing Console
2. Create billing alerts at:
   - $25/month (Warning)
   - $50/month (Alert)
   - $75/month (Critical)

### **Monitor ECS Costs**
```bash
# Check ECS service status
aws ecs describe-services --cluster bedrock-chat-cluster-dev --services bedrock-chat-strands-agents-dev

# View CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=bedrock-chat-strands-agents-dev \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average
```

## 🎯 Recommendations

### **For Personal Use (You)**
1. **Start with current config** ($58/month) for testing
2. **Enable scheduled scaling** after testing ($35/month)
3. **Monitor actual usage** and adjust accordingly
4. **Consider Spot instances** for development ($30/month)

### **For Production Use**
1. **Use 2+ tasks** for high availability
2. **Keep regular Fargate** (not Spot) for reliability
3. **Implement proper monitoring** and alerting
4. **Use longer log retention** (30 days)

### **Cost vs Reliability Trade-offs**
- **$58/month**: Full reliability, 24/7 availability
- **$35/month**: Scheduled availability (12 hours/day)
- **$30/month**: Full availability with interruption risk
- **$25/month**: Scheduled + interruption risk

## 🔄 Migration Benefits

### **Why ECS Fargate vs Lambda?**
1. **Better MCP Support**: Full Python environment
2. **No Cold Starts**: Always warm and ready
3. **Advanced Monitoring**: Container insights
4. **Flexible Scaling**: More control over scaling
5. **Cost Predictability**: Fixed compute costs
6. **Development Experience**: Easier debugging

### **Trade-offs**
- **Higher base cost**: $36/month vs $0/month
- **More complex**: Infrastructure management
- **Learning curve**: ECS concepts

**Bottom Line**: For your use case, ECS Fargate provides better performance and MCP support for a reasonable cost increase, with multiple optimization options available.