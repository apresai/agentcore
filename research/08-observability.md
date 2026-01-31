# AgentCore Observability

## Overview

AgentCore Observability helps you trace, debug, and monitor agent performance in production environments. It provides detailed visualizations of each step in the agent workflow.

## Key Capabilities

### Workflow Visualization
- Inspect agent execution path
- Audit intermediate outputs
- Debug performance bottlenecks and failures

### Real-Time Visibility
Access dashboards powered by Amazon CloudWatch with:
- Session count
- Latency
- Duration
- Token usage
- Error rates

### Metadata & Filtering
- Rich metadata tagging
- Filtering for issue investigation
- Quality maintenance at scale

### OpenTelemetry Compatible
- Standardized OTEL-compatible telemetry format
- Integrate with existing monitoring stacks

## Built-in Metrics

By default, AgentCore outputs metrics for:
- Agents
- Gateway resources
- Memory resources

For memory resources, optional spans and log data can be enabled.

## Custom Instrumentation

Instrument your agent code to provide:
- Additional span and trace data
- Custom metrics
- Custom logs

## Data Storage

All metrics, spans, and logs are stored in Amazon CloudWatch:
- View in CloudWatch console
- Download via AWS CLI
- Access through AWS SDKs

## Observability Dashboard

For agent runtime data, CloudWatch console provides:
- Trace visualizations
- Custom span metrics graphs
- Error breakdowns
- And more

## Framework Support

Supports evaluations on sessions, traces, and spans from:
- Strands Agent
- LangGraph

Instrumented using:
- OpenTelemetry
- OpenInference

## Pricing

Follows Amazon CloudWatch pricing for:
- Data ingestion
- Storage
- Queries
