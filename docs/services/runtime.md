# Runtime

> Serverless hosting with microVM isolation for AI agents

## Overview

AgentCore Runtime is the foundational service that hosts and executes your agent code. It transforms any local agent into a cloud-native deployment with just a few lines of code, regardless of the underlying framework.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Your Request                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AgentCore Runtime                           │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │   MicroVM 1   │  │   MicroVM 2   │  │   MicroVM N   │       │
│  │  (Session A)  │  │  (Session B)  │  │  (Session N)  │       │
│  │               │  │               │  │               │       │
│  │  Isolated:    │  │  Isolated:    │  │  Isolated:    │       │
│  │  • CPU        │  │  • CPU        │  │  • CPU        │       │
│  │  • Memory     │  │  • Memory     │  │  • Memory     │       │
│  │  • Filesystem │  │  • Filesystem │  │  • Filesystem │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

### MicroVM Session Isolation

Every user session runs in a dedicated microVM with complete isolation:

| Resource | Isolation Level |
|----------|----------------|
| CPU | Dedicated per session |
| Memory | Isolated, sanitized on termination |
| Filesystem | Ephemeral, destroyed after session |
| Network | Session-scoped |

After session completion, the entire microVM is terminated and memory is sanitized, providing **deterministic security** even with non-deterministic AI processes.

### Extended Execution Time

| Use Case | Duration |
|----------|----------|
| Real-time interactions | Fast cold starts |
| Long-running workloads | Up to **8 hours** |
| Multi-agent collaboration | Extended sessions |
| Complex reasoning | As needed |

### Consumption-Based Pricing

```
┌─────────────────────────────────────────────────────────────────┐
│  Agent Execution Timeline                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ████ Processing ████ │ ░░░░ I/O Wait ░░░░ │ ████ Processing    │
│       (charged)       │      (FREE!)       │     (charged)      │
│                                                                  │
│  Typical agent: 30-70% of execution time is I/O wait            │
└─────────────────────────────────────────────────────────────────┘
```

**Billing model**:
- CPU: Charged only during active processing
- Memory: Billed based on peak consumption per second
- I/O Wait: **No CPU charges** while waiting for LLM responses, API calls, or database queries

### Enhanced Payload Handling

- **Maximum payload**: 100MB
- **Supported modalities**: Text, images, audio, video

### Streaming Responses

`invoke_agent_runtime` returns a chunked HTTP response (`text/event-stream`) that you iterate over, not a separate WebSocket protocol - see the streaming example under [Invoke with boto3](#invoke-with-boto3) below.

| Protocol | Use Case |
|----------|----------|
| HTTP API | Request/response, including chunked streaming |
| MCP / A2A / AGUI | Tool-calling and agent-to-agent/UI protocols (`protocolConfiguration.serverProtocol`) |

---

## Technical Specifications

| Specification | Value |
|--------------|-------|
| Minimum memory | 128MB |
| Maximum session duration | 8 hours |
| Maximum payload size | 100MB |
| Deployment options | Direct code, ECR container |
| Protocols | MCP, HTTP, A2A, AGUI |

---

## Quick Start

### Deploy with CLI

`create` takes `-p`/`--project-name`, not a positional name, and project names are alphanumeric only (no `-`/`_`); `invoke`'s payload is JSON, and the agent name (if needed) is `--agent`/`-a`:

```bash
# Create agent project
agentcore create --project-name myagent --agent-framework Strands --model-provider Bedrock

# Deploy
cd myagent
agentcore deploy

# Invoke
agentcore invoke '{"prompt": "Hello!"}'
```

### Deploy with SDK

`bedrock_agentcore.runtime` exports `AgentCoreRuntimeClient`, not `RuntimeClient`, and it manages runtime *resources* (create/update/delete agent runtimes and endpoints) - it has no `create_agent()` or `invoke()` method. Deploying is what `agentcore deploy` (above) does under the hood; invoking a deployed agent is a data-plane call (below).

### Invoke with boto3

Only `bedrock-agentcore` is a real data-plane service - there is no `bedrock-agentcore-runtime`, and the operation is `invoke_agent_runtime`, not `invoke_agent`:

```python
import json
import boto3

client = boto3.client('bedrock-agentcore', region_name='us-east-1')

response = client.invoke_agent_runtime(
    agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:123456789012:agent-runtime/myagent-abc123',
    runtimeSessionId='session-123',
    payload=json.dumps({'prompt': 'Hello, agent!'}).encode(),
)

# Process streaming response
if "text/event-stream" in response.get("contentType", ""):
    for line in response["response"].iter_lines(chunk_size=10):
        if line:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                print(line[6:])
```

---

## Agent Code Structure

### Strands Framework

```python
# agent.py
from strands import Agent
from strands.models import BedrockModel

def create_agent():
    model = BedrockModel(
        model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0"
    )

    agent = Agent(
        model=model,
        system_prompt="You are a helpful assistant.",
        tools=[...]
    )

    return agent

# AgentCore Runtime entry point
agent = create_agent()
```

### LangGraph Framework

```python
# agent.py
from langgraph.graph import StateGraph, START, END
from langchain_aws import ChatBedrock

def create_agent():
    model = ChatBedrock(
        model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0"
    )

    # Define graph
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_edge(START, "agent")
    workflow.add_edge("agent", END)

    return workflow.compile()

agent = create_agent()
```

---

## Configuration

### .bedrock_agentcore.yaml

The config file is `.bedrock_agentcore.yaml` (not `agentcore.yaml`), generated by `agentcore create`/`agentcore configure`, not hand-authored from a flat schema. It nests everything under the agent's name, and keys like memory mode, network mode, and session lifecycle live several levels deep (verified against a live `agentcore create` run, 0.3.10):

```yaml
default_agent: myagent_Agent
agents:
  myagent_Agent:
    name: myagent_Agent
    entrypoint: /path/to/myagent/src/main.py
    deployment_type: direct_code_deploy
    aws:
      execution_role_auto_create: true
      region: null  # set via `agentcore configure --region`
      network_configuration:
        network_mode: PUBLIC
      protocol_configuration:
        server_protocol: HTTP
      observability:
        enabled: true
      lifecycle_configuration:
        idle_runtime_session_timeout: null  # set via `agentcore configure --idle-timeout`
        max_lifetime: null                  # set via `agentcore configure --max-lifetime`
    memory:
      mode: NO_MEMORY  # set via `agentcore configure` or `create --memory`
```

Edit these through `agentcore configure` rather than by hand where a flag exists - see the [CLI reference](../../research/01-runtime.md#agentcore-create) for the full flag list.

---

## Security

### Session Isolation

```
┌─────────────────────────────────────────────────────────────────┐
│  Security Boundary                                               │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  MicroVM                                                    ││
│  │  ┌─────────────────────────────────────────────────────────┐││
│  │  │  User Session                                           │││
│  │  │  • Isolated CPU allocation                              │││
│  │  │  • Isolated memory space                                │││
│  │  │  • Ephemeral filesystem                                 │││
│  │  │  • Session-scoped network                               │││
│  │  └─────────────────────────────────────────────────────────┘││
│  │                                                             ││
│  │  On termination:                                            ││
│  │  • MicroVM destroyed                                        ││
│  │  • Memory sanitized                                         ││
│  │  • Filesystem deleted                                       ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Built-in Authentication

Runtime integrates with [AgentCore Identity](identity.md) for:
- **Inbound auth**: Verify users calling your agent
- **Outbound auth**: Access external services

---

## When to Use Runtime

| Scenario | Recommendation |
|----------|----------------|
| Deploy agents to production | ✅ Use Runtime |
| Need session isolation | ✅ Use Runtime |
| Long-running sessions (>15 min) | ✅ Use Runtime |
| Avoid infrastructure management | ✅ Use Runtime |
| Optimize costs with I/O wait | ✅ Use Runtime |
| Need full control over infrastructure | Consider self-managed |

---

## Related Services

| Service | Integration |
|---------|-------------|
| [Memory](memory.md) | Store conversation context |
| [Gateway](gateway.md) | Connect to tools and APIs |
| [Identity](identity.md) | Authentication and credentials |
| [Observability](observability.md) | Monitor agent performance |

---

## Resources

- [Runtime Developer Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html)
- [Detailed Research](../../research/01-runtime.md)
- [Runtime Examples](../../articles/examples/runtime/)
