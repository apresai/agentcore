Your AI agent hallucinated in production. It took three days to find out. Here's how to catch it in seconds:

![AgentCore Observability](images/overview-article.webp)

Production agents fail in ways traditional software doesn't. A REST API either returns 200 or 500. An agent can return 200, sound confident, and be completely wrong. It can call the wrong tool, misinterpret context, or loop through reasoning steps that go nowhere. Without visibility into what your agent is actually doing — every span, every tool call, every decision — you're flying blind.

AgentCore Observability gives you that visibility through **OpenTelemetry (OTEL) integration** backed by Amazon CloudWatch. Every agent invocation produces structured traces with spans for each step: intent classification, tool selection, LLM calls, and response generation. You get built-in metrics under the `Bedrock-AgentCore` namespace, custom instrumentation with standard OTEL APIs, and CloudWatch dashboards that show you exactly where things break.

## Prerequisites

- AWS account with Bedrock AgentCore access
- Python 3.10+ installed
- boto3 and OpenTelemetry SDKs (`pip install boto3 opentelemetry-api opentelemetry-sdk`)
- AWS credentials configured
- CloudWatch Transaction Search enabled (one-time account setup)

## Environment Setup

```bash
# Install dependencies
pip install boto3 opentelemetry-api opentelemetry-sdk aws-opentelemetry-distro

# OTEL environment variables for AgentCore-hosted agents
export AGENT_OBSERVABILITY_ENABLED=true
export OTEL_PYTHON_DISTRO=aws_distro
export OTEL_PYTHON_CONFIGURATOR=aws_configurator
export OTEL_RESOURCE_ATTRIBUTES="service.name=my-agent,aws.log.group.names=/aws/bedrock-agentcore/runtimes/my-agent-id"
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_TRACES_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_LOGS_HEADERS="x-aws-log-group=/aws/bedrock-agentcore/runtimes/my-agent-id,x-aws-log-stream=runtime-logs,x-aws-metric-namespace=bedrock-agentcore"

# AWS region
export AWS_REGION=us-east-1
```

## Implementation

### Add Custom Spans and Metrics to Your Agent

```python
import time
from opentelemetry import trace, metrics
from opentelemetry.trace import SpanKind, Status, StatusCode

# Initialize tracer and meter
tracer = trace.get_tracer("my-agent", "1.0.0")
meter = metrics.get_meter("my-agent")

# Custom metrics for production monitoring
tool_counter = meter.create_counter(
    name="tool_invocations",
    description="Number of tool invocations by tool name",
    unit="1"
)
response_histogram = meter.create_histogram(
    name="response_time_ms",
    description="Agent response generation time",
    unit="ms"
)

def process_request(user_input: str, session_id: str) -> str:
    """Process a user request with full OTEL instrumentation."""
    with tracer.start_as_current_span(
        "agent.process_request",
        kind=SpanKind.SERVER,
        attributes={
            "session.id": session_id,
            "input.length": len(user_input),
            "agent.version": "1.0.0"
        }
    ) as root_span:
        try:
            # Classify intent — each step gets its own span
            with tracer.start_as_current_span(
                "agent.classify_intent",
                attributes={"input.preview": user_input[:100]}
            ) as intent_span:
                intent = classify(user_input)
                intent_span.set_attribute("intent.type", intent)
                intent_span.add_event("intent_classified", {"intent": intent})

            # Execute tools with per-tool spans
            with tracer.start_as_current_span(
                "agent.execute_tools",
                kind=SpanKind.CLIENT,
                attributes={"intent": intent}
            ) as tool_span:
                start = time.time()
                tool_results = execute_tools(intent, user_input)
                duration_ms = (time.time() - start) * 1000

                tool_span.set_attribute("tools.count", len(tool_results))
                tool_span.set_attribute("tools.duration_ms", duration_ms)
                tool_counter.add(1, {"tool.name": intent, "status": "success"})

            # Generate LLM response
            with tracer.start_as_current_span(
                "llm.generate",
                kind=SpanKind.CLIENT,
                attributes={"llm.model": "claude-haiku-4-5-20251001"}
            ) as llm_span:
                gen_start = time.time()
                response = generate_response(user_input, tool_results)
                gen_ms = (time.time() - gen_start) * 1000

                llm_span.set_attribute("llm.response.length", len(response))
                response_histogram.record(gen_ms, {"step": "llm_generate"})

            root_span.set_status(Status(StatusCode.OK))
            return response

        except Exception as e:
            root_span.set_status(Status(StatusCode.ERROR, str(e)))
            root_span.record_exception(e)
            tool_counter.add(1, {"tool.name": "unknown", "status": "error"})
            raise
```

### Create CloudWatch Alarms with boto3

```python
import boto3

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

agent_arn = "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/my-agent"
sns_topic_arn = "arn:aws:sns:us-east-1:123456789012:agent-alerts"

# Error rate alarm — fires when system errors exceed threshold
cloudwatch.put_metric_alarm(
    AlarmName="MyAgent-HighErrorRate",
    AlarmDescription="Agent system errors exceed 5 in 5 minutes",
    MetricName="SystemErrors",
    Namespace="Bedrock-AgentCore",
    Statistic="Sum",
    Period=300,
    EvaluationPeriods=2,
    Threshold=5,
    ComparisonOperator="GreaterThanThreshold",
    Dimensions=[{"Name": "Resource", "Value": agent_arn}],
    AlarmActions=[sns_topic_arn],
    TreatMissingData="notBreaching"
)

# P99 latency alarm — catches performance degradation
cloudwatch.put_metric_alarm(
    AlarmName="MyAgent-HighLatency",
    AlarmDescription="P99 latency exceeds 10 seconds",
    MetricName="Latency",
    Namespace="Bedrock-AgentCore",
    ExtendedStatistic="p99",
    Period=300,
    EvaluationPeriods=2,
    Threshold=10000,
    ComparisonOperator="GreaterThanThreshold",
    Dimensions=[{"Name": "Resource", "Value": agent_arn}],
    AlarmActions=[sns_topic_arn],
    TreatMissingData="notBreaching"
)

# Throttling alarm — detects capacity issues immediately
cloudwatch.put_metric_alarm(
    AlarmName="MyAgent-Throttling",
    AlarmDescription="Requests are being throttled",
    MetricName="Throttles",
    Namespace="Bedrock-AgentCore",
    Statistic="Sum",
    Period=60,
    EvaluationPeriods=1,
    Threshold=1,
    ComparisonOperator="GreaterThanOrEqualToThreshold",
    Dimensions=[{"Name": "Resource", "Value": agent_arn}],
    AlarmActions=[sns_topic_arn],
    TreatMissingData="notBreaching"
)

print("Alarms created: HighErrorRate, HighLatency, Throttling")
```

### Create a CloudWatch Dashboard

```python
import json

agent_arn = "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/my-agent"
region = "us-east-1"

dashboard_body = {
    "widgets": [
        {
            "type": "metric",
            "x": 0, "y": 0, "width": 12, "height": 6,
            "properties": {
                "title": "Invocations & Errors",
                "region": region,
                "metrics": [
                    ["Bedrock-AgentCore", "Invocations", "Resource", agent_arn],
                    [".", "SystemErrors", ".", "."],
                    [".", "UserErrors", ".", "."],
                    [".", "Throttles", ".", "."]
                ],
                "period": 60,
                "stat": "Sum"
            }
        },
        {
            "type": "metric",
            "x": 12, "y": 0, "width": 12, "height": 6,
            "properties": {
                "title": "Latency (p50, p90, p99)",
                "region": region,
                "metrics": [
                    ["Bedrock-AgentCore", "Latency", "Resource", agent_arn, {"stat": "p50"}],
                    ["...", {"stat": "p90"}],
                    ["...", {"stat": "p99"}]
                ],
                "period": 60
            }
        },
        {
            "type": "metric",
            "x": 0, "y": 6, "width": 12, "height": 6,
            "properties": {
                "title": "Session Count",
                "region": region,
                "metrics": [
                    ["Bedrock-AgentCore", "SessionCount", "Resource", agent_arn]
                ],
                "period": 60,
                "stat": "Sum"
            }
        },
        {
            "type": "metric",
            "x": 12, "y": 6, "width": 12, "height": 6,
            "properties": {
                "title": "Resource Usage (CPU & Memory)",
                "region": region,
                "metrics": [
                    ["Bedrock-AgentCore", "CPUUsed-vCPUHours", "Service", "AgentCore.Runtime", "Resource", agent_arn],
                    [".", "MemoryUsed-GBHours", ".", ".", ".", "."]
                ],
                "period": 300,
                "stat": "Sum"
            }
        }
    ]
}

cloudwatch = boto3.client('cloudwatch', region_name=region)
cloudwatch.put_dashboard(
    DashboardName="MyAgent-Observability",
    DashboardBody=json.dumps(dashboard_body)
)

print(f"Dashboard: https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#dashboards:name=MyAgent-Observability")
```

### Debug Agent Reasoning with Log Insights

Use these CloudWatch Log Insights queries against your agent's log group to diagnose production issues.

**Find errors in the last hour:**

```sql
fields @timestamp, @message, error_type
| filter error_type != ""
| sort @timestamp desc
| limit 100
```

**Analyze latency by endpoint:**

```sql
stats avg(latency_ms) as avg_latency,
      max(latency_ms) as max_latency,
      percentile(latency_ms, 95) as p95_latency
by aws.endpoint.name
| sort avg_latency desc
```

**Trace tool invocation performance:**

```sql
filter aws.operation.name = "InvokeGateway"
| stats avg(latency_ms) as avg_latency,
        percentile(latency_ms, 99) as p99_latency,
        count(*) as calls
by tool.name
| sort avg_latency desc
```

**Track error rates by operation:**

```sql
fields @timestamp, aws.operation.name, error_type
| stats count(*) as total,
        sum(case when error_type != "" then 1 else 0 end) as errors
by aws.operation.name
| display aws.operation.name, total, errors, (errors * 100.0 / total) as error_rate_pct
```

## Key Benefits

- **Zero-config built-in metrics**: Invocations, latency, errors, sessions, and resource usage are tracked automatically under the `Bedrock-AgentCore` CloudWatch namespace with no extra code
- **Standard OTEL instrumentation**: Add custom spans and metrics using OpenTelemetry APIs you already know — no proprietary SDKs to learn
- **End-to-end trace correlation**: Session IDs, trace IDs, and span IDs connect across Runtime, Gateway, Memory, and Policy services so you can follow a single request through your entire agent stack

## Common Patterns

Teams typically start with the built-in metrics and alarms for error rate, latency, and throttling. As agents mature, they add custom spans around business-critical steps — intent classification, tool selection, and LLM generation — to identify exactly where reasoning breaks down. The Log Insights queries become essential for post-incident analysis: tracing a specific session through every tool call and LLM interaction to understand why an agent produced a bad response.

## Next Steps

Enable CloudWatch Transaction Search in your account, deploy your agent with `aws-opentelemetry-distro` in your requirements, and create the three core alarms (errors, latency, throttling). Add custom spans to your most critical agent steps, then build a dashboard to watch them in real time.

Documentation: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html
CloudWatch GenAI Observability: https://console.aws.amazon.com/cloudwatch/home#gen-ai-observability
GitHub samples: https://github.com/awslabs/amazon-bedrock-agentcore-samples/

#AWS #AI #AgentCore #Observability #CloudWatch #Developers
