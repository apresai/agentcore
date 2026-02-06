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
.claude/skills/    # Claude Code skills (portable with repo)
research/          # Documentation summaries for each AgentCore service
articles/          # Published articles showcasing AgentCore
examples/          # Code examples demonstrating AgentCore features
```

## Skills

This repo includes two Claude Code skills. See `SKILLS.md` for full documentation.

| Skill | Purpose | Trigger |
|-------|---------|---------|
| `/agentcore` | Build agents, API help, troubleshooting | "How do I deploy an agent?" |
| `/agentcore-article` | Create articles, update research | "Write an article about Memory" |

Skills are stored in `.claude/skills/` and symlinked to `~/.claude/skills/` for portability.

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

### Hitchhiker's Guide to the Galaxy Theme (REQUIRED)

All articles, code examples, and documentation must weave in **Hitchhiker's Guide to the Galaxy** references and witty comedy throughout:

- **Articles**: Use HHGTTG quotes, character references, and analogies to explain AgentCore concepts
- **Code examples**: Include themed print output, ASCII art banners, themed variable names, and witty comments
- **READMEs**: Maintain the playful tone while staying technically accurate

**Character/concept mapping:**
| AgentCore Concept | HHGTTG Analog |
|-------------------|---------------|
| Runtime | Deep Thought (computing answers) |
| Memory | Marvin the Paranoid Android (remembers everything, wishes he didn't) |
| Gateway | The Babel Fish (universal translator for APIs) |
| Browser | The Hitchhiker's Guide (the ultimate reference) |
| Code Interpreter | Deep Thought's Calculator |
| Framework comparison | Ford Prefect (simple) vs Zaphod Beeblebrox (flashy) |
| The Answer | 42 (always) |

**Tone**: Witty, self-deprecating, technically accurate. Think Douglas Adams explaining cloud infrastructure.

## Code Examples - STRICT REQUIREMENTS

**NO MOCKING ALLOWED.** All code examples must:

1. **Use real AWS APIs** - Never mock AWS services, boto3 clients, or AgentCore SDK
2. **Actually work** - Code must be copy-paste runnable with real AWS credentials
3. **Call real services** - Examples should make actual API calls (Bedrock, AgentCore, etc.)
4. **Test against production** - Verify examples work against real AWS infrastructure before committing

If a service requires deployment or complex setup, the example should:
- Show the real SDK/API calls (not mocks)
- Include clear prerequisites for what needs to be deployed first
- Provide deployment commands if applicable

**Forbidden patterns:**
- `class MockXxx` or `class FakeXxx`
- `def mock_xxx()`
- `unittest.mock`, `MagicMock`, `patch`
- Simulated responses or hardcoded fake data pretending to be API responses
- Any class/function that pretends to be an AWS service

The goal is working code that demonstrates real AgentCore capabilities, not fake demonstrations.

## TODO

### Articles to Write
Use `/agentcore-article` with the prompts in `articles/00-article-ideas.md` for each.

- [x] #6: MCP Gateway Deep Dive
- [x] #7: Agent Security with Cedar Policies
- [x] #8: Building a Customer Support Agent (tutorial)
- [x] #9: Multi-Agent SRE Assistant (tutorial)
- [x] #10: Device Management Agent for IoT (tutorial)
- [x] #11: Deep Research Agents on AgentCore
- [x] #12: Enterprise Agent Platform Architecture
- [x] #13: Cost Optimization Strategies
- [x] #14: Observability Best Practices
- [x] #15: AgentCore vs Self-Hosted LangGraph
- [x] #16: Migrating from PoC to Production
- [x] #17: Using Strands Agents with AgentCore
- [x] #18: LangGraph on AgentCore
- [x] #19: OpenAI Agents SDK to AWS

### Housekeeping
- [x] Push latest commit to origin
- [x] `venv/` dirs already ignored by root `.gitignore`

## Bedrock Model ID

All code examples and articles must use **Claude Haiku 4.5** via Bedrock:

```
us.anthropic.claude-haiku-4-5-20251001-v1:0
```

- The `us.` prefix is required (cross-region inference profile)
- The `-v1:0` suffix is required
- This applies to both `strands.models.BedrockModel` and `langchain_aws.ChatBedrock`
- For OpenAI Agents SDK: `bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0`

## Key Technical Details

- **Frameworks**: LangGraph, Strands, CrewAI, LlamaIndex, Google ADK, OpenAI Agents SDK
- **Models**: Any model (Bedrock, OpenAI, Gemini, Claude, Nova, Llama, Mistral)
- **Protocols**: MCP (Model Context Protocol), A2A (Agent to Agent)
- **Pricing**: Consumption-based, I/O wait is free, $200 free tier for new customers
- **Regions**: 14 regions for core services (Runtime, Memory, Gateway, Identity) including us-east-1, us-east-2, us-west-2, eu-central-1, eu-west-1, eu-west-2, eu-west-3, eu-north-1, ap-south-1, ap-southeast-1, ap-southeast-2, ap-northeast-1, ap-northeast-2, ca-central-1
