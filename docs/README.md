# AgentCore Documentation

> Comprehensive guides for AWS Bedrock AgentCore

## Navigation

### Getting Started

- **[Quick Start Guide](getting-started.md)** — Deploy your first agent in minutes
- **[Installation](getting-started.md#installation)** — SDK and CLI setup
- **[Hello World Example](getting-started.md#hello-world)** — Your first AgentCore agent

### Services Reference

| Service | Description | Status |
|---------|-------------|--------|
| [Runtime](services/runtime.md) | Serverless hosting with microVM isolation | GA |
| [Memory](services/memory.md) | Short-term and long-term context | GA |
| [Gateway](services/gateway.md) | API to MCP tool conversion | GA |
| [Identity](services/identity.md) | Agent auth and credentials | GA |
| [Code Interpreter](services/code-interpreter.md) | Secure Python/JS/TS execution | GA |
| [Browser](services/browser.md) | Isolated web automation | GA |
| [Observability](services/observability.md) | OTEL tracing and metrics | GA |
| [Evaluations](services/evaluations.md) | LLM-as-a-Judge quality | Preview |
| [Policy](services/policy.md) | Cedar access control | Preview |

### Examples

| Example | Description | Location |
|---------|-------------|----------|
| Runtime Deployment | Basic agent deployment | [articles/examples/runtime/](../articles/examples/runtime/) |
| Memory Integration | Context-aware conversations | [articles/examples/memory/](../articles/examples/memory/) |

### Research & Reference

Detailed documentation for each service is in the `research/` directory:

```
research/
├── 00-overview.md          # Platform overview (start here)
├── 01-runtime.md           # Runtime deep dive
├── 02-memory.md            # Memory deep dive
├── 03-gateway.md           # Gateway deep dive
├── 04-identity.md          # Identity deep dive
├── 05-code-interpreter.md  # Code Interpreter
├── 06-browser.md           # Browser deep dive
├── 07-policy.md            # Policy deep dive
├── 08-observability.md     # Observability
├── 09-evaluations.md       # Evaluations
├── 10-getting-started.md   # Official getting started
└── 11-pricing.md           # Pricing details
```

### Contributing

- **[Contributing Guide](../CONTRIBUTING.md)** — How to contribute to this repo
- **[Claude Code Skills](../SKILLS.md)** — Using the `/agentcore` and `/agentcore-article` skills

---

## Quick Links

| Resource | Link |
|----------|------|
| AWS Documentation | [docs.aws.amazon.com/bedrock-agentcore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/) |
| GitHub Samples | [awslabs/amazon-bedrock-agentcore-samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples/) |
| Pricing | [aws.amazon.com/bedrock/agentcore/pricing](https://aws.amazon.com/bedrock/agentcore/pricing/) |
| Product Page | [aws.amazon.com/bedrock/agentcore](https://aws.amazon.com/bedrock/agentcore/) |

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                         Your Application                           │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────────┐
│                        AgentCore Runtime                           │
│  • MicroVM isolation per session                                   │
│  • Up to 8-hour execution                                          │
│  • Consumption-based billing (I/O wait is free)                    │
└──────────────────────────────┬─────────────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│     Gateway     │   │     Memory      │   │    Identity     │
│                 │   │                 │   │                 │
│ • MCP tools     │   │ • Short-term    │   │ • IdP support   │
│ • 1-click apps  │   │ • Long-term     │   │ • Credentials   │
│ • Semantic find │   │ • Shared stores │   │ • OAuth flows   │
└────────┬────────┘   └─────────────────┘   └─────────────────┘
         │
         ▼
┌─────────────────┐
│     Policy      │
│                 │
│ • Cedar rules   │
│ • NL authoring  │
│ • Deterministic │
└─────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                        Built-in Tools                              │
├──────────────────────────────┬─────────────────────────────────────┤
│      Code Interpreter        │           Browser                   │
│                              │                                     │
│ • Python, JS, TypeScript     │ • Isolated sessions                 │
│ • Up to 5GB files            │ • Live view & recording             │
│ • 8-hour execution           │ • Playwright compatible             │
└──────────────────────────────┴─────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                         Operations                                 │
├──────────────────────────────┬─────────────────────────────────────┤
│       Observability          │         Evaluations                 │
│                              │                                     │
│ • OTEL compatible            │ • LLM-as-a-Judge                    │
│ • CloudWatch dashboards      │ • Online & on-demand                │
│ • Step-by-step traces        │ • Custom evaluators                 │
└──────────────────────────────┴─────────────────────────────────────┘
```

---

## Framework Support Matrix

| Framework | Runtime | Memory | Gateway | Observability | Evaluations |
|-----------|:-------:|:------:|:-------:|:-------------:|:-----------:|
| Strands | ✅ | ✅ | ✅ | ✅ | ✅ |
| LangGraph | ✅ | ✅ | ✅ | ✅ | ✅ |
| CrewAI | ✅ | ✅ | ✅ | ✅ | ✅ |
| LlamaIndex | ✅ | ✅ | ✅ | ✅ | ✅ |
| Google ADK | ✅ | ✅ | ✅ | ✅ | — |
| OpenAI SDK | ✅ | ✅ | ✅ | ✅ | — |
| Custom | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Common Tasks

### Deploy an Agent

```bash
# Create
agentcore create my-agent

# Deploy
agentcore deploy my-agent

# Invoke
agentcore invoke my-agent "Hello!"
```

### Add Memory to Your Agent

```python
from bedrock_agentcore.memory import MemoryClient

memory = MemoryClient()
session = memory.create_session(agent_id="my-agent")

# Store context
session.add_message(role="user", content="I prefer window seats")

# Retrieve later
context = session.get_messages()
```

### Connect APIs via Gateway

```python
from bedrock_agentcore.gateway import GatewayClient

gateway = GatewayClient()

# Create MCP tools from OpenAPI spec
tools = gateway.create_from_openapi(
    name="my-api",
    spec_url="https://api.example.com/openapi.json"
)
```

### Add Policy Rules

```python
from bedrock_agentcore.policy import PolicyClient

policy = PolicyClient()

# Natural language policy
policy.create_from_description(
    "Allow read-only access to customer data for support agents"
)
```

---

## Need Help?

- **Questions**: [AWS re:Post AgentCore](https://repost.aws/tags/TAG-agentcore)
- **Issues**: [GitHub Issues](https://github.com/awslabs/amazon-bedrock-agentcore-samples/issues)
- **Support**: [AWS Support](https://aws.amazon.com/support/)
