Your AI agents are running 24/7 but you're paying for 100% of compute. You should be paying for 30%:

![AgentCore Runtime](images/runtime-article.webp)

Self-hosted agent infrastructure bleeds money. You provision EC2 instances for peak load, pay for idle containers overnight, and absorb the CPU cost while your agent waits 5 seconds for an LLM response. At scale, 30-70% of your compute bill goes toward doing nothing — your agent is simply waiting for external API calls, model inference, and database queries.

AgentCore's consumption-based pricing eliminates this waste. You pay **$0.0895/vCPU-hour** for active CPU and **$0.00945/GB-hour** for memory — but only when your agent is actually computing. I/O wait time is free. When your agent calls Claude and waits 3 seconds for a response, those 3 seconds cost you nothing. Combine that with 1-second billing granularity, no upfront commitments, and a **$200 free tier** for new customers, and the economics shift dramatically.

## Prerequisites

- AWS account with Bedrock AgentCore access
- Python 3.10+ installed
- boto3 SDK (`pip install boto3`)
- AWS credentials configured
- At least one deployed AgentCore agent (for metric queries)

## Environment Setup

```bash
pip install boto3
export AWS_REGION=us-east-1
```

## Implementation

### Query AgentCore Cost Metrics

```python
import boto3
from datetime import datetime, timedelta, timezone

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

# Define time range — last 24 hours
end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days=1)

agent_arn = "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/my-agent"

# Query CPU consumption (vCPU-Hours)
cpu_response = cloudwatch.get_metric_statistics(
    Namespace='Bedrock-AgentCore',
    MetricName='CPUUsed-vCPUHours',
    Dimensions=[
        {'Name': 'Service', 'Value': 'AgentCore.Runtime'},
        {'Name': 'Resource', 'Value': agent_arn}
    ],
    StartTime=start_time,
    EndTime=end_time,
    Period=3600,
    Statistics=['Sum']
)

# Query memory consumption (GB-Hours)
mem_response = cloudwatch.get_metric_statistics(
    Namespace='Bedrock-AgentCore',
    MetricName='MemoryUsed-GBHours',
    Dimensions=[
        {'Name': 'Service', 'Value': 'AgentCore.Runtime'},
        {'Name': 'Resource', 'Value': agent_arn}
    ],
    StartTime=start_time,
    EndTime=end_time,
    Period=3600,
    Statistics=['Sum']
)

# Calculate estimated costs
total_cpu_hours = sum(dp['Sum'] for dp in cpu_response['Datapoints'])
total_mem_gb_hours = sum(dp['Sum'] for dp in mem_response['Datapoints'])

cpu_cost = total_cpu_hours * 0.0895
mem_cost = total_mem_gb_hours * 0.00945

print(f"CPU: {total_cpu_hours:.4f} vCPU-hours = ${cpu_cost:.4f}")
print(f"Memory: {total_mem_gb_hours:.4f} GB-hours = ${mem_cost:.4f}")
print(f"Estimated daily cost: ${cpu_cost + mem_cost:.4f}")
```

### Build a Cost Monitoring Dashboard

```python
import json

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

agent_arn = "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/my-agent"
region = "us-east-1"

dashboard_body = {
    "widgets": [
        {
            "type": "metric",
            "x": 0, "y": 0, "width": 12, "height": 6,
            "properties": {
                "title": "CPU Consumption (vCPU-Hours)",
                "region": region,
                "metrics": [
                    ["Bedrock-AgentCore", "CPUUsed-vCPUHours",
                     "Service", "AgentCore.Runtime",
                     "Resource", agent_arn]
                ],
                "period": 3600,
                "stat": "Sum",
                "yAxis": {"left": {"label": "vCPU-Hours"}}
            }
        },
        {
            "type": "metric",
            "x": 12, "y": 0, "width": 12, "height": 6,
            "properties": {
                "title": "Memory Consumption (GB-Hours)",
                "region": region,
                "metrics": [
                    ["Bedrock-AgentCore", "MemoryUsed-GBHours",
                     "Service", "AgentCore.Runtime",
                     "Resource", agent_arn]
                ],
                "period": 3600,
                "stat": "Sum",
                "yAxis": {"left": {"label": "GB-Hours"}}
            }
        },
        {
            "type": "metric",
            "x": 0, "y": 6, "width": 12, "height": 6,
            "properties": {
                "title": "Invocations & Errors",
                "region": region,
                "metrics": [
                    ["Bedrock-AgentCore", "Invocations", "Resource", agent_arn],
                    [".", "SystemErrors", ".", "."],
                    [".", "Throttles", ".", "."]
                ],
                "period": 300,
                "stat": "Sum"
            }
        },
        {
            "type": "metric",
            "x": 12, "y": 6, "width": 12, "height": 6,
            "properties": {
                "title": "Session Count",
                "region": region,
                "metrics": [
                    ["Bedrock-AgentCore", "SessionCount", "Resource", agent_arn]
                ],
                "period": 300,
                "stat": "Sum"
            }
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName="AgentCore-CostMonitor",
    DashboardBody=json.dumps(dashboard_body)
)
print(f"Dashboard: https://{region}.console.aws.amazon.com/cloudwatch/home"
      f"?region={region}#dashboards:name=AgentCore-CostMonitor")
```

### Set Up a Budget Alert

```python
budgets = boto3.client('budgets', region_name='us-east-1')
sts = boto3.client('sts')
account_id = sts.get_caller_identity()['Account']

budgets.create_budget(
    AccountId=account_id,
    Budget={
        'BudgetName': 'AgentCore-Monthly',
        'BudgetLimit': {'Amount': '500', 'Unit': 'USD'},
        'BudgetType': 'COST',
        'TimeUnit': 'MONTHLY',
        'CostFilters': {
            'Service': ['Amazon Bedrock']
        }
    },
    NotificationsWithSubscribers=[{
        'Notification': {
            'NotificationType': 'ACTUAL',
            'ComparisonOperator': 'GREATER_THAN',
            'Threshold': 80.0,
            'ThresholdType': 'PERCENTAGE'
        },
        'Subscribers': [{
            'SubscriptionType': 'EMAIL',
            'Address': 'finops-team@example.com'
        }]
    }]
)
print("Budget alert created: notify at 80% of $500/month")
```

## Self-Hosted vs AgentCore: Cost Comparison

A customer support agent handling 1 million conversations per month with 90-second average sessions and 70% I/O wait:

| Component | Self-Hosted (EC2 + ECS) | AgentCore |
|-----------|------------------------|-----------|
| Compute (CPU) | $4,200 (10x m5.large) | $573 |
| Load balancer + NAT | $120 | $0 (included) |
| Container orchestration | $150 | $0 (included) |
| Over-provisioning (30%) | $1,350 | $0 (consumption-based) |
| Engineering ops overhead | $5,000+ | $0 (fully managed) |
| **Total** | **$10,820+** | **$573** |

The gap comes from two factors: I/O wait is free (70% of session time costs nothing), and there is no over-provisioning since you pay per-second for actual consumption only.

## Key Benefits

- **I/O wait is free**: Agents spend 30-70% of time waiting for LLM responses, API calls, and database queries — all at zero CPU cost
- **No capacity planning**: No instances to size, no auto-scaling groups to tune, no idle resources to pay for
- **$200 free tier**: New customers can run approximately 275,000 simple chatbot sessions before spending a dollar

## Common Patterns

Decision makers typically start by running a single agent on the free tier to validate the pricing model against their workload profile. The key variable is I/O wait percentage — the higher it is, the greater the savings. Most agentic workloads fall in the 50-80% I/O wait range, translating to 50-80% CPU cost savings compared to pre-allocated compute. Teams that need cost governance use AWS Budgets alerts paired with the CloudWatch dashboard above to track consumption in real time.

## Next Steps

Deploy one agent to AgentCore, run it for a week, and compare the bill against your current infrastructure cost for the same workload. Use the CloudWatch metrics code above to measure your actual I/O wait ratio — that number tells you exactly how much you will save.

📚 Documentation: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/
💰 Pricing details: https://aws.amazon.com/bedrock/agentcore/pricing/
🔧 GitHub samples: https://github.com/awslabs/amazon-bedrock-agentcore-samples/

#AWS #AI #AgentCore #CostOptimization #FinOps #DecisionMakers
