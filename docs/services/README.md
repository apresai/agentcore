# AgentCore Services Reference

AgentCore provides nine modular services that work independently or together.

## Service Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                           CORE SERVICES                             │
├─────────────────┬─────────────────┬─────────────────┬───────────────┤
│     Runtime     │     Memory      │     Gateway     │   Identity    │
│                 │                 │                 │               │
│ Serverless      │ Context         │ API to MCP      │ Auth &        │
│ hosting with    │ management for  │ tools with      │ credential    │
│ microVM         │ stateful        │ 1-click         │ management    │
│ isolation       │ conversations   │ integrations    │               │
└─────────────────┴─────────────────┴─────────────────┴───────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          BUILT-IN TOOLS                             │
├───────────────────────────────────┬─────────────────────────────────┤
│        Code Interpreter           │            Browser              │
│                                   │                                 │
│ Secure Python, JavaScript, and    │ Isolated web automation with    │
│ TypeScript execution with up to   │ live view, session recording,   │
│ 5GB file support                  │ and Playwright compatibility    │
└───────────────────────────────────┴─────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                           OPERATIONS                                │
├───────────────────────────────────┬─────────────────────────────────┤
│         Observability             │          Evaluations            │
│                                   │                                 │
│ OTEL-compatible tracing with      │ LLM-as-a-Judge quality          │
│ CloudWatch dashboards and         │ assessment with custom          │
│ step-by-step visualization        │ evaluators (Preview)            │
└───────────────────────────────────┴─────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          GOVERNANCE                                 │
├─────────────────────────────────────────────────────────────────────┤
│                            Policy                                   │
│                                                                     │
│ Cedar-based deterministic access control with natural language      │
│ policy authoring (Preview)                                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

| Service | Purpose | Key Feature | Status |
|---------|---------|-------------|--------|
| [Runtime](runtime.md) | Host agents | MicroVM isolation | GA |
| [Memory](memory.md) | Store context | Short + long-term | GA |
| [Gateway](gateway.md) | Connect tools | MCP conversion | GA |
| [Identity](identity.md) | Manage auth | IdP integration | GA |
| [Code Interpreter](code-interpreter.md) | Run code | 5GB file support | GA |
| [Browser](browser.md) | Automate web | Session recording | GA |
| [Observability](observability.md) | Monitor agents | OTEL traces | GA |
| [Evaluations](evaluations.md) | Assess quality | LLM-as-Judge | Preview |
| [Policy](policy.md) | Control access | Cedar rules | Preview |

---

## Service Details

### Runtime

**Serverless hosting with microVM isolation**

Every user session runs in a dedicated microVM with isolated CPU, memory, and filesystem. After session completion, the microVM is terminated and memory is sanitized.

| Feature | Specification |
|---------|---------------|
| Session duration | Up to 8 hours |
| Payload size | Up to 100MB |
| Memory billing | 128MB minimum |
| Streaming | HTTP + WebSocket |
| Protocols | MCP, A2A |

**Pricing**: CPU consumption + peak memory, per second. **I/O wait is free.**

[Learn more →](runtime.md)

---

### Memory

**Short-term and long-term context management**

| Memory Type | Scope | Persistence | Use Case |
|-------------|-------|-------------|----------|
| Short-term | Single session | Session duration | Multi-turn conversations |
| Long-term | Cross-session | Permanent | User preferences, learned facts |

**Key capabilities**:
- Shared memory stores across agents
- Automatic insight extraction
- Framework integration (Strands, LangGraph, LlamaIndex)

[Learn more →](memory.md)

---

### Gateway

**Convert APIs and Lambda functions to MCP-compatible tools**

**Tool sources**:
- OpenAPI specifications
- Lambda functions
- Existing MCP servers
- Smithy models

**1-click integrations**:
- Salesforce, Slack, Jira, Asana, Zendesk, Zoom, GitHub

**Features**:
- Semantic tool discovery
- OAuth flow management
- Protocol translation

[Learn more →](gateway.md)

---

### Identity

**Secure authentication and credential management**

**Supported IdPs**:
- Amazon Cognito
- Okta
- Microsoft Entra ID
- Auth0
- Any OIDC-compliant provider

**Flows**:
- Inbound: JWT authorization for users calling agents
- Outbound: Credential vault for agents calling tools

[Learn more →](identity.md)

---

### Code Interpreter

**Secure sandbox for code execution**

| Feature | Specification |
|---------|---------------|
| Languages | Python, JavaScript, TypeScript |
| Inline upload | Up to 100MB |
| S3 upload | Up to 5GB |
| Default timeout | 15 minutes |
| Max timeout | 8 hours |

**Use cases**: Data analysis, calculations, file processing, code generation

[Learn more →](code-interpreter.md)

---

### Browser

**Isolated web automation environment**

| Feature | Specification |
|---------|---------------|
| Session duration | Up to 8 hours |
| Default timeout | 15 minutes |
| Streaming | WebSocket |
| Frameworks | Playwright, BrowserUse |

**Capabilities**:
- Navigation, form filling, screenshots
- Live view monitoring
- Session recording (DOM, actions, network)
- Reduced CAPTCHA with AWS managed browser

[Learn more →](browser.md)

---

### Observability

**OTEL-compatible tracing and monitoring**

**Built-in metrics**:
- Session count, latency, duration, error rates
- Tool call counts, response times
- Memory operation counts

**Features**:
- Step-by-step visualization
- CloudWatch dashboards
- Rich metadata tagging
- Custom spans and traces

[Learn more →](observability.md)

---

### Evaluations (Preview)

**Automated quality assessment using LLM-as-a-Judge**

| Evaluation Type | Description |
|----------------|-------------|
| Online | Real-time scoring of production responses |
| On-demand | Batch evaluation of historical data |
| Built-in | Pre-configured evaluators |
| Custom | User-defined criteria |

**No charges during Preview.**

[Learn more →](evaluations.md)

---

### Policy (Preview)

**Cedar-based deterministic access control**

**Capabilities**:
- Natural language policy authoring
- Fine-grained rules based on identity and parameters
- Gateway integration for request interception
- CloudWatch logging for audit

**No charges during Preview.**

[Learn more →](policy.md)

---

## Service Combinations

Common patterns for combining services:

### Conversational Agent
```
Runtime + Memory + Gateway
```
- Runtime hosts the agent
- Memory maintains conversation context
- Gateway provides tools

### Secure Enterprise Agent
```
Runtime + Identity + Gateway + Policy
```
- Runtime hosts the agent
- Identity manages authentication
- Gateway provides tools
- Policy enforces access control

### Data Analysis Agent
```
Runtime + Code Interpreter + Memory
```
- Runtime hosts the agent
- Code Interpreter executes analysis
- Memory stores analysis patterns

### Web Research Agent
```
Runtime + Browser + Code Interpreter + Memory
```
- Runtime hosts long-running sessions
- Browser navigates websites
- Code Interpreter processes data
- Memory tracks research over time

---

## Regional Availability

| Service | us-east-1 | us-west-2 | ap-southeast-2 | eu-central-1 |
|---------|:---------:|:---------:|:--------------:|:------------:|
| Runtime | ✅ | ✅ | ✅ | ✅ |
| Memory | ✅ | ✅ | ✅ | ✅ |
| Gateway | ✅ | ✅ | ✅ | ✅ |
| Identity | ✅ | ✅ | ✅ | ✅ |
| Code Interpreter | ✅ | ✅ | ✅ | ✅ |
| Browser | ✅ | ✅ | ✅ | ✅ |
| Observability | ✅ | ✅ | ✅ | ✅ |
| Evaluations | ✅ | ✅ | ✅ | ✅ |
| Policy | ✅ | ✅ | ✅ | ✅ |
