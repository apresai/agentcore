# AgentCore Observability

## Quick Reference

### Key Metrics

| Metric | Description | Unit | Resource Types |
|--------|-------------|------|----------------|
| `Invocations` | Total API requests | Count | Runtime, Gateway, Memory |
| `Latency` | Time to first response token | Milliseconds | Runtime, Gateway |
| `Duration` | End-to-end processing time | Milliseconds | Gateway |
| `SessionCount` | Total agent sessions | Count | Runtime |
| `Throttles` | Rate-limited requests (429) | Count | All |
| `SystemErrors` | Server-side errors (5xx) | Count | All |
| `UserErrors` | Client-side errors (4xx) | Count | All |
| `CPUUsed-vCPUHours` | CPU consumption | vCPU-Hours | Runtime |
| `MemoryUsed-GBHours` | Memory consumption | GB-Hours | Runtime |

### Log Group Locations

| Resource Type | Log Group Format |
|---------------|------------------|
| Runtime (stdout/stderr) | `/aws/bedrock-agentcore/runtimes/<agent_id>-<endpoint_name>/[runtime-logs] <UUID>` |
| Runtime (OTEL structured) | `/aws/bedrock-agentcore/runtimes/<agent_id>-<endpoint_name>/otel-rt-logs` |
| Gateway | `/aws/vendedlogs/bedrock-agentcore/gateway/APPLICATION_LOGS/<gateway_id>` |
| Memory | `/aws/vendedlogs/bedrock-agentcore/memory/APPLICATION_LOGS/<memory_id>` |
| Traces/Spans | `/aws/spans/default` |

### OTEL Environment Variables

```bash
# Required for AgentCore-hosted agents
AGENT_OBSERVABILITY_ENABLED=true
OTEL_PYTHON_DISTRO=aws_distro
OTEL_PYTHON_CONFIGURATOR=aws_configurator

# Resource attributes
OTEL_RESOURCE_ATTRIBUTES=service.name=<agent-name>,aws.log.group.names=/aws/bedrock-agentcore/runtimes/<agent-id>

# Exporter configuration
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_TRACES_EXPORTER=otlp
OTEL_EXPORTER_OTLP_LOGS_HEADERS=x-aws-log-group=/aws/bedrock-agentcore/runtimes/<agent-id>,x-aws-log-stream=runtime-logs,x-aws-metric-namespace=bedrock-agentcore
```

### CloudWatch Namespace

- **Metrics**: `Bedrock-AgentCore`
- **Traces**: CloudWatch Transaction Search
- **Dashboard**: CloudWatch GenAI Observability

---

## Overview

AgentCore Observability enables tracing, debugging, and monitoring of AI agent performance in production environments. It provides detailed visualizations of agent workflows, real-time visibility into operational metrics, and access to dashboards powered by Amazon CloudWatch.

Key capabilities include:

- **Workflow Visualization**: Inspect execution paths, audit intermediate outputs, debug bottlenecks
- **Real-Time Dashboards**: Session counts, latency, duration, token usage, error rates
- **OpenTelemetry Compatible**: Standardized OTEL-compatible telemetry format
- **Framework Support**: Strands, LangGraph, LangChain, CrewAI with automatic instrumentation

All observability data is stored in Amazon CloudWatch, accessible via the console, AWS CLI, or SDKs.

---

## Core Concepts

### Sessions, Traces, and Spans Hierarchy

AgentCore observability follows a three-tiered hierarchical model:

```
Session (highest level)
  |
  +-- Trace 1 (request-response cycle)
  |     |
  |     +-- Span 1.1 (parse input)
  |     +-- Span 1.2 (retrieve context)
  |     +-- Span 1.3 (generate response)
  |
  +-- Trace 2 (next interaction)
        |
        +-- Span 2.1 (tool invocation)
        +-- Span 2.2 (LLM call)
```

#### Sessions

A session represents a complete interaction context between a user and an agent. Sessions:

- Encapsulate the entire conversation flow
- Maintain state and context across multiple exchanges
- Have unique identifiers (`session.id`)
- Provide isolation between different user interactions
- Enable context persistence and conversation history tracking

#### Traces

A trace records a single request-response cycle, capturing:

- Request details (timestamps, input parameters, context)
- Processing steps and execution sequence
- Tool invocations with input/output and execution times
- Resource utilization metrics
- Error information and recovery attempts
- Response generation details

#### Spans

Spans are discrete, measurable units of work with:

- **Operation name**: The specific function being executed
- **Timestamps**: Exact start and end times
- **Parent-child relationships**: Hierarchical nesting
- **Tags and attributes**: Contextual metadata
- **Events**: Significant occurrences within the span
- **Status**: Success, failure, or other completion states

### OpenTelemetry Compatibility

AgentCore uses OpenTelemetry (OTEL) as the standard telemetry format:

- **Traces**: W3C traceparent format supported
- **Metrics**: Enhanced Metric Format (EMF) for CloudWatch
- **Logs**: Structured OTEL logs with correlation IDs

Supported instrumentation libraries:
- [OpenInference](https://github.com/Arize-ai/openinference)
- [Openllmetry](https://github.com/traceloop/openllmetry)
- [OpenLit](https://github.com/openlit/openlit)
- [Traceloop](https://www.traceloop.com/docs/introduction)

---

## Configuration

### Enabling CloudWatch Transaction Search

Transaction Search must be enabled once per AWS account to view traces and spans.

**Console Method:**

1. Open [CloudWatch Console](https://console.aws.amazon.com/cloudwatch)
2. Navigate to **Application Signals (APM)** > **Transaction Search**
3. Choose **Enable Transaction Search**
4. Select checkbox to ingest spans as structured logs
5. Choose **Save**

**API Method:**

```bash
# Step 1: Add resource policy for X-Ray
aws logs put-resource-policy \
  --policy-name TransactionSearchPolicy \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "TransactionSearchXRayAccess",
      "Effect": "Allow",
      "Principal": {"Service": "xray.amazonaws.com"},
      "Action": "logs:PutLogEvents",
      "Resource": [
        "arn:aws:logs:us-east-1:123456789012:log-group:aws/spans:*",
        "arn:aws:logs:us-east-1:123456789012:log-group:/aws/application-signals/data:*"
      ],
      "Condition": {
        "ArnLike": {"aws:SourceArn": "arn:aws:xray:us-east-1:123456789012:*"},
        "StringEquals": {"aws:SourceAccount": "123456789012"}
      }
    }]
  }'

# Step 2: Configure trace destination
aws xray update-trace-segment-destination --destination CloudWatchLogs

# Step 3 (Optional): Set sampling percentage
aws xray update-indexing-rule \
  --name "Default" \
  --rule '{"Probabilistic": {"DesiredSamplingPercentage": 100}}'
```

### AWS Distro for OpenTelemetry (ADOT) Setup

Add ADOT to your agent's dependencies:

```bash
# requirements.txt
aws-opentelemetry-distro>=0.10.0
boto3
strands-agents[otel]  # For Strands framework
```

Or install directly:

```bash
pip install aws-opentelemetry-distro>=0.10.0 boto3
```

Run with auto-instrumentation:

```bash
opentelemetry-instrument python my_agent.py
```

For containerized environments:

```dockerfile
CMD ["opentelemetry-instrument", "python", "main.py"]
```

### Enabling Observability for Non-Runtime Agents

For agents running outside AgentCore Runtime:

```bash
# AWS environment variables
export AWS_ACCOUNT_ID=123456789012
export AWS_DEFAULT_REGION=us-east-1
export AWS_REGION=us-east-1

# OpenTelemetry environment variables
export AGENT_OBSERVABILITY_ENABLED=true
export OTEL_PYTHON_DISTRO=aws_distro
export OTEL_PYTHON_CONFIGURATOR=aws_configurator
export OTEL_RESOURCE_ATTRIBUTES="service.name=my-agent,aws.log.group.names=/aws/bedrock-agentcore/runtimes/my-agent-id"
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_TRACES_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_LOGS_HEADERS="x-aws-log-group=/aws/bedrock-agentcore/runtimes/my-agent-id,x-aws-log-stream=runtime-logs,x-aws-metric-namespace=bedrock-agentcore"
```

---

## Built-in Metrics

### Runtime Metrics

Runtime metrics are batched at 1-minute intervals and available in CloudWatch GenAI Observability.

| Metric | Description | Statistics | Unit |
|--------|-------------|------------|------|
| `Invocations` | Total API requests | Sum | Count |
| `Invocations (aggregated)` | Total invocations across all resources | Sum | Count |
| `Throttles` | Requests throttled (HTTP 429) | Sum | Count |
| `SystemErrors` | Server-side errors | Sum | Count |
| `UserErrors` | Client-side errors | Sum | Count |
| `Latency` | End-to-end processing time | Avg, Min, Max, p50, p90, p99 | Milliseconds |
| `TotalErrors` | Combined error count (% of invocations) | Sum | Count |
| `SessionCount` | Total agent sessions | Sum | Count |
| `Sessions (aggregated)` | Total sessions across all resources | Sum | Count |

**WebSocket-only Metrics:**

| Metric | Description | Statistics | Unit |
|--------|-------------|------------|------|
| `ActiveStreamingConnections` | Current WebSocket connections | Sum (1-min) | Count |
| `InboundStreamingBytesProcessed` | Bytes received from clients | Sum | Bytes |
| `OutboundStreamingBytesProcessed` | Bytes sent to clients | Sum | Bytes |

**Resource Usage Metrics:**

| Metric | Dimensions | Description |
|--------|------------|-------------|
| `CPUUsed-vCPUHours` | Service; Service, Resource; Service, Resource, Name | Total vCPU consumed |
| `MemoryUsed-GBHours` | Service; Service, Resource; Service, Resource, Name | Total memory consumed |

### Memory Metrics

Memory metrics are published under the `Bedrock-AgentCore` namespace:

| Metric | Description | Unit |
|--------|-------------|------|
| `Invocations` | CreateEvent/RetrieveMemoryRecord calls | Count |
| `Latency` | Operation response time | Milliseconds |
| `Errors` | Failed operations | Count |
| `NumberOfMemoryRecords` | Records during extraction/consolidation | Count |

### Gateway Metrics

Gateway metrics include invocation and usage statistics:

**Invocation Metrics (Dimensions: Operation, Protocol, Method, Resource, Name):**

| Metric | Description | Statistics | Unit |
|--------|-------------|------------|------|
| `Invocations` | Total Data Plane API requests | Sum | Count |
| `Throttles` | Rate-limited requests | Sum | Count |
| `SystemErrors` | 5xx errors | Sum | Count |
| `UserErrors` | 4xx errors (except 429) | Sum | Count |
| `Latency` | Time to first response token | Avg, Min, Max, p50, p90, p99 | Milliseconds |
| `Duration` | Complete processing time | Avg, Min, Max, p50, p90, p99 | Milliseconds |
| `TargetExecutionTime` | Target (Lambda/OpenAPI) execution time | Avg, Min, Max, p50, p90, p99 | Milliseconds |

**Usage Metrics:**

| Metric | Description | Unit |
|--------|-------------|------|
| `TargetType` | Requests by target type (MCP, Lambda, OpenAPI) | Count |

### Policy Metrics

Policy metrics track authorization decisions:

| Metric | Description | Unit |
|--------|-------------|------|
| `Invocations` | Policy evaluation requests | Count |
| `SystemErrors` | Server-side errors (5xx) | Count |
| `UserErrors` | Client-side errors (4xx) | Count |
| `Latency` | Evaluation time | Milliseconds |
| `AllowDecisions` | ALLOW decisions | Count |
| `DenyDecisions` | DENY decisions | Count |
| `TotalMismatchedPolicies` | Policies with missing/mismatched attributes | Count |
| `DeterminingPolicies` | Policies that determined the decision | Count |
| `NoDeterminingPolicies` | Denials due to no determining policies | Count |

**Policy Dimensions:**

| Dimension | Description |
|-----------|-------------|
| `OperationName` | `AuthorizeAction` or `PartiallyAuthorizeActions` |
| `PolicyEngine` | Policy Engine identifier |
| `Policy` | Policy identifier |
| `TargetResource` | Gateway resource identifier |
| `ToolName` | Tool name |
| `Mode` | `LOG_ONLY` or `ENFORCE` |

### Identity Metrics

Identity service metrics track authentication operations:

**Authorization Metrics (Namespace: AWS/Bedrock-AgentCore):**

| Metric | Dimensions | Description |
|--------|------------|-------------|
| `WorkloadAccessTokenFetchSuccess` | WorkloadIdentity, Directory, Operation | Successful token fetches |
| `WorkloadAccessTokenFetchFailures` | WorkloadIdentity, Directory, Operation, ExceptionType | Failed token fetches |
| `WorkloadAccessTokenFetchThrottles` | WorkloadIdentity, Directory, Operation | Throttled token fetches |

**Resource Access Metrics:**

| Metric | Description |
|--------|-------------|
| `ResourceAccessTokenFetchSuccess` | Successful OAuth2 token fetches |
| `ResourceAccessTokenFetchFailures` | Failed OAuth2 token fetches |
| `ApiKeyFetchSuccess` | Successful API key fetches |
| `ApiKeyFetchFailures` | Failed API key fetches |

---

## Custom Instrumentation

### Adding Custom Spans

Create custom spans using OpenTelemetry:

```python
from opentelemetry import trace
from opentelemetry.trace import SpanKind

tracer = trace.get_tracer("my-agent")

def process_user_query(query: str):
    with tracer.start_as_current_span(
        "process_user_query",
        kind=SpanKind.INTERNAL,
        attributes={
            "query.length": len(query),
            "query.type": "natural_language"
        }
    ) as span:
        # Parse input
        with tracer.start_as_current_span("parse_input") as parse_span:
            parsed = parse_query(query)
            parse_span.set_attribute("tokens.count", len(parsed.tokens))

        # Generate response
        with tracer.start_as_current_span("generate_response") as gen_span:
            response = generate(parsed)
            gen_span.set_attribute("response.length", len(response))
            gen_span.add_event("response_generated", {
                "model": "claude-3-5-sonnet"
            })

        return response
```

### Custom Metrics

Emit custom metrics using OpenTelemetry:

```python
from opentelemetry import metrics

meter = metrics.get_meter("my-agent")

# Counter for tool invocations
tool_counter = meter.create_counter(
    name="tool_invocations",
    description="Number of tool invocations",
    unit="1"
)

# Histogram for response times
response_histogram = meter.create_histogram(
    name="response_time",
    description="Response generation time",
    unit="ms"
)

def invoke_tool(tool_name: str):
    start_time = time.time()
    result = execute_tool(tool_name)

    # Record metrics
    tool_counter.add(1, {"tool.name": tool_name, "status": "success"})
    response_histogram.record(
        (time.time() - start_time) * 1000,
        {"tool.name": tool_name}
    )
    return result
```

### Structured Logging

Add structured logs with trace correlation:

```python
import logging
import json
from opentelemetry import trace

class OTELFormatter(logging.Formatter):
    def format(self, record):
        span = trace.get_current_span()
        span_context = span.get_span_context()

        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "trace_id": format(span_context.trace_id, "032x"),
            "span_id": format(span_context.span_id, "016x"),
            "service": "my-agent"
        }
        return json.dumps(log_record)

# Configure logger
logger = logging.getLogger("my-agent")
handler = logging.StreamHandler()
handler.setFormatter(OTELFormatter())
logger.addHandler(handler)

# Usage
logger.info("Processing user request", extra={"user_id": "12345"})
```

### Session ID Propagation

Propagate session IDs across distributed traces:

```python
from opentelemetry import baggage
from opentelemetry.context import attach

def start_session(session_id: str):
    # Set session ID in OTEL baggage
    ctx = baggage.set_baggage("session.id", session_id)
    attach(ctx)
```

---

## CloudWatch Integration

### Viewing Data in CloudWatch

**GenAI Observability Dashboard:**

1. Open [CloudWatch GenAI Observability](https://console.aws.amazon.com/cloudwatch/home#gen-ai-observability)
2. View tailored dashboards with graphs and visualizations
3. Explore error breakdowns and trace visualizations
4. Drill into individual sessions and traces

**Logs:**

1. Open CloudWatch Console > **Logs** > **Log groups**
2. Search for your agent's log group:
   - Standard logs: `/aws/bedrock-agentcore/runtimes/<agent_id>-<endpoint_name>/[runtime-logs]`
   - OTEL logs: `/aws/bedrock-agentcore/runtimes/<agent_id>-<endpoint_name>/otel-rt-logs`

**Traces:**

1. Open CloudWatch Console > **Transaction Search**
2. Filter by service name or other criteria
3. Select a trace to view the execution graph

### CloudWatch Log Insights Queries

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
      count(*) as invocations
by aws.endpoint.name
| sort avg_latency desc
```

**Session activity analysis:**

```sql
fields @timestamp, session.id, aws.operation.name
| filter session.id != ""
| stats count(*) as operations by session.id
| sort operations desc
| limit 20
```

**Error rate by operation:**

```sql
fields @timestamp, aws.operation.name, error_type
| stats count(*) as total,
        sum(case when error_type != "" then 1 else 0 end) as errors
by aws.operation.name
| display aws.operation.name, total, errors, (errors * 100.0 / total) as error_rate
```

**Tool invocation performance:**

```sql
filter aws.operation.name = "InvokeGateway"
| stats avg(latency_ms) as avg_latency,
        percentile(latency_ms, 95) as p95_latency,
        percentile(latency_ms, 99) as p99_latency
by tool.name
| sort avg_latency desc
```

### Setting Up Alarms

**High Error Rate Alarm:**

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "AgentCore-HighErrorRate" \
  --alarm-description "Alarm when error rate exceeds 5%" \
  --metric-name "SystemErrors" \
  --namespace "Bedrock-AgentCore" \
  --statistic "Sum" \
  --dimensions "Name=Resource,Value=arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/my-agent" \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 5 \
  --comparison-operator "GreaterThanThreshold" \
  --alarm-actions "arn:aws:sns:us-east-1:123456789012:alerts"
```

**High Latency Alarm:**

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "AgentCore-HighLatency" \
  --alarm-description "Alarm when p99 latency exceeds 10 seconds" \
  --metric-name "Latency" \
  --namespace "Bedrock-AgentCore" \
  --extended-statistic "p99" \
  --dimensions "Name=Resource,Value=arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/my-agent" \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 10000 \
  --comparison-operator "GreaterThanThreshold" \
  --alarm-actions "arn:aws:sns:us-east-1:123456789012:alerts"
```

**Throttling Alarm:**

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "AgentCore-Throttling" \
  --alarm-description "Alarm when throttling occurs" \
  --metric-name "Throttles" \
  --namespace "Bedrock-AgentCore" \
  --statistic "Sum" \
  --period 60 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator "GreaterThanOrEqualToThreshold" \
  --alarm-actions "arn:aws:sns:us-east-1:123456789012:alerts"
```

---

## Code Examples

### Example 1: Basic Observability Setup (Strands)

```python
"""
Basic observability setup for a Strands agent deployed to AgentCore Runtime.
"""
from strands import Agent, tool
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Initialize AgentCore app
app = BedrockAgentCoreApp()

# Define a custom tool
@tool
def get_weather(location: str) -> str:
    """Get current weather for a location."""
    return f"Weather in {location}: Sunny, 72F"

# Configure model and agent
model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
)

agent = Agent(
    model=model,
    tools=[get_weather],
    system_prompt="You're a helpful assistant that provides weather information."
)

@app.entrypoint
def invoke_agent(payload):
    """Agent entrypoint - automatically instrumented with OTEL."""
    user_input = payload.get("prompt")
    response = agent(user_input)
    return response.message['content'][0]['text']

if __name__ == "__main__":
    app.run()
```

**Deploy with observability:**

```python
from bedrock_agentcore_starter_toolkit import Runtime

runtime = Runtime()
runtime.configure(
    entrypoint="agent.py",
    agent_name="weather-agent",
    auto_create_execution_role=True,
    auto_create_ecr=True,
    requirements_file="requirements.txt",  # Include aws-opentelemetry-distro
    region="us-east-1"
)
runtime.launch()
```

### Example 2: Custom Spans with Context

```python
"""
Adding custom spans with rich context for debugging.
"""
from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode
import time

tracer = trace.get_tracer("my-agent", "1.0.0")

class AgentWithCustomSpans:
    def __init__(self, model_client):
        self.model = model_client

    def process_request(self, user_input: str, session_id: str) -> str:
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
                # Intent classification
                intent = self._classify_intent(user_input)
                root_span.set_attribute("intent.type", intent)

                # Tool selection
                tools = self._select_tools(intent)
                root_span.set_attribute("tools.selected", len(tools))

                # Execute tools
                tool_results = self._execute_tools(tools, user_input)

                # Generate response
                response = self._generate_response(user_input, tool_results)

                root_span.set_status(Status(StatusCode.OK))
                return response

            except Exception as e:
                root_span.set_status(Status(StatusCode.ERROR, str(e)))
                root_span.record_exception(e)
                raise

    def _classify_intent(self, input_text: str) -> str:
        with tracer.start_as_current_span(
            "agent.classify_intent",
            attributes={"input.preview": input_text[:100]}
        ) as span:
            # Intent classification logic
            intent = "weather_query"  # Example
            span.add_event("intent_classified", {"intent": intent})
            return intent

    def _select_tools(self, intent: str) -> list:
        with tracer.start_as_current_span(
            "agent.select_tools",
            attributes={"intent": intent}
        ) as span:
            tools = ["weather_api", "location_service"]
            span.set_attribute("tools.names", tools)
            return tools

    def _execute_tools(self, tools: list, input_text: str) -> dict:
        results = {}
        for tool in tools:
            with tracer.start_as_current_span(
                f"tool.execute.{tool}",
                kind=SpanKind.CLIENT,
                attributes={"tool.name": tool}
            ) as span:
                start = time.time()
                result = self._call_tool(tool, input_text)
                duration = (time.time() - start) * 1000

                span.set_attribute("tool.duration_ms", duration)
                span.set_attribute("tool.result.size", len(str(result)))
                results[tool] = result
        return results

    def _generate_response(self, input_text: str, context: dict) -> str:
        with tracer.start_as_current_span(
            "llm.generate",
            kind=SpanKind.CLIENT,
            attributes={
                "llm.model": "claude-3-5-sonnet",
                "llm.context.size": len(str(context))
            }
        ) as span:
            response = self.model.generate(input_text, context)

            span.set_attribute("llm.response.tokens", response.token_count)
            span.set_attribute("llm.response.length", len(response.text))
            span.add_event("generation_complete", {
                "finish_reason": response.finish_reason
            })
            return response.text
```

### Example 3: Strands Framework Integration

```python
"""
Complete Strands agent with observability integration.
"""
from strands import Agent, tool
from strands.models import BedrockModel
from strands.telemetry import OTELConfig
from opentelemetry import trace
import boto3

# Configure OTEL for Strands
otel_config = OTELConfig(
    service_name="strands-weather-agent",
    enable_tracing=True,
    enable_metrics=True
)

tracer = trace.get_tracer("strands-weather-agent")

@tool
def get_current_weather(location: str, units: str = "fahrenheit") -> dict:
    """
    Get current weather for a location.

    Args:
        location: City name or coordinates
        units: Temperature units (fahrenheit or celsius)
    """
    with tracer.start_as_current_span(
        "tool.get_current_weather",
        attributes={
            "weather.location": location,
            "weather.units": units
        }
    ) as span:
        # Simulated weather data
        weather_data = {
            "location": location,
            "temperature": 72 if units == "fahrenheit" else 22,
            "units": units,
            "conditions": "sunny",
            "humidity": 45
        }
        span.set_attribute("weather.temperature", weather_data["temperature"])
        span.set_attribute("weather.conditions", weather_data["conditions"])
        return weather_data

@tool
def get_forecast(location: str, days: int = 5) -> list:
    """
    Get weather forecast for a location.

    Args:
        location: City name or coordinates
        days: Number of days to forecast (1-10)
    """
    with tracer.start_as_current_span(
        "tool.get_forecast",
        attributes={
            "forecast.location": location,
            "forecast.days": days
        }
    ) as span:
        # Simulated forecast
        forecast = [
            {"day": i, "high": 75 - i, "low": 55 - i, "conditions": "partly cloudy"}
            for i in range(days)
        ]
        span.set_attribute("forecast.count", len(forecast))
        return forecast

# Create agent with Bedrock model
model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    region_name="us-east-1"
)

agent = Agent(
    model=model,
    tools=[get_current_weather, get_forecast],
    system_prompt="""You are a helpful weather assistant.
    Use the available tools to provide accurate weather information.
    Always mention the location and conditions clearly."""
)

def main():
    # Invoke with session tracking
    session_id = "session-12345"

    with tracer.start_as_current_span(
        "agent.session",
        attributes={"session.id": session_id}
    ):
        response = agent("What's the weather like in Seattle?")
        print(response.message['content'][0]['text'])

if __name__ == "__main__":
    main()
```

### Example 4: LangGraph Tracing Integration

```python
"""
LangGraph agent with AgentCore observability.
"""
from langgraph.graph import StateGraph, END
from langchain_aws import ChatBedrock
from langchain.schema import HumanMessage, AIMessage
from opentelemetry import trace
from opentelemetry.instrumentation.langchain import LangChainInstrumentor
from typing import TypedDict, Annotated
import operator

# Enable automatic LangChain instrumentation
LangChainInstrumentor().instrument()

tracer = trace.get_tracer("langgraph-agent")

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    next_action: str

def create_research_agent():
    """Create a LangGraph research agent with observability."""

    llm = ChatBedrock(
        model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        region_name="us-east-1"
    )

    def classify_intent(state: AgentState) -> AgentState:
        """Classify the user's intent."""
        with tracer.start_as_current_span(
            "node.classify_intent",
            attributes={"messages.count": len(state["messages"])}
        ) as span:
            last_message = state["messages"][-1]

            # Simple intent classification
            if "weather" in last_message.content.lower():
                next_action = "weather"
            elif "search" in last_message.content.lower():
                next_action = "search"
            else:
                next_action = "chat"

            span.set_attribute("intent.classified", next_action)
            return {"messages": [], "next_action": next_action}

    def process_weather(state: AgentState) -> AgentState:
        """Handle weather-related queries."""
        with tracer.start_as_current_span("node.process_weather") as span:
            response = llm.invoke([
                HumanMessage(content="Provide weather information based on: " +
                            state["messages"][-1].content)
            ])
            span.set_attribute("response.length", len(response.content))
            return {"messages": [response], "next_action": "end"}

    def process_search(state: AgentState) -> AgentState:
        """Handle search queries."""
        with tracer.start_as_current_span("node.process_search") as span:
            response = llm.invoke([
                HumanMessage(content="Search and provide information for: " +
                            state["messages"][-1].content)
            ])
            span.set_attribute("response.length", len(response.content))
            return {"messages": [response], "next_action": "end"}

    def process_chat(state: AgentState) -> AgentState:
        """Handle general chat."""
        with tracer.start_as_current_span("node.process_chat") as span:
            response = llm.invoke(state["messages"])
            span.set_attribute("response.length", len(response.content))
            return {"messages": [response], "next_action": "end"}

    def route_action(state: AgentState) -> str:
        """Route to appropriate node based on intent."""
        return state["next_action"]

    # Build the graph
    workflow = StateGraph(AgentState)

    workflow.add_node("classify", classify_intent)
    workflow.add_node("weather", process_weather)
    workflow.add_node("search", process_search)
    workflow.add_node("chat", process_chat)

    workflow.set_entry_point("classify")

    workflow.add_conditional_edges(
        "classify",
        route_action,
        {
            "weather": "weather",
            "search": "search",
            "chat": "chat"
        }
    )

    workflow.add_edge("weather", END)
    workflow.add_edge("search", END)
    workflow.add_edge("chat", END)

    return workflow.compile()

def invoke_with_tracing(user_input: str, session_id: str):
    """Invoke the LangGraph agent with full tracing."""
    agent = create_research_agent()

    with tracer.start_as_current_span(
        "langgraph.invoke",
        attributes={
            "session.id": session_id,
            "input.length": len(user_input)
        }
    ) as span:
        result = agent.invoke({
            "messages": [HumanMessage(content=user_input)],
            "next_action": ""
        })

        span.set_attribute("result.messages", len(result["messages"]))
        return result

if __name__ == "__main__":
    response = invoke_with_tracing(
        "What's the weather in Seattle?",
        session_id="lg-session-001"
    )
    print(response)
```

### Example 5: Comprehensive Alerting Setup

```python
"""
Set up comprehensive CloudWatch alerting for AgentCore agents.
"""
import boto3
import json

def create_agentcore_alerts(
    agent_arn: str,
    sns_topic_arn: str,
    agent_name: str
):
    """Create a comprehensive set of CloudWatch alarms for an AgentCore agent."""

    cloudwatch = boto3.client('cloudwatch')

    alarms = [
        # Error rate alarm
        {
            "AlarmName": f"{agent_name}-HighErrorRate",
            "AlarmDescription": "Error rate exceeds 5% of invocations",
            "MetricName": "SystemErrors",
            "Namespace": "Bedrock-AgentCore",
            "Statistic": "Sum",
            "Period": 300,
            "EvaluationPeriods": 2,
            "Threshold": 5,
            "ComparisonOperator": "GreaterThanThreshold",
            "Dimensions": [{"Name": "Resource", "Value": agent_arn}],
            "AlarmActions": [sns_topic_arn],
            "TreatMissingData": "notBreaching"
        },
        # High latency alarm (p99 > 10s)
        {
            "AlarmName": f"{agent_name}-HighLatency",
            "AlarmDescription": "P99 latency exceeds 10 seconds",
            "MetricName": "Latency",
            "Namespace": "Bedrock-AgentCore",
            "ExtendedStatistic": "p99",
            "Period": 300,
            "EvaluationPeriods": 2,
            "Threshold": 10000,
            "ComparisonOperator": "GreaterThanThreshold",
            "Dimensions": [{"Name": "Resource", "Value": agent_arn}],
            "AlarmActions": [sns_topic_arn],
            "TreatMissingData": "notBreaching"
        },
        # Throttling alarm
        {
            "AlarmName": f"{agent_name}-Throttling",
            "AlarmDescription": "Requests being throttled",
            "MetricName": "Throttles",
            "Namespace": "Bedrock-AgentCore",
            "Statistic": "Sum",
            "Period": 60,
            "EvaluationPeriods": 1,
            "Threshold": 1,
            "ComparisonOperator": "GreaterThanOrEqualToThreshold",
            "Dimensions": [{"Name": "Resource", "Value": agent_arn}],
            "AlarmActions": [sns_topic_arn],
            "TreatMissingData": "notBreaching"
        },
        # Low invocation alarm (potential downtime)
        {
            "AlarmName": f"{agent_name}-LowInvocations",
            "AlarmDescription": "Invocations dropped significantly",
            "MetricName": "Invocations",
            "Namespace": "Bedrock-AgentCore",
            "Statistic": "Sum",
            "Period": 300,
            "EvaluationPeriods": 3,
            "Threshold": 10,
            "ComparisonOperator": "LessThanThreshold",
            "Dimensions": [{"Name": "Resource", "Value": agent_arn}],
            "AlarmActions": [sns_topic_arn],
            "TreatMissingData": "breaching"
        },
        # High CPU usage
        {
            "AlarmName": f"{agent_name}-HighCPU",
            "AlarmDescription": "CPU usage is high",
            "MetricName": "CPUUsed-vCPUHours",
            "Namespace": "Bedrock-AgentCore",
            "Statistic": "Sum",
            "Period": 300,
            "EvaluationPeriods": 2,
            "Threshold": 10,  # Adjust based on expected usage
            "ComparisonOperator": "GreaterThanThreshold",
            "Dimensions": [
                {"Name": "Service", "Value": "AgentCore.Runtime"},
                {"Name": "Resource", "Value": agent_arn}
            ],
            "AlarmActions": [sns_topic_arn],
            "TreatMissingData": "notBreaching"
        }
    ]

    created_alarms = []
    for alarm_config in alarms:
        try:
            cloudwatch.put_metric_alarm(**alarm_config)
            created_alarms.append(alarm_config["AlarmName"])
            print(f"Created alarm: {alarm_config['AlarmName']}")
        except Exception as e:
            print(f"Failed to create alarm {alarm_config['AlarmName']}: {e}")

    return created_alarms

def create_dashboard(agent_name: str, agent_arn: str, region: str = "us-east-1"):
    """Create a CloudWatch dashboard for the agent."""

    cloudwatch = boto3.client('cloudwatch')

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
                    "title": "Resource Usage",
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

    cloudwatch.put_dashboard(
        DashboardName=f"{agent_name}-Observability",
        DashboardBody=json.dumps(dashboard_body)
    )

    print(f"Dashboard created: {agent_name}-Observability")
    return f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#dashboards:name={agent_name}-Observability"

if __name__ == "__main__":
    agent_arn = "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/my-agent"
    sns_topic = "arn:aws:sns:us-east-1:123456789012:agent-alerts"

    # Create alarms
    alarms = create_agentcore_alerts(agent_arn, sns_topic, "my-agent")

    # Create dashboard
    dashboard_url = create_dashboard("my-agent", agent_arn)
    print(f"Dashboard URL: {dashboard_url}")
```

---

## Integration Patterns

### Integration with AgentCore Runtime

Runtime observability is automatic when deployed via the starter toolkit:

```python
from bedrock_agentcore_starter_toolkit import Runtime

runtime = Runtime()
runtime.configure(
    entrypoint="agent.py",
    requirements_file="requirements.txt",  # Must include aws-opentelemetry-distro
    agent_name="my-agent",
    region="us-east-1"
)
runtime.launch()

# Invoke with custom tracing headers
response = runtime.invoke(
    {"prompt": "Hello"},
    headers={
        "X-Amzn-Trace-Id": "Root=1-5759e988-bd862e3fe1be46a994272793;Parent=53995c3f42cd8ad8;Sampled=1",
        "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": "session-12345"
    }
)
```

### Integration with AgentCore Memory

Enable memory observability through log delivery configuration:

```python
import boto3

logs_client = boto3.client('logs')
agentcore = boto3.client('bedrock-agentcore')

# Configure log delivery for memory resource
agentcore.update_memory(
    memoryId="my-memory-id",
    logDeliveryConfiguration={
        "logType": "APPLICATION_LOGS",
        "destination": {
            "cloudWatchLogs": {
                "logGroupArn": "arn:aws:logs:us-east-1:123456789012:log-group:/aws/vendedlogs/bedrock-agentcore/memory/APPLICATION_LOGS/my-memory-id"
            }
        }
    }
)
```

### Integration with AgentCore Gateway

Gateway observability requires enabling log destinations:

```python
# Enable gateway logging
agentcore.update_gateway(
    gatewayId="my-gateway-id",
    logDeliveryConfiguration={
        "logType": "APPLICATION_LOGS",
        "destination": {
            "cloudWatchLogs": {
                "logGroupArn": "arn:aws:logs:us-east-1:123456789012:log-group:/aws/vendedlogs/bedrock-agentcore/gateway/APPLICATION_LOGS/my-gateway-id"
            }
        }
    }
)
```

Correlate gateway spans with logs using `span_id` and `trace_id`:

```json
{
    "resource_arn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/my-gateway",
    "event_timestamp": 1759370851622,
    "body": {
        "isError": false,
        "log": "Started processing request with requestId: 1",
        "requestBody": "{...}"
    },
    "trace_id": "160fc209c3befef4857ab1007d041db0",
    "span_id": "81346de89c725310"
}
```

### Integration with AgentCore Identity

Enable identity observability for OAuth2 and API key operations:

```python
# Headers for identity observability
headers = {
    "X-Amzn-Trace-Id": "Root=1-5759e988-bd862e3fe1be46a994272793;Parent=53995c3f42cd8ad8;Sampled=1"
}

# Supported APIs:
# - GetWorkloadAccessToken
# - GetWorkloadAccessTokenForJWT
# - GetResourceOauth2Token
# - GetResourceAPIKey
```

### Integration with AgentCore Policy

Policy metrics and spans are available through Gateway observability:

```python
# Policy metrics dimensions
dimensions = {
    "OperationName": "AuthorizeAction",
    "PolicyEngine": "my-policy-engine",
    "Mode": "ENFORCE"  # or "LOG_ONLY"
}

# View policy decisions in spans:
# - aws.agentcore.policy.authorization_decision (ALLOW/DENY)
# - aws.agentcore.policy.determining_policies
# - aws.agentcore.policy.mismatched_policies
```

### Integration with Built-in Tools

Code Interpreter and Browser support custom tracing headers:

```python
# Supported APIs:
# - StartCodeInterpreterSession
# - InvokeCodeInterpreter
# - StopCodeInterpreterSession
# - StartBrowserSession
# - StopBrowserSession

headers = {
    "X-Amzn-Trace-Id": "Root=...",
    "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
}
```

---

## Best Practices

1. **Enable CloudWatch Transaction Search First**
   - Complete one-time setup before deploying agents
   - Wait 10 minutes after enabling for spans to become available

2. **Use Consistent Session IDs**
   - Reuse the same session ID for related requests
   - Set via `X-Amzn-Bedrock-AgentCore-Runtime-Session-Id` header or OTEL baggage

3. **Implement Distributed Tracing**
   - Include `X-Amzn-Trace-Id` or `traceparent` headers
   - Enables end-to-end visibility across services

4. **Add Meaningful Custom Attributes**
   - Include business context (user IDs, request types)
   - Add tool names and parameters to spans
   - Track model versions and configurations

5. **Configure Sampling Appropriately**
   - Use 100% sampling during development
   - Reduce to 10-20% in high-volume production
   - Use probabilistic sampling via `UpdateIndexingRule`

6. **Set Up Proactive Alerting**
   - Create alarms for error rates, latency, throttling
   - Configure SNS notifications for on-call teams
   - Use anomaly detection for traffic patterns

7. **Monitor Resource Usage**
   - Track `CPUUsed-vCPUHours` and `MemoryUsed-GBHours`
   - Set alerts for unexpected usage spikes
   - Use metrics for cost optimization

8. **Structure Logs for Analysis**
   - Use JSON format with consistent fields
   - Include trace and span IDs for correlation
   - Add contextual metadata (tool names, user IDs)

9. **Create Custom Dashboards**
   - Build service-specific dashboards
   - Include error rates, latency percentiles, throughput
   - Add business metrics alongside technical metrics

10. **Use Log Insights for Investigation**
    - Create saved queries for common patterns
    - Use aggregations to identify trends
    - Correlate logs with traces using IDs

---

## Troubleshooting

### Common Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| `No traces appearing` | Transaction Search not enabled | Enable CloudWatch Transaction Search in console or via API |
| `Missing spans` | ADOT not configured | Add `aws-opentelemetry-distro` to requirements, run with `opentelemetry-instrument` |
| `Session ID not propagating` | Baggage not attached | Use `baggage.set_baggage("session.id", id)` and `attach(ctx)` |
| `Metrics not in CloudWatch` | Wrong namespace | Verify metrics are under `Bedrock-AgentCore` namespace |
| `Logs not appearing` | Log delivery not configured | Configure log destinations for memory/gateway resources |
| `ThrottlingException` | Rate limit exceeded | Review quotas, implement exponential backoff |
| `ValidationException` | Invalid request format | Check request parameters match API requirements |
| `ResourceNotFoundException` | Resource doesn't exist | Verify resource ARN and region |
| `AccessDeniedException` | Missing permissions | Check IAM policies for CloudWatch, X-Ray, Logs |
| `Trace context lost` | Headers not propagated | Include trace headers in all service calls |

### Debugging Tips

**Verify ADOT Configuration:**

```bash
# Check environment variables
env | grep OTEL

# Expected output:
# OTEL_PYTHON_DISTRO=aws_distro
# OTEL_TRACES_EXPORTER=otlp
# AGENT_OBSERVABILITY_ENABLED=true
```

**Check Log Group Permissions:**

```bash
aws logs describe-log-groups --log-group-name-prefix /aws/bedrock-agentcore
```

**Verify Transaction Search Status:**

```bash
aws xray get-trace-segment-destination
# Should return: {"Destination": "CloudWatchLogs"}
```

**Test Span Ingestion:**

```python
from opentelemetry import trace

tracer = trace.get_tracer("test")
with tracer.start_as_current_span("test-span") as span:
    span.set_attribute("test", "value")
    print(f"Trace ID: {span.get_span_context().trace_id}")
```

**Query Recent Spans:**

```sql
-- CloudWatch Log Insights query
fields @timestamp, @message
| filter @logStream like /spans/
| sort @timestamp desc
| limit 10
```

---

## Limits & Quotas

| Resource | Limit | Notes |
|----------|-------|-------|
| Span retention (CloudWatch) | 15 months | Standard CloudWatch Logs retention |
| Metric resolution | 1 minute | Runtime metrics batched at 1-minute intervals |
| Resource usage data delay | Up to 60 minutes | CPU/memory metrics may be delayed |
| Sampling percentage | 1-100% | Configurable via `UpdateIndexingRule` |
| Log group name prefix | `/aws/vendedlogs/` | Required for memory/gateway custom log groups |
| Trace ID format (X-Ray) | 35 characters | `Root=1-{8hex}-{24hex}` |
| Trace ID format (W3C) | 32 hex characters | Version-TraceID-ParentID-Flags |
| Span attributes | 128 per span | OpenTelemetry limit |
| Attribute value length | 4096 characters | OpenTelemetry limit |
| Log event size | 256 KB | CloudWatch Logs limit |

---

## Pricing

AgentCore Observability uses Amazon CloudWatch pricing:

| Component | Pricing |
|-----------|---------|
| **Logs Ingestion** | $0.50 per GB |
| **Logs Storage** | $0.03 per GB/month |
| **Metrics** | $0.30 per metric/month (first 10K), $0.10 per metric/month (next 240K) |
| **Metric API Requests** | $0.01 per 1,000 GetMetricData requests |
| **Dashboards** | $3.00 per dashboard/month |
| **Alarms** | $0.10 per standard alarm/month |
| **Transaction Search** | 1% of traces indexed free, additional indexing varies |
| **Log Insights Queries** | $0.005 per GB scanned |

**Cost Optimization Tips:**

- Reduce sampling percentage for high-volume production workloads
- Use Log Insights queries sparingly on large log groups
- Set appropriate log retention periods
- Filter out debug-level logs in production
- Use metric filters instead of querying logs for common patterns

---

## Related Services

- [AgentCore Runtime](./02-runtime.md) - Serverless agent hosting
- [AgentCore Memory](./03-memory.md) - Context persistence
- [AgentCore Gateway](./04-gateway.md) - API and tool management
- [AgentCore Identity](./05-identity.md) - Authentication and authorization
- [AgentCore Policy](./09-policy.md) - Access control
- [AgentCore Evaluations](./10-evaluations.md) - Quality assessment

**External Resources:**

- [CloudWatch GenAI Observability Console](https://console.aws.amazon.com/cloudwatch/home#gen-ai-observability)
- [AWS Distro for OpenTelemetry (ADOT)](https://aws-otel.github.io/)
- [OpenTelemetry GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [CloudWatch Transaction Search Documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Transaction-Search.html)
- [AgentCore Observability AWS Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html)
