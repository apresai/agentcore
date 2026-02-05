# AgentCore Runtime

> Serverless hosting environment for AI agents with microVM isolation, 8-hour execution, and 100MB payload support.

## Quick Reference

| CLI Command | Description |
|-------------|-------------|
| `agentcore create` | Bootstrap new agent project |
| `agentcore dev` | Start local development server |
| `agentcore deploy` | Deploy agent to Runtime |
| `agentcore invoke` | Invoke deployed agent |
| `agentcore status` | Check deployment status |
| `agentcore destroy` | Remove deployed agent |

| SDK Client | Purpose |
|------------|---------|
| `bedrock-agentcore` (data plane) | Invoke agents, manage sessions |
| `bedrock-agentcore-control` (control plane) | Create/manage agent resources |

| Key API | Description |
|---------|-------------|
| `InvokeAgentRuntime` | Send prompts, receive streaming responses |
| `CreateAgentRuntime` | Create new agent runtime resource |
| `CreateAgentRuntimeEndpoint` | Create invocable endpoint for agent |
| `GetAgentRuntime` | Get agent runtime details |
| `ListAgentRuntimes` | List all agent runtimes |

---

## Overview

Amazon Bedrock AgentCore Runtime provides a secure, serverless, purpose-built hosting environment for deploying and running AI agents or tools. It transforms any local agent code into cloud-native deployments with minimal configuration changes.

## Core Concepts

### Framework Agnostic
Runtime supports agents built with any framework:
- **Strands Agents** - AWS's native agent framework
- **LangGraph** - LangChain's graph-based orchestration
- **CrewAI** - Multi-agent collaboration framework
- **OpenAI Agents SDK** - OpenAI's agent framework
- **Google ADK** - Google's Agent Development Kit
- **Custom agents** - Any Python-based agent

### Model Flexibility
Works with any foundation model:
- Amazon Bedrock models (Claude, Nova, Llama, Mistral)
- OpenAI API (GPT-4, GPT-4o)
- Anthropic API (Claude direct)
- Google Gemini
- Self-hosted models

### Session Isolation
Each user session runs in a **dedicated microVM** providing:
- Isolated CPU, memory, and filesystem
- Complete separation between user sessions
- Memory sanitization after session completion
- Deterministic security for non-deterministic AI processes

### Protocol Support
- **Model Context Protocol (MCP)** - Tool connectivity standard
- **Agent to Agent (A2A)** - Inter-agent communication

---

## CLI Reference

### Installation

```bash
pip install bedrock-agentcore-starter-toolkit
```

Requires Python 3.10+.

### agentcore create

Bootstrap a new agent project with framework and model selection.

```bash
agentcore create [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--framework` | Agent framework (strands, langgraph, openai, google) | Interactive |
| `--model-provider` | Model provider (bedrock, openai, anthropic, google) | Interactive |
| `--output` | Output type (python, terraform, cdk) | python |
| `--name` | Project name | my-agent |
| `--with-memory` | Include memory configuration | false |
| `--with-gateway` | Include gateway configuration | false |

**Examples:**

```bash
# Interactive creation
agentcore create

# Create Strands agent with Bedrock
agentcore create --framework strands --model-provider bedrock --name my-agent

# Create with infrastructure as code
agentcore create --framework langgraph --output cdk

# Create with memory and gateway
agentcore create --with-memory --with-gateway
```

### agentcore dev

Start local development server for testing.

```bash
agentcore dev [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--port` | Local server port | 8080 |
| `--host` | Host to bind | localhost |
| `--reload` | Auto-reload on changes | true |

**Example:**

```bash
# Start dev server
agentcore dev

# Custom port
agentcore dev --port 9000
```

### agentcore deploy

Deploy agent to AgentCore Runtime.

```bash
agentcore deploy [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--region` | AWS region | us-east-1 |
| `--name` | Deployment name | from project |
| `--role-arn` | Custom IAM role ARN | auto-created |
| `--memory` | Memory allocation (MB) | 512 |
| `--timeout` | Timeout (seconds) | 900 |

**What it does:**
1. Packages Python code into zip file
2. Creates/updates IAM execution role
3. Deploys to AgentCore Runtime
4. Configures CloudWatch logging
5. Returns agent ARN and endpoint

**Examples:**

```bash
# Basic deploy
agentcore deploy

# Deploy with custom settings
agentcore deploy --region us-west-2 --memory 1024 --timeout 3600

# Deploy with existing role
agentcore deploy --role-arn arn:aws:iam::123456789012:role/MyAgentRole
```

### agentcore invoke

Invoke a deployed agent with a prompt.

```bash
agentcore invoke [OPTIONS] PAYLOAD
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--dev` | Invoke local dev server | false |
| `--session-id` | Session ID for context | auto-generated |
| `--stream` | Stream response | true |
| `--timeout` | Request timeout (seconds) | 120 |

**Examples:**

```bash
# Invoke deployed agent
agentcore invoke '{"prompt": "Hello, tell me a joke"}'

# Invoke local dev server
agentcore invoke --dev "Hello!"

# Continue conversation with session
agentcore invoke --session-id abc123 '{"prompt": "Tell me another"}'
```

### agentcore status

Check deployment status.

```bash
agentcore status [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--name` | Agent name | from project |
| `--watch` | Watch for changes | false |

### agentcore destroy

Remove deployed agent and clean up resources.

```bash
agentcore destroy [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--name` | Agent name | from project |
| `--force` | Skip confirmation | false |

---

## SDK Reference

### Control Plane APIs

The control plane client manages agent runtime resources.

```python
import boto3

control_client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
```

#### CreateAgentRuntime

Create a new agent runtime resource.

```python
response = control_client.create_agent_runtime(
    agentRuntimeName='my-agent',
    description='My production agent',
    roleArn='arn:aws:iam::123456789012:role/AgentRole',
    agentRuntimeArtifact={
        's3': {
            'bucket': 'my-bucket',
            'key': 'agents/my-agent.zip'
        }
    },
    networkConfiguration={
        'networkMode': 'PUBLIC'  # or 'VPC'
    },
    protocolConfiguration={
        'serverProtocol': 'MCP'  # or 'HTTP', 'A2A'
    },
    tags={
        'Environment': 'production'
    }
)

agent_runtime_id = response['agentRuntimeId']
agent_runtime_arn = response['agentRuntimeArn']
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agentRuntimeName` | string | Yes | Unique name (1-48 chars) |
| `roleArn` | string | Yes | IAM execution role ARN |
| `agentRuntimeArtifact` | object | Yes | Code artifact location |
| `description` | string | No | Description (1-256 chars) |
| `networkConfiguration` | object | No | Network settings |
| `protocolConfiguration` | object | No | Protocol (MCP/HTTP/A2A) |
| `tags` | dict | No | Resource tags |

#### CreateAgentRuntimeEndpoint

Create an invocable endpoint for an agent runtime.

```python
response = control_client.create_agent_runtime_endpoint(
    agentRuntimeId='my-agent-abc123xyz',
    name='production',
    description='Production endpoint',
    agentRuntimeVersion='1'
)

endpoint_arn = response['agentRuntimeEndpointArn']
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agentRuntimeId` | string | Yes | Agent runtime ID |
| `name` | string | Yes | Endpoint name |
| `agentRuntimeVersion` | string | No | Target version |
| `description` | string | No | Description |

#### GetAgentRuntime

Get details of an agent runtime.

```python
response = control_client.get_agent_runtime(
    agentRuntimeId='my-agent-abc123xyz'
)

status = response['status']  # CREATING, READY, UPDATING, FAILED
```

#### ListAgentRuntimes

List all agent runtimes in the account.

```python
response = control_client.list_agent_runtimes(
    maxResults=50
)

for agent in response['agentRuntimeSummaries']:
    print(f"{agent['agentRuntimeName']}: {agent['status']}")
```

#### UpdateAgentRuntime

Update an existing agent runtime.

```python
response = control_client.update_agent_runtime(
    agentRuntimeId='my-agent-abc123xyz',
    agentRuntimeArtifact={
        's3': {
            'bucket': 'my-bucket',
            'key': 'agents/my-agent-v2.zip'
        }
    }
)
```

#### DeleteAgentRuntime

Delete an agent runtime.

```python
control_client.delete_agent_runtime(
    agentRuntimeId='my-agent-abc123xyz'
)
```

### Data Plane APIs

The data plane client invokes agents and manages sessions.

```python
import boto3

data_client = boto3.client('bedrock-agentcore', region_name='us-east-1')
```

#### InvokeAgentRuntime

Send prompts and receive streaming responses.

```python
import json

payload = json.dumps({"prompt": "Tell me a joke"}).encode()

response = data_client.invoke_agent_runtime(
    agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:123456789012:agent/abc123',
    runtimeSessionId='session-123',
    payload=payload
)

# Process streaming response
if "text/event-stream" in response.get("contentType", ""):
    for line in response["response"].iter_lines(chunk_size=10):
        if line:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                print(line[6:])
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agentRuntimeArn` | string | Yes | Agent ARN or endpoint ARN |
| `payload` | bytes | Yes | Request payload (up to 100MB) |
| `runtimeSessionId` | string | No | Session ID for context |
| `qualifier` | string | No | Version qualifier |
| `bearerAuthToken` | string | No | OAuth bearer token |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| `contentType` | string | Response content type |
| `response` | StreamingBody | Response data stream |
| `sessionId` | string | Session identifier |

---

## Configuration Reference

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_REGION` | AWS region | us-east-1 |
| `AGENTCORE_LOG_LEVEL` | Logging level | INFO |
| `AGENTCORE_TIMEOUT` | Request timeout (seconds) | 900 |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTEL endpoint | CloudWatch |

### Runtime Requirements

For deploying custom agents without the starter toolkit:

1. **Endpoints**: Must expose `/invocations` (POST) and `/ping` (GET)
2. **Port**: Application runs on port 8080
3. **Architecture**: ARM64 (linux/arm64)
4. **Container**: Docker image deployed to ECR

### Agent Entry Point

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint()
async def main(request):
    prompt = request.get("prompt", "")
    # Your agent logic here
    return {"response": f"Processed: {prompt}"}

if __name__ == "__main__":
    app.run()
```

---

## Code Examples

### Basic Agent with Strands

```python
from strands import Agent
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Initialize model
model = BedrockModel(
    model_id="anthropic.claude-sonnet-4-20250514",
    region_name="us-east-1"
)

# Create agent
agent = Agent(
    model=model,
    system_prompt="You are a helpful assistant."
)

# AgentCore Runtime wrapper
app = BedrockAgentCoreApp()

@app.entrypoint()
async def main(request):
    prompt = request.get("prompt", "")
    response = agent(prompt)
    return {"response": str(response)}

if __name__ == "__main__":
    app.run()
```

### Multi-Modal Agent

```python
import base64
import json
import boto3

client = boto3.client('bedrock-agentcore', region_name='us-east-1')

# Read and encode image
with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Create multi-modal payload
payload = json.dumps({
    "prompt": "Describe what you see in this image",
    "media": {
        "type": "image",
        "format": "jpeg",
        "data": image_data
    }
}).encode()

# Invoke agent
response = client.invoke_agent_runtime(
    agentRuntimeArn=agent_arn,
    runtimeSessionId="session-123",
    payload=payload
)

# Process response
for chunk in response["response"]:
    print(chunk.decode('utf-8'), end='')
```

### Session Management

```python
import uuid
import boto3
import json

client = boto3.client('bedrock-agentcore', region_name='us-east-1')

# Start new conversation
session_id = str(uuid.uuid4())

def chat(message: str) -> str:
    """Send message and maintain session context."""
    payload = json.dumps({"prompt": message}).encode()

    response = client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        runtimeSessionId=session_id,
        payload=payload
    )

    # Collect streaming response
    content = []
    for line in response["response"].iter_lines():
        if line:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                content.append(line[6:])

    return "\n".join(content)

# Multi-turn conversation
print(chat("My name is Alice"))
print(chat("What's my name?"))  # Agent remembers context
```

### LangGraph Agent

```python
from langgraph.graph import StateGraph
from langchain_aws import ChatBedrock
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Define state
class AgentState(TypedDict):
    messages: list
    response: str

# Create graph
graph = StateGraph(AgentState)

def process_message(state):
    model = ChatBedrock(model_id="anthropic.claude-sonnet-4-20250514")
    response = model.invoke(state["messages"])
    return {"response": response.content}

graph.add_node("process", process_message)
graph.set_entry_point("process")
graph.set_finish_point("process")

agent = graph.compile()

# AgentCore wrapper
app = BedrockAgentCoreApp()

@app.entrypoint()
async def main(request):
    prompt = request.get("prompt", "")
    result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    return {"response": result["response"]}

if __name__ == "__main__":
    app.run()
```

### A2A Server Deployment

```python
from a2a import A2AServer, AgentCard
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Define agent card for discovery
card = AgentCard(
    name="MyAgent",
    description="A helpful assistant agent",
    capabilities=["chat", "analysis"]
)

# Create A2A server
server = A2AServer(agent_card=card)

@server.handler
async def handle_message(message):
    # Process A2A message
    return {"response": f"Received: {message.content}"}

# Run on AgentCore (A2A uses port 9000)
app = BedrockAgentCoreApp(protocol="A2A")

@app.entrypoint()
async def main(request):
    return await server.process(request)

if __name__ == "__main__":
    app.run()
```

---

## Integration Patterns

### With AgentCore Memory

```python
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent

memory_client = MemoryClient(memory_id="my-memory-id")
app = BedrockAgentCoreApp()

@app.entrypoint()
async def main(request):
    session_id = request.get("session_id")
    prompt = request.get("prompt")

    # Retrieve relevant memories
    memories = memory_client.retrieve_memories(
        session_id=session_id,
        query=prompt
    )

    # Include memories in context
    context = "\n".join([m["content"] for m in memories])
    enhanced_prompt = f"Context:\n{context}\n\nUser: {prompt}"

    # Process with agent
    response = agent(enhanced_prompt)

    # Store interaction
    memory_client.create_event(
        session_id=session_id,
        messages=[
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": str(response)}
        ]
    )

    return {"response": str(response)}
```

### With AgentCore Gateway

```python
from bedrock_agentcore.gateway import GatewayClient
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.tools import tool

gateway = GatewayClient(gateway_id="my-gateway-id")

# Get tools from gateway
mcp_tools = gateway.list_tools()

@tool
def call_gateway_tool(tool_name: str, arguments: dict):
    """Call a tool through the gateway."""
    return gateway.call_tool(tool_name, arguments)

agent = Agent(
    model=model,
    tools=[call_gateway_tool],
    system_prompt="Use available tools to help users."
)

app = BedrockAgentCoreApp()

@app.entrypoint()
async def main(request):
    return {"response": str(agent(request["prompt"]))}
```

### With AgentCore Browser

```python
from bedrock_agentcore.browser import BrowserClient
from bedrock_agentcore.runtime import BedrockAgentCoreApp

browser = BrowserClient()
app = BedrockAgentCoreApp()

@app.entrypoint()
async def main(request):
    url = request.get("url")
    action = request.get("action", "screenshot")

    # Start browser session
    session = browser.start_session(timeout_seconds=300)

    try:
        # Navigate and interact
        await session.navigate(url)

        if action == "screenshot":
            screenshot = await session.screenshot()
            return {"image": screenshot}
        elif action == "extract":
            content = await session.get_page_text()
            return {"content": content}
    finally:
        session.stop()
```

---

## Best Practices

1. **Use session IDs consistently** - Pass the same session ID across related requests to maintain conversation context.

2. **Process streaming responses** - Handle streaming incrementally for better user experience rather than waiting for complete responses.

3. **Implement retry logic** - Use exponential backoff for throttling and transient errors.

4. **Set appropriate timeouts** - Configure timeouts based on expected agent execution time (up to 8 hours).

5. **Use ARM64 architecture** - Runtime uses Graviton2 (ARM64) for cost efficiency. Build containers for `linux/arm64`.

6. **Keep payloads under 100MB** - Large payloads may increase latency. Use S3 for larger files.

7. **Enable observability** - Configure CloudWatch logging and OTEL tracing for debugging.

8. **Use structured logging** - Log agent decisions and tool calls for auditability.

9. **Separate concerns** - Use Gateway for tools, Memory for context, Identity for auth.

10. **Test locally first** - Use `agentcore dev` to validate before deploying.

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ValidationException` | Invalid request parameters | Check ARN format, session ID, payload encoding |
| `ResourceNotFoundException` | Agent not found | Verify agent ARN exists in account/region |
| `AccessDeniedException` | Missing permissions | Add `bedrock-agentcore:InvokeAgentRuntime` to IAM policy |
| `ThrottlingException` | Rate limit exceeded | Implement exponential backoff |
| `ServiceException` | Internal error | Retry with backoff, check service health |
| `ModelAccessDenied` | Model not enabled | Enable model in Bedrock console |
| `Port 8080 in use` | Local conflict | Kill process or use `--port` option |

### Debugging Tips

```bash
# Check agent status
agentcore status --name my-agent

# View CloudWatch logs
aws logs tail /aws/bedrock-agentcore/runtimes/<agent_id> --follow

# Test locally with verbose logging
AGENTCORE_LOG_LEVEL=DEBUG agentcore dev

# Invoke with debug output
agentcore invoke --debug '{"prompt": "test"}'
```

### IAM Permission Issues

Required IAM policy for agent execution:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock-agentcore:InvokeAgentRuntime",
                "bedrock-agentcore:CreateAgentRuntime",
                "bedrock-agentcore:CreateAgentRuntimeEndpoint",
                "bedrock-agentcore:GetAgentRuntime",
                "bedrock-agentcore:ListAgentRuntimes",
                "bedrock-agentcore:UpdateAgentRuntime",
                "bedrock-agentcore:DeleteAgentRuntime"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "arn:aws:bedrock:*::foundation-model/*"
        }
    ]
}
```

---

## Limits & Quotas

| Resource | Default Limit | Adjustable |
|----------|--------------|------------|
| Agent runtimes per account | 100 | Yes |
| Endpoints per runtime | 10 | Yes |
| Concurrent sessions per endpoint | 1000 | Yes |
| Maximum execution time | 8 hours | No |
| Maximum payload size | 100 MB | No |
| Minimum memory | 128 MB | No |
| Maximum memory | 10,240 MB | No |
| Minimum billing increment | 1 second | No |
| Session timeout (default) | 15 minutes | Yes |
| Session timeout (max) | 8 hours | No |

---

## Pricing

### Consumption-Based Model

AgentCore Runtime uses consumption-based pricing:

| Resource | Rate |
|----------|------|
| vCPU time | Per vCPU-second |
| Memory | Per GB-second |
| I/O wait | **Free** |
| Minimum billing | 1 second, 128 MB |

### Cost Optimization Tips

1. **I/O wait is free** - When waiting for LLM responses, you're not charged for CPU.
2. **Right-size memory** - Start with 512MB, increase if needed.
3. **Use ARM64** - Graviton2 is more cost-effective than x86.
4. **Enable observability** - Monitor usage to optimize.

### Free Tier

- **$200 free credits** for new AgentCore customers
- Preview period: Free until September 16, 2025

---

## Related Services

- [AgentCore Memory](./02-memory.md) - Add conversation memory
- [AgentCore Gateway](./03-gateway.md) - Connect tools via MCP
- [AgentCore Identity](./04-identity.md) - Authentication and authorization
- [AgentCore Observability](./08-observability.md) - Monitoring and tracing
