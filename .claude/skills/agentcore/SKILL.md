---
name: agentcore
description: Build and deploy AI agents with AWS Bedrock AgentCore. Use for questions about AgentCore APIs, SDK usage, CLI commands, deploying agents, Memory/Gateway/Identity/Code Interpreter/Browser services, MCP tools, or troubleshooting. NOT for writing articles (use /agentcore-article).
---

# AgentCore Builder

Help users build, deploy, and troubleshoot AI agents with AWS Bedrock AgentCore.

> **Related Skills:**
> - Use this skill (`/agentcore`) for building agents, API usage, troubleshooting
> - Use `/agentcore-article` skill for creating articles and content

## Quick Reference

### Services Overview

| Service | Purpose | Status |
|---------|---------|--------|
| **Runtime** | Serverless microVM hosting, 8hr sessions | GA |
| **Memory** | Short-term + long-term context | GA |
| **Gateway** | Convert APIs/Lambda to MCP tools | GA |
| **Identity** | Agent auth with IdP integration | GA |
| **Code Interpreter** | Secure Python/JS/TS execution | GA |
| **Browser** | Isolated web interaction | GA |
| **Observability** | OTEL-compatible tracing | GA |
| **Evaluations** | LLM-as-a-Judge quality | Preview |
| **Policy** | Cedar-based access control | Preview |

### CLI Commands

```bash
# Install CLI
pip install bedrock-agentcore-starter-toolkit

# Core commands
agentcore create [--framework strands|langgraph|openai|google] [--model-provider bedrock|openai|anthropic|google]
agentcore dev [--port 8080]              # Local development server
agentcore deploy [--region us-east-1]    # Deploy to Runtime
agentcore invoke '{"prompt": "..."}'     # Invoke agent
agentcore status                         # Check deployment
agentcore destroy                        # Remove agent
```

### SDK Imports

```python
# Control plane (create/manage agents)
import boto3
control = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

# Data plane (invoke agents)
data = boto3.client('bedrock-agentcore', region_name='us-east-1')

# High-level SDK
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.gateway import GatewayClient
```

### Regions

- `us-east-1` (N. Virginia)
- `us-west-2` (Oregon)
- `ap-southeast-2` (Sydney)
- `eu-central-1` (Frankfurt)

### Pricing

- **Consumption-based**: Pay per vCPU-second + GB-second
- **I/O wait is FREE**: No charge while waiting for LLM/API responses
- **Free tier**: $200 credits for new customers
- **Minimum billing**: 1 second, 128 MB

---

## Dynamic Loading Strategy

When answering questions, load relevant files based on the topic:

### File Mapping

| Topic | Read These Files |
|-------|------------------|
| Overview/Getting Started | `research/00-overview.md`, `research/10-getting-started.md` |
| Runtime/Deployment | `research/01-runtime.md` |
| Memory | `research/02-memory.md` |
| Gateway/Tools/MCP | `research/03-gateway.md` |
| Identity/Auth | `research/04-identity.md` |
| Code Interpreter | `research/05-code-interpreter.md` |
| Browser | `research/06-browser.md` |
| Policy/Cedar | `research/07-policy.md` |
| Observability/Tracing | `research/08-observability.md` |
| Evaluations | `research/09-evaluations.md` |
| Pricing | `research/11-pricing.md` |

### When to Read Local Files

- User asks detailed questions about a service
- User needs code examples for a specific feature
- User asks "how do I..." questions

### When to Fetch from GitHub

Fetch from `https://github.com/awslabs/amazon-bedrock-agentcore-samples/` when:
- User asks for "latest examples"
- Local examples are missing for a service
- User wants to see official sample code

Use WebFetch to browse the repo structure, then provide relevant code.

### When to Search AWS Docs

Use `mcp__aws-mcp__aws___search_documentation` when:
- User asks "what's new" in AgentCore
- User needs API reference details not in research
- User asks about recent updates or announcements

```
search_phrase: "Bedrock AgentCore [topic]"
topics: ["reference_documentation", "current_awareness"]
```

---

## Code Patterns

### Basic Agent Setup (Strands)

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

### Memory Integration

```python
from bedrock_agentcore.memory import MemoryClient

memory = MemoryClient(memory_id="my-memory-id")

# Store interaction
memory.create_event(
    session_id="session-123",
    messages=[
        {"role": "user", "content": "My name is Alice"},
        {"role": "assistant", "content": "Hello Alice!"}
    ]
)

# Retrieve relevant memories
memories = memory.retrieve_memories(
    session_id="session-123",
    query="What is my name?"
)
```

### Gateway Tool Registration

```python
from bedrock_agentcore.gateway import GatewayClient

gateway = GatewayClient(gateway_id="my-gateway-id")

# List available tools
tools = gateway.list_tools()

# Call a tool
result = gateway.call_tool(
    tool_name="get_weather",
    arguments={"city": "Seattle"}
)
```

### Deployment Workflow

```bash
# 1. Create project
agentcore create --framework strands --model-provider bedrock --name my-agent

# 2. Develop locally
cd my-agent
agentcore dev

# 3. Test locally
agentcore invoke --dev '{"prompt": "Hello!"}'

# 4. Deploy to AWS
agentcore deploy --region us-east-1

# 5. Invoke in production
agentcore invoke '{"prompt": "Hello!"}'
```

### Session Management

```python
import uuid
import boto3
import json

client = boto3.client('bedrock-agentcore', region_name='us-east-1')
session_id = str(uuid.uuid4())

def chat(message: str, agent_arn: str) -> str:
    """Send message with session context."""
    payload = json.dumps({"prompt": message}).encode()

    response = client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        runtimeSessionId=session_id,
        payload=payload
    )

    # Process streaming response
    content = []
    for line in response["response"].iter_lines():
        if line:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                content.append(line[6:])
    return "\n".join(content)

# Multi-turn conversation
print(chat("My name is Alice", agent_arn))
print(chat("What's my name?", agent_arn))  # Agent remembers
```

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ValidationException` | Invalid request parameters | Check ARN format, payload encoding |
| `ResourceNotFoundException` | Agent not found | Verify agent exists in account/region |
| `AccessDeniedException` | Missing IAM permissions | Add `bedrock-agentcore:*` to policy |
| `ThrottlingException` | Rate limit | Implement exponential backoff |
| `ModelAccessDenied` | Model not enabled | Enable model in Bedrock console |
| `Port 8080 in use` | Local conflict | Use `agentcore dev --port 9000` |

### IAM Permission Checklist

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

### Debug Commands

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

---

## Key Facts

### Runtime Limits

| Resource | Limit |
|----------|-------|
| Max execution time | 8 hours |
| Max payload size | 100 MB |
| Min memory | 128 MB |
| Max memory | 10,240 MB |
| Concurrent sessions | 1000 per endpoint |

### Supported Frameworks

- **Strands** - AWS native, simplest path
- **LangGraph** - LangChain ecosystem
- **CrewAI** - Multi-agent collaboration
- **LlamaIndex** - RAG-focused
- **Google ADK** - Google's framework
- **OpenAI Agents SDK** - OpenAI's framework
- **Custom** - Any Python agent

### Supported Models

- Amazon Bedrock: Claude, Nova, Llama, Mistral
- OpenAI: GPT-4, GPT-4o
- Anthropic: Claude (direct API)
- Google: Gemini
- Self-hosted models

### Protocols

- **MCP** (Model Context Protocol) - Tool connectivity
- **A2A** (Agent to Agent) - Inter-agent communication

---

## Documentation Links

- **Developer Guide**: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/
- **Product Page**: https://aws.amazon.com/bedrock/agentcore/
- **GitHub Samples**: https://github.com/awslabs/amazon-bedrock-agentcore-samples/
- **Pricing**: https://aws.amazon.com/bedrock/agentcore/pricing/
- **FAQs**: https://aws.amazon.com/bedrock/agentcore/faqs/

---

## Response Guidelines

When helping users:

1. **Read relevant research files first** - Don't guess at API details
2. **Provide complete code** - Include all imports, error handling
3. **Show both SDK options** - AgentCore SDK (simple) + boto3 (control)
4. **Include verification** - Code should print success/failure
5. **Link to docs** - Always provide relevant documentation links

For article creation, direct users to `/agentcore-article` skill.
