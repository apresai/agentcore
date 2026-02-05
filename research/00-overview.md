# AWS Bedrock AgentCore Overview

## Executive Summary

Amazon Bedrock AgentCore is a comprehensive agentic platform designed to help developers build, deploy, and operate AI agents securely at enterprise scale. Unlike traditional approaches that force a choice between open-source flexibility and enterprise-grade security, AgentCore delivers both through a modular architecture of nine interconnected services.

### What is AgentCore?

AgentCore is AWS's answer to the operational complexity of deploying AI agents in production. It provides the infrastructure layer that sits between your agent code (built with any framework) and the foundation models (from any provider), handling the undifferentiated heavy lifting of:

- **Secure execution** with microVM isolation for each session
- **Tool integration** through MCP-compatible gateways
- **Context management** with short-term and long-term memory
- **Identity and access** with enterprise IdP integration
- **Observability** with OTEL-compatible tracing and metrics
- **Policy enforcement** with deterministic access controls

### Who is AgentCore For?

AgentCore is designed for:

- **Enterprise development teams** building production AI applications that require security, compliance, and scale
- **Platform teams** creating internal AI infrastructure for multiple development teams
- **Startups and scale-ups** needing enterprise-grade capabilities without building infrastructure from scratch
- **ISVs and SaaS providers** embedding AI agent capabilities into their products

### Key Differentiators

**Framework Agnostic**: Unlike vertically integrated solutions, AgentCore works with LangGraph, Strands, CrewAI, LlamaIndex, Google ADK, OpenAI Agents SDK, or custom frameworks. You are not locked into any particular agent framework.

**Model Agnostic**: Use models from Amazon Bedrock (Claude, Nova, Llama, Mistral), OpenAI, Google Gemini, or any other provider. AgentCore does not dictate your model choices.

**Modular Architecture**: Each of the nine services can be used independently or together. Start with Runtime, add Memory when needed, integrate Gateway as your tool requirements grow.

**Consumption-Based Pricing**: Pay only for actual resource consumption. During I/O wait periods (which can be 30-70% of agent execution time), CPU charges are eliminated. No pre-allocated resources, no idle costs.

**Enterprise Security**: MicroVM isolation, enterprise IdP integration, deterministic policy enforcement, and comprehensive audit trails address the security requirements of regulated industries.

---

## Architecture Overview

AgentCore follows a layered architecture where each service handles a specific aspect of agent operations. The services are designed to work together seamlessly while remaining independently usable.

### High-Level Architecture

```
                              +------------------+
                              |   Your Agent     |
                              | (Any Framework)  |
                              +--------+---------+
                                       |
                    +------------------v------------------+
                    |        AgentCore Runtime           |
                    |  (MicroVM Isolation, 8hr Sessions) |
                    +------------------+-----------------+
                                       |
        +------------------------------+------------------------------+
        |                              |                              |
+-------v--------+            +--------v--------+            +--------v--------+
|    Gateway     |            |     Memory      |            |    Identity     |
| (MCP Tools)    |            | (Context Store) |            | (Auth/Creds)    |
+-------+--------+            +-----------------+            +-----------------+
        |
+-------v--------+
|     Policy     |
| (Cedar Rules)  |
+----------------+

                        +------------------+
                        |   Built-in Tools |
                        +--------+---------+
                                 |
              +------------------+------------------+
              |                                    |
    +---------v----------+              +----------v---------+
    |  Code Interpreter  |              |      Browser       |
    |  (Python/JS/TS)    |              | (Web Automation)   |
    +--------------------+              +--------------------+

                        +------------------+
                        |   Operations     |
                        +--------+---------+
                                 |
              +------------------+------------------+
              |                                    |
    +---------v----------+              +----------v---------+
    |   Observability    |              |    Evaluations     |
    | (OTEL/CloudWatch)  |              | (LLM-as-a-Judge)   |
    +--------------------+              +--------------------+
```

### Data Flow

1. **Inbound Request**: User or system sends a request to your agent
2. **Runtime Processing**: AgentCore Runtime spawns an isolated microVM session
3. **Agent Execution**: Your agent code (in any framework) processes the request
4. **Tool Access**: Agent requests tools through Gateway, which checks Policy
5. **Context Retrieval**: Memory service provides relevant short-term and long-term context
6. **Identity Resolution**: Identity service handles authentication for external services
7. **Built-in Tools**: Code Interpreter and Browser provide compute and web capabilities
8. **Observability**: All operations are traced and logged via CloudWatch
9. **Response**: Results stream back to the user through Runtime

### Integration Points

AgentCore integrates with the broader AWS ecosystem and external services:

| Integration Type | Supported Services |
|-----------------|-------------------|
| **Foundation Models** | Amazon Bedrock (Claude, Nova, Llama, Mistral), OpenAI, Google Gemini, Anthropic API |
| **Identity Providers** | Amazon Cognito, Okta, Microsoft Entra ID, Auth0, any OIDC-compliant IdP |
| **Tool Sources** | OpenAPI specs, Lambda functions, existing MCP servers, Smithy models |
| **1-Click Integrations** | Salesforce, Slack, Jira, Asana, Zendesk, Zoom, GitHub |
| **Observability** | Amazon CloudWatch, any OTEL-compatible system |
| **Agent Frameworks** | LangGraph, Strands, CrewAI, LlamaIndex, Google ADK, OpenAI Agents SDK |
| **Protocols** | MCP (Model Context Protocol), A2A (Agent to Agent) |

---

## Service Deep Dives

### Runtime

**Purpose**: Secure, serverless hosting environment purpose-built for AI agents and tools.

AgentCore Runtime is the foundational service that hosts and executes your agent code. It transforms any local agent into a cloud-native deployment with just a few lines of code, regardless of the underlying framework. The service provides the compute environment, session management, and connectivity that agents need to operate at scale.

**Key Features**:

- **MicroVM Session Isolation**: Each user session runs in a dedicated microVM with isolated CPU, memory, and filesystem resources. After session completion, the entire microVM is terminated and memory is sanitized, providing deterministic security even with non-deterministic AI processes.

- **Extended Execution Time**: Supports both real-time interactions with fast cold starts and long-running workloads up to 8 hours. This enables complex agent reasoning, multi-agent collaboration, and extended problem-solving sessions.

- **Consumption-Based Pricing**: Charges only for actual CPU consumption, not allocated resources. During I/O wait periods (waiting for LLM responses, API calls, database queries), there are no CPU charges. Memory is billed based on peak consumption per second.

- **Enhanced Payload Handling**: Processes payloads up to 100MB, enabling seamless handling of multiple modalities including text, images, audio, and video.

- **Bidirectional Streaming**: Supports both HTTP API calls and persistent WebSocket connections for real-time bidirectional streaming, enabling interactive applications with immediate response feedback.

- **Built-in Authentication**: Powered by AgentCore Identity, Runtime assigns distinct identities to agents and integrates with corporate identity providers for both inbound authentication (verifying users) and outbound authentication (accessing external services).

**When to Use**:
- You need to deploy agents to production with enterprise security
- Your agents require long-running sessions (up to 8 hours)
- You want to avoid infrastructure management
- You need session isolation between users
- You want to optimize costs by paying only for actual compute usage

**Technical Details**:
- Minimum memory billing: 128MB
- Maximum session duration: 8 hours
- Maximum payload size: 100MB
- Deployment options: Direct code deployment or container-based (ECR)
- Protocol support: MCP, A2A

---

### Memory

**Purpose**: Short-term and long-term context management for context-aware agents.

AgentCore Memory addresses the fundamental challenge of statelessness in AI agents. Without memory, agents treat each interaction as isolated, with no knowledge of previous conversations. Memory provides the capability for agents to build coherent understanding over time, enabling personalized and contextual responses.

**Key Features**:

- **Short-Term Memory**: Captures turn-by-turn interactions within a single session. This allows agents to maintain immediate context without requiring users to repeat information. When a user asks "What about tomorrow?" after inquiring about Seattle weather, short-term memory provides the context that "tomorrow" refers to Seattle.

- **Long-Term Memory**: Automatically extracts and stores key insights from conversations across multiple sessions. This includes user preferences, important facts, and session summaries. If a customer mentions preferring window seats during flight booking, the agent stores this and proactively offers window seats in future sessions.

- **Shared Memory Stores**: Memory stores can be shared across multiple agents, enabling multi-agent systems to maintain synchronized state. This is crucial for complex workflows where multiple specialized agents collaborate.

- **Learning from Experiences**: Beyond simple storage, Memory enables agents to learn patterns and improve over time based on accumulated interactions.

**Memory Types**:

| Type | Scope | Persistence | Use Case |
|------|-------|-------------|----------|
| Short-term | Single session | Session duration | Multi-turn conversations, context continuity |
| Long-term | Cross-session | Permanent | User preferences, learned facts, personalization |

**When to Use**:
- Building conversational agents that need context within sessions
- Creating personalized experiences based on user history
- Developing multi-agent systems that need shared state
- Implementing task-oriented agents that track workflow progress

**Framework Integration**:
Memory works with LangGraph, LangChain, Strands, and LlamaIndex through native SDKs.

---

### Gateway

**Purpose**: Convert APIs, Lambda functions, and services into MCP-compatible tools for agent access.

AgentCore Gateway provides the bridge between your existing enterprise systems and AI agents. Instead of spending months writing custom integration code, Gateway transforms APIs into agent-ready tools with just a few lines of code. It handles protocol translation, authentication, and intelligent tool discovery at enterprise scale.

**Key Features**:

- **Multi-Source Tool Creation**: Convert OpenAPI specifications, Smithy models, Lambda functions, and existing MCP servers into unified agent-accessible tools. A single Gateway endpoint can aggregate tools from multiple sources.

- **1-Click Integrations**: Pre-built connectors for popular services including Salesforce, Slack, Jira, Asana, Zendesk, and Zoom. These integrations handle OAuth flows and authentication automatically.

- **Semantic Tool Discovery**: As your tool collection grows (potentially to thousands of tools), built-in semantic search helps agents find the right tools based on task context. This improves agent performance while reducing prompt size and latency.

- **Comprehensive Authentication**: Gateway manages both inbound authentication (verifying agent identity) and outbound authentication (connecting to tools). It handles OAuth flows, token refresh, and secure credential storage.

- **Protocol Translation**: Converts agent requests using MCP into API requests and Lambda invocations, eliminating the need to manage protocol integration or version support.

**Key Capabilities**:

| Capability | Description |
|------------|-------------|
| Security Guard | OAuth authorization ensuring only valid users and agents access tools |
| Translation | Converts MCP requests to API calls and Lambda invocations |
| Composition | Combines multiple APIs, functions, and tools into a single endpoint |
| Credential Exchange | Handles credential injection for tools with different auth requirements |
| Semantic Selection | Enables agents to search across tools to find appropriate ones |
| Infrastructure Manager | Serverless with built-in observability and auditing |

**When to Use**:
- You have existing APIs that agents need to access
- You want to create MCP-compatible tools from Lambda functions
- You need centralized authentication for multiple tool sources
- Your agents need to discover and use hundreds or thousands of tools
- You want pre-built integrations with SaaS services

---

### Identity

**Purpose**: Secure identity and credential management for AI agents and automated workloads.

AgentCore Identity solves the complex problem of how AI agents authenticate and authorize access to resources. It provides secure authentication, authorization, and credential management that enables agents to access AWS resources and third-party services on behalf of users while maintaining strict security controls and audit trails.

**Key Features**:

- **Workload Identity**: Agent identities are implemented as workload identities with specialized attributes that enable agent-specific capabilities while maintaining compatibility with industry-standard workload identity patterns.

- **IdP Integration**: Native integration with existing identity providers including Amazon Cognito, Okta, Microsoft Entra ID, and Auth0. No user migration or rebuilt authentication flows required.

- **Inbound Authentication**: JWT authorizer configuration for verifying the identity of users and systems calling your agents.

- **Outbound Credential Management**: Secure vault storage for credentials that agents use to access external services. Supports both OAuth flows and API keys.

- **Identity-Aware Authorization**: Authorization decisions can incorporate user identity, enabling fine-grained access control based on who is using the agent.

**Authentication Flows**:

```
Inbound (User to Agent):
User --> IdP --> JWT --> AgentCore Identity --> Verified Session

Outbound (Agent to Tool):
Agent --> Identity --> Credential Vault --> OAuth Token/API Key --> External Service
```

**When to Use**:
- Agents need to act on behalf of authenticated users
- You need centralized credential management for external services
- You want to integrate with existing enterprise identity providers
- You require audit trails for agent authentication events

---

### Code Interpreter

**Purpose**: Secure sandbox environment for agents to execute code.

AgentCore Code Interpreter enables AI agents to write and execute code securely, enhancing their accuracy and expanding their ability to solve complex end-to-end tasks. This is critical in agentic AI applications where agents may need to perform calculations, data analysis, or file processing that cannot be achieved through reasoning alone.

**Key Features**:

- **Secure Execution**: Code runs in a containerized sandbox environment within AgentCore, ensuring isolation and security. This prevents arbitrary code from compromising data or systems.

- **Multi-Language Support**: Pre-built runtimes for Python, JavaScript, and TypeScript with common libraries pre-installed.

- **Large File Support**: Inline uploads up to 100MB, with S3 uploads supporting files up to 5GB. This enables processing of substantial datasets.

- **Extended Execution Time**: Default execution time of 15 minutes, extendable up to 8 hours for complex operations.

- **Network Access**: Configurable network modes allow code to access external resources when needed.

- **CloudTrail Logging**: All code execution is logged for audit and compliance purposes.

**Capabilities**:

| Capability | Details |
|------------|---------|
| Languages | Python, JavaScript, TypeScript |
| Inline Upload | Up to 100MB |
| S3 Upload | Up to 5GB |
| Default Timeout | 15 minutes |
| Maximum Timeout | 8 hours |
| Data Formats | CSV, Excel, JSON, and more |

**When to Use**:
- Agents need to perform precise mathematical calculations
- Data analysis and processing requirements exceed reasoning capabilities
- Agents must generate and execute code dynamically
- You need to process structured data files (CSV, Excel, JSON)
- Complex workflows require multi-step computation

---

### Browser

**Purpose**: Secure, isolated browser environment for web automation.

AgentCore Browser provides a managed browser runtime that enables AI agents to interact with web applications at scale. It runs in containerized environments, keeping web activity separate from your systems while providing comprehensive observability through live viewing, session recording, and CloudTrail logging.

**Key Features**:

- **Session Isolation**: Each browser session runs in an ephemeral containerized environment that resets after use, preventing cross-session data contamination.

- **Configurable Sessions**: Sessions support configurable timeouts from the default 15 minutes up to 8 hours maximum. Multiple sessions can run simultaneously.

- **WebSocket Streaming**: Real-time interaction through WebSocket-based APIs. Agents can navigate websites, click elements, fill forms, and take screenshots.

- **Live View**: Real-time monitoring capability allows operators to watch browser sessions as they happen and interact directly when needed.

- **Session Recording**: Custom browsers can capture DOM changes, user actions, console logs, and network events. Recordings are stored in S3 for replay and analysis.

- **Framework Compatibility**: Works with popular browser automation frameworks including Playwright and BrowserUse.

**Browser Workflow**:

1. **Create Browser Tool**: Enable browsing capabilities with AWS managed browser or custom configuration
2. **Start Session**: Launch isolated session with configured timeout
3. **Interact**: Use WebSocket APIs for navigation, form filling, screenshots
4. **Monitor**: Live view for real-time observation, recording for post-analysis

**When to Use**:
- Agents need to navigate and interact with web applications
- Web scraping or data extraction from websites
- Form filling and submission automation
- Web-based workflow automation
- Testing web applications through agent interaction

**Security Features**:
- Containerized isolation from your systems
- Ephemeral sessions that reset after each use
- Automatic termination when TTL expires
- Reduced CAPTCHA interruptions (AWS managed browser)

---

### Observability

**Purpose**: Trace, debug, and monitor agent performance in production.

AgentCore Observability provides visibility into how your agents behave in production. It offers detailed visualizations of each step in agent workflows, enabling you to inspect execution paths, audit intermediate outputs, and debug performance bottlenecks and failures.

**Key Features**:

- **Step-by-Step Visualization**: Detailed traces showing each step of agent execution, including reasoning steps, tool invocations, and model interactions.

- **Real-Time Dashboards**: CloudWatch-powered dashboards provide real-time visibility into operational metrics including session count, latency, duration, token usage, and error rates.

- **OTEL Compatibility**: Telemetry data is emitted in standardized OpenTelemetry format, enabling integration with existing monitoring and observability stacks.

- **Rich Metadata Tagging**: Metadata tagging and filtering capabilities simplify issue investigation and quality maintenance at scale.

- **Built-in Metrics**: Default metrics for agents, gateway resources, and memory resources without additional instrumentation.

**Metrics Available**:

| Category | Metrics |
|----------|---------|
| Runtime | Session count, latency, duration, error rates |
| Gateway | Tool call counts, response times, error rates |
| Memory | Operation counts, retrieval latency |
| Custom | Instrumented spans, traces, logs |

**When to Use**:
- Debugging agent behavior in production
- Understanding agent decision-making processes
- Identifying performance bottlenecks
- Auditing agent actions for compliance
- Monitoring operational health at scale

---

### Evaluations

**Purpose**: Automated assessment of agent and tool quality.

AgentCore Evaluations provides purpose-built evaluation tools to measure how well agents perform tasks, handle edge cases, and maintain consistency across different inputs. The service uses LLM-as-a-Judge techniques to provide measurable quality signals and structured insights for optimization.

**Key Features**:

- **LLM-as-a-Judge**: Automated scoring using large language models to evaluate agent outputs against quality criteria.

- **Built-in Evaluators**: Pre-configured evaluators for common quality dimensions like helpfulness, accuracy, and coherence.

- **Custom Evaluators**: Create evaluators tailored to your specific use cases and quality requirements.

- **Online Evaluation**: Real-time evaluation of agent responses in production.

- **On-Demand Evaluation**: Batch evaluation of historical traces and outputs.

- **Framework Integration**: Native integration with Strands and LangGraph using OpenTelemetry and OpenInference instrumentation.

**Evaluation Types**:

| Type | Description | Use Case |
|------|-------------|----------|
| Online | Real-time scoring of production responses | Continuous quality monitoring |
| On-Demand | Batch evaluation of historical data | Regression testing, optimization |
| Built-in | Pre-configured evaluators | Quick quality assessment |
| Custom | User-defined evaluation criteria | Domain-specific requirements |

**When to Use**:
- Ensuring agents meet quality standards before deployment
- Continuous monitoring of production agent quality
- Comparing different agent configurations or models
- Identifying quality regressions after changes
- Building confidence in agent reliability

**Note**: Evaluations is currently in Preview with no additional charges.

---

### Policy

**Purpose**: Deterministic control over agent actions and tool access.

AgentCore Policy enables developers to define and enforce security controls for AI agent interactions with tools. It creates a protective boundary around agent operations, ensuring agents operate within defined boundaries and business rules without slowing them down.

**Key Features**:

- **Cedar Policy Language**: Policies are written in Cedar, AWS's open-source policy language for fine-grained permissions. Cedar provides clear, auditable, and verifiable access control rules.

- **Natural Language Authoring**: Describe rules in plain English instead of formal policy code. The system interprets intent, generates candidate policies, validates against tool schemas, and uses automated reasoning to check safety conditions.

- **Gateway Integration**: Policy intercepts all agent traffic through AgentCore Gateway, evaluating each request against defined policies before allowing tool access.

- **Fine-Grained Control**: Define permissions based on user identity, tool input parameters, and contextual conditions. Specify which tools agents can access, what actions they can perform, and under what conditions.

- **Deterministic Enforcement**: Every agent action is evaluated at the boundary outside of agent code, ensuring consistent enforcement regardless of how the agent is implemented.

**Policy Capabilities**:

| Capability | Description |
|------------|-------------|
| Enforcement | Intercepts and evaluates all requests before tool access |
| Access Controls | Fine-grained rules based on identity and parameters |
| Authoring | Cedar language or natural language descriptions |
| Monitoring | CloudWatch integration for evaluation decisions |
| Audit Logging | Detailed logs for compliance and troubleshooting |

**When to Use**:
- Agents need restricted access to sensitive tools or data
- Compliance requirements mandate deterministic access control
- You want to prevent agents from exceeding intended authority
- Business rules must be enforced consistently across all agents
- You need audit trails for all agent-to-tool interactions

**Note**: Policy is currently in Preview with no additional charges.

---

## Framework Compatibility

AgentCore is designed to work with any agent framework, providing infrastructure services without dictating implementation choices.

### LangGraph

**Description**: LangGraph is a framework for building stateful, multi-actor applications with LLMs, built on top of LangChain.

**Integration with AgentCore**:
- Runtime: Deploy LangGraph agents with microVM isolation
- Memory: Native integration for short-term and long-term memory
- Observability: Compatible with LangGraph's tracing for unified visibility
- Evaluations: Direct support with OpenTelemetry instrumentation

**Strengths**:
- Excellent for complex, multi-step workflows
- Strong state management capabilities
- Rich ecosystem of tools and integrations
- Well-documented with active community

**Considerations**:
- Learning curve for graph-based programming model
- Requires LangChain familiarity for advanced features

### Strands Agents

**Description**: Strands is AWS's open-source agent framework designed for simplicity and production readiness.

**Integration with AgentCore**:
- Runtime: First-class support with minimal configuration
- Memory: Native SDK integration
- Gateway: Direct tool registration and discovery
- Evaluations: Built-in evaluator support

**Strengths**:
- Simplest path to AgentCore deployment
- Designed with AgentCore in mind
- Clean, intuitive API
- AWS-supported and maintained

**Considerations**:
- Newer framework with smaller community
- Fewer third-party integrations compared to LangChain ecosystem

### CrewAI

**Description**: CrewAI is a framework for orchestrating role-playing AI agents that collaborate on complex tasks.

**Integration with AgentCore**:
- Runtime: Deploy CrewAI crews with full isolation
- Memory: Shared memory stores across crew members
- Gateway: Tool access for all agents in a crew

**Strengths**:
- Intuitive role-based agent design
- Natural multi-agent collaboration
- Good for team-like task decomposition
- Growing community and ecosystem

**Considerations**:
- Newer framework, rapidly evolving
- May require adjustment for production patterns

### LlamaIndex

**Description**: LlamaIndex is a data framework for connecting LLMs with external data sources.

**Integration with AgentCore**:
- Runtime: Deploy LlamaIndex agents
- Memory: Native memory integration
- Gateway: Connect to data sources through tools

**Strengths**:
- Excellent RAG (Retrieval-Augmented Generation) capabilities
- Strong data ingestion and indexing
- Flexible architecture for custom pipelines

**Considerations**:
- Primarily focused on data retrieval use cases
- Agent capabilities are secondary to data handling

### Google ADK (Agent Development Kit)

**Description**: Google's framework for building AI agents.

**Integration with AgentCore**:
- Runtime: Full deployment support
- Model flexibility: Can use Gemini or other models

**Strengths**:
- Well-designed developer experience
- Strong documentation
- Native Gemini integration

**Considerations**:
- Newer framework
- Smaller community compared to LangChain

### OpenAI Agents SDK

**Description**: OpenAI's official SDK for building agents.

**Integration with AgentCore**:
- Runtime: Deploy OpenAI-based agents
- Model flexibility: Can use OpenAI models or others

**Strengths**:
- Official support from OpenAI
- Clean, modern API design
- Strong documentation

**Considerations**:
- Optimized for OpenAI models
- Newer framework with evolving features

### Custom Frameworks

AgentCore also supports custom agent implementations that do not use any specific framework. The key requirement is that your code can be containerized or deployed as a Python application.

---

## Model Flexibility

AgentCore is model-agnostic, enabling you to use any foundation model from any provider.

### Supported Model Providers

| Provider | Models | Access Method |
|----------|--------|---------------|
| Amazon Bedrock | Claude, Nova, Llama, Mistral | Bedrock API |
| Anthropic | Claude (direct API) | Anthropic API |
| OpenAI | GPT-4, GPT-4o, o1 | OpenAI API |
| Google | Gemini | Google AI API |
| Meta | Llama (self-hosted) | Custom endpoint |
| Mistral | Mistral models | Mistral API |
| Any other | Any model | Custom endpoint |

### Multi-Model Architectures

AgentCore supports architectures where different models are used for different purposes:

- **Reasoning Model**: High-capability model for complex reasoning (e.g., Claude Opus, GPT-4)
- **Fast Model**: Lower-latency model for simple tasks (e.g., Claude Haiku, GPT-4o-mini)
- **Specialized Model**: Domain-specific models for particular tasks
- **Evaluation Model**: Model used for LLM-as-a-Judge evaluations

### Model Switching

Because AgentCore is model-agnostic, you can:

- Switch models without changing infrastructure
- A/B test different models in production
- Use different models for different user tiers
- Migrate between providers without lock-in

---

## Protocol Support

AgentCore supports two key protocols for agent interoperability.

### Model Context Protocol (MCP)

MCP is an open protocol that standardizes how AI applications connect to data sources, tools, and services.

**Key Concepts**:
- **Tools**: Functions that agents can invoke to perform actions
- **Resources**: Data sources that agents can read from
- **Prompts**: Template prompts that agents can use

**AgentCore MCP Support**:
- Gateway converts APIs and Lambda functions to MCP-compatible tools
- Gateway can connect to existing MCP servers
- Runtime supports MCP for tool invocation
- Semantic search helps agents discover relevant MCP tools

**Benefits**:
- Standardized tool interface across frameworks
- Growing ecosystem of MCP-compatible tools
- Interoperability with MCP-compatible agents

### Agent to Agent (A2A)

A2A is a protocol for enabling communication between AI agents.

**Key Concepts**:
- **Agent Cards**: Metadata describing agent capabilities
- **Inter-Agent Communication**: Standardized message passing
- **Task Delegation**: Agents can delegate tasks to specialized agents

**AgentCore A2A Support**:
- Runtime can deploy A2A-compatible servers
- Agents can discover and communicate with other A2A agents
- Supports multi-agent collaboration patterns

**Benefits**:
- Build complex systems from specialized agents
- Enable agent marketplaces and discovery
- Standardized inter-agent communication

---

## Use Case Examples

### 1. Enterprise Customer Support Agent

**Scenario**: A financial services company wants to deploy an AI agent that can handle customer inquiries, access account information, and perform transactions.

**Architecture**:
- **Runtime**: Hosts the support agent with session isolation per customer
- **Identity**: Integrates with corporate Okta for customer authentication
- **Gateway**: Connects to CRM (Salesforce), core banking API, and ticketing system (Zendesk)
- **Policy**: Enforces rules like "agent can view account balance but cannot initiate transfers over $1000 without manager approval"
- **Memory**: Stores customer preferences and interaction history
- **Observability**: Tracks all agent actions for compliance auditing

**Benefits**:
- 24/7 customer support with consistent quality
- Secure access to sensitive financial data
- Compliance with financial regulations
- Personalized interactions based on history

### 2. Internal Developer Platform

**Scenario**: A technology company wants to provide AI agent capabilities to multiple internal development teams.

**Architecture**:
- **Runtime**: Centralized hosting for all team agents
- **Gateway**: Curated set of approved tools (JIRA, GitHub, internal APIs)
- **Memory**: Shared knowledge bases across teams
- **Policy**: Per-team access controls on tools and data
- **Identity**: SSO integration with Microsoft Entra ID
- **Evaluations**: Centralized quality monitoring across all agents

**Benefits**:
- Accelerated agent development for all teams
- Consistent security and governance
- Shared infrastructure reduces costs
- Centralized observability and quality assurance

### 3. Data Analysis Agent

**Scenario**: A retail company needs an agent that can analyze sales data, generate reports, and answer business questions.

**Architecture**:
- **Runtime**: Hosts the analysis agent
- **Code Interpreter**: Executes Python for data analysis and visualization
- **Gateway**: Connects to data warehouse and reporting APIs
- **Memory**: Stores analysis patterns and user preferences

**Benefits**:
- Natural language queries for complex data analysis
- Automated report generation
- Secure execution of analytical code
- Learning from past analyses

### 4. Web Research Agent

**Scenario**: A market research firm needs an agent that can gather information from the web and compile reports.

**Architecture**:
- **Runtime**: Hosts the research agent
- **Browser**: Navigates websites and extracts information
- **Code Interpreter**: Processes and structures gathered data
- **Memory**: Tracks research topics and findings over time

**Benefits**:
- Automated web research at scale
- Secure, isolated browsing
- Structured data extraction
- Continuous knowledge accumulation

### 5. Multi-Agent Workflow Orchestration

**Scenario**: A healthcare organization needs to automate patient intake, insurance verification, and appointment scheduling.

**Architecture**:
- **Runtime**: Hosts multiple specialized agents (intake, verification, scheduling)
- **Memory**: Shared state across agents for patient context
- **Gateway**: Connects to EHR, insurance APIs, scheduling system
- **Policy**: Enforces HIPAA compliance rules
- **Identity**: Patient authentication and consent management

**Benefits**:
- Reduced manual processing time
- Consistent compliance with regulations
- Improved patient experience
- Coordinated multi-step workflows

### 6. Code Assistant Agent

**Scenario**: A software company wants to deploy an AI coding assistant that can help developers write, review, and debug code.

**Architecture**:
- **Runtime**: Hosts the coding assistant with per-developer sessions
- **Code Interpreter**: Executes and tests generated code
- **Gateway**: Integrates with GitHub, JIRA, documentation APIs
- **Memory**: Tracks developer preferences and codebase context
- **Evaluations**: Monitors code quality suggestions

**Benefits**:
- Accelerated developer productivity
- Secure code execution environment
- Context-aware assistance
- Continuous quality improvement

---

## Comparison with Alternatives

### vs. Self-Managed Infrastructure

| Aspect | AgentCore | Self-Managed |
|--------|-----------|--------------|
| **Setup Time** | Hours | Weeks to months |
| **Security** | Built-in microVM isolation | Build from scratch |
| **Scaling** | Automatic | Manual configuration |
| **Identity Integration** | Native IdP support | Build integrations |
| **Observability** | Built-in OTEL | Set up monitoring stack |
| **Cost Model** | Consumption-based | Fixed infrastructure costs |
| **Maintenance** | Fully managed | Ongoing operations burden |

**When to choose AgentCore**: You want to focus on agent capabilities rather than infrastructure, need enterprise security, or want to avoid operational overhead.

**When to choose self-managed**: You have unique requirements not met by AgentCore, need complete control over all aspects, or have existing infrastructure investments.

### vs. Amazon Bedrock Agents

| Aspect | AgentCore | Bedrock Agents |
|--------|-----------|----------------|
| **Framework** | Any framework | Bedrock-native |
| **Model** | Any model | Bedrock models |
| **Customization** | Full code control | Configuration-based |
| **Execution Time** | Up to 8 hours | Standard limits |
| **Tool Integration** | MCP/Gateway | Action groups |
| **Use Case** | Complex custom agents | Managed agent experiences |

**When to choose AgentCore**: You need framework flexibility, custom agent logic, long-running sessions, or multi-model architectures.

**When to choose Bedrock Agents**: You want a fully managed experience with minimal code, standard patterns, and Bedrock model integration.

### vs. Other Agent Platforms

| Aspect | AgentCore | Generic Platforms |
|--------|-----------|-------------------|
| **AWS Integration** | Native | Requires configuration |
| **Enterprise Features** | Built-in | Variable |
| **Security** | AWS-grade | Variable |
| **Pricing** | Consumption-based | Often seat-based |
| **Vendor Lock-in** | Framework/model agnostic | Often locked |

---

## Security and Compliance

### Security Features

**Session Isolation**:
Every user session runs in a dedicated microVM with isolated CPU, memory, and filesystem. After session completion, the microVM is terminated and memory is sanitized. This provides complete separation between sessions and deterministic security for non-deterministic AI processes.

**Identity and Access Management**:
- Integration with enterprise identity providers (Okta, Entra ID, Cognito)
- JWT-based inbound authentication
- Secure credential vault for outbound authentication
- Identity-aware authorization in Policy rules

**Network Security**:
- VPC support for network isolation
- Private endpoints available
- Configurable network modes for Code Interpreter and Browser

**Encryption**:
- Data encrypted in transit (TLS)
- Data encrypted at rest
- Customer-managed keys supported where applicable

**Audit and Compliance**:
- CloudTrail logging for all API operations
- Detailed observability traces for agent actions
- Policy evaluation logs for compliance auditing

### Compliance Considerations

AgentCore inherits AWS compliance certifications and can be used in regulated environments. Key considerations:

- **Data Residency**: Available in multiple regions; data stays within selected region
- **Access Control**: IAM policies and AgentCore Policy provide fine-grained control
- **Audit Trails**: Comprehensive logging meets audit requirements
- **Encryption**: Encryption at rest and in transit

Organizations in regulated industries should review specific compliance requirements with AWS and conduct appropriate due diligence.

---

## Regional Availability

### Available Regions

| Region | Code | Runtime | Memory | Gateway | Identity | Code Interpreter | Browser | Observability | Evaluations | Policy |
|--------|------|---------|--------|---------|----------|-----------------|---------|---------------|-------------|--------|
| US East (N. Virginia) | us-east-1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Preview | Preview |
| US West (Oregon) | us-west-2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Preview | Preview |
| Asia Pacific (Sydney) | ap-southeast-2 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Preview | Preview |
| Europe (Frankfurt) | eu-central-1 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Preview | Preview |

**Note**: AgentCore is now generally available with additional regions announced. Check the AWS documentation for the latest availability.

### Region Selection Considerations

- **Latency**: Choose regions closest to your users and data sources
- **Data Residency**: Select regions that meet compliance requirements
- **Model Availability**: Ensure required Bedrock models are available in your region
- **Service Availability**: Verify all needed AgentCore services are available

---

## Pricing Model

### Pricing Philosophy

AgentCore uses consumption-based pricing with no upfront commitments or minimum fees. Each service is billed independently, allowing you to start small and scale as needed.

**Key Principle**: You pay for actual resource consumption, not allocated resources. During I/O wait periods (30-70% of typical agent execution), CPU charges are eliminated.

### Service Pricing Overview

| Service | Pricing Model |
|---------|---------------|
| **Runtime** | CPU consumption + peak memory, per second |
| **Browser** | CPU consumption + peak memory, per second |
| **Code Interpreter** | CPU consumption + peak memory, per second |
| **Gateway** | Per MCP operation + tool indexing |
| **Identity** | Per credential request (free through Runtime/Gateway) |
| **Memory** | Per event (short-term) + per memory record (long-term) |
| **Observability** | CloudWatch pricing for logs and metrics |
| **Evaluations** | Preview (no charge) |
| **Policy** | Preview (no charge) |

### Free Tier

New AWS customers receive up to $200 in Free Tier credits for AgentCore.

### Cost Optimization Tips

1. **Optimize I/O patterns**: Structure agent logic to minimize active CPU during LLM waits
2. **Right-size memory**: Monitor peak memory usage and optimize where possible
3. **Use semantic search**: Reduce prompt sizes by leveraging Gateway's tool discovery
4. **Batch evaluations**: Use on-demand evaluations for cost-effective quality assessment
5. **Monitor with Observability**: Identify and fix inefficient agent patterns

---

## Getting Started

### Prerequisites

1. **AWS Account**: Active AWS account with appropriate permissions
2. **IAM Configuration**: Roles and policies for AgentCore access
3. **Development Environment**: Python environment for SDK usage

### Quick Start Path

1. **Install AgentCore SDK**:
   ```bash
   pip install amazon-bedrock-agentcore
   ```

2. **Install AgentCore Starter Toolkit**:
   ```bash
   pip install agentcore-starter-toolkit
   ```

3. **Create your first agent**:
   ```bash
   agentcore create my-first-agent
   ```

4. **Deploy to AgentCore**:
   ```bash
   agentcore deploy my-first-agent
   ```

5. **Invoke your agent**:
   ```bash
   agentcore invoke my-first-agent "Hello, agent!"
   ```

### Development Interfaces

| Interface | Use Case |
|-----------|----------|
| AgentCore Starter Toolkit | CLI for create, deploy, invoke, manage |
| AgentCore Python SDK | Programmatic agent development |
| AWS SDK (boto3) | Low-level API access |
| AWS Console | Visual management and monitoring |
| AgentCore MCP Server | MCP client integration |

### Learning Path

1. Start with the [AgentCore Developer Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
2. Try the tutorials in [AgentCore Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples/)
3. Explore the [AgentCore Starter Toolkit documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-get-started-toolkit.html)
4. Review pricing and optimize costs
5. Build your production agent

---

## Related Resources

### Official Documentation

- [Amazon Bedrock AgentCore Developer Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [Amazon Bedrock AgentCore Product Page](https://aws.amazon.com/bedrock/agentcore/)
- [Amazon Bedrock AgentCore Pricing](https://aws.amazon.com/bedrock/agentcore/pricing/)
- [Amazon Bedrock AgentCore FAQs](https://aws.amazon.com/bedrock/agentcore/faqs/)

### Code Samples and Tutorials

- [Amazon Bedrock AgentCore Samples (GitHub)](https://github.com/awslabs/amazon-bedrock-agentcore-samples/)
- [Strands Agents Framework](https://github.com/strands-agents/strands-agents)
- [AWS Samples for Agentic AI](https://github.com/aws-samples?q=agent)

### AWS Blog Posts

- [Introducing Amazon Bedrock AgentCore](https://aws.amazon.com/blogs/aws/introducing-amazon-bedrock-agentcore-securely-deploy-and-operate-ai-agents-at-any-scale/)
- [Running Deep Research AI Agents on AgentCore](https://aws.amazon.com/blogs/machine-learning/running-deep-research-ai-agents-on-amazon-bedrock-agentcore/)
- [Building Healthcare Agents with AgentCore](https://aws.amazon.com/blogs/machine-learning/building-health-care-agents-using-amazon-bedrock-agentcore/)
- [AgentCore and Claude: Transforming Business with Agentic AI](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-agentcore-and-claude-transforming-business-with-agentic-ai/)

### Related AWS Services

- [Amazon Bedrock](https://aws.amazon.com/bedrock/) - Foundation models service
- [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/) - Managed agent service
- [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) - Monitoring and observability
- [AWS Lambda](https://aws.amazon.com/lambda/) - Serverless compute
- [Amazon Cognito](https://aws.amazon.com/cognito/) - Identity management

### Community and Support

- [AWS re:Post AgentCore Community](https://repost.aws/tags/TAG-agentcore)
- [AWS Developer Forums](https://forums.aws.amazon.com/)
- [AWS Support](https://aws.amazon.com/support/)

---

## Glossary

| Term | Definition |
|------|------------|
| **A2A** | Agent to Agent protocol for inter-agent communication |
| **Cedar** | AWS open-source policy language used by AgentCore Policy |
| **IdP** | Identity Provider (e.g., Okta, Entra ID, Cognito) |
| **LLM-as-a-Judge** | Technique using LLMs to evaluate agent output quality |
| **MCP** | Model Context Protocol for standardized tool access |
| **MicroVM** | Lightweight virtual machine providing session isolation |
| **OTEL** | OpenTelemetry, standard for observability telemetry |
| **Session** | Isolated execution context for a single user interaction |
| **Short-term Memory** | Context retained within a single session |
| **Long-term Memory** | Knowledge persisted across multiple sessions |
| **Workload Identity** | Identity assigned to automated processes (like agents) |

---

## Status and Roadmap

### Current Status (As of 2025)

- **Generally Available**: Runtime, Memory, Gateway, Identity, Code Interpreter, Browser, Observability
- **Preview**: Evaluations, Policy

### Recent Announcements

- General availability with VPC support
- A2A protocol support
- Expanded regional availability
- MCP server connectivity
- Identity-aware authorization enhancements

### Known Limitations

- Policy and Evaluations are in Preview (no charges during preview)
- Regional availability varies; check documentation for latest
- Some framework integrations are more mature than others

---

## Conclusion

Amazon Bedrock AgentCore represents AWS's comprehensive approach to production AI agent infrastructure. By providing modular, enterprise-grade services that work with any framework and any model, AgentCore eliminates the traditional trade-off between open-source flexibility and enterprise security.

Key takeaways:

1. **Modular Architecture**: Use what you need, when you need it
2. **Framework Agnostic**: Bring your own agent framework
3. **Model Agnostic**: Use any foundation model
4. **Enterprise Security**: MicroVM isolation, IdP integration, deterministic policy
5. **Consumption Pricing**: Pay for actual usage, not allocated resources
6. **Production Ready**: Built for scale, reliability, and compliance

Whether you are building customer support agents, internal developer platforms, data analysis tools, or complex multi-agent systems, AgentCore provides the infrastructure foundation to deploy and operate AI agents at enterprise scale.
