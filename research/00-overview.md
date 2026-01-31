# AWS Bedrock AgentCore Overview

## What is Amazon Bedrock AgentCore?

Amazon Bedrock AgentCore is an agentic platform for building, deploying, and operating highly effective agents securely at scale using **any framework** and **any foundation model**. It eliminates infrastructure management while providing enterprise-grade security and reliability.

**Key Value Proposition**: AgentCore lets you choose between open-source flexibility AND enterprise-grade security - you don't have to pick one or the other.

## Core Services

AgentCore is a modular platform with 9 services that can be used independently or together:

| Service | Purpose |
|---------|---------|
| **Runtime** | Secure, serverless hosting for AI agents and tools |
| **Memory** | Short-term and long-term context management |
| **Gateway** | Convert APIs/Lambda into MCP-compatible tools |
| **Identity** | Agent authentication and credential management |
| **Code Interpreter** | Secure sandbox for code execution |
| **Browser** | Web interaction in isolated environments |
| **Observability** | Tracing, debugging, and monitoring |
| **Evaluations** | Automated agent quality assessment |
| **Policy** | Deterministic control over agent actions |

## Framework & Model Compatibility

### Supported Frameworks
- LangGraph
- Strands Agents
- CrewAI
- LlamaIndex
- Google ADK
- OpenAI Agents SDK
- Custom frameworks

### Supported Models
- Amazon Nova
- Anthropic Claude
- Meta Llama
- Mistral
- OpenAI
- Google Gemini
- Any model in or outside Amazon Bedrock

### Supported Protocols
- Model Context Protocol (MCP)
- Agent to Agent (A2A)

## Common Use Cases

1. **Autonomous AI Applications**: Customer support, workflow automation, data analysis, coding assistance
2. **Tools and MCP Servers**: Transform existing APIs/databases into agent-accessible tools
3. **Agent Platforms**: Internal developer platforms with approved tools, shared memory, governed access

## Pricing Model

- **Consumption-based** with no upfront commitments or minimum fees
- Pay only for what you use
- Each service billed independently
- **$200 Free Tier credits** for new AWS customers

## Regional Availability

Available in:
- US East (N. Virginia)
- US West (Oregon)
- Asia Pacific (Sydney)
- Europe (Frankfurt)

## Status

**Preview** - Some services (Policy, Evaluations) are in preview with no additional charges.
