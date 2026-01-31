# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a knowledge base for AWS Bedrock AgentCore - a collection of research, documentation summaries, and articles showcasing the product.

**What is AgentCore?** A modular, agentic platform for building, deploying, and operating AI agents securely at scale using any framework and any foundation model.

## Primary Sources

- Documentation: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/
- Product page: https://aws.amazon.com/bedrock/agentcore/
- GitHub samples: https://github.com/awslabs/amazon-bedrock-agentcore-samples/

## Repository Structure

```
research/          # Documentation summaries for each AgentCore service
articles/          # Published articles showcasing AgentCore
examples/          # Code examples demonstrating AgentCore features
```

## AgentCore Services (Quick Reference)

| Service | Purpose |
|---------|---------|
| Runtime | Serverless hosting with microVM isolation, 8-hour execution |
| Memory | Short-term (session) + long-term (cross-session) context |
| Gateway | Convert APIs/Lambda to MCP tools, 1-click integrations |
| Identity | Agent auth with IdP integration (Okta, Entra ID, Cognito) |
| Code Interpreter | Secure Python/JS/TS execution, up to 5GB files |
| Browser | Isolated web interaction with session recording |
| Observability | OTEL-compatible tracing via CloudWatch |
| Evaluations | LLM-as-a-Judge quality assessment (Preview) |
| Policy | Cedar-based deterministic access control (Preview) |

## Content Guidelines

- All content should be original analysis and synthesis, not copied documentation
- Focus on practical use cases and architectural patterns
- Include working code examples where applicable
- Cross-reference official AWS documentation
- Use AgentCore CLI commands (`agentcore create`, `agentcore deploy`, `agentcore invoke`)

## Key Technical Details

- **Frameworks**: LangGraph, Strands, CrewAI, LlamaIndex, Google ADK, OpenAI Agents SDK
- **Models**: Any model (Bedrock, OpenAI, Gemini, Claude, Nova, Llama, Mistral)
- **Protocols**: MCP (Model Context Protocol), A2A (Agent to Agent)
- **Pricing**: Consumption-based, I/O wait is free, $200 free tier for new customers
- **Regions**: us-east-1, us-west-2, ap-southeast-2, eu-central-1
