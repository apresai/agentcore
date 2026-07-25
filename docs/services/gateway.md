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

`GatewayClient` manages gateway and target *resources* (create/get/list/update/delete, plus `*_and_wait` variants) - it has no `create_from_openapi`, `create_from_lambda`, `enable_integration`, or `connect_mcp_server` methods, and it does not proxy tool calls. Create a gateway once, then attach one or more targets to it.

### Create a Gateway

```python
from bedrock_agentcore.gateway import GatewayClient

gateway = GatewayClient(region_name="us-east-1")

# Waits for the gateway to reach READY (or raises on FAILED)
gw = gateway.create_gateway_and_wait(
    name="MyGateway",
    roleArn="arn:aws:iam::123456789012:role/GatewayRole",
    authorizerType="AWS_IAM",
    protocolType="MCP",
    protocolConfiguration={"mcp": {"searchType": "SEMANTIC"}},
)

gateway_id = gw["gatewayId"]
gateway_url = gw["gatewayUrl"]
```

### Add an OpenAPI Target

```python
# The OpenAPI spec must be staged in S3 first.
target = gateway.create_gateway_target_and_wait(
    gatewayIdentifier=gateway_id,
    name="my-api",
    targetConfiguration={
        "mcp": {
            "openApiSchema": {
                "s3": {"uri": "s3://my-bucket/specs/my-api.yaml"},
            }
        }
    },
)
```

### Add a Lambda Target

```python
# Wrap a Lambda function as an MCP tool
target = gateway.create_gateway_target_and_wait(
    gatewayIdentifier=gateway_id,
    name="process-order",
    targetConfiguration={
        "mcp": {
            "lambda": {
                "lambdaArn": "arn:aws:lambda:us-east-1:123456789012:function:process-order",
                "toolSchema": {
                    "inlinePayload": [
                        {
                            "name": "process_order",
                            "description": "Process a customer order",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"order_id": {"type": "string"}},
                                "required": ["order_id"],
                            },
                        }
                    ]
                },
            }
        }
    },
)
```

### Enable a 1-Click Integration

1-click integrations are a `connector` target backed by AWS's managed connector catalog, not an `enable_integration()` SDK call:

```python
target = gateway.create_gateway_target_and_wait(
    gatewayIdentifier=gateway_id,
    name="SlackConnector",
    targetConfiguration={
        "mcp": {
            "connector": {
                "source": {"connectorId": "slack", "version": "1"},  # see the console's connector catalog for valid IDs
            }
        }
    },
    credentialProviderConfigurations=[
        {
            "credentialProviderType": "OAUTH",
            "credentialProvider": {
                "oauthCredentialProvider": {
                    "providerArn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:credential-provider/slack-oauth",
                    "scopes": ["chat:write", "channels:read"],
                }
            },
        }
    ],
)
```

### Connect an Existing MCP Server

```python
target = gateway.create_gateway_target_and_wait(
    gatewayIdentifier=gateway_id,
    name="company-tools",
    targetConfiguration={
        "mcp": {
            "mcpServer": {
                "endpoint": "https://mcp.company.com",
                "listingMode": "AUTOMATIC",
            }
        }
    },
)
```

---

## Calling Tools via MCP

Gateway has no data-plane boto3 API and `GatewayClient` doesn't proxy tool calls - agents call gateway tools by speaking MCP over HTTP against `gw["gatewayUrl"]`, using the `mcp` package (or a framework's MCP client, e.g. Strands' `MCPClient`):

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def list_and_call(gateway_url: str, bearer_token: str):
    async with streamablehttp_client(
        gateway_url, headers={"Authorization": f"Bearer {bearer_token}"}
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            result = await session.call_tool("process_order", {"order_id": "123"})
            return tools, result
```

For an `authorizerType='AWS_IAM'` gateway, sign the HTTP request with SigV4 instead of a bearer token.

---

## boto3 Alternative

Only `bedrock-agentcore-control` (control plane) is real for gateway resource management - there is no `bedrock-agentcore-gateway` service, and Gateway has no data-plane boto3 API for invoking tools (that happens over MCP, above).

```python
import boto3

control_client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

# Create gateway
response = control_client.create_gateway(
    name='my-api',
    roleArn='arn:aws:iam::123456789012:role/GatewayRole',
    authorizerType='AWS_IAM',
    protocolType='MCP',
)
gateway_id = response['gatewayId']

# List gateways
for gw in control_client.list_gateways(maxResults=50)['items']:
    print(f"{gw['name']}: {gw['status']}")

# List targets on a gateway
for target in control_client.list_gateway_targets(gatewayIdentifier=gateway_id)['items']:
    print(f"{target['name']}: {target['status']}")
```

---

## Semantic Tool Discovery

Semantic ranking is a gateway-level setting, not a separate indexing step - set `protocolConfiguration.mcp.searchType='SEMANTIC'` when creating (or updating) the gateway, and tool discovery through the standard MCP `tools/list` call is ranked by relevance:

```python
gateway.update_gateway_and_wait(
    gatewayIdentifier=gateway_id,
    protocolConfiguration={"mcp": {"searchType": "SEMANTIC"}},
)
```

There is no separate `search_tools()` call - once semantic search is enabled, the standard MCP `tools/list` call (shown under [Calling Tools via MCP](#calling-tools-via-mcp) above) itself returns tools ranked by relevance.

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

Outbound authentication is attached to a *target* via `credentialProviderConfigurations`, referencing a credential provider created through [AgentCore Identity](identity.md) - it isn't an `auth=`/`enable_integration()` keyword on a gateway-creation call.

### OAuth 2.0

```python
from bedrock_agentcore.identity.auth import IdentityClient

identity = IdentityClient(region="us-east-1")

# Create the credential provider once (see AgentCore Identity for details)
provider = identity.create_oauth2_credential_provider({
    "name": "SalesforceProvider",
    "credentialProviderVendor": "SalesforceOauth2",
    "oauth2ProviderConfigInput": {
        "salesforceOauth2ProviderConfig": {
            "clientId": "your-client-id",
            "clientSecret": "your-client-secret",
        }
    },
})

# Reference it from a target
target = gateway.create_gateway_target_and_wait(
    gatewayIdentifier=gateway_id,
    name="SalesforceTools",
    targetConfiguration={"mcp": {"openApiSchema": {"s3": {"uri": "s3://my-bucket/salesforce.yaml"}}}},
    credentialProviderConfigurations=[
        {
            "credentialProviderType": "OAUTH",
            "credentialProvider": {
                "oauthCredentialProvider": {
                    "providerArn": provider["credentialProviderArn"],
                    "scopes": ["api"],
                }
            },
        }
    ],
)
```

### API Key Authentication

```python
provider = identity.create_api_key_credential_provider({
    "name": "MyApiKey",
    "apiKey": "your-api-key",
})

target = gateway.create_gateway_target_and_wait(
    gatewayIdentifier=gateway_id,
    name="my-api",
    targetConfiguration={"mcp": {"openApiSchema": {"s3": {"uri": "s3://my-bucket/specs/my-api.yaml"}}}},
    credentialProviderConfigurations=[
        {
            "credentialProviderType": "API_KEY",
            "credentialProvider": {
                "apiKeyCredentialProvider": {"providerArn": provider["credentialProviderArn"]}
            },
        }
    ],
)
```

### User-Level Credentials

For per-user OAuth (each user authenticates independently and Gateway stores their token separately), use the `USER_FEDERATION` auth flow when the tool ultimately calls `requires_access_token` / `IdentityClient.get_token` - see [AgentCore Identity](identity.md) for the full pattern.

---

## Using Tools in Agents

There is no `strands.tools.AgentCoreGatewayTools` or `langchain_agentcore.AgentCoreToolkit` package. Both frameworks connect the same way: an MCP client pointed at the gateway's URL.

### Strands Integration

Strands has a built-in `MCPClient` over the `mcp` package's streamable-HTTP transport:

```python
from strands import Agent
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

def make_mcp_client(gateway_url: str, bearer_token: str) -> MCPClient:
    return MCPClient(
        lambda: streamablehttp_client(
            gateway_url,
            headers={"Authorization": f"Bearer {bearer_token}"},
        )
    )

mcp_client = make_mcp_client(gateway_url, bearer_token)

with mcp_client:
    tools = mcp_client.list_tools_sync()

    agent = Agent(
        model=model,
        tools=tools,
        system_prompt="You are a helpful assistant.",
    )

    response = agent("Send a Slack message to #general saying hello")
```

### LangGraph Integration

Outside Strands, the raw `mcp` client SDK works the same way against any framework, including inside a LangGraph tool node:

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def list_gateway_tools(gateway_url: str, bearer_token: str):
    async with streamablehttp_client(
        gateway_url, headers={"Authorization": f"Bearer {bearer_token}"}
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await session.list_tools()
```

---

## Policy Integration

Gateway integrates with [AgentCore Policy](policy.md) by attaching a policy engine to the gateway itself (`policyEngineConfiguration` on `UpdateGateway`) - there is no per-call `invoke_tool(user_id=...)` parameter, because Gateway has no data-plane boto3 API in the first place (see [Calling Tools via MCP](#calling-tools-via-mcp)):

```python
# UpdateGateway is not a sparse patch: name, roleArn and authorizerType are
# required on every call, so read the current configuration back first.
gw = control_client.get_gateway(gatewayIdentifier=gateway_id)
control_client.update_gateway(
    gatewayIdentifier=gateway_id,
    name=gw["name"],
    roleArn=gw["roleArn"],
    authorizerType=gw["authorizerType"],
    policyEngineConfiguration={"arn": policy_engine_arn, "mode": "ENFORCE"},
)

# Every MCP tool call through this gateway is now evaluated against the
# attached policy engine before the target executes.
```

---

## Best Practices

### 1. Organize Tools by Domain

```python
# Group related tools under separate gateways
crm_gateway = gateway.create_gateway_and_wait(name="crm-tools", roleArn=role_arn, protocolType="MCP")
billing_gateway = gateway.create_gateway_and_wait(name="billing-tools", roleArn=role_arn, protocolType="MCP")
```

### 2. Use Descriptive Tool Names

```python
# Good: descriptive names and descriptions in the tool schema
tool_schema = {
    "name": "get_customer_by_email",
    "description": "Look up a customer record using their email address",
}

# Bad: vague names
tool_schema = {
    "name": "process",
    "description": "Process something",
}
```

### 3. Enable Semantic Search for Large Collections

```python
# For 50+ tools, enable semantic search at the gateway level
gateway.update_gateway_and_wait(
    gatewayIdentifier=gateway_id,
    protocolConfiguration={"mcp": {"searchType": "SEMANTIC"}},
)
```

### 4. Store Credentials Securely

Credential material lives in a credential provider (created via [AgentCore Identity](identity.md)), referenced from the target by ARN - never inline in `targetConfiguration`:

```python
credential_provider_configurations = [
    {
        "credentialProviderType": "API_KEY",
        "credentialProvider": {
            "apiKeyCredentialProvider": {"providerArn": "arn:aws:bedrock-agentcore:..."}
        },
    }
]
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
