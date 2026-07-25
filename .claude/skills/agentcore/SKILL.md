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
| **Evaluations** | LLM-as-a-Judge quality | GA |
| **Policy** | Cedar-based access control | GA |
| **Harness** | Managed multi-turn agent hosting | GA |
| **Registry** | Discover/manage agents, tools, resources | Preview |
| **Payments** | Agent-initiated payment authorization | Preview |

### CLI Commands

```bash
# Install CLI
pip install bedrock-agentcore-starter-toolkit

# Core commands
agentcore create [--project-name NAME] [--agent-framework Strands|LangChain_LangGraph|GoogleADK|OpenAIAgents|...] [--model-provider Bedrock|OpenAI|...]
agentcore dev [--port 8080]              # Local development server
agentcore deploy [--local|--local-build] # Deploy to Runtime (region comes from AWS config)
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

# Newer submodules (bedrock-agentcore 1.18.1)
from bedrock_agentcore.policy import PolicyEngineClient
from bedrock_agentcore.payments import PaymentClient, PaymentManager
from bedrock_agentcore.knowledge_base import KnowledgeBaseClient
from bedrock_agentcore.config_bundle import ConfigBundleClient
```

### Regions

Commonly used: `us-east-1` (N. Virginia), `us-west-2` (Oregon), `ap-southeast-2` (Sydney), `eu-central-1` (Frankfurt).

Per-feature availability varies; do not assume every region supports every service. Full, current list: [AgentCore Supported AWS Regions](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-regions.html).

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

### Memory Integration

```python
from bedrock_agentcore.memory import MemoryClient

# The client is region-scoped; the memory resource is named per call.
memory = MemoryClient(region_name="us-east-1")

# Store interaction. messages are (text, role) TUPLES, not dicts.
memory.create_event(
    memory_id="my-memory-id",
    actor_id="user-alice",
    session_id="session-123",
    messages=[
        ("My name is Alice", "USER"),
        ("Hello Alice!", "ASSISTANT"),
    ],
)

# Retrieve relevant memories (there is no session_id arg; namespace is optional)
memories = memory.retrieve_memories(
    memory_id="my-memory-id",
    namespace="/facts/user-alice",
    query="What is my name?",
    top_k=3,
)
```

### Gateway Tool Registration

```python
from bedrock_agentcore.gateway import GatewayClient

# The client is region-scoped; gateways are addressed per call.
gateway = GatewayClient(region_name="us-east-1")

# Create a gateway and attach targets. The *_and_wait helpers block until the
# resource reaches a terminal state. create_gateway_and_wait passes its
# arguments through as **kwargs to the underlying control-plane call.
# CreateGateway requires name, roleArn and authorizerType together.
gw = gateway.create_gateway_and_wait(
    name="my-gateway",
    roleArn="arn:aws:iam::123456789012:role/AgentCoreGatewayRole",
    authorizerType="CUSTOM_JWT",
    authorizerConfiguration={
        "customJWTAuthorizer": {
            "discoveryUrl": "https://your-idp/.well-known/openid-configuration",
            "allowedClients": ["your-client-id"],
        }
    },
)
target = gateway.create_knowledge_base_target(
    gateway_identifier=gw["gatewayId"],
    knowledge_base_id="my-kb-id",
    name="docs-kb",
)

# Gateways expose their targets to agents over MCP; the client manages the
# gateway, it does not proxy individual tool calls.
```

### Deployment Workflow

```bash
# 1. Create project
agentcore create --project-name myagent --agent-framework Strands --model-provider Bedrock

# 2. Develop locally
cd myagent
agentcore dev

# 3. Test locally
agentcore invoke --dev '{"prompt": "Hello!"}'

# 4. Deploy to AWS (region comes from your AWS config/AWS_REGION)
agentcore deploy

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

## Long-Running Tasks Pattern

Authoritative AWS guidance for agents that do work longer than a synchronous request can hold open (5–60+ minutes: video/audio pipelines, large-batch inference, multi-step data processing).

**Sources (verbatim reference material):**
- Docs: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-long-run.html
- AWS blog: https://aws.amazon.com/blogs/machine-learning/build-long-running-mcp-servers-on-amazon-bedrock-agentcore-with-strands-agents-integration/
- Sample repo: https://github.com/aws-samples/sample-mcp-for-long-runing-tasks-with-amazon-bedrock-agentcore

### The core pattern — job_id + polling on a sticky session

1. **Tool returns a job_id immediately.** Don't block the MCP request. The tool kicks off a goroutine/thread that does the real work, then returns a handle (UUID, ULID, or deterministic ID derived from the task).
2. **Background goroutine writes progress to durable storage** — DynamoDB, AgentCore Memory, or similar. Never in-memory only; the microVM can be recycled between invocations.
3. **Client polls a separate status tool** (`check_task_status(job_id)`, `get_podcast(id)`, etc.). AWS's sample repo does exactly this — no push, no webhooks, no SNS.
4. **Client reuses the same `Mcp-Session-Id` across every call tied to the job.** This is the single most important detail — AgentCore routes all requests for a given Mcp-Session-Id to the **same microVM**. If the client creates a new session per poll, AgentCore boots a fresh microVM per poll and you get a container churn storm (and orphan false-positives if you have any boot-time cleanup logic).
   - **Recommended**: use the `job_id` itself as the `Mcp-Session-Id`. Deterministic, stateless clients (Lambda, browsers) don't need to remember session IDs.

### `/ping` HealthyBusy — the 15-minute idle-timeout escape hatch

AgentCore kills idle sessions after 15 minutes by default. *Idle means "no in-flight invocation AND no HealthyBusy ping."* Long-running background work must signal busy state or the session gets recycled mid-job.

Python SDK (built-in task tracking):

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp
app = BedrockAgentCoreApp()

@app.tool
def start_work():
    task_id = app.add_async_task("processing")  # /ping now returns HealthyBusy
    def worker():
        # ... do work ...
        app.complete_async_task(task_id)  # /ping flips back to Healthy
    threading.Thread(target=worker, daemon=True).start()
    return {"task_id": task_id}
```

Or custom ping handler:

```python
@app.ping
def status():
    return PingStatus.HEALTHY_BUSY if system_busy() else PingStatus.HEALTHY
```

Go (no SDK — implement the HTTP handler directly):

```go
// /ping must NEVER block. Keep ActiveCount() behind a mutex-guarded counter.
mux.HandleFunc("/ping", func(w http.ResponseWriter, r *http.Request) {
    status := "Healthy"
    if taskMgr.ActiveCount() > 0 {
        status = "HealthyBusy"
    }
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{"status": status})
})
```

**Critical**: the `/ping` handler must never block — if the entrypoint goroutine holds a lock the ping thread needs, the session gets idle-killed at minute 15 with no warning. Separate threads or async.

### Session lifecycle knobs (LifecycleConfiguration)

- `idleRuntimeSessionTimeout`: default 900 s (15 min), range 60–28800 s. Resets on every invoke OR HealthyBusy ping.
- `maxLifetime`: default 28800 s (8 h), range 60–28800 s. Starts at microVM creation, **does not reset** — a job longer than this gets cycled regardless.
- Constraint: `idle ≤ max`.
- Configure via `aws bedrock-agentcore-control update-agent-runtime --lifecycle-configuration '{"idleRuntimeSessionTimeout": 1800, "maxLifetime": 28800}'` or via CDK `LifecycleConfiguration` on `CfnAgentRuntime`.

### What AWS explicitly does NOT recommend

- **Push notifications via EventBridge, SNS, SQS, AppSync, DDB Streams** — AWS's official sample uses polling only. Rationale: simpler, one source of truth, no eventual-consistency headaches. Add push layers only if the job volume or client pattern demands it.
- **Blocking the MCP request for the full job duration** — works for jobs under 15 min but can't survive reconnects or container cycling. Break into async-task pattern even for 5–10 minute jobs.
- **In-memory state** — the microVM can be replaced between calls even inside a "sticky" session. Every state mutation goes to durable storage (DDB / Memory).

### Common pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Clients create fresh `Mcp-Session-Id` per poll | Container boot storm; cross-microVM races; false-positive "orphan" cleanup | Reuse one session_id for the job lifetime (use job_id itself) |
| `/ping` blocked by main work | Session killed at 15 min with no log | Keep ping on a separate thread; never acquire locks held by workers |
| Progress only in memory | Client reconnects see stale/no progress | Write progress to DDB / AgentCore Memory on every update |
| No `HealthyBusy` signal | Long jobs killed mid-flight at 15 min | Call `add_async_task` (SDK) or return `HealthyBusy` from `/ping` |
| Background goroutine holds the parent request's `ctx` | Goroutine cancelled when the invoke response returns | Derive a detached context from a base context that outlives the request |
| Retry loops that go silent for >5 min | Boot-time orphan scanners (if any) mistakenly fail the job | Heartbeat to DDB separately from progress writes |

### When to reach for AgentCore Memory

AgentCore Memory is AWS's built-in durable state service (short + long-term). For long-running jobs, Memory is better than raw DDB when:
- You need cross-agent or cross-session context
- You want AWS to manage the schema
- You're using the Strands/LangGraph SDK's built-in `AgentCoreMemorySessionManager`

Raw DDB is better when:
- You need arbitrary secondary indexes / custom queries
- The schema is project-specific (e.g. podcast metadata, status enums, credit balances)
- You already have a single-table design

Either way: write progress ON EVERY MEANINGFUL STATE CHANGE so clients polling see a fresh row and session-reconnects can resume from known state.

### Verification checklist

Before declaring a long-running agent "production ready":

- [ ] Tool returns `job_id` in <5 seconds; actual work runs in a goroutine/thread.
- [ ] Progress writes land in durable storage every 1–5 s.
- [ ] `/ping` returns `HealthyBusy` while workers are active (test with `curl /ping` during a job).
- [ ] Client uses a single `Mcp-Session-Id` across all calls for one job (test: `aws logs filter-log-events ... "Podcaster MCP Server starting"` should show one boot per job, not one per poll).
- [ ] Reconnect works: kill the client mid-job, start fresh with the same session_id, poll returns current status.
- [ ] `LifecycleConfiguration` is set and sized for the longest job you expect.
- [ ] Logs carry the session_id so CloudWatch queries can scope to a single job.
- [ ] Credit/billing handled idempotently — a retried invocation must not double-bill.

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
agentcore status --agent myagent

# View CloudWatch logs (log group includes the endpoint name)
aws logs tail /aws/bedrock-agentcore/runtimes/<agent_id>-<endpoint_name> --follow

# Local dev server logs stream to the terminal directly
# (there is no AGENTCORE_LOG_LEVEL env var; `agentcore dev` has no debug/verbose flag)
agentcore dev

# Invoke (there is no --debug flag)
agentcore invoke '{"prompt": "test"}'
```

---

## Key Facts

### Runtime Limits

Verified against the AgentCore Runtime quota tables (2026-07-25).

| Resource | Limit |
|----------|-------|
| Synchronous request timeout | 15 min (not adjustable) |
| Idle session timeout | 15 min of inactivity (adjustable — see Session lifecycle knobs above) |
| Max session duration | 8 hrs (adjustable — see Session lifecycle knobs above) |
| Max async job duration | 8 hrs (not adjustable) |
| Max payload size | 100 MB |
| Hardware per session | 2 vCPU / 8 GB (not adjustable; there is no separate "per-agent" memory quota) |
| Active session workloads per account | 5,000 in us-east-1 & us-west-2; 2,500 elsewhere (adjustable via Service Quotas) |

### Supported Frameworks

- **Strands** - AWS native, simplest path
- **LangGraph** - LangChain ecosystem
- **CrewAI** - Multi-agent collaboration
- **AutoGen** - Multi-agent conversations
- **Google ADK** - Google's framework
- **OpenAI Agents SDK** - OpenAI's framework
- **Custom** - Any Python agent (values above match `agentcore create --agent-framework`; anything else brings your own runtime code)

### Supported Models

- Amazon Bedrock: Claude, Nova, Llama, Mistral
- OpenAI: GPT-5.5 and earlier GPT models
- Anthropic: Claude (direct API)
- Google: Gemini
- Self-hosted models

### Protocols

- **MCP** (Model Context Protocol) - Tool connectivity
- **A2A** (Agent to Agent) - Inter-agent communication
- **AG-UI** - Agent-to-frontend UI streaming (`AGUIApp`, `build_ag_ui_app`, `serve_ag_ui` in `bedrock_agentcore.runtime`)

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
