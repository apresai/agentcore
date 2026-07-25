# AgentCore Runtime

> Serverless hosting environment for AI agents with microVM isolation, 8-hour session support, and 100MB payload support.

## Quick Reference

| CLI Command | Description |
|-------------|-------------|
| `agentcore create` | Bootstrap new agent project |
| `agentcore dev` | Start local development server |
| `agentcore deploy` | Deploy agent to Runtime |
| `agentcore invoke` | Invoke deployed agent |
| `agentcore status` | Check deployment status |
| `agentcore stop-session` | Stop an active runtime session |
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
- **AutoGen** - Multi-agent conversation framework
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
- **AG-UI** - Agent-to-frontend UI streaming (`AGUIApp`, `build_ag_ui_app`, `serve_ag_ui` in `bedrock_agentcore.runtime`)

---

## CLI Reference

### Installation

```bash
pip install bedrock-agentcore-starter-toolkit
```

Requires Python 3.10+.

> The starter toolkit's own `--help` output now recommends the newer AgentCore CLI (`npm install -g @aws/agentcore`) for new projects, and prints a deprecation notice on `create`/`deploy` ("The Starter Toolkit CLI is no longer supported... New Bedrock AgentCore features are only accessible in the AgentCore CLI"). Set `AGENTCORE_SUPPRESS_RECOMMENDATION=1` to silence it. This reference documents the Python starter toolkit (`bedrock-agentcore-starter-toolkit` 0.3.10) since that is what ships today; it has not been re-verified against `@aws/agentcore`.

### agentcore create

Bootstrap a new agent project with framework and model selection.

```bash
agentcore create [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--project-name`, `-p` | Project name to create | Interactive |
| `--template`, `-t` | Template: `basic` (runtime code only) or `production` (adds MCP setup + IaC) | `basic` |
| `--agent-framework` | Agent SDK: `Strands`, `LangChain_LangGraph`, `GoogleADK`, `OpenAIAgents`, `AutoGen`, `CrewAI` | `Strands` |
| `--model-provider`, `-mp` | Model provider: `Bedrock`, `OpenAI`, `Anthropic`, `Gemini` | `Bedrock` |
| `--provider-api-key`, `-key` | API key for the model provider | None |
| `--iac` | Infrastructure as code: `CDK` or `Terraform` | `CDK` |
| `--memory`, `-m` | Memory configuration: `STM_ONLY`, `STM_AND_LTM`, `NO_MEMORY` | Interactive |
| `--non-interactive` | Run without prompts | false |
| `--venv` / `--no-venv` | Auto-create a venv and install dependencies | `--venv` |

**Examples:**

```bash
# Interactive creation
agentcore create

# Create a Strands agent with Bedrock
agentcore create --project-name my-agent --agent-framework Strands --model-provider Bedrock

# Create with Terraform instead of CDK
agentcore create --project-name my-agent --agent-framework LangChain_LangGraph --iac Terraform

# Create with short-term + long-term memory, non-interactively
agentcore create --project-name my-agent --memory STM_AND_LTM --non-interactive
```

`agentcore create import` can also generate an AgentCore project from an existing Amazon Bedrock Agent.

### agentcore dev

Start a local development server for your agent with hot reloading.

```bash
agentcore dev [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--port`, `-p` | Local server port | 8080 |
| `--env`, `-env` | Environment variables (`KEY=VALUE`), repeatable | None |

**Example:**

```bash
# Start dev server
agentcore dev

# Custom port
agentcore dev --port 9000
```

There is no `--host`, `--reload`, or `--watch` flag; the dev server always binds locally and reloads automatically.

### agentcore deploy

Deploy the agent to AgentCore Runtime. (Formerly `agentcore launch`; that command name no longer exists.)

```bash
agentcore deploy [OPTIONS]
```

Deploy has three modes: cloud runtime (default - builds ARM64 containers in the cloud via CodeBuild, no local Docker needed), `--local` (build and run locally), and `--local-build` (build locally, deploy to cloud runtime).

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--agent`, `-a` | Agent name (see `agentcore configure list`) | from config |
| `--local`, `-l` | Run locally instead of deploying | false |
| `--local-build`, `-lb` | Build locally, deploy to cloud runtime (container deployments only) | false |
| `--image-tag`, `-t` | Custom image tag | auto-generated timestamp |
| `--auto-update-on-conflict`, `-auc` | Update existing agent instead of failing on conflict | false |
| `--force-rebuild-deps`, `-frd` | Force rebuild of dependencies (direct-code-deploy only) | false |
| `--env`, `-env` | Environment variables (`KEY=VALUE`), repeatable | None |

There is no `--region`, `--role-arn`, `--memory`, or `--timeout` flag on `deploy`. Region and IAM role are set once via `agentcore configure` (`--region`, `--execution-role`), not passed per deploy; session idle timeout and max lifetime are also `configure`-level flags (`--idle-timeout`, `--max-lifetime`, both 60-28800 seconds).

**Examples:**

```bash
# Deploy to the cloud (default)
agentcore deploy

# Run locally for testing
agentcore deploy --local

# Build locally, deploy to Runtime
agentcore deploy --local-build

# Deploy and overwrite an existing agent with the same name
agentcore deploy --auto-update-on-conflict
```

### agentcore invoke

Invoke a deployed agent with a JSON payload.

```bash
agentcore invoke [OPTIONS] PAYLOAD
```

`PAYLOAD` is a required positional argument and must be JSON, not a bare string.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--agent`, `-a` | Agent name | from config |
| `--session-id`, `-s` | Session ID for context | auto-generated |
| `--bearer-token`, `-bt` | Bearer token for OAuth authentication | None |
| `--local`, `-l` | Send request to a running local container | false |
| `--dev`, `-d` | Send request to the local dev server | false |
| `--port` | Port for the local dev server | 8080 |
| `--user-id`, `-u` | User ID for authorization flows | None |
| `--headers` | Custom headers (`Header1:value,Header2:value2`), auto-prefixed with `X-Amzn-Bedrock-AgentCore-Runtime-Custom-` | None |

There is no `--stream` or `--timeout` flag, and no `--debug` flag.

**Examples:**

```bash
# Invoke deployed agent
agentcore invoke '{"prompt": "Hello, tell me a joke"}'

# Invoke the local dev server (payload is still JSON)
agentcore invoke --dev '{"prompt": "Hello!"}'

# Continue a conversation with an explicit session
agentcore invoke --session-id abc123 '{"prompt": "Tell me another"}'
```

### agentcore status

Get deployment status including config and runtime details.

```bash
agentcore status [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--agent`, `-a` | Agent name | from config |
| `--verbose`, `-v` | Verbose JSON output of config, agent, and endpoint status | false |

There is no `--watch` flag.

### agentcore stop-session

Stop an active runtime session, freeing resources without waiting for the idle timeout.

```bash
agentcore stop-session [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--session-id`, `-s` | Session ID to stop | last invoked session |
| `--agent`, `-a` | Agent name | from config |

### agentcore destroy

Remove deployed agent and clean up resources (endpoint, agent runtime, ECR images, CodeBuild project, IAM execution role if unshared, and deployment config; the ECR repository itself is kept unless `--delete-ecr-repo` is passed).

```bash
agentcore destroy [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--agent`, `-a` | Agent name | from config |
| `--dry-run` | Preview what would be destroyed | false |
| `--force` | Skip confirmation prompts | false |
| `--delete-ecr-repo` | Also delete the ECR repository | false |

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
| `contentType` / `accept` | string | No | Request/response content negotiation |
| `runtimeUserId` | string | No | User ID for authorization flows |
| `traceId` / `traceParent` / `traceState` / `baggage` | string | No | Distributed-tracing propagation headers |

There is no `bearerAuthToken` field on this API call; OAuth bearer tokens are sent as the standard HTTP `Authorization` header (the CLI's `--bearer-token` flag sets this for you), not as a request parameter.

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| `contentType` | string | Response content type |
| `response` | StreamingBody | Response data stream |
| `runtimeSessionId` | string | Session identifier |
| `statusCode` | integer | HTTP-style status code |

---

## Configuration Reference

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_REGION` | AWS region used by boto3/the CLI | us-east-1 |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTEL endpoint | CloudWatch |
| `AGENTCORE_SUPPRESS_RECOMMENDATION` | Set to `1` to silence the starter-toolkit's `@aws/agentcore` deprecation banner | unset |

There is no `AGENTCORE_LOG_LEVEL` or `AGENTCORE_TIMEOUT` environment variable anywhere in the SDK or CLI.

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

@app.entrypoint
async def main(request):
    prompt = request.get("prompt", "")
    # Your agent logic here
    return {"response": f"Processed: {prompt}"}

if __name__ == "__main__":
    app.run()
```

`entrypoint` is a plain decorator (`entrypoint(self, func)`), not a decorator factory - use `@app.entrypoint`, never `@app.entrypoint()`.

---

## Code Examples

### Basic Agent with Strands

```python
from strands import Agent
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Initialize model
model = BedrockModel(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    region_name="us-east-1"
)

# Create agent
agent = Agent(
    model=model,
    system_prompt="You are a helpful assistant."
)

# AgentCore Runtime wrapper
app = BedrockAgentCoreApp()

@app.entrypoint
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
    model = ChatBedrock(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0")
    response = model.invoke(state["messages"])
    return {"response": response.content}

graph.add_node("process", process_message)
graph.set_entry_point("process")
graph.set_finish_point("process")

agent = graph.compile()

# AgentCore wrapper
app = BedrockAgentCoreApp()

@app.entrypoint
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

# Run on AgentCore (A2A uses port 9000). BedrockAgentCoreApp takes no
# protocol argument; A2A has its own builder in bedrock_agentcore.runtime.
app = BedrockAgentCoreApp()

@app.entrypoint
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

memory_client = MemoryClient(region_name="us-east-1")
app = BedrockAgentCoreApp()

@app.entrypoint
async def main(request):
    session_id = request.get("session_id")
    actor_id = request.get("user_id", "default-user")
    prompt = request.get("prompt")

    # Retrieve relevant long-term memories (namespace is where strategies wrote them)
    memories = memory_client.retrieve_memories(
        memory_id=MEMORY_ID,
        namespace=f"/facts/{actor_id}",
        query=prompt,
        top_k=5,
    )

    # Include memories in context
    context = "\n".join(m["content"]["text"] for m in memories)
    enhanced_prompt = f"Context:\n{context}\n\nUser: {prompt}"

    # Process with agent
    response = agent(enhanced_prompt)

    # Store interaction. messages are (text, role) tuples, not dicts.
    memory_client.create_event(
        memory_id=MEMORY_ID,
        actor_id=actor_id,
        session_id=session_id,
        messages=[
            (prompt, "USER"),
            (str(response), "ASSISTANT"),
        ],
    )

    return {"response": str(response)}
```

See [AgentCore Memory](./02-memory.md) for the full `MemoryClient` surface, namespace conventions, and the exact shape of retrieved memory records.

### With AgentCore Gateway

```python
from bedrock_agentcore.gateway import GatewayClient
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# GatewayClient manages gateway/target resources (create, get, list, update,
# delete); it does not proxy individual tool calls. Agents call tools over
# MCP directly against the gateway's endpoint URL - see AgentCore Gateway for
# the MCP client pattern and authentication.
gateway = GatewayClient(region_name="us-east-1")

app = BedrockAgentCoreApp()

@app.entrypoint
async def main(request):
    # Look up the gateway's MCP endpoint once (or read it from config)
    gw = gateway.get_gateway_by_name(name="my-gateway")
    gateway_url = gw["gatewayUrl"]

    # Hand gateway_url to your framework's MCP tool integration (Strands,
    # LangGraph, or a raw `mcp` client) so the agent can call tools directly.
    return {"response": str(agent(request["prompt"]))}
```

### With AgentCore Browser

```python
from bedrock_agentcore.tools.browser_client import BrowserClient
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
async def main(request):
    # BrowserClient takes region positionally; there is no create_session().
    browser = BrowserClient("us-east-1")

    # start() launches a session and returns its identifier; stop() ends it.
    session_id = browser.start(session_timeout_seconds=300)

    try:
        # Actual page interaction (navigate, screenshot, extract text) happens
        # over CDP/Playwright using generate_ws_headers() to connect - see
        # AgentCore Browser for the full connection pattern.
        ws_url, headers = browser.generate_ws_headers()
        return {"session_id": session_id, "ws_url": ws_url}
    finally:
        browser.stop()
```

---

## Best Practices

1. **Use session IDs consistently** - Pass the same session ID across related requests to maintain conversation context.

2. **Process streaming responses** - Handle streaming incrementally for better user experience rather than waiting for complete responses.

3. **Implement retry logic** - Use exponential backoff for throttling and transient errors.

4. **Size lifecycle timeouts deliberately** - `idleRuntimeSessionTimeout` (default 15 min) and `maxLifetime` (default 8 hr, hard cap) are both set at `agentcore configure` time via `--idle-timeout`/`--max-lifetime`, not per invoke.

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
| `Port 8080 in use` | Local conflict | Use `agentcore dev --port 9000` |

### Debugging Tips

```bash
# Check agent status
agentcore status --agent my-agent

# List recent traces for the last invoked session (or --session-id / --agent)
agentcore obs list

# Show a specific trace with full detail
agentcore obs show --trace-id <trace-id>

# View CloudWatch logs directly (log group includes the endpoint name)
aws logs tail /aws/bedrock-agentcore/runtimes/<agent_id>-<endpoint_name> --follow

# Test locally - the dev server streams its own logs to the terminal
agentcore dev

# Invoke with a JSON payload (there is no --debug flag)
agentcore invoke '{"prompt": "test"}'
```

`agentcore obs` replaces any earlier `logs`/`list`/`delete`/`describe` commands; its real subcommands are `list` (enumerate traces for a session) and `show` (visualize one trace or all traces in a session) - there is no `agentcore obs status` or `agentcore obs destroy`.

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

Verified against the AgentCore Runtime quota tables (docs.aws.amazon.com/bedrock-agentcore, checked 2026-07-25).

| Resource | Limit | Adjustable |
|----------|-------|------------|
| Synchronous request timeout | 15 minutes | No |
| Idle session timeout | 15 minutes of inactivity | Yes - `idleRuntimeSessionTimeout`, 60-28800s |
| Maximum session duration (max lifetime) | 8 hours | Yes - `maxLifetime`, 60-28800s |
| Maximum asynchronous job duration | 8 hours | No |
| Maximum payload size | 100 MB | No |
| Hardware per session | 2 vCPU / 8 GB | No |
| Active session workloads per account | 5,000 in us-east-1 & us-west-2; 2,500 elsewhere | Yes - Service Quotas |

There is no documented per-agent memory quota in MB; the nearest figure AWS documents is the 2vCPU/8GB hardware allocation above, and it is scoped per session, not per agent. For the full, current quota table see the [AgentCore limits page](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/bedrock-agentcore-limits.html).

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
2. **Right-size memory** - Start small, increase if needed.
3. **Use ARM64** - Graviton2 is more cost-effective than x86.
4. **Enable observability** - Monitor usage to optimize.

### Free Tier

New AWS customers receive up to $200 in Free Tier credits for AgentCore. See the [AgentCore pricing page](https://aws.amazon.com/bedrock/agentcore/pricing/) for current terms.

---

## Related Services

- [AgentCore Memory](./02-memory.md) - Add conversation memory
- [AgentCore Gateway](./03-gateway.md) - Connect tools via MCP
- [AgentCore Identity](./04-identity.md) - Authentication and authorization
- [AgentCore Observability](./08-observability.md) - Monitoring and tracing
