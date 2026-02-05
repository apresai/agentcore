# AgentCore Pricing

A comprehensive guide to understanding and optimizing costs for Amazon Bedrock AgentCore services.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Pricing Philosophy](#pricing-philosophy)
3. [Free Tier Details](#free-tier-details)
4. [Service-by-Service Pricing](#service-by-service-pricing)
   - [Runtime](#runtime)
   - [Browser](#browser)
   - [Code Interpreter](#code-interpreter)
   - [Gateway](#gateway)
   - [Identity](#identity)
   - [Memory](#memory)
   - [Policy (Preview)](#policy-preview)
   - [Evaluations (Preview)](#evaluations-preview)
   - [Observability](#observability)
5. [Cost Scenarios](#cost-scenarios)
6. [Cost Calculator](#cost-calculator)
7. [Cost Optimization Strategies](#cost-optimization-strategies)
8. [Billing and Monitoring](#billing-and-monitoring)
9. [Cost Comparison](#cost-comparison)
10. [FAQ](#faq)
11. [Related Resources](#related-resources)

---

## Quick Reference

### Pricing Summary Table

| Service | Pricing Model | Key Metrics | Price |
|---------|---------------|-------------|-------|
| **Runtime** | Active Consumption | CPU | $0.0895/vCPU-hour |
| | | Memory | $0.00945/GB-hour |
| **Browser** | Active Consumption | CPU | $0.0895/vCPU-hour |
| | | Memory | $0.00945/GB-hour |
| **Code Interpreter** | Active Consumption | CPU | $0.0895/vCPU-hour |
| | | Memory | $0.00945/GB-hour |
| **Gateway** | Per Request | API Invocations | $0.005/1,000 invocations |
| | | Search API | $0.025/1,000 invocations |
| | | Tool Indexing | $0.02/100 tools indexed/month |
| **Identity** | Per Request | Token/API Key Requests | $0.010/1,000 requests |
| | | Via Runtime/Gateway | **FREE** |
| **Memory** | Per Operation | Short-term Events | $0.25/1,000 events |
| | | Long-term Storage (built-in) | $0.75/1,000 records/month |
| | | Long-term Storage (self-managed) | $0.25/1,000 records/month |
| | | Long-term Retrieval | $0.50/1,000 retrievals |
| **Policy** | Per Request | Authorization Requests | $0.000025/request |
| | | NL Policy Authoring | $0.13/1,000 input tokens |
| **Evaluations** | Per Evaluation | Built-in (input tokens) | $0.0024/1,000 tokens |
| | | Built-in (output tokens) | $0.012/1,000 tokens |
| | | Custom Evaluators | $1.50/1,000 evaluations |
| **Observability** | CloudWatch Pricing | Span Ingestion | $0.35/GB |
| | | Event Logging | $0.50/GB |

### Key Pricing Facts

- **No upfront commitments** - Pay only for what you use
- **No minimum fees** - Start with zero cost
- **$200 Free Tier** - For new AWS customers
- **I/O wait is FREE** - Only pay for active CPU consumption
- **1-second billing granularity** - No rounding up to minutes
- **128MB minimum memory** - Minimum billable memory per session
- **Services bill independently** - Use only what you need

---

## Pricing Philosophy

### Consumption-Based Model

AgentCore fundamentally changes how you pay for agent infrastructure. Unlike traditional compute services that charge for pre-allocated resources, AgentCore charges only for **active resource consumption**.

#### The Problem with Traditional Pricing

Traditional compute pricing (EC2, ECS, Lambda with provisioned concurrency) requires you to:

1. **Estimate capacity upfront** - Guess how much CPU and memory you need
2. **Pay for idle time** - Resources cost money whether used or not
3. **Over-provision for safety** - Pay extra to handle peak loads
4. **Accept waste** - 30-70% of provisioned capacity often sits idle

#### AgentCore's Solution

AgentCore's consumption-based model:

1. **No capacity planning** - Resources scale automatically
2. **I/O wait is free** - When your agent waits for LLM responses, API calls, or database queries, you pay nothing for CPU
3. **Pay for actual usage** - Charged per second based on real consumption
4. **Peak memory billing** - Memory charged at peak level per second, not pre-allocated maximum

### Why I/O Wait Matters

Agentic workloads have a unique characteristic: they spend **30-70% of their time waiting** for external responses:

- Waiting for LLM inference (Claude, GPT, etc.)
- Waiting for API responses
- Waiting for database queries
- Waiting for tool execution results

With traditional pricing, you pay for CPU during all this waiting time. With AgentCore:

```
Traditional: 60 seconds session x $0.0895/vCPU-hour = $0.00149/session
AgentCore:   18 seconds active x $0.0895/vCPU-hour = $0.00045/session
                                                     ─────────────────
                                          Savings:   70% lower cost
```

### Modular Service Architecture

Each AgentCore service is:

- **Independently priced** - Pay only for services you use
- **Independently scalable** - Each service scales based on your needs
- **Composable** - Mix and match services as needed
- **No bundle requirements** - Use Runtime without Gateway, or Gateway without Runtime

This modularity means you can start with just the services you need and add more as your agent capabilities grow.

---

## Free Tier Details

### What's Included

New AWS customers receive **$200 in Free Tier credits** to explore AgentCore services at no cost.

#### Eligibility

- Available to **new AWS customers** only
- Credits apply across all AgentCore services
- No credit card required to start exploring (with AWS Free Tier account)
- Credits do not expire based on time (subject to AWS Free Tier terms)

#### Credit Application

Free Tier credits apply to:

| Service | Credit Application |
|---------|-------------------|
| Runtime | CPU and memory consumption |
| Browser | CPU and memory consumption |
| Code Interpreter | CPU and memory consumption |
| Gateway | API invocations, search, indexing |
| Identity | Token and API key requests |
| Memory | Events, storage, and retrievals |
| Policy | Authorization requests and policy authoring |
| Evaluations | Built-in and custom evaluations |
| Observability | CloudWatch charges |

#### What $200 Gets You

Estimated usage with $200 in credits:

| Scenario | Estimated Sessions/Operations |
|----------|------------------------------|
| Simple chatbot (Runtime only) | ~275,000 sessions |
| Browser automation | ~16,000 sessions |
| Code execution tasks | ~55,000 executions |
| Gateway API calls | ~40,000,000 invocations |
| Memory operations | ~400,000 short-term events |

### Tracking Free Tier Usage

Monitor your Free Tier consumption through:

1. **AWS Cost Explorer** - Filter by AgentCore services
2. **AWS Budgets** - Set alerts for Free Tier depletion
3. **CloudWatch** - Track service-specific metrics
4. **Billing Console** - View current month usage

#### Setting Up Free Tier Alerts

```bash
# Create a budget alert for Free Tier spending
aws budgets create-budget \
  --account-id YOUR_ACCOUNT_ID \
  --budget '{
    "BudgetName": "AgentCore-FreeTier-Alert",
    "BudgetLimit": {
      "Amount": "150",
      "Unit": "USD"
    },
    "BudgetType": "COST",
    "CostFilters": {
      "Service": ["Amazon Bedrock AgentCore"]
    },
    "TimeUnit": "MONTHLY"
  }' \
  --notifications-with-subscribers '[{
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 75
    },
    "Subscribers": [{
      "SubscriptionType": "EMAIL",
      "Address": "your-email@example.com"
    }]
  }]'
```

### Preview Services (Currently Free)

The following services are in preview and **currently have no charges**:

- **Policy** - Authorization requests and policy authoring
- **Evaluations** - Built-in and custom evaluations

Take advantage of these services during the preview period to:
- Develop and test policy enforcement patterns
- Build evaluation pipelines for agent quality
- Familiarize with features before GA pricing begins

---

## Service-by-Service Pricing

### Runtime

AgentCore Runtime provides secure, serverless infrastructure for deploying agents with microVM isolation.

#### Pricing Metrics

| Metric | Price | Minimum |
|--------|-------|---------|
| CPU | $0.0895/vCPU-hour | 1-second billing |
| Memory | $0.00945/GB-hour | 128MB minimum |

#### How Billing Works

**CPU Billing:**
- Charged based on **actual CPU consumption** per second
- If your agent consumes no CPU (I/O wait), there are no CPU charges
- Billing includes system overhead in addition to application usage

**Memory Billing:**
- Charged for **peak memory consumed** up to that second
- Memory is tracked per-second and charged at the highest level reached
- 128MB minimum applies regardless of actual usage

**Session Lifecycle:**
Billing covers the entire session from microVM boot through shutdown:
1. MicroVM boot and initialization
2. Active processing periods
3. Idle/I/O wait periods (CPU free if no background processes)
4. Session termination

#### Storage Costs

**Container Deployment:**
- Container images stored in ECR
- Billed separately at ECR rates
- See [ECR Pricing](https://aws.amazon.com/ecr/pricing/)

**Direct Code Deployment:**
- Code artifacts stored in S3
- Billed at S3 Standard rates (starting February 27, 2026)
- Example: 100MB agent = ~$0.0023/month

**Network Transfer:**
- Standard EC2 data transfer rates apply
- See [EC2 Data Transfer Pricing](https://aws.amazon.com/ec2/pricing/on-demand/)

#### Detailed Example: Customer Support Agent

**Scenario:**
- 10 million monthly user requests
- 60-second average session duration
- 70% I/O wait time (waiting for LLM responses and API calls)
- 1 vCPU during active processing
- Memory: 1GB at init, 2GB during RAG, 2.5GB peak during tool calls

**Calculation:**

```
Active CPU time: 60 seconds × 30% active = 18 seconds

CPU cost per session:
  18 seconds × 1 vCPU × ($0.0895 / 3600 seconds)
  = 18 × 1 × $0.0000249
  = $0.0004475

Memory cost per session:
  Phase 1: 10 seconds × 1GB × ($0.00945 / 3600) = $0.000026
  Phase 2: 20 seconds × 2GB × ($0.00945 / 3600) = $0.000053
  Phase 3: 30 seconds × 2.5GB × ($0.00945 / 3600) = $0.000197
  Total memory: $0.000276

Total per session: $0.0004475 + $0.000276 = $0.0007235

Monthly cost: 10,000,000 × $0.0007235 = $7,235
```

#### Cost Comparison: Runtime vs Traditional

| Approach | CPU Cost | Memory Cost | Total |
|----------|----------|-------------|-------|
| AgentCore Runtime | $4,475 | $2,760 | $7,235 |
| Pre-allocated (full 60s) | $14,917 | $3,938 | $18,855 |
| **Savings** | 70% | 30% | **62%** |

---

### Browser

AgentCore Browser provides cloud-based browser runtime for agents to interact with websites.

#### Pricing Metrics

| Metric | Price | Minimum |
|--------|-------|---------|
| CPU | $0.0895/vCPU-hour | 1-second billing |
| Memory | $0.00945/GB-hour | 128MB minimum |

#### How Billing Works

Browser sessions follow the same consumption-based model as Runtime:

- **CPU** - Charged only during active browser operations
- **Memory** - Charged at peak level per second
- **I/O wait** - Free when waiting for page loads, network requests, or LLM decisions

#### What's Included

- Session-isolated sandbox compute
- Headless browser instances
- Live View for debugging
- Session Replay for auditing
- Network isolation and security

#### Browser-Specific Considerations

Browser workloads often have high I/O wait percentages:
- Page load times: 2-10 seconds of network I/O
- Rendering wait: 0.5-2 seconds per interaction
- Screenshot processing: Minimal CPU, mostly I/O

Typical I/O wait: **70-85%** of session time

#### Detailed Example: Travel Booking Agent

**Scenario:**
- 100,000 monthly requests
- 10-minute sessions (600 seconds)
- 80% I/O wait time
- 2 vCPU during active processing
- 4GB memory continuously

**Calculation:**

```
Active CPU time: 600 seconds × 20% active = 120 seconds

CPU cost per session:
  120 seconds × 2 vCPU × ($0.0895 / 3600)
  = 120 × 2 × $0.0000249
  = $0.005967

Memory cost per session:
  600 seconds × 4GB × ($0.00945 / 3600)
  = 600 × 4 × $0.00000263
  = $0.0063

Total per session: $0.005967 + $0.0063 = $0.012267

Monthly cost: 100,000 × $0.012267 = $1,226.67
```

---

### Code Interpreter

AgentCore Code Interpreter enables secure code execution in sandbox environments.

#### Pricing Metrics

| Metric | Price | Minimum |
|--------|-------|---------|
| CPU | $0.0895/vCPU-hour | 1-second billing |
| Memory | $0.00945/GB-hour | 128MB minimum |

#### Supported Languages

- Python
- JavaScript
- TypeScript

#### What's Included

- Isolated sandbox execution
- Pre-built runtimes with common packages
- File handling up to 5GB
- Enterprise security compliance
- Session persistence within execution

#### Detailed Example: Data Analysis Agent

**Scenario:**
- 10,000 monthly requests
- 3 code executions per request (30,000 total)
- 2-minute execution time per code run
- 60% I/O wait time
- 2 vCPU during active processing
- 4GB memory continuously

**Calculation:**

```
Active CPU time: 120 seconds × 40% active = 48 seconds

CPU cost per execution:
  48 seconds × 2 vCPU × ($0.0895 / 3600)
  = 48 × 2 × $0.0000249
  = $0.002387

Memory cost per execution:
  120 seconds × 4GB × ($0.00945 / 3600)
  = 120 × 4 × $0.00000263
  = $0.00126

Total per execution: $0.002387 + $0.00126 = $0.003647

Monthly cost: 30,000 × $0.003647 = $109.40
```

---

### Gateway

AgentCore Gateway transforms APIs and Lambda functions into agent-compatible MCP tools.

#### Pricing Metrics

| Operation | Price |
|-----------|-------|
| API Invocations (ListTools, InvokeTool, Ping) | $0.005/1,000 invocations |
| Search API | $0.025/1,000 invocations |
| Tool Indexing | $0.02/100 tools indexed/month |

#### What's Billed

**API Invocations:**
- `ListTools` - Enumerate available tools
- `InvokeTool` - Execute a tool
- `Ping` - Health check operations

**Search API:**
- Semantic search across indexed tools
- Tool discovery based on context

**Tool Indexing:**
- Monthly charge per 100 tools indexed
- Enables semantic search functionality

#### What's Included (No Extra Charge)

- MCP server creation from APIs
- Lambda function wrapping
- OpenAPI specification parsing
- Tool metadata management

#### Detailed Example: HR Assistant

**Scenario:**
- 200 internal tools indexed
- 50 million monthly interactions
- Each interaction: 1 Search API + 4 InvokeTool calls

**Calculation:**

```
Tool Indexing:
  200 tools × ($0.02 / 100 tools) = $0.04/month

Search API:
  50,000,000 × ($0.025 / 1,000) = $1,250

InvokeTool API:
  200,000,000 × ($0.005 / 1,000) = $1,000

Monthly cost: $0.04 + $1,250 + $1,000 = $2,250.04
```

#### Cost Per Interaction Breakdown

```
Per interaction cost:
  Search: 1 × $0.000025 = $0.000025
  InvokeTool: 4 × $0.000005 = $0.000020
  Total: $0.000045 per interaction

At 50M interactions: 50,000,000 × $0.000045 = $2,250
```

---

### Identity

AgentCore Identity manages authentication and access for agents accessing external services.

#### Pricing Metrics

| Scenario | Price |
|----------|-------|
| Via AgentCore Runtime | **FREE** |
| Via AgentCore Gateway | **FREE** |
| Standalone usage | $0.010/1,000 token requests |

#### What's Included

- OAuth token management
- API key management
- Integration with identity providers (Okta, Entra ID, Cognito)
- Delegated access for user actions
- Pre-authorized agent actions

#### When You Pay

**FREE scenarios:**
- Agent deployed on AgentCore Runtime uses Identity
- Agent accessing tools through AgentCore Gateway

**Charged scenarios:**
- Direct Identity API calls outside Runtime/Gateway
- Custom integrations using Identity APIs directly

#### Detailed Example: Support Agent with Tool Access

**Scenario:**
- 10,000 monthly active users
- 5 sessions per user
- 3 tools accessed per session (Slack, Zoom, GitHub)
- Using Identity standalone (not through Runtime/Gateway)

**Calculation:**

```
Total token requests:
  10,000 users × 5 sessions × 3 tools = 150,000 requests

Monthly cost:
  150,000 × ($0.010 / 1,000) = $1.50
```

**Note:** If this same agent runs on AgentCore Runtime, Identity costs = $0.

---

### Memory

AgentCore Memory provides context management for agents with short-term and long-term storage.

#### Pricing Metrics

| Type | Operation | Price |
|------|-----------|-------|
| Short-term | Event creation | $0.25/1,000 events |
| Long-term | Storage (built-in strategies) | $0.75/1,000 records/month |
| Long-term | Storage (self-managed strategies) | $0.25/1,000 records/month |
| Long-term | Retrieval | $0.50/1,000 retrievals |

#### Memory Strategies

**Built-in Memory Strategies ($0.75/1,000 records):**
- Automatic processing and extraction
- Managed by AgentCore
- No additional model costs

**Built-in with Override / Self-managed ($0.25/1,000 records):**
- Configurable extraction logic
- Uses your choice of model and prompt
- May incur additional model usage costs in your account

#### Short-term vs Long-term

**Short-term Memory:**
- In-session context
- Raw events (messages, actions, tool calls)
- Priced per event creation
- Automatically expires after session

**Long-term Memory:**
- Cross-session persistence
- Extracted knowledge and preferences
- Priced per storage and retrieval
- Persists until explicitly deleted

#### Detailed Example: Coding Assistant

**Scenario:**
- 100,000 monthly short-term events
- 10,000 stored long-term records
- 20,000 monthly retrieval calls
- Using built-in memory strategies

**Calculation:**

```
Short-term memory:
  100,000 × ($0.25 / 1,000) = $25.00

Long-term storage:
  10,000 × ($0.75 / 1,000) = $7.50

Long-term retrieval:
  20,000 × ($0.50 / 1,000) = $10.00

Monthly cost: $25.00 + $7.50 + $10.00 = $42.50
```

#### Self-managed Alternative

Same scenario with self-managed strategies:

```
Short-term memory: $25.00 (same)
Long-term storage: 10,000 × ($0.25 / 1,000) = $2.50
Long-term retrieval: $10.00 (same)

AgentCore cost: $37.50
+ Additional model costs for extraction (varies by model)
```

---

### Policy (Preview)

Policy provides Cedar-based deterministic access control for agent actions.

#### Pricing Metrics

| Operation | Price |
|-----------|-------|
| Authorization request | $0.000025/request |
| Natural language policy authoring | $0.13/1,000 input tokens |

#### Current Status

**Preview Period:** Currently offered at no charge during preview.

Post-preview pricing will follow the metrics above.

#### What's Included

- Cedar policy enforcement
- Real-time authorization checks
- Integration with AgentCore Gateway
- Policy versioning and management

#### Natural Language Policy Authoring

Create Cedar policies using plain language:

```
Input: "Allow agents to read customer data but not modify it"
Output: Cedar policy statements
Cost: Based on input tokens processed
```

#### Detailed Example: Procurement Agent

**Scenario:**
- 100,000 monthly sessions
- 5 tool calls per session
- 1 authorization request per tool call
- 20,000 input tokens for policy authoring (one-time)

**Calculation (Post-Preview):**

```
Authorization requests:
  100,000 sessions × 5 tool calls × 1 auth/call = 500,000 requests
  500,000 × $0.000025 = $12.50

Policy authoring (one-time):
  20,000 tokens × ($0.13 / 1,000) = $2.60

Monthly recurring: $12.50
One-time setup: $2.60
```

---

### Evaluations (Preview)

AgentCore Evaluations provides quality assessment using LLM-as-a-Judge methodology.

#### Pricing Metrics

| Type | Metric | Price |
|------|--------|-------|
| Built-in evaluators | Input tokens | $0.0024/1,000 tokens |
| Built-in evaluators | Output tokens | $0.012/1,000 tokens |
| Custom evaluators | Per evaluation | $1.50/1,000 evaluations |

#### Current Status

**Preview Period:** Currently offered at no charge during preview.

Post-preview pricing will follow the metrics above.

#### Built-in Evaluators

13 built-in evaluators covering common quality dimensions:
- Correctness
- Helpfulness
- Goal success rate
- Safety
- Relevance
- And more...

**Model costs are included** in built-in evaluator pricing.

#### Custom Evaluators

- Define business-specific quality metrics
- Use your own LLM infrastructure
- Per-evaluation charge plus separate model inference costs

#### Detailed Example: E-commerce Quality Monitoring

**Scenario:**
- 5,000 development test interactions
- 10,000 production interactions (2% sampling)
- 3 built-in evaluators per interaction
- 1 custom evaluator per interaction
- 15,000 input tokens per evaluation
- 300 output tokens per evaluation

**Calculation (Post-Preview):**

```
Total interactions: 15,000
Built-in evaluations: 15,000 × 3 = 45,000

Built-in input tokens:
  45,000 × 15,000 = 675,000,000 tokens
  675,000,000 × ($0.0024 / 1,000) = $1,620

Built-in output tokens:
  45,000 × 300 = 13,500,000 tokens
  13,500,000 × ($0.012 / 1,000) = $162

Custom evaluations:
  15,000 × ($1.50 / 1,000) = $22.50

Monthly cost: $1,620 + $162 + $22.50 = $1,804.50
+ Additional model costs for custom evaluators
```

---

### Observability

AgentCore Observability provides tracing, debugging, and monitoring through Amazon CloudWatch.

#### Pricing Model

Observability costs follow Amazon CloudWatch pricing:

| Operation | Price |
|-----------|-------|
| Span ingestion | $0.35/GB |
| Event logging | $0.50/GB |
| Storage | CloudWatch rates |
| Queries | CloudWatch rates |
| PII masking | CloudWatch rates |

#### What's Tracked

- Agent workflow traces
- Tool call spans
- Model invocation events
- Performance metrics
- Error logs

#### Detailed Example: Financial Advisory Platform

**Scenario:**
- Multiple specialized agents
- 10 TB monthly observability data
- 30% event logs (~6 TB at 2KB per span)

**Calculation:**

```
Span ingestion:
  10 TB × 1,000 GB/TB × $0.35/GB = $3,500

Event logging:
  6 TB × 1,000 GB/TB × $0.50/GB = $3,000

Monthly cost: $3,500 + $3,000 = $6,500
+ Additional CloudWatch costs for storage and queries
```

---

## Cost Scenarios

### Scenario 1: Simple Chatbot

**Use Case:** Basic Q&A chatbot with no persistent memory or tools.

**Configuration:**
- Runtime only
- 100,000 monthly conversations
- 30-second average session
- 80% I/O wait (waiting for LLM)
- 0.5 vCPU active
- 512MB memory

**Monthly Cost Estimate:**

| Component | Calculation | Cost |
|-----------|-------------|------|
| CPU | 100K × 6s × 0.5 × $0.0000249 | $7.47 |
| Memory | 100K × 30s × 0.5GB × $0.00000263 | $3.95 |
| **Total** | | **$11.42** |

**Cost per conversation:** $0.000114

---

### Scenario 2: Customer Support Agent

**Use Case:** Full-featured support agent with tools and memory.

**Configuration:**
- Runtime + Gateway + Memory
- 500,000 monthly conversations
- 90-second average session
- 70% I/O wait
- 1 vCPU active
- 2GB peak memory
- 3 tool calls per conversation
- Short-term memory for all conversations
- Long-term memory for 10% of users

**Monthly Cost Estimate:**

| Component | Calculation | Cost |
|-----------|-------------|------|
| **Runtime** | | |
| CPU | 500K × 27s × 1 × $0.0000249 | $336.15 |
| Memory | 500K × 90s × 2GB × $0.00000263 | $236.70 |
| **Gateway** | | |
| InvokeTool | 1.5M × $0.000005 | $7.50 |
| **Memory** | | |
| Short-term | 500K × $0.00025 | $125.00 |
| Long-term storage | 50K × $0.00075 | $37.50 |
| Long-term retrieval | 100K × $0.0005 | $50.00 |
| **Total** | | **$792.85** |

**Cost per conversation:** $0.00159

---

### Scenario 3: Data Analysis Agent

**Use Case:** Business analytics with code execution.

**Configuration:**
- Runtime + Code Interpreter + Gateway
- 50,000 monthly analysis requests
- 5-minute average session
- 3 code executions per request
- 50% I/O wait (more compute-heavy)
- 2 vCPU active
- 8GB peak memory

**Monthly Cost Estimate:**

| Component | Calculation | Cost |
|-----------|-------------|------|
| **Runtime** | | |
| CPU | 50K × 150s × 2 × $0.0000249 | $373.50 |
| Memory | 50K × 300s × 8GB × $0.00000263 | $315.60 |
| **Code Interpreter** | | |
| CPU | 150K × 60s × 2 × $0.0000249 | $447.00 |
| Memory | 150K × 120s × 4GB × $0.00000263 | $189.36 |
| **Gateway** | | |
| InvokeTool | 200K × $0.000005 | $1.00 |
| **Total** | | **$1,326.46** |

**Cost per analysis:** $0.0265

---

### Scenario 4: Multi-Agent System

**Use Case:** Orchestrator with specialized worker agents.

**Configuration:**
- 1 orchestrator + 4 worker agents
- 200,000 monthly requests
- Orchestrator: 2-minute sessions, 1 vCPU, 2GB
- Workers: 30-second sessions each, 0.5 vCPU, 1GB
- 60% I/O wait average
- Gateway for inter-agent communication
- Memory for context sharing

**Monthly Cost Estimate:**

| Component | Calculation | Cost |
|-----------|-------------|------|
| **Orchestrator Runtime** | | |
| CPU | 200K × 48s × 1 × $0.0000249 | $239.04 |
| Memory | 200K × 120s × 2GB × $0.00000263 | $126.24 |
| **Worker Runtimes (×4)** | | |
| CPU | 800K × 12s × 0.5 × $0.0000249 | $119.52 |
| Memory | 800K × 30s × 1GB × $0.00000263 | $63.12 |
| **Gateway** | | |
| InvokeTool | 1M × $0.000005 | $5.00 |
| **Memory** | | |
| Short-term | 200K × $0.00025 | $50.00 |
| Long-term storage | 20K × $0.00075 | $15.00 |
| Long-term retrieval | 40K × $0.0005 | $20.00 |
| **Total** | | **$637.92** |

**Cost per request:** $0.00319

---

### Scenario 5: Browser Automation Agent

**Use Case:** Web scraping and form automation.

**Configuration:**
- Runtime + Browser
- 25,000 monthly automation tasks
- 15-minute average session
- 85% I/O wait (page loads, rendering)
- 2 vCPU during active processing
- 6GB memory for browser

**Monthly Cost Estimate:**

| Component | Calculation | Cost |
|-----------|-------------|------|
| **Runtime** | | |
| CPU | 25K × 135s × 2 × $0.0000249 | $168.08 |
| Memory | 25K × 900s × 2GB × $0.00000263 | $118.35 |
| **Browser** | | |
| CPU | 25K × 135s × 2 × $0.0000249 | $168.08 |
| Memory | 25K × 900s × 6GB × $0.00000263 | $355.05 |
| **Total** | | **$809.56** |

**Cost per automation:** $0.0324

---

### Scenario 6: Enterprise Agent Platform

**Use Case:** Full platform with all services for enterprise deployment.

**Configuration:**
- All services enabled
- 1,000,000 monthly interactions
- Multiple agent types
- Full observability
- Quality evaluations (5% sampling)

**Monthly Cost Estimate:**

| Component | Cost |
|-----------|------|
| Runtime | $3,500 |
| Browser (subset of tasks) | $500 |
| Code Interpreter (subset) | $200 |
| Gateway | $1,000 |
| Identity (free via Runtime) | $0 |
| Memory | $500 |
| Policy | $50 |
| Evaluations | $1,500 |
| Observability | $2,000 |
| **Total** | **$9,250** |

**Cost per interaction:** $0.00925

---

## Cost Calculator

### Manual Calculation Steps

#### Step 1: Estimate Session Characteristics

For each agent type, determine:
- Average session duration (seconds)
- I/O wait percentage
- CPU usage during active processing (vCPU)
- Peak memory usage (GB)
- Monthly session volume

#### Step 2: Calculate Compute Costs

**CPU Cost Formula:**
```
CPU_cost = sessions × (duration × (1 - io_wait%)) × vCPU × ($0.0895 / 3600)
```

**Memory Cost Formula:**
```
Memory_cost = sessions × duration × peak_memory_GB × ($0.00945 / 3600)
```

#### Step 3: Calculate Service Costs

**Gateway:**
```
Gateway_cost = (invocations × $0.000005) + (searches × $0.000025) + (tools_indexed × $0.0002)
```

**Memory:**
```
Memory_cost = (short_term_events × $0.00025) +
              (long_term_records × storage_rate) +
              (retrievals × $0.0005)
```

**Identity:**
```
Identity_cost = 0  (if using Runtime/Gateway)
                OR
              = requests × $0.00001
```

#### Step 4: Add Ancillary Costs

- Network data transfer (EC2 rates)
- Storage (S3/ECR rates)
- Observability (CloudWatch rates)
- Evaluations (if enabled)

### Example Calculation Worksheet

```
Agent: Customer Support Bot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Session Parameters:
  Monthly sessions:     500,000
  Session duration:     90 seconds
  I/O wait:            70%
  Active CPU:          1 vCPU
  Peak memory:         2 GB

Compute Costs:
  Active time:         90s × 30% = 27s
  CPU:                 500,000 × 27 × 1 × $0.0000249 = $336.15
  Memory:              500,000 × 90 × 2 × $0.00000263 = $236.70
  Subtotal:            $572.85

Gateway:
  Tool calls:          3 per session = 1,500,000
  InvokeTool:          1,500,000 × $0.000005 = $7.50

Memory:
  Short-term events:   500,000 × $0.00025 = $125.00
  Long-term records:   50,000 × $0.00075 = $37.50
  Retrievals:          100,000 × $0.0005 = $50.00
  Subtotal:            $212.50

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL MONTHLY COST:    $792.85
COST PER SESSION:      $0.00159
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### AWS Pricing Calculator

Use the AWS Pricing Calculator for detailed estimates:
- [AWS Pricing Calculator](https://calculator.aws/)
- Select "Amazon Bedrock" services
- Configure AgentCore components

---

## Cost Optimization Strategies

### Strategy 1: Maximize I/O Wait Efficiency

**The Opportunity:**
AgentCore charges nothing for CPU during I/O wait. Design your agents to maximize this benefit.

**Implementation:**
- Use async patterns for LLM calls
- Batch API requests where possible
- Avoid CPU-intensive preprocessing
- Let the LLM do heavy lifting (it's already paid for separately)

**Example Optimization:**
```python
# Before: CPU-intensive local processing
def process_data(data):
    # Heavy local computation
    processed = expensive_local_transform(data)
    response = llm.invoke(processed)
    return response

# After: LLM-heavy processing
def process_data(data):
    # Minimal local work
    prompt = f"Transform and analyze: {data}"
    response = llm.invoke(prompt)  # I/O wait - free
    return response
```

**Savings:** Up to 70% reduction in CPU costs

---

### Strategy 2: Use Identity Through Runtime/Gateway

**The Opportunity:**
Identity is free when accessed through Runtime or Gateway.

**Implementation:**
- Deploy agents on AgentCore Runtime
- Access tools through AgentCore Gateway
- Avoid direct Identity API calls

**Cost Impact:**
- Without Runtime/Gateway: $0.01/1,000 requests
- With Runtime/Gateway: $0.00/1,000 requests

---

### Strategy 3: Optimize Memory Strategy Selection

**The Opportunity:**
Self-managed memory strategies cost 70% less than built-in.

**Trade-off Analysis:**

| Strategy | Storage Cost | Additional Costs | Best For |
|----------|--------------|------------------|----------|
| Built-in | $0.75/1,000 | None | Simplicity |
| Self-managed | $0.25/1,000 | Model inference | High volume |

**Break-even Analysis:**
```
Built-in: $0.75 per 1,000 records
Self-managed: $0.25 per 1,000 records + model costs

If model cost < $0.50 per 1,000 extractions:
  → Self-managed is cheaper

For high-volume scenarios:
  100,000 records/month
  Built-in: $75.00
  Self-managed: $25.00 + model costs (~$20 for Claude Haiku)
  Savings: ~$30/month
```

---

### Strategy 4: Right-Size Browser Sessions

**The Opportunity:**
Browser sessions consume significant memory. Optimize session lifecycle.

**Implementation:**
- Close browser sessions promptly after task completion
- Reuse sessions for related tasks
- Use appropriate memory allocation
- Implement session pooling for high-volume scenarios

**Configuration Tips:**
```python
# Optimize session duration
browser_config = {
    "timeout": 30000,  # 30s timeout per operation
    "max_session_duration": 300000,  # 5 minute max
    "memory_profile": "standard"  # Not "high" unless needed
}
```

---

### Strategy 5: Batch Gateway Operations

**The Opportunity:**
Gateway charges per operation. Batch when possible.

**Implementation:**
- Use `ListTools` once per session, cache results
- Batch multiple tool calls in single transactions
- Minimize ping operations

**Example:**
```python
# Before: Frequent ListTools calls
for task in tasks:
    tools = gateway.list_tools()  # $0.000005 each
    result = gateway.invoke_tool(tools[0], task)

# After: Cache tool list
tools = gateway.list_tools()  # Once
for task in tasks:
    result = gateway.invoke_tool(tools[0], task)
```

---

### Strategy 6: Sample Evaluations Wisely

**The Opportunity:**
Evaluations are expensive at scale. Use strategic sampling.

**Implementation:**
- Development: 100% evaluation coverage
- Production: 1-5% sampling based on risk

**Sampling Configuration:**
```yaml
evaluation_config:
  development:
    sample_rate: 1.0  # 100%
    evaluators:
      - correctness
      - helpfulness
      - safety

  production:
    sample_rate: 0.02  # 2%
    evaluators:
      - correctness  # Critical only
    conditional_sampling:
      - condition: "error_detected"
        sample_rate: 1.0
```

**Cost Impact:**
- 100% sampling at 1M interactions: ~$12,000/month
- 2% sampling at 1M interactions: ~$240/month

---

### Strategy 7: Optimize Observability Data

**The Opportunity:**
Observability costs scale with data volume. Be selective.

**Implementation:**
- Enable selective tracing (not all spans)
- Set appropriate log levels
- Use sampling for high-volume traces
- Archive old data to cheaper storage

**Configuration:**
```yaml
observability_config:
  tracing:
    sample_rate: 0.1  # 10% of traces
    always_trace:
      - error_conditions
      - slow_operations

  logging:
    level: WARN  # Not DEBUG
    include_payloads: false

  metrics:
    resolution: 60  # 1 minute, not 1 second
```

---

### Strategy 8: Use Preview Services

**The Opportunity:**
Policy and Evaluations are currently free during preview.

**Implementation:**
- Implement Policy enforcement now
- Build evaluation pipelines now
- Establish baselines before GA pricing

---

### Strategy 9: Optimize Code Interpreter Usage

**The Opportunity:**
Code Interpreter sessions have fixed overhead. Batch executions.

**Implementation:**
- Execute multiple operations per session
- Reuse interpreter instances
- Avoid session creation for trivial operations

**Example:**
```python
# Before: New session per operation
for analysis in analyses:
    result = code_interpreter.execute(analysis)  # New session each

# After: Batch in single session
with code_interpreter.session() as session:
    results = [session.execute(a) for a in analyses]
```

---

### Strategy 10: Monitor and Alert

**The Opportunity:**
Unexpected costs often come from runaway processes or bugs.

**Implementation:**
- Set up AWS Budgets alerts
- Monitor session duration anomalies
- Track memory spikes
- Review weekly cost reports

**Budget Alert Configuration:**
```bash
aws budgets create-budget \
  --account-id $ACCOUNT_ID \
  --budget '{
    "BudgetName": "AgentCore-Daily",
    "BudgetLimit": {"Amount": "50", "Unit": "USD"},
    "BudgetType": "COST",
    "TimeUnit": "DAILY",
    "CostFilters": {
      "Service": ["Amazon Bedrock AgentCore"]
    }
  }' \
  --notifications-with-subscribers '[{
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80
    },
    "Subscribers": [{
      "SubscriptionType": "EMAIL",
      "Address": "ops@example.com"
    }]
  }]'
```

---

### Strategy 11: Design for Efficient Agent Architecture

**The Opportunity:**
Agent architecture significantly impacts costs.

**Guidelines:**

| Approach | Cost Impact |
|----------|-------------|
| Single multi-purpose agent | Higher per-session, fewer sessions |
| Specialized micro-agents | Lower per-session, more sessions |
| Orchestrator + workers | Balanced, good for complex tasks |

**Architecture Decision Framework:**
```
If task_complexity is HIGH and volume is LOW:
  → Single capable agent (reduces Gateway calls)

If task_complexity is LOW and volume is HIGH:
  → Specialized micro-agents (reduces session duration)

If task_complexity is VARIABLE:
  → Orchestrator routing to specialists
```

---

### Strategy 12: Leverage Spot Capacity (When Available)

**The Opportunity:**
AWS may offer spot/preemptible pricing for non-critical workloads.

**Candidates for Spot:**
- Batch processing jobs
- Development/testing
- Non-time-sensitive analytics
- Evaluation runs

*Note: Check AWS documentation for current spot availability.*

---

## Billing and Monitoring

### Understanding Your Bill

#### Bill Structure

AgentCore charges appear in your AWS bill under "Amazon Bedrock":

```
Amazon Bedrock
├── AgentCore Runtime
│   ├── vCPU-Hours: $X.XX
│   └── GB-Hours: $X.XX
├── AgentCore Browser
│   ├── vCPU-Hours: $X.XX
│   └── GB-Hours: $X.XX
├── AgentCore Code Interpreter
│   ├── vCPU-Hours: $X.XX
│   └── GB-Hours: $X.XX
├── AgentCore Gateway
│   ├── API Invocations: $X.XX
│   ├── Search API: $X.XX
│   └── Tool Indexing: $X.XX
├── AgentCore Memory
│   ├── Short-term Events: $X.XX
│   ├── Long-term Storage: $X.XX
│   └── Retrievals: $X.XX
├── AgentCore Identity
│   └── Token Requests: $X.XX
├── AgentCore Policy
│   ├── Authorization Requests: $X.XX
│   └── Input Tokens: $X.XX
└── AgentCore Evaluations
    ├── Built-in Input Tokens: $X.XX
    ├── Built-in Output Tokens: $X.XX
    └── Custom Evaluations: $X.XX

Amazon CloudWatch (Observability)
├── Data Ingestion: $X.XX
├── Logs: $X.XX
└── Storage: $X.XX
```

### Setting Up Cost Monitoring

#### AWS Cost Explorer

1. Navigate to AWS Cost Explorer
2. Filter by Service: "Amazon Bedrock"
3. Group by: "Usage Type" to see AgentCore components
4. Set date range for analysis

#### CloudWatch Dashboards

Create a custom dashboard for AgentCore metrics:

```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "title": "AgentCore Session Duration",
        "metrics": [
          ["AgentCore", "SessionDuration", "AgentName", "MyAgent"]
        ],
        "period": 300
      }
    },
    {
      "type": "metric",
      "properties": {
        "title": "AgentCore CPU Utilization",
        "metrics": [
          ["AgentCore", "CPUUtilization", "AgentName", "MyAgent"]
        ],
        "period": 60
      }
    },
    {
      "type": "metric",
      "properties": {
        "title": "Gateway Invocations",
        "metrics": [
          ["AgentCore", "GatewayInvocations"]
        ],
        "period": 300
      }
    }
  ]
}
```

### Setting Up Alerts

#### Budget Alerts

```bash
# Monthly budget with 50%, 80%, 100% thresholds
aws budgets create-budget \
  --account-id $ACCOUNT_ID \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json
```

**budget.json:**
```json
{
  "BudgetName": "AgentCore-Monthly",
  "BudgetLimit": {
    "Amount": "1000",
    "Unit": "USD"
  },
  "BudgetType": "COST",
  "TimeUnit": "MONTHLY",
  "CostFilters": {
    "Service": ["Amazon Bedrock"]
  }
}
```

#### Anomaly Detection

```bash
# Create cost anomaly monitor
aws ce create-anomaly-monitor \
  --anomaly-monitor '{
    "MonitorName": "AgentCore-Anomalies",
    "MonitorType": "DIMENSIONAL",
    "MonitorDimension": "SERVICE"
  }'
```

### Cost Allocation Tags

Tag your AgentCore resources for detailed cost tracking:

```yaml
tags:
  Environment: production
  Team: customer-support
  Agent: support-bot-v2
  CostCenter: CS-001
```

Enable cost allocation tags in AWS Billing:
1. Go to AWS Billing Console
2. Select "Cost allocation tags"
3. Activate relevant tags

---

## Cost Comparison

### AgentCore vs Self-Hosted Infrastructure

#### Scenario: Customer Support Agent at Scale

**Requirements:**
- 1 million conversations/month
- 90-second average session
- High availability (99.9%)
- Auto-scaling capability

**Self-Hosted (EC2 + Custom)**

| Component | Monthly Cost |
|-----------|--------------|
| EC2 instances (m5.large × 10) | $700 |
| Load balancer | $20 |
| NAT Gateway | $100 |
| ECS/EKS management | $150 |
| Engineering overhead (ops) | $5,000+ |
| Over-provisioning buffer (30%) | $300 |
| **Total** | **$6,270+** |

**AgentCore**

| Component | Monthly Cost |
|-----------|--------------|
| Runtime | $573 |
| Gateway | $8 |
| Memory | $213 |
| **Total** | **$794** |

**Savings: 87%** (excluding engineering time)

### AgentCore vs Lambda-Based Architecture

**Scenario: Code Execution Agent**

**Lambda-Based**

| Component | Monthly Cost |
|-----------|--------------|
| Lambda (1M invocations, 2GB, 2min) | $2,400 |
| Lambda provisioned concurrency | $500 |
| API Gateway | $100 |
| Custom orchestration Lambda | $200 |
| **Total** | **$3,200** |

**AgentCore Code Interpreter**

| Component | Monthly Cost |
|-----------|--------------|
| Code Interpreter | $109 |
| Runtime (orchestration) | $200 |
| Gateway | $5 |
| **Total** | **$314** |

**Savings: 90%**

### AgentCore vs Other Agent Platforms

| Platform | Model | Typical Cost (1M interactions) |
|----------|-------|-------------------------------|
| AgentCore | Consumption-based | $500-2,000 |
| Platform A | Per-seat licensing | $5,000-20,000 |
| Platform B | Per-interaction flat | $3,000-5,000 |
| Self-hosted | Infrastructure + ops | $6,000-15,000 |

**Key Differentiators:**
- I/O wait is free (unique to AgentCore)
- No upfront commitments
- Per-second billing granularity
- No over-provisioning waste

---

## FAQ

### General Pricing Questions

**Q: Is there a minimum commitment?**
A: No. AgentCore has no minimum fees, no upfront commitments, and no long-term contracts. Pay only for what you use.

**Q: How does the $200 Free Tier work?**
A: New AWS customers receive $200 in credits that apply to all AgentCore services. Credits are consumed as you use services and do not have a time-based expiration under standard AWS Free Tier terms.

**Q: Are Preview services really free?**
A: Yes. Policy and Evaluations are currently in preview and have no charges. Use them now to build familiarity before GA pricing begins.

### Compute Pricing Questions

**Q: What exactly is "I/O wait" and why is it free?**
A: I/O wait is time when your agent is waiting for external responses (LLM inference, API calls, database queries) and not actively using CPU. AgentCore detects this idle state and does not charge for CPU during these periods, as long as no background processes are running.

**Q: What's included in the 128MB minimum memory?**
A: Every session is billed for at least 128MB of memory, even if actual usage is lower. This covers the base overhead of the microVM environment.

**Q: Does memory billing include system overhead?**
A: Yes. Memory billing includes both your application's memory usage and system overhead required by the microVM environment.

**Q: How is memory calculated - average or peak?**
A: Peak memory per second. Each second, AgentCore records the highest memory usage, and you're billed at that peak level for that second.

### Service-Specific Questions

**Q: When is Identity free vs charged?**
A: Identity is free when your agent runs on AgentCore Runtime or accesses tools through AgentCore Gateway. Direct API calls to Identity outside these contexts are charged at $0.01/1,000 requests.

**Q: What's the difference between built-in and self-managed memory strategies?**
A: Built-in strategies ($0.75/1,000 records) are fully managed by AgentCore with automatic extraction. Self-managed strategies ($0.25/1,000 records) let you control the extraction logic using your own models, which may incur separate inference costs.

**Q: Do Evaluations model costs get charged separately?**
A: For built-in evaluators, model costs are included in the per-token pricing. For custom evaluators, you pay the per-evaluation fee plus whatever model inference costs you incur in your account.

**Q: How does Observability pricing work?**
A: Observability data flows to Amazon CloudWatch and follows CloudWatch pricing. You pay for span ingestion, log storage, queries, and any additional CloudWatch features you enable.

### Billing Questions

**Q: How often am I billed?**
A: AgentCore charges are billed monthly as part of your standard AWS bill.

**Q: Can I set spending limits?**
A: Yes. Use AWS Budgets to set alerts and, with AWS Organizations, you can set hard limits through Service Control Policies.

**Q: How do I track costs by agent or project?**
A: Use AWS cost allocation tags. Tag your AgentCore resources with project, team, or agent identifiers, then view costs in Cost Explorer filtered by those tags.

**Q: What happens if I exceed my budget?**
A: AWS Budgets can send alerts but won't automatically stop services. For hard limits, use AWS Organizations SCPs or implement application-level controls.

### Technical Questions

**Q: Is there a maximum session duration?**
A: AgentCore Runtime supports sessions up to 8 hours (28,800 seconds).

**Q: What regions is AgentCore available in?**
A: Currently available in us-east-1, us-west-2, ap-southeast-2, and eu-central-1. Check AWS documentation for the latest availability.

**Q: Are data transfer costs included?**
A: No. Network data transfer is charged at standard EC2 rates and is separate from AgentCore service pricing.

---

## Related Resources

### Official AWS Resources

- [AgentCore Pricing Page](https://aws.amazon.com/bedrock/agentcore/pricing/) - Official pricing details
- [AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/) - Developer guide
- [AWS Pricing Calculator](https://calculator.aws/) - Estimate your costs
- [AWS Free Tier](https://aws.amazon.com/free/) - Free Tier details

### Billing and Cost Management

- [AWS Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/) - Analyze spending
- [AWS Budgets](https://aws.amazon.com/aws-cost-management/aws-budgets/) - Set spending alerts
- [AWS Cost Anomaly Detection](https://aws.amazon.com/aws-cost-management/aws-cost-anomaly-detection/) - Detect unusual spending

### Related Service Pricing

- [Amazon CloudWatch Pricing](https://aws.amazon.com/cloudwatch/pricing/) - Observability costs
- [Amazon S3 Pricing](https://aws.amazon.com/s3/pricing/) - Storage for code artifacts
- [Amazon ECR Pricing](https://aws.amazon.com/ecr/pricing/) - Container image storage
- [EC2 Data Transfer Pricing](https://aws.amazon.com/ec2/pricing/on-demand/) - Network costs

### AgentCore Resources

- [AgentCore FAQs](https://aws.amazon.com/bedrock/agentcore/faqs/) - Common questions
- [AgentCore Overview](https://aws.amazon.com/bedrock/agentcore/) - Product overview
- [AgentCore Samples on GitHub](https://github.com/awslabs/amazon-bedrock-agentcore-samples/) - Code examples

---

*Last updated: February 2026*
*Prices are subject to change. Always refer to the [official AWS pricing page](https://aws.amazon.com/bedrock/agentcore/pricing/) for current rates.*
