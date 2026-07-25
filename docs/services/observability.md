# Observability

> OTEL-compatible tracing and monitoring for production agents

## Overview

AgentCore Observability provides visibility into how your agents behave in production. It offers detailed visualizations of each step in agent workflows, enabling you to inspect execution paths, audit intermediate outputs, and debug performance bottlenecks.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Your Agent                               │
│                                                                 │
│  ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐             │
│  │Step │──►│Step │──►│Step │──►│Step │──►│Step │             │
│  │  1  │   │  2  │   │  3  │   │  4  │   │  5  │             │
│  └──┬──┘   └──┬──┘   └──┬──┘   └──┬──┘   └──┬──┘             │
│     │        │        │        │        │                     │
└─────┼────────┼────────┼────────┼────────┼─────────────────────┘
      │        │        │        │        │
      ▼        ▼        ▼        ▼        ▼
┌─────────────────────────────────────────────────────────────────┐
│                  AgentCore Observability                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Trace Collection                      │   │
│  │                                                          │   │
│  │  • Spans with timing                                    │   │
│  │  • Metadata tags                                        │   │
│  │  • Error information                                    │   │
│  │  • Tool invocations                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │  CloudWatch   │  │   Dashboards  │  │    Alerts     │       │
│  │     Logs      │  │               │  │               │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## Built-in Metrics

### Runtime Metrics

| Metric | Description |
|--------|-------------|
| `SessionCount` | Active sessions |
| `SessionLatency` | Time to first response |
| `SessionDuration` | Total session time |
| `SessionErrors` | Error count |

### Gateway Metrics

| Metric | Description |
|--------|-------------|
| `ToolCallCount` | Tool invocations |
| `ToolCallLatency` | Tool response time |
| `ToolCallErrors` | Failed tool calls |

### Memory Metrics

| Metric | Description |
|--------|-------------|
| `MemoryOperations` | Read/write count |
| `MemoryLatency` | Operation latency |

## Quick Start

There is no `bedrock_agentcore.observability` module - Observability isn't a client-managed resource, it's the AgentCore Runtime automatically exporting OpenTelemetry traces/spans to CloudWatch when the OTEL environment variables in the Quick Reference above are set. Viewing traces goes through CloudWatch (console, Log Insights, or the `logs` boto3 client); adding custom instrumentation goes through the standard `opentelemetry` SDK.

### View Traces

```python
import time
import boto3

logs_client = boto3.client('logs', region_name='us-east-1')

# CloudWatch Logs Insights query against the shared trace/span destination
query = logs_client.start_query(
    logGroupName='aws/spans',
    startTime=int(time.time() - 3600),
    endTime=int(time.time()),
    queryString="""
        fields @timestamp, @message, error_type
        | filter error_type != ""
        | sort @timestamp desc
        | limit 100
    """,
)

# Poll until the query completes
while True:
    result = logs_client.get_query_results(queryId=query['queryId'])
    if result['status'] in ('Complete', 'Failed', 'Cancelled'):
        break
    time.sleep(1)

for row in result['results']:
    print({field['field']: field['value'] for field in row})
```

For a visual view (execution graph, error breakdowns, session drill-down), use the [CloudWatch GenAI Observability console](https://console.aws.amazon.com/cloudwatch/home#gen-ai-observability) instead of writing a query.

### Add Custom Spans

There is no `bedrock_agentcore.observability.tracer` - use the standard `opentelemetry` SDK directly; AgentCore's OTEL configuration (set via the environment variables above) picks up any span you create this way:

```python
from opentelemetry import trace

tracer = trace.get_tracer("my-agent")

with tracer.start_as_current_span("custom-operation") as span:
    span.set_attribute("operation.type", "data-processing")
    span.set_attribute("records.count", 100)

    # Your code here
    result = process_data()

    span.set_attribute("operation.status", "success")
```

### Create a Dashboard

There is no `create_dashboard()` on any AgentCore client - dashboards are a generic CloudWatch resource, created with the standard `cloudwatch` client:

```python
import json
import boto3

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

cloudwatch.put_dashboard(
    DashboardName='my-agent-dashboard',
    DashboardBody=json.dumps({
        "widgets": [
            {
                "type": "metric",
                "properties": {
                    "metrics": [["Bedrock-AgentCore", "SessionCount"], [".", "Latency"], [".", "SystemErrors"]],
                    "period": 300,
                    "stat": "Sum",
                    "region": "us-east-1",
                },
            }
        ]
    }),
)
```

## OTEL Integration

AgentCore emits OpenTelemetry-compatible telemetry:

```python
# Export to your OTEL collector
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Configure exporter
exporter = OTLPSpanExporter(
    endpoint="your-otel-collector:4317"
)

# AgentCore traces flow to your collector
```

## Debugging Workflow

```
1. Identify Issue
   └─► Check error rate metrics

2. Find Affected Traces
   └─► Filter by error status

3. Inspect Trace
   └─► View step-by-step execution

4. Identify Root Cause
   └─► Check span attributes, errors

5. Fix and Verify
   └─► Monitor metrics for improvement
```

## Pricing

- CloudWatch pricing for logs and metrics
- No additional AgentCore charge

## Related

- [Detailed Research](../../research/08-observability.md)
- [Observability Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html)
