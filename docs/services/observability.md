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

### View Traces

```python
from bedrock_agentcore.observability import ObservabilityClient

obs = ObservabilityClient()

# Get traces for an agent
traces = obs.list_traces(
    agent_id="my-agent",
    start_time=datetime.now() - timedelta(hours=1),
    end_time=datetime.now()
)

for trace in traces:
    print(f"Trace: {trace.trace_id}")
    print(f"  Duration: {trace.duration_ms}ms")
    print(f"  Spans: {len(trace.spans)}")
```

### Inspect Trace Details

```python
# Get detailed trace
trace = obs.get_trace(trace_id="abc123")

for span in trace.spans:
    print(f"{span.name}: {span.duration_ms}ms")
    if span.attributes:
        for key, value in span.attributes.items():
            print(f"  {key}: {value}")
```

### Add Custom Spans

```python
from bedrock_agentcore.observability import tracer

# Add custom instrumentation
with tracer.start_span("custom-operation") as span:
    span.set_attribute("operation.type", "data-processing")
    span.set_attribute("records.count", 100)

    # Your code here
    result = process_data()

    span.set_attribute("operation.status", "success")
```

### Create Dashboard

```python
# Create CloudWatch dashboard
dashboard = obs.create_dashboard(
    name="my-agent-dashboard",
    agent_id="my-agent",
    widgets=[
        {"type": "session_count", "period": 300},
        {"type": "latency_p99", "period": 300},
        {"type": "error_rate", "period": 300},
        {"type": "tool_usage", "period": 300}
    ]
)

print(f"Dashboard URL: {dashboard.url}")
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
