# Multi-Agent SRE Assistant with AgentCore

![AgentCore Runtime](images/runtime-article.webp)

## The Problem

It's 3 AM. PagerDuty fires. Your on-call engineer opens a dozen tabs: Kubernetes dashboard, CloudWatch logs, Grafana metrics, runbook wiki, and the incident Slack channel. They spend 20 minutes correlating signals before they even understand the problem. By then, customer impact has been accumulating for half an hour.

Site reliability engineering during incidents requires parallel investigation across multiple systems — logs, metrics, infrastructure state, and runbooks — while maintaining a coherent picture of what's happening. A single agent can't effectively manage this breadth. It needs to be good at everything simultaneously.

This tutorial builds a **supervisor + specialist** multi-agent system on AgentCore Runtime. A supervisor agent decomposes incidents into investigation tasks and delegates them to specialized sub-agents: a **Logs Agent** that searches and analyzes log patterns, a **Metrics Agent** that queries CloudWatch for anomalies, a **Kubernetes Agent** that checks cluster and pod state, and a **Runbook Agent** that retrieves relevant procedures. Runtime's 8-hour session support means the system can manage extended incidents without timing out.

## Prerequisites

### AWS Account Setup

- AWS account with Bedrock AgentCore access enabled
- IAM permissions: `bedrock-agentcore:*`, `bedrock:InvokeModel`, `logs:*`, `cloudwatch:GetMetricData`
- Region: us-east-1

### Local Environment

- Python 3.10+
- pip for package management

### Required Packages

```bash
# requirements.txt
boto3>=1.34.0
strands-agents>=0.1.0
bedrock-agentcore-sdk>=1.0.0
python-dotenv>=1.0.0
```

## Getting Started

### Step 1: Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Define Specialist Agents

Each specialist focuses on one investigation domain.

```python
import os
import json
import boto3
from datetime import datetime, timezone, timedelta
from strands import Agent, tool
from strands.models import BedrockModel

REGION = os.getenv("AWS_REGION", "us-east-1")
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    region_name=REGION
)

# === LOGS AGENT ===

@tool
def search_logs(log_group: str, query: str, hours_back: int = 1) -> str:
    """Search CloudWatch logs using Log Insights query.

    Args:
        log_group: CloudWatch log group name
        query: CloudWatch Log Insights query
        hours_back: How many hours back to search
    """
    logs = boto3.client('logs', region_name=REGION)
    end_time = int(datetime.now(timezone.utc).timestamp())
    start_time = end_time - (hours_back * 3600)

    response = logs.start_query(
        logGroupName=log_group,
        startTime=start_time,
        endTime=end_time,
        queryString=query
    )

    query_id = response['queryId']

    import time
    while True:
        result = logs.get_query_results(queryId=query_id)
        if result['status'] == 'Complete':
            break
        time.sleep(1)

    results = []
    for row in result.get('results', [])[:20]:
        entry = {field['field']: field['value'] for field in row}
        results.append(entry)

    return json.dumps(results, indent=2)

@tool
def get_error_patterns(log_group: str, hours_back: int = 1) -> str:
    """Find the most common error patterns in a log group.

    Args:
        log_group: CloudWatch log group name
        hours_back: How many hours back to analyze
    """
    query = """
    filter @message like /ERROR|Exception|FATAL/
    | stats count(*) as error_count by @message
    | sort error_count desc
    | limit 10
    """
    return search_logs(log_group, query, hours_back)

logs_agent = Agent(
    model=model,
    tools=[search_logs, get_error_patterns],
    system_prompt="""You are a log analysis specialist. When investigating an incident:
1. Search for errors and exceptions in the relevant time window
2. Identify recurring patterns
3. Look for the first occurrence of the error (root cause timeline)
4. Summarize findings with specific log entries and timestamps"""
)

# === METRICS AGENT ===

@tool
def get_metric(namespace: str, metric_name: str, dimensions: list,
               stat: str = "Average", period: int = 60, hours_back: int = 1) -> str:
    """Query a CloudWatch metric.

    Args:
        namespace: CloudWatch namespace (e.g., AWS/EC2, AWS/ECS)
        metric_name: Metric name (e.g., CPUUtilization)
        dimensions: List of dimension dicts with Name and Value
        stat: Statistic (Average, Sum, Maximum, Minimum, p99)
        period: Period in seconds
        hours_back: How many hours back to query
    """
    cw = boto3.client('cloudwatch', region_name=REGION)
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours_back)

    response = cw.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        StartTime=start,
        EndTime=end,
        Period=period,
        Statistics=[stat]
    )

    datapoints = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
    results = [{
        'timestamp': dp['Timestamp'].isoformat(),
        'value': dp[stat]
    } for dp in datapoints]

    return json.dumps(results, indent=2)

@tool
def check_alarms(state_filter: str = "ALARM") -> str:
    """List CloudWatch alarms in a given state.

    Args:
        state_filter: Alarm state (ALARM, OK, INSUFFICIENT_DATA)
    """
    cw = boto3.client('cloudwatch', region_name=REGION)
    response = cw.describe_alarms(StateValue=state_filter)

    alarms = [{
        'name': a['AlarmName'],
        'metric': a.get('MetricName', 'N/A'),
        'reason': a.get('StateReason', 'N/A')[:200]
    } for a in response['MetricAlarms'][:20]]

    return json.dumps(alarms, indent=2)

metrics_agent = Agent(
    model=model,
    tools=[get_metric, check_alarms],
    system_prompt="""You are a metrics analysis specialist. When investigating an incident:
1. Check which CloudWatch alarms are firing
2. Query relevant metrics (CPU, memory, error rates, latency)
3. Identify anomalies by comparing current values to baselines
4. Report specific numbers and timestamps"""
)

# === KUBERNETES AGENT ===

@tool
def describe_pods(namespace: str = "default", label_selector: str = "") -> str:
    """Get pod status from EKS via CloudWatch Container Insights.

    Args:
        namespace: Kubernetes namespace
        label_selector: Label selector to filter pods
    """
    logs = boto3.client('logs', region_name=REGION)
    end_time = int(datetime.now(timezone.utc).timestamp())
    start_time = end_time - 3600

    query = f"""
    filter kubernetes.namespace_name = "{namespace}"
    | filter @message like /pod/
    | stats count(*) as count by kubernetes.pod_name, kubernetes.container_name
    | sort count desc
    | limit 20
    """

    try:
        response = logs.start_query(
            logGroupName='/aws/containerinsights/cluster/performance',
            startTime=start_time,
            endTime=end_time,
            queryString=query
        )
        import time
        query_id = response['queryId']
        while True:
            result = logs.get_query_results(queryId=query_id)
            if result['status'] == 'Complete':
                break
            time.sleep(1)

        return json.dumps([
            {field['field']: field['value'] for field in row}
            for row in result.get('results', [])
        ], indent=2)
    except Exception as e:
        return f"Error querying container insights: {e}"

k8s_agent = Agent(
    model=model,
    tools=[describe_pods],
    system_prompt="""You are a Kubernetes specialist. When investigating an incident:
1. Check pod status and restart counts
2. Identify pods in CrashLoopBackOff or Error states
3. Look for resource pressure (CPU/memory limits)
4. Report specific pod names and states"""
)

# === RUNBOOK AGENT ===

@tool
def search_runbooks(query: str) -> str:
    """Search runbooks stored in S3 for relevant procedures.

    Args:
        query: Search query describing the incident type
    """
    s3 = boto3.client('s3', region_name=REGION)
    bucket = os.getenv("RUNBOOK_BUCKET", "my-runbooks-bucket")

    try:
        # List runbooks and find relevant ones
        response = s3.list_objects_v2(Bucket=bucket, Prefix="runbooks/")
        runbooks = []
        for obj in response.get('Contents', []):
            if obj['Key'].endswith('.md'):
                runbooks.append(obj['Key'])

        # Read matching runbooks
        results = []
        for key in runbooks[:10]:
            obj = s3.get_object(Bucket=bucket, Key=key)
            content = obj['Body'].read().decode('utf-8')[:2000]
            if any(term.lower() in content.lower() for term in query.split()):
                results.append({'runbook': key, 'excerpt': content[:500]})

        return json.dumps(results, indent=2) if results else "No matching runbooks found."
    except Exception as e:
        return f"Error searching runbooks: {e}"

runbook_agent = Agent(
    model=model,
    tools=[search_runbooks],
    system_prompt="""You are a runbook specialist. When investigating an incident:
1. Search for runbooks matching the incident symptoms
2. Extract the most relevant remediation steps
3. Adapt procedures to the specific situation
4. Provide step-by-step instructions"""
)
```

### Step 3: Build the Supervisor Agent

```python
@tool
def investigate_logs(question: str) -> str:
    """Delegate a log analysis question to the Logs Agent.

    Args:
        question: The log investigation question
    """
    response = logs_agent(question)
    return str(response)

@tool
def investigate_metrics(question: str) -> str:
    """Delegate a metrics analysis question to the Metrics Agent.

    Args:
        question: The metrics investigation question
    """
    response = metrics_agent(question)
    return str(response)

@tool
def investigate_kubernetes(question: str) -> str:
    """Delegate a Kubernetes investigation to the K8s Agent.

    Args:
        question: The Kubernetes investigation question
    """
    response = k8s_agent(question)
    return str(response)

@tool
def find_runbook(incident_description: str) -> str:
    """Find relevant runbooks for an incident.

    Args:
        incident_description: Description of the incident
    """
    response = runbook_agent(incident_description)
    return str(response)

supervisor = Agent(
    model=model,
    tools=[investigate_logs, investigate_metrics, investigate_kubernetes, find_runbook],
    system_prompt="""You are an SRE incident supervisor. When an incident is reported:

1. ASSESS: Understand the symptoms and affected services
2. INVESTIGATE: Delegate to specialist agents in parallel:
   - Logs Agent: Search for errors and patterns
   - Metrics Agent: Check alarms and metric anomalies
   - Kubernetes Agent: Inspect pod and cluster state
   - Runbook Agent: Find relevant procedures
3. CORRELATE: Combine findings into a coherent picture
4. RECOMMEND: Provide actionable remediation steps with priority

Structure your response as:
## Incident Summary
## Findings
### Logs Analysis
### Metrics Analysis
### Infrastructure State
## Root Cause Assessment
## Recommended Actions (ordered by priority)
## Relevant Runbooks"""
)
```

### Step 4: Deploy to Runtime

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint()
async def handle_incident(request):
    incident = request.get("incident", "")
    severity = request.get("severity", "medium")
    session_id = request.get("session_id", "incident-default")

    prompt = f"[Severity: {severity}] Incident report: {incident}"
    response = supervisor(prompt)
    return {"analysis": str(response)}

if __name__ == "__main__":
    app.run()
```

Deploy with 8-hour timeout for extended incidents:

```bash
agentcore deploy --name sre-assistant --memory 2048 --timeout 28800
```

### Step 5: Run It

```bash
agentcore invoke '{"incident": "API latency spike on payments service. P99 went from 200ms to 5s starting 10 minutes ago. Error rate climbing.", "severity": "high", "session_id": "INC-2024-001"}'
```

Expected output:
```
## Incident Summary
Payment service experiencing latency spike with climbing error rate.

## Findings
### Logs Analysis
- First error at 02:47 UTC: "Connection pool exhausted" in payments-service
- 847 errors in last 10 minutes, all related to database connections
...

### Metrics Analysis
- P99 latency: 200ms → 5,200ms (26x increase)
- Error rate: 0.1% → 12.3%
- CPU: Normal (45%)
- Active DB connections: 100/100 (max pool)
...

## Root Cause Assessment
Database connection pool exhaustion causing cascading failures...

## Recommended Actions
1. **Immediate**: Increase connection pool size from 100 to 200
2. **Short-term**: Restart pods to clear stale connections
3. **Investigation**: Check for connection leaks in recent deployments
```

## Architecture

```
          PagerDuty / Slack Alert
                   |
                   v
         [Supervisor Agent]
         (AgentCore Runtime)
         8-hour session support
        /     |      |      \
       v      v      v       v
    [Logs]  [Metrics] [K8s]  [Runbook]
    Agent    Agent    Agent   Agent
      |        |       |       |
      v        v       v       v
  CloudWatch  CW     Container S3
  Logs      Metrics  Insights  Runbooks
```

## Key Benefits

### Long-Running Incident Support
Runtime supports sessions up to 8 hours. Complex incidents that span shift changes can be managed by a single persistent agent session.

### Specialist Decomposition
Each sub-agent has focused tools and prompts for its domain. The supervisor coordinates without needing to be expert in everything.

### Real AWS Integration
Every tool calls real AWS APIs — CloudWatch Logs, CloudWatch Metrics, Container Insights, S3. No simulated data.

## Pricing

- **Runtime**: CPU consumption only (I/O wait while sub-agents think is free)
- **Bedrock**: Per-token pricing for Claude model calls
- **CloudWatch**: Standard query and API pricing
- **Free tier**: $200 for new AgentCore customers

## Troubleshooting

**Issue: Sub-agent calls timeout**
Solution: Increase the Runtime timeout. Long CloudWatch Log Insights queries can take 30+ seconds.

**Issue: Too many concurrent model calls**
Solution: Bedrock has per-model rate limits. Add retry logic with exponential backoff to sub-agent tool calls.

## Next Steps

Start with the supervisor and one specialist (Logs Agent). Add specialists incrementally as you validate the pattern. Connect to your incident management system (PagerDuty, OpsGenie) via Gateway for automated incident creation and updates.

📚 **Documentation**: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/
💻 **Full runnable code**: `articles/examples/runtime/`
🔧 **GitHub samples**: https://github.com/awslabs/amazon-bedrock-agentcore-samples/

#AWS #AI #AgentCore #SRE #MultiAgent #Tutorial
