# What is AWS Bedrock AgentCore? A Complete Guide

![AgentCore Overview](images/overview-article.webp)

**DON'T PANIC.**

In *The Hitchhiker's Guide to the Galaxy*, the Guide itself was described as the most remarkable book ever to come out of the great publishing corporations of Ursa Minor -- not because it was accurate (it had many omissions and contained much that was apocryphal), but because it had the words **DON'T PANIC** inscribed on its cover in large, friendly letters. It also told you everything you needed to know about navigating an impossibly complex galaxy.

Building production AI agents feels a lot like navigating that galaxy. Most teams spend months building infrastructure before their agent handles a single customer request. Security reviews, compliance audits, scaling concerns, and operational overhead consume engineering cycles that should go toward building actual agent capabilities.

**Amazon Bedrock AgentCore** is the Guide for AI agents. It provides enterprise-grade infrastructure as a managed service, inscribed with its own version of "DON'T PANIC" -- letting you focus on what your agents do rather than how they run.

This guide explains what AgentCore is, how its nine services work together, and when you should (or should not) use it for your AI initiatives.

## Executive Summary

AgentCore is AWS's modular platform for building, deploying, and operating AI agents at enterprise scale. Unlike vertically integrated solutions that lock you into specific frameworks and models, AgentCore provides the infrastructure layer that sits between your agent code and the foundation models, handling:

- **Secure execution** with microVM isolation for each user session
- **Tool integration** through MCP-compatible gateways
- **Context management** with short-term and long-term memory
- **Identity and access** with enterprise IdP integration
- **Observability** with OpenTelemetry-compatible tracing
- **Policy enforcement** with deterministic access controls

The platform is framework-agnostic (works with LangGraph, Strands, CrewAI, and others), model-agnostic (use Claude, GPT, Gemini, Nova, or any model), and consumption-priced (pay only for actual resource usage, with I/O wait time free).

## The Nine AgentCore Services

The original *Hitchhiker's Guide* had entries on everything from Babel fish to Vogon poetry. AgentCore takes a similar approach to agent infrastructure: nine interconnected services, each covering a distinct region of the operational galaxy. Each can be used independently or together, allowing you to start with what you need and add capabilities as your requirements grow.

### 1. Runtime

**What it does**: Serverless hosting environment purpose-built for AI agents.

Runtime transforms any local agent into a cloud-native deployment. Each user session runs in a dedicated microVM with isolated CPU, memory, and filesystem. When a session completes, the microVM is terminated and memory is sanitized.

**Key capabilities**:
- MicroVM isolation per session
- Up to 8-hour execution time (not the typical 15-minute Lambda limit)
- 100MB payload support for multi-modal content
- Bidirectional WebSocket streaming
- Consumption-based pricing with free I/O wait

**When to use**: You need to deploy agents to production with enterprise security, support long-running sessions, or want to avoid infrastructure management.

### 2. Memory

**What it does**: Short-term and long-term context management.

Memory addresses the statelessness problem in AI agents. Without memory, agents are like Marvin the Paranoid Android perpetually introduced to the same people -- they treat each interaction as isolated, with no recollection of what came before. Memory provides both session-level context (short-term) and cross-session learning (long-term).

**Key capabilities**:
- Short-term memory for multi-turn conversations within a session
- Long-term memory for user preferences and facts across sessions
- Shared memory stores for multi-agent coordination
- Automatic extraction and storage of key insights

**When to use**: Building conversational agents that need context continuity, personalizing experiences based on user history, or coordinating state across multiple agents.

### 3. Gateway

**What it does**: Converts APIs, Lambda functions, and services into MCP-compatible tools.

Gateway is the Babel fish of the platform -- it bridges your existing enterprise systems and AI agents, translating between incompatible worlds. Instead of writing custom integration code, Gateway transforms APIs into agent-ready tools with configuration, not code.

**Key capabilities**:
- Multi-source tool creation (OpenAPI specs, Lambda functions, MCP servers)
- 1-click integrations for Salesforce, Slack, Jira, Asana, Zendesk, Zoom, GitHub
- Semantic tool discovery for large tool collections
- Comprehensive authentication handling (OAuth, API keys)

**When to use**: Agents need to access existing APIs, you want pre-built integrations with SaaS services, or your agents need to discover and use hundreds of tools.

### 4. Identity

**What it does**: Secure identity and credential management for AI agents.

Identity solves authentication and authorization for agents. It provides secure authentication for both inbound requests (who is calling your agent) and outbound requests (what your agent can access).

**Key capabilities**:
- Native integration with Okta, Microsoft Entra ID, Amazon Cognito, Auth0
- Inbound JWT authentication for verifying callers
- Outbound credential vault for accessing external services
- Identity-aware authorization in Policy rules

**When to use**: Agents need to act on behalf of authenticated users, you need centralized credential management, or you want to integrate with existing enterprise identity providers.

### 5. Code Interpreter

**What it does**: Secure sandbox environment for agents to execute code.

Code Interpreter enables agents to write and run code securely. This is critical for tasks that require precise calculations, data analysis, or file processing that cannot be achieved through reasoning alone.

**Key capabilities**:
- Python, JavaScript, and TypeScript runtimes
- Containerized sandbox execution
- File uploads up to 5GB via S3
- Execution time up to 8 hours
- Network access configurable

**When to use**: Agents need to perform calculations, analyze data, process files (CSV, Excel, JSON), or generate and test code dynamically.

### 6. Browser

**What it does**: Managed browser runtime for web automation.

Browser provides isolated browser sessions for agents to interact with web applications. Each session runs in an ephemeral container that resets after use.

**Key capabilities**:
- Session isolation with automatic cleanup
- Live view for real-time monitoring
- Session recording for audit and replay
- Configurable timeouts up to 8 hours
- Playwright and BrowserUse compatibility

**When to use**: Agents need to navigate websites, extract web data, fill and submit forms, or automate web-based workflows.

### 7. Observability

**What it does**: Trace, debug, and monitor agent performance.

Observability provides visibility into how agents behave in production. It offers detailed visualizations of each execution step, enabling inspection of reasoning paths, tool invocations, and performance bottlenecks.

**Key capabilities**:
- Step-by-step execution traces
- Real-time CloudWatch dashboards
- OpenTelemetry (OTEL) compatibility
- Rich metadata tagging
- Built-in metrics for all services

**When to use**: Debugging agent behavior, understanding decision-making processes, identifying performance issues, or auditing agent actions for compliance.

### 8. Evaluations (Preview)

**What it does**: Automated quality assessment using LLM-as-a-Judge.

Evaluations measures how well agents perform tasks, handle edge cases, and maintain consistency. It provides measurable quality signals for optimization.

**Key capabilities**:
- 13 built-in evaluators (correctness, helpfulness, safety, etc.)
- Custom evaluator support for domain-specific metrics
- Online evaluation (real-time) and on-demand (batch)
- Framework integration with Strands and LangGraph

**When to use**: Ensuring agents meet quality standards before deployment, continuous monitoring in production, comparing different configurations, or identifying regressions after changes.

### 9. Policy (Preview)

**What it does**: Deterministic control over agent actions.

Policy creates a protective boundary around agent operations using Cedar, AWS's open-source policy language. Think of it as the Vogon bureaucracy, except actually useful -- it ensures agents operate within defined boundaries with the kind of rigid determinism that would make a Vogon captain weep with joy.

**Key capabilities**:
- Cedar policy language for fine-grained permissions
- Natural language policy authoring
- Gateway integration for enforcement
- Fine-grained control based on user identity and context

**When to use**: Agents need restricted access to sensitive tools, compliance requires deterministic access control, or business rules must be enforced consistently.

## Key Differentiators

Like the Guide itself, AgentCore's value is not in any single entry -- it is in the comprehensiveness of the whole thing.

### Framework Agnostic

AgentCore works with any agent framework: LangGraph, Strands Agents, CrewAI, LlamaIndex, Google ADK, OpenAI Agents SDK, or custom frameworks. You are not locked in. Start with Strands and migrate to LangGraph later without changing infrastructure.

### Model Agnostic

Use any foundation model: Claude, GPT, Gemini, Nova, Llama, Mistral, or self-hosted models. You can use different models for different purposes within the same agent.

### Consumption-Based Pricing

The Guide was always notable for being slightly cheaper than the *Encyclopedia Galactica*, and considerably more popular. AgentCore takes a similar approach to economics.

AgentCore charges for actual resource consumption, not allocated resources:
- **I/O wait is free**: When your agent waits for LLM responses, API calls, or database queries (often 30-70% of execution time), you pay nothing for CPU
- **Per-second billing**: No rounding up to minutes or hours
- **Peak memory billing**: Charged at highest level reached per second
- **No minimum fees**: Start with zero fixed costs

A typical customer support agent that spends 70% of its time waiting for LLM responses pays 70% less for CPU than it would on traditional compute.

### Enterprise Security

Security features designed for regulated industries:
- **MicroVM isolation**: Each session runs in a dedicated virtual machine
- **Memory sanitization**: VMs are terminated and memory cleared after sessions
- **IdP integration**: Native support for Okta, Entra ID, Cognito
- **Deterministic policy**: Cedar-based access control evaluated at the boundary
- **Audit trails**: CloudTrail logging for all operations
- **VPC support**: Network isolation for sensitive deployments

## Use Cases

### Customer Support Agent

**Problem**: Support bots forget context between sessions. Customers repeat themselves. Agents cannot access CRM data.

**AgentCore solution**:
- **Runtime**: Hosts the agent with per-session isolation
- **Memory**: Stores conversation history and customer preferences
- **Gateway**: Connects to Salesforce, Zendesk, or internal ticketing
- **Identity**: Integrates with corporate SSO for authentication
- **Policy**: Enforces rules like "cannot issue refunds over $500"

**Result**: 24/7 support with consistent quality, personalized interactions, and secure access to customer data.

### Internal Developer Platform

**Problem**: Multiple teams building AI agents with inconsistent security and duplicated infrastructure work.

**AgentCore solution**: Centralized Runtime for all agents, Gateway with approved tools, shared Memory stores, per-team Policy controls, and Evaluations for quality monitoring.

**Result**: Faster agent development, consistent security, reduced costs.

### Data Analysis Agent

**Problem**: Business users need insights from complex data but lack technical skills.

**AgentCore solution**: Runtime hosts the agent, Code Interpreter runs pandas/matplotlib analysis, Gateway connects to data warehouse APIs, Memory stores patterns.

**Result**: Natural language queries for complex analysis, automated reports, secure execution.

### Web Research Agent

**Problem**: Market research requires gathering and synthesizing information from many websites.

**AgentCore solution**: Runtime hosts the agent, Browser navigates and extracts data, Code Interpreter structures findings, Memory tracks research over time.

**Result**: Automated web research at scale with isolated, secure browsing.

## When to Use AgentCore (and When Not To)

### Choose AgentCore when:

- **You need production-grade security**: MicroVM isolation, IdP integration, and audit trails matter
- **You want to avoid infrastructure overhead**: Focus on agent capabilities, not operations
- **Your agents need long-running sessions**: Up to 8 hours vs typical 15-minute limits
- **You work with multiple frameworks or models**: Flexibility matters more than tight integration
- **Cost optimization is important**: Consumption pricing with free I/O wait
- **You need enterprise integrations**: 1-click connectors for Salesforce, Slack, Jira, etc.

### Consider alternatives when:

- **You need maximum control**: Self-managed infrastructure gives complete control
- **Simple use cases**: Fully managed Amazon Bedrock Agents may be simpler for straightforward scenarios
- **Existing infrastructure investments**: You have container orchestration and want to leverage it
- **Unique requirements**: Specialized needs not addressed by AgentCore services

## Getting Started

### Prerequisites

1. AWS account with AgentCore access
2. Python 3.10+ installed
3. AWS CLI configured (`aws configure`)
4. Model access enabled in Amazon Bedrock console

### Quickstart

```bash
# Install packages
pip install bedrock-agentcore strands-agents

# Create your agent
agentcore create my-first-agent

# Test locally
agentcore dev
agentcore invoke --dev "Hello, agent!"

# Deploy to AWS
agentcore launch
agentcore invoke '{"prompt": "Hello from production!"}'
```

### Simple Agent Code

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent

app = BedrockAgentCoreApp()
agent = Agent(system_prompt="You are a helpful assistant.")

@app.entrypoint
def invoke(payload, context):
    result = agent(payload.get("prompt", "Hello!"))
    return {"result": result.message}

if __name__ == "__main__":
    app.run()
```

## Pricing Overview

### Service Pricing Summary

| Service | Model | Key Prices |
|---------|-------|------------|
| Runtime | Consumption | $0.0895/vCPU-hour, $0.00945/GB-hour |
| Code Interpreter | Consumption | Same as Runtime |
| Browser | Consumption | Same as Runtime |
| Gateway | Per request | $0.005/1K invocations |
| Memory | Per operation | $0.25/1K short-term events |
| Identity | Free via Runtime | $0.01/1K standalone requests |
| Policy | Preview | Currently free |
| Evaluations | Preview | Currently free |

### Cost Example: Customer Support Agent

For a support agent handling 500,000 monthly conversations:
- 90-second average session
- 70% I/O wait time
- 2GB peak memory
- 3 tool calls per conversation

**Estimated monthly cost**: ~$800 (vs ~$3,200 with traditional compute)

### Free Tier

New AWS customers receive **$200 in Free Tier credits** for AgentCore services.

## Regional Availability

AgentCore core services (Runtime, Memory, Gateway, Identity) are available in 14 regions:
- **US**: us-east-1 (N. Virginia), us-east-2 (Ohio), us-west-2 (Oregon)
- **Europe**: eu-central-1 (Frankfurt), eu-west-1 (Ireland), eu-west-2 (London), eu-west-3 (Paris), eu-north-1 (Stockholm)
- **Asia Pacific**: ap-south-1 (Mumbai), ap-southeast-1 (Singapore), ap-southeast-2 (Sydney), ap-northeast-1 (Tokyo), ap-northeast-2 (Seoul)
- **Canada**: ca-central-1 (Canada)

Memory is also available in sa-east-1 (Sao Paulo). Observability and Policy are available in a subset of 9 regions. Evaluations is currently available in 4 regions.

## Key Takeaways

1. **AgentCore is infrastructure, not a framework**: Works with your choice of framework and model
2. **Modular architecture**: Use only the services you need
3. **Enterprise security**: MicroVM isolation, IdP integration, deterministic policy
4. **Consumption pricing**: Pay for actual usage, I/O wait is free
5. **Production-ready**: Built for scale and compliance from day one

The *Hitchhiker's Guide* succeeded because it told a confused and frightened galaxy exactly what it needed to know in terms it could understand -- and stamped **DON'T PANIC** on the cover. AgentCore does the same for teams building production AI agents: it eliminates the infrastructure overhead so you can focus on what your agents actually do. The galaxy of production AI is vast and complicated, but with the right Guide, it is also navigable.

---

**Documentation**: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/

**Samples**: https://github.com/awslabs/amazon-bedrock-agentcore-samples/

**Code Example**: `articles/examples/overview/` | [View complete example on GitHub](https://github.com/apresai/agentcore/tree/main/articles/examples/overview/)
