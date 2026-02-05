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

### Bidirectional Streaming

| Protocol | Use Case |
|----------|----------|
| HTTP API | Simple request/response |
| WebSocket | Real-time bidirectional streaming |

---

## Technical Specifications

| Specification | Value |
|--------------|-------|
| Minimum memory | 128MB |
| Maximum session duration | 8 hours |
| Maximum payload size | 100MB |
| Deployment options | Direct code, ECR container |
| Protocols | MCP, A2A |

---

## Quick Start

### Deploy with CLI

```bash
# Create agent project
agentcore create my-agent

# Deploy
cd my-agent
agentcore deploy

# Invoke
agentcore invoke my-agent "Hello!"
```

### Deploy with SDK

```python
from bedrock_agentcore.runtime import RuntimeClient

runtime = RuntimeClient()

# Deploy agent
runtime.create_agent(
    name="my-agent",
    code_path="./agent",
    runtime="python3.11"
)

# Invoke
response = runtime.invoke(
    agent_id="my-agent",
    input="Hello, agent!"
)

print(response.output)
```

### Deploy with boto3

```python
import boto3

runtime = boto3.client('bedrock-agentcore-runtime')

# Invoke existing agent
response = runtime.invoke_agent(
    agentId='my-agent',
    input={'text': 'Hello, agent!'}
)

# Stream response
for event in response['body']:
    if 'chunk' in event:
        print(event['chunk']['content'], end='')
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
        model_id="anthropic.claude-3-sonnet-20240229-v1:0"
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
        model_id="anthropic.claude-3-sonnet-20240229-v1:0"
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

### agentcore.yaml

```yaml
name: my-agent
runtime: python3.11
memory: 512  # MB
timeout: 300  # seconds (default)
max_session_duration: 28800  # seconds (8 hours)

# Environment variables
environment:
  LOG_LEVEL: INFO
  MODEL_ID: anthropic.claude-3-sonnet-20240229-v1:0

# VPC configuration (optional)
vpc:
  subnet_ids:
    - subnet-12345678
  security_group_ids:
    - sg-12345678
```

---

## WebSocket Streaming

### Client Example

```python
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(data.get('content', ''), end='')

def on_open(ws):
    ws.send(json.dumps({
        'action': 'invoke',
        'input': 'Tell me about AgentCore'
    }))

ws = websocket.WebSocketApp(
    "wss://my-agent.agentcore.us-east-1.amazonaws.com/ws",
    on_message=on_message,
    on_open=on_open
)

ws.run_forever()
```

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
