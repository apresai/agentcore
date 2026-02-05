# Gateway

> Convert APIs, Lambda functions, and services into MCP-compatible tools

## Overview

AgentCore Gateway provides the bridge between your existing enterprise systems and AI agents. Instead of spending months writing custom integration code, Gateway transforms APIs into agent-ready tools with just a few lines of code.

```
┌─────────────────────────────────────────────────────────────────┐
│                      Your Agent                                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │ MCP Request
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AgentCore Gateway                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Semantic Discovery                      │   │
│  │           "Find tools for customer lookup"               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│  ┌──────────┬────────────┼────────────┬──────────┐             │
│  ▼          ▼            ▼            ▼          ▼             │
│ ┌────┐   ┌────┐      ┌────┐      ┌────┐    ┌────────┐         │
│ │ API│   │API │      │Lambda│    │MCP │    │1-Click │         │
│ │ 1  │   │ 2  │      │Func │    │Server   │(Slack) │         │
│ └────┘   └────┘      └────┘      └────┘    └────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

### Multi-Source Tool Creation

| Source | Description | Use Case |
|--------|-------------|----------|
| **OpenAPI** | Convert REST API specs | Existing APIs |
| **Lambda** | Wrap Lambda functions | Custom logic |
| **MCP Servers** | Connect existing MCP | MCP ecosystem |
| **Smithy** | AWS service models | AWS integration |

### 1-Click Integrations

Pre-built connectors with automatic OAuth handling:

| Integration | Capabilities |
|-------------|-------------|
| **Salesforce** | CRM operations, account management |
| **Slack** | Messaging, channel management |
| **Jira** | Issue tracking, project management |
| **Asana** | Task management, projects |
| **Zendesk** | Support tickets, customer service |
| **Zoom** | Meetings, scheduling |
| **GitHub** | Repositories, issues, PRs |

### Semantic Tool Discovery

As your tool collection grows to hundreds or thousands, agents find the right tools automatically:

```
Agent: "I need to look up customer information"
       ↓
Gateway: Semantic search across 500+ tools
       ↓
Returns: [get_customer, search_customers, get_customer_orders]
```

### Comprehensive Authentication

| Flow | Description |
|------|-------------|
| **Inbound** | Verify agent identity calling Gateway |
| **Outbound** | Handle OAuth, API keys for target tools |
| **Token refresh** | Automatic credential management |

---

## Quick Start

### Create Gateway from OpenAPI

```python
from bedrock_agentcore.gateway import GatewayClient

gateway = GatewayClient()

# Create tools from OpenAPI spec
tools = gateway.create_from_openapi(
    name="my-api",
    spec_url="https://api.example.com/openapi.json"
)

print(f"Created {len(tools)} tools")
for tool in tools:
    print(f"  - {tool.name}: {tool.description}")
```

### Create Gateway from Lambda

```python
# Wrap Lambda function as MCP tool
tool = gateway.create_from_lambda(
    name="process-order",
    function_arn="arn:aws:lambda:us-east-1:123456789:function:process-order",
    description="Process a customer order"
)
```

### Enable 1-Click Integration

```python
# Enable Slack integration
slack_tools = gateway.enable_integration(
    name="slack",
    config={
        "workspace_id": "T12345678"
    }
)

# OAuth flow handled automatically
print(f"Slack tools: {[t.name for t in slack_tools]}")
# ['slack_send_message', 'slack_list_channels', ...]
```

### Connect Existing MCP Server

```python
# Connect to external MCP server
tools = gateway.connect_mcp_server(
    name="company-tools",
    url="https://mcp.company.com",
    auth_token="..."
)
```

---

## boto3 Alternative

```python
import boto3

gateway = boto3.client('bedrock-agentcore-gateway')

# Create gateway resource
response = gateway.create_gateway_resource(
    name='my-api',
    type='OPENAPI',
    source={
        'url': 'https://api.example.com/openapi.json'
    }
)

# List tools
tools = gateway.list_tools(gatewayResourceId=response['id'])

# Invoke tool
result = gateway.invoke_tool(
    gatewayResourceId=response['id'],
    toolName='get_customer',
    input={'customer_id': '123'}
)
```

---

## Semantic Tool Discovery

### Enable Indexing

```python
# Index tools for semantic search
gateway.index_tools(
    gateway_resource_id="my-api",
    enable_semantic_search=True
)
```

### Search Tools

```python
# Agent searches for relevant tools
relevant_tools = gateway.search_tools(
    query="get customer billing information",
    limit=5
)

for tool in relevant_tools:
    print(f"{tool.name} (score: {tool.relevance_score:.2f})")
    print(f"  {tool.description}")
```

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│  Tool Collection (1000+ tools)                                  │
│                                                                 │
│  Agent query: "I need to refund a customer order"               │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Semantic Embedding Search                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  Relevant tools returned:                                       │
│  1. process_refund (0.95)                                       │
│  2. get_order_details (0.82)                                    │
│  3. update_order_status (0.78)                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Authentication Patterns

### OAuth 2.0 Flow

```python
# Gateway handles OAuth automatically for 1-click integrations
tools = gateway.enable_integration(
    name="salesforce",
    config={
        "instance_url": "https://mycompany.salesforce.com"
    }
)

# User completes OAuth flow once
# Gateway stores and refreshes tokens automatically
```

### API Key Authentication

```python
# Configure API key auth
tools = gateway.create_from_openapi(
    name="my-api",
    spec_url="https://api.example.com/openapi.json",
    auth={
        "type": "api_key",
        "header": "X-API-Key",
        "secret_arn": "arn:aws:secretsmanager:us-east-1:123456789:secret:my-api-key"
    }
)
```

### User-Level Credentials

```python
# Different credentials per user
tools = gateway.create_from_openapi(
    name="user-api",
    spec_url="https://api.example.com/openapi.json",
    auth={
        "type": "user_credential",
        "credential_type": "oauth2"
    }
)

# Each user authenticates independently
# Gateway manages credential per user_id
```

---

## Using Tools in Agents

### Strands Integration

```python
from strands import Agent
from strands.tools import AgentCoreGatewayTools

# Load tools from Gateway
tools = AgentCoreGatewayTools(
    gateway_resource_ids=["my-api", "slack"]
)

agent = Agent(
    model=model,
    tools=tools,
    system_prompt="You are a helpful assistant."
)

response = agent.run("Send a Slack message to #general saying hello")
```

### LangGraph Integration

```python
from langchain_agentcore import AgentCoreToolkit

# Get tools as LangChain tools
toolkit = AgentCoreToolkit(
    gateway_resource_ids=["my-api"]
)
tools = toolkit.get_tools()

# Use in graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", create_agent_node(tools))
```

---

## Policy Integration

Gateway integrates with [AgentCore Policy](policy.md) for access control:

```python
# All requests through Gateway are evaluated against Policy
# See Policy service for rule configuration

# Example: Agent requests customer data
result = gateway.invoke_tool(
    gateway_resource_id="crm-api",
    tool_name="get_customer",
    input={"customer_id": "123"},
    user_id="user-456"  # Used for policy evaluation
)

# Policy evaluates:
# - Can this user access customer data?
# - Is this operation allowed for this agent?
```

---

## Best Practices

### 1. Organize Tools by Domain

```python
# Group related tools
crm_tools = gateway.create_from_openapi(
    name="crm-tools",
    spec_url="https://crm.example.com/openapi.json"
)

billing_tools = gateway.create_from_openapi(
    name="billing-tools",
    spec_url="https://billing.example.com/openapi.json"
)
```

### 2. Use Descriptive Tool Names

```python
# Good: Descriptive names
tool = gateway.create_from_lambda(
    name="get-customer-by-email",
    description="Look up a customer record using their email address"
)

# Bad: Vague names
tool = gateway.create_from_lambda(
    name="process",
    description="Process something"
)
```

### 3. Enable Semantic Search for Large Collections

```python
# For 50+ tools, enable semantic search
gateway.index_tools(
    gateway_resource_id="my-api",
    enable_semantic_search=True
)
```

### 4. Store Credentials Securely

```python
# Use Secrets Manager for API keys
auth={
    "type": "api_key",
    "secret_arn": "arn:aws:secretsmanager:..."  # Never hardcode
}
```

---

## Pricing

| Operation | Cost |
|-----------|------|
| MCP operation | Per request |
| Tool indexing | Per tool indexed |
| Semantic search | Per search |

---

## When to Use Gateway

| Scenario | Recommendation |
|----------|----------------|
| Existing REST APIs | ✅ OpenAPI conversion |
| Custom business logic | ✅ Lambda integration |
| SaaS integrations | ✅ 1-Click connectors |
| Existing MCP servers | ✅ MCP server connection |
| 50+ tools | ✅ Enable semantic search |

---

## Related Services

| Service | Integration |
|---------|-------------|
| [Runtime](runtime.md) | Agents access tools via Gateway |
| [Identity](identity.md) | Credential management |
| [Policy](policy.md) | Access control for tool calls |
| [Observability](observability.md) | Track tool usage |

---

## Resources

- [Gateway Developer Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)
- [Detailed Research](../../research/03-gateway.md)
- [1-Click Integrations Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-integrations.html)
