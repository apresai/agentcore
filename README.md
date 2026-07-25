<p align="center">
  <img src="https://img.shields.io/badge/AWS-Bedrock%20AgentCore-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white" alt="AWS Bedrock AgentCore"/>
</p>

<h1 align="center">AgentCore Knowledge Base</h1>

<p align="center">
  <strong>Build, deploy, and operate AI agents at enterprise scale</strong>
</p>

<p align="center">
  <a href="https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/"><img src="https://img.shields.io/badge/docs-AWS%20Documentation-232F3E?logo=amazonaws" alt="AWS Docs"/></a>
  <a href="https://github.com/awslabs/amazon-bedrock-agentcore-samples/"><img src="https://img.shields.io/badge/samples-GitHub-181717?logo=github" alt="Samples"/></a>
  <a href="https://aws.amazon.com/bedrock/agentcore/pricing/"><img src="https://img.shields.io/badge/pricing-consumption--based-green" alt="Pricing"/></a>
  <a href="#regional-availability"><img src="https://img.shields.io/badge/regions-multi--region-blue" alt="Regions"/></a>
</p>

<p align="center">
  <a href="#what-is-agentcore">What is AgentCore?</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#services">Services</a> •
  <a href="docs/">Documentation</a> •
  <a href="#claude-code-skills">Skills</a>
</p>

---

## What is AgentCore?

**Amazon Bedrock AgentCore** is AWS's modular platform for building production AI agents. It provides the infrastructure layer between your agent code (any framework) and foundation models (any provider), handling:

| Capability | Description |
|------------|-------------|
| **Secure Execution** | MicroVM isolation for each session |
| **Tool Integration** | MCP-compatible gateways with 1-click integrations |
| **Context Management** | Short-term and long-term memory |
| **Identity & Access** | Enterprise IdP integration (Okta, Entra ID, Cognito) |
| **Observability** | OTEL-compatible tracing and metrics |
| **Policy Enforcement** | Cedar-based deterministic access controls |

### Key Differentiators

```
┌─────────────────────────────────────────────────────────────────┐
│  🔓 Framework Agnostic    Use LangGraph, Strands, CrewAI,       │
│                          LlamaIndex, Google ADK, OpenAI SDK     │
├─────────────────────────────────────────────────────────────────┤
│  🤖 Model Agnostic        Claude, Nova, GPT-4, Gemini, Llama,   │
│                          Mistral, or any model                  │
├─────────────────────────────────────────────────────────────────┤
│  📦 Modular Architecture  Use services independently or         │
│                          together—start small, scale up         │
├─────────────────────────────────────────────────────────────────┤
│  💰 Consumption Pricing   Pay for actual usage; I/O wait        │
│                          periods (30-70% of execution) are FREE │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Install the SDK and CLI

```bash
pip install bedrock-agentcore bedrock-agentcore-starter-toolkit
```

### 2. Create Your First Agent

```bash
agentcore create -p myfirstagent
cd myfirstagent
```

### 3. Deploy to AgentCore

```bash
agentcore deploy
```

### 4. Invoke Your Agent

```bash
agentcore invoke '{"prompt": "Hello, agent!"}'
```

> [!TIP]
> New AWS customers get **$200 in Free Tier credits** for AgentCore.

---

## Architecture

```
                              ┌──────────────────┐
                              │   Your Agent     │
                              │ (Any Framework)  │
                              └────────┬─────────┘
                                       │
                    ┌──────────────────▼──────────────────┐
                    │        AgentCore Runtime            │
                    │  (MicroVM Isolation, 8hr Sessions)  │
                    └──────────────────┬──────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        ▼                              ▼                              ▼
┌───────────────┐            ┌─────────────────┐            ┌─────────────────┐
│    Gateway    │            │     Memory      │            │    Identity     │
│  (MCP Tools)  │            │ (Context Store) │            │  (Auth/Creds)   │
└───────┬───────┘            └─────────────────┘            └─────────────────┘
        │
        ▼
┌───────────────┐
│    Policy     │
│ (Cedar Rules) │
└───────────────┘

                    ┌─────────────────────────────────┐
                    │         Built-in Tools          │
                    ├────────────────┬────────────────┤
                    │ Code Interpreter│    Browser    │
                    │ (Python/JS/TS) │(Web Automation)│
                    └────────────────┴────────────────┘

                    ┌─────────────────────────────────┐
                    │          Operations             │
                    ├────────────────┬────────────────┤
                    │  Observability │  Evaluations   │
                    │(OTEL/CloudWatch)│(LLM-as-Judge) │
                    └────────────────┴────────────────┘
```

---

## Services

<table>
<tr>
<td width="33%">

### Runtime
Serverless hosting with microVM isolation

- 8-hour sessions
- 100MB payloads
- WebSocket streaming
- Consumption pricing

[Learn more →](docs/services/runtime.md)

</td>
<td width="33%">

### Memory
Short-term + long-term context

- Session continuity
- Cross-session learning
- Shared memory stores
- Multi-agent state

[Learn more →](docs/services/memory.md)

</td>
<td width="33%">

### Gateway
APIs to MCP tools

- OpenAPI conversion
- Lambda integration
- 1-click connectors
- Semantic discovery

[Learn more →](docs/services/gateway.md)

</td>
</tr>
<tr>
<td>

### Identity
Agent auth & credentials

- IdP integration
- JWT authorization
- Credential vault
- OAuth flows

[Learn more →](docs/services/identity.md)

</td>
<td>

### Code Interpreter
Secure code execution

- Python, JS, TypeScript
- Up to 5GB files
- 8-hour execution
- Network access

[Learn more →](docs/services/code-interpreter.md)

</td>
<td>

### Browser
Web automation

- Session isolation
- Live view
- Recording
- Playwright support

[Learn more →](docs/services/browser.md)

</td>
</tr>
<tr>
<td>

### Observability
OTEL tracing

- Step-by-step traces
- CloudWatch dashboards
- Custom metrics
- Rich metadata

[Learn more →](docs/services/observability.md)

</td>
<td>

### Evaluations
LLM-as-a-Judge

- Online evaluation
- Custom evaluators
- Quality monitoring
- GA, billed per token

[Learn more →](docs/services/evaluations.md)

</td>
<td>

### Policy
Cedar access control

- Natural language authoring
- Fine-grained rules
- Deterministic enforcement
- GA, billed per token

[Learn more →](docs/services/policy.md)

</td>
</tr>
</table>

---

## Framework Support

AgentCore works with **any agent framework**:

| Framework | Integration Level | Best For |
|-----------|------------------|----------|
| **[Strands](https://github.com/strands-agents/strands-agents)** | First-class | Simplest path to production |
| **[LangGraph](https://github.com/langchain-ai/langgraph)** | Native | Complex multi-step workflows |
| **[CrewAI](https://github.com/crewAIInc/crewAI)** | Full | Multi-agent collaboration |
| **[LlamaIndex](https://github.com/run-llama/llama_index)** | Native | RAG-focused agents |
| **[Google ADK](https://github.com/google/adk-python)** | Full | Gemini integration |
| **[OpenAI SDK](https://github.com/openai/openai-python)** | Full | OpenAI model optimization |
| **Custom** | Full | Complete control |

---

## Regional Availability

AgentCore spans many AWS regions, and coverage varies by service (Runtime, Gateway, Identity, Built-in Tools, and Observability have the broadest reach; some newer capabilities are checked in a narrower subset). See the [AWS AgentCore Supported Regions page](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-regions.html) for the current, authoritative list rather than relying on a hardcoded table here.

Commonly used regions:

| Region | Code |
|--------|------|
| US East (N. Virginia) | `us-east-1` |
| US West (Oregon) | `us-west-2` |
| Asia Pacific (Sydney) | `ap-southeast-2` |
| Europe (Frankfurt) | `eu-central-1` |

---

## Repository Structure

```
agentcore/
├── research/                    # Service documentation (source of truth)
│   ├── 00-overview.md          # Platform overview
│   ├── 01-runtime.md           # Runtime service
│   ├── 02-memory.md            # Memory service
│   ├── 03-gateway.md           # Gateway service
│   ├── 04-identity.md          # Identity service
│   ├── 05-code-interpreter.md  # Code Interpreter
│   ├── 06-browser.md           # Browser service
│   ├── 07-policy.md            # Policy service
│   ├── 08-observability.md     # Observability
│   ├── 09-evaluations.md       # Evaluations
│   ├── 10-getting-started.md   # Getting started guide
│   └── 11-pricing.md           # Pricing details
├── articles/                    # Published content
│   ├── examples/               # Runnable code examples
│   └── images/                 # Generated artwork
├── docs/                        # GitHub documentation
│   ├── getting-started.md      # Quick start guide
│   └── services/               # Service deep dives
├── CONTRIBUTING.md              # How to contribute
└── .claude/skills/              # Claude Code skills
    ├── agentcore/              # Developer assistance
    └── agentcore-article/      # Content generation
```

---

## Claude Code Skills

This repo includes two [Claude Code](https://claude.ai/code) skills for working with AgentCore:

### `/agentcore` — Build Agents

Get help building, deploying, and troubleshooting AgentCore agents.

```
"How do I deploy an agent to AgentCore?"
"What is AgentCore Memory?"
"Show me a Strands agent example"
"My deployment is failing with permission errors"
```

### `/agentcore-article` — Generate Content

Create articles with research, runnable code examples, and branded artwork.

```
"Write an article about AgentCore Runtime"
"Create a tutorial for Memory integration"
```

<details>
<summary><b>Skill Installation</b></summary>

Skills are stored in `.claude/skills/` and symlinked to your global skills directory:

```bash
# Create symlinks (adjust repo path as needed)
ln -s /path/to/agentcore/.claude/skills/agentcore ~/.claude/skills/agentcore
ln -s /path/to/agentcore/.claude/skills/agentcore-article ~/.claude/skills/agentcore-article
```

Verify:
```bash
ls -la ~/.claude/skills/agentcore*
```

</details>

---

## Use Cases

<details>
<summary><b>Enterprise Customer Support</b></summary>

- **Runtime**: Session isolation per customer
- **Identity**: Corporate IdP integration
- **Gateway**: CRM, ticketing, banking APIs
- **Policy**: Transaction limits, data access rules
- **Memory**: Customer preferences, interaction history

</details>

<details>
<summary><b>Internal Developer Platform</b></summary>

- **Runtime**: Centralized hosting for all teams
- **Gateway**: Curated approved tools (JIRA, GitHub)
- **Memory**: Shared knowledge bases
- **Policy**: Per-team access controls
- **Evaluations**: Quality monitoring across agents

</details>

<details>
<summary><b>Data Analysis Agent</b></summary>

- **Runtime**: Hosts analysis workflows
- **Code Interpreter**: Python for analysis and visualization
- **Gateway**: Data warehouse connections
- **Memory**: Analysis patterns and preferences

</details>

<details>
<summary><b>Web Research Agent</b></summary>

- **Runtime**: Long-running research sessions
- **Browser**: Web navigation and extraction
- **Code Interpreter**: Data processing
- **Memory**: Research tracking over time

</details>

---

## Documentation

| Document | Description |
|----------|-------------|
| [Getting Started](docs/getting-started.md) | Quick start guide |
| [Services Reference](docs/services/) | Deep dives on each service |
| [Examples](articles/examples/) | Runnable code examples |
| [Contributing](CONTRIBUTING.md) | How to contribute |

### External Resources

- [AWS AgentCore Developer Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [AWS AgentCore Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples/)
- [AgentCore Pricing](https://aws.amazon.com/bedrock/agentcore/pricing/)
- [Strands Agents Framework](https://github.com/strands-agents/strands-agents)

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. **Research updates**: Edit files in `research/`
2. **New articles**: Use the `/agentcore-article` skill
3. **Code examples**: Add to `articles/examples/`
4. **Documentation**: Update files in `docs/`

---

## License

This knowledge base is for educational purposes. AWS Bedrock AgentCore is a product of Amazon Web Services. See [AWS Service Terms](https://aws.amazon.com/service-terms/) for AgentCore usage.

---

<p align="center">
  <sub>Built with Claude Code • Powered by AWS Bedrock AgentCore</sub>
</p>
