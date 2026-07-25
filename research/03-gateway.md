# AgentCore Gateway

> Convert APIs, Lambda functions, and services into MCP-compatible tools with unified access, semantic search, and built-in authentication.

## Quick Reference

| CLI Command | Description |
|-------------|-------------|
| `agentcore gateway create-mcp-gateway` | Create new gateway |
| `agentcore gateway create-mcp-gateway-target` | Add target to gateway |
| `agentcore gateway list-mcp-gateways` | List all gateways |
| `agentcore gateway get-mcp-gateway` | Get details for a gateway |
| `agentcore gateway update-gateway` | Update gateway description / policy engine |
| `agentcore gateway delete-mcp-gateway` | Delete a gateway |
| `agentcore gateway list-mcp-gateway-targets` | List targets for a gateway |
| `agentcore gateway get-mcp-gateway-target` | Get details for a target |
| `agentcore gateway delete-mcp-gateway-target` | Delete a target |

| SDK Client | Purpose |
|------------|---------|
| `GatewayClient` (AgentCore SDK) | Create/get/list/update/delete gateways and targets |
| `bedrock-agentcore-control` (control plane) | Manage gateway resources directly via boto3 |

| Key API | Description |
|---------|-------------|
| `CreateGateway` | Create gateway resource |
| `CreateGatewayTarget` | Add tool target |
| `GetGateway` / `ListGateways` | Read gateway resources |
| `UpdateGateway` / `DeleteGateway` | Manage gateway resources |

There is no `bedrock-agentcore` **data-plane** API for gateways - no `ListTools`, `CallTool`, or `Ping` operation exists in boto3. Once a gateway is created, agents call its tools by speaking MCP directly to the gateway's URL (see "Calling Tools via MCP" below), not through a boto3 call.

---

## Overview

Amazon Bedrock AgentCore Gateway provides an easy and secure way to build, deploy, discover, and connect to tools at scale. It converts APIs, Lambda functions, and services into **Model Context Protocol (MCP)-compatible tools**.

## The Problem It Solves

AI agents need tools to perform real-world tasks (querying databases, sending messages, analyzing documents). Gateway eliminates weeks of custom code development, infrastructure provisioning, and security implementation.

---

## Core Concepts

### Gateway

A gateway is the central endpoint that agents connect to for tool access. It:
- Aggregates multiple tool targets
- Handles authentication (inbound and outbound)
- Provides MCP-compatible interface
- Enables semantic tool discovery

### Targets

Targets define how the gateway routes requests to specific tools. The real target types (`targetConfiguration.mcp.*` in `CreateGatewayTarget`) are:
- **`lambda`** - AWS Lambda functions
- **`openApiSchema`** - REST APIs described by an OpenAPI spec
- **`smithyModel`** - APIs defined with Smithy models
- **`mcpServer`** - External MCP servers
- **`apiGateway`** - Amazon API Gateway APIs
- **`connector`** - AWS's pre-built connector catalog (Salesforce, Slack, Jira, etc. - see "1-Click Integrations" below)

### Tool Discovery

Gateway supports intelligent tool discovery:
- **`tools/list`** (MCP) - Enumerate all available tools
- **Semantic search** - Set `protocolConfiguration.mcp.searchType='SEMANTIC'` on the gateway to have it rank tools by natural-language relevance during `tools/list`
- Agents dynamically select appropriate tools based on context

### Authentication

Gateway handles dual-sided security:
- **Inbound auth** - Verify agent/user identity (`AWS_IAM`, `CUSTOM_JWT`, `NONE`, or `AUTHENTICATE_ONLY`)
- **Outbound auth** - Connect to backend services (OAuth2, API key, or IAM SigV4 credential providers)

---

## CLI Reference

### Installation

```bash
pip install bedrock-agentcore-starter-toolkit
```

### agentcore gateway create-mcp-gateway

Create a new gateway.

```bash
agentcore gateway create-mcp-gateway [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--region` | AWS region | us-west-2 |
| `--name` | Gateway name | `TestGateway` |
| `--role-arn` | IAM role ARN (created if omitted) | auto-created |
| `--authorizer-config` | Serialized authorizer config JSON (created if omitted) | auto-created |
| `--enable_semantic_search`, `-sem` | Enable the semantic search tool | true |

**Examples:**

```bash
# Basic gateway, everything auto-created
agentcore gateway create-mcp-gateway --name MyGateway --region us-east-1

# Disable semantic search
agentcore gateway create-mcp-gateway --name MyGateway --enable_semantic_search=false
```

### agentcore gateway create-mcp-gateway-target

Add a target to an existing gateway. Unlike gateway creation, this needs the gateway's ARN, URL, and role ARN explicitly - there is no `--gateway-id` shortcut.

```bash
agentcore gateway create-mcp-gateway-target [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--gateway-arn` | ARN of the gateway (required) | - |
| `--gateway-url` | URL of the gateway (required) | - |
| `--role-arn` | IAM role ARN of the gateway (required) | - |
| `--region` | AWS region | us-west-2 |
| `--name` | Target name | `TestGatewayTarget` |
| `--target-type` | `lambda`, `openApiSchema`, `mcpServer`, or `smithyModel` | `lambda` |
| `--target-payload` | Target specification JSON (required for `openApiSchema`) | - |
| `--credentials` | Credentials JSON for target access (`openApiSchema` only) | - |

**Examples:**

```bash
# Lambda target
agentcore gateway create-mcp-gateway-target \
    --gateway-arn arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/gw-abc123 \
    --gateway-url https://gw-abc123.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp \
    --role-arn arn:aws:iam::123456789012:role/MyGatewayRole \
    --name WeatherTool \
    --target-type lambda \
    --target-payload '{"lambdaArn": "arn:aws:lambda:us-east-1:123456789012:function:GetWeather", "toolSchema": {"inlinePayload": [{"name": "get_weather", "description": "Get current weather", "inputSchema": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}}]}}'
```

`--target-type` values are case-sensitive and camelCase (`openApiSchema`, not `openapi`); `apiGateway` and `connector` targets are not exposed through this CLI command and must be created via the SDK or `create_gateway_target` boto3 call.

### agentcore gateway list-mcp-gateways

```bash
agentcore gateway list-mcp-gateways [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--region` | AWS region | - |
| `--name` | Filter by gateway name | - |
| `--max-results`, `-m` | Max results (1-1000) | 50 |

### agentcore gateway get-mcp-gateway / delete-mcp-gateway

Both take the gateway by ID, ARN, or name:

```bash
agentcore gateway get-mcp-gateway --id gw-abc123
agentcore gateway get-mcp-gateway --name MyGateway

agentcore gateway delete-mcp-gateway --id gw-abc123 --force
```

`delete-mcp-gateway --force` deletes all targets before deleting the gateway; without it, deletion fails if the gateway still has targets.

### agentcore gateway update-gateway

Updates description and policy engine attachment only - gateway names cannot be changed after creation.

```bash
agentcore gateway update-gateway --id gw-abc123 \
    --description "Updated description" \
    --policy-engine-arn arn:aws:bedrock-agentcore:us-east-1:123456789012:policy-engine/pe-abc123 \
    --policy-engine-mode ENFORCE
```

`--policy-engine-mode` accepts `LOG_ONLY` or `ENFORCE`.

---

## SDK Reference

### GatewayClient

```python
from bedrock_agentcore.gateway import GatewayClient

client = GatewayClient(region_name='us-east-1')
```

`GatewayClient` takes `region_name`, not `gateway_id` - it manages gateways and targets by ID/ARN/name per call, it is not scoped to one gateway. Its real surface is:

- **Pass-through boto3 methods** (accept camelCase or snake_case kwargs): `create_gateway`, `get_gateway`, `list_gateways`, `update_gateway`, `delete_gateway`, `create_gateway_target`, `get_gateway_target`, `list_gateway_targets`, `update_gateway_target`, `delete_gateway_target`.
- **`*_and_wait` variants** that block until the resource reaches a terminal state: `create_gateway_and_wait`, `update_gateway_and_wait`, `delete_gateway_and_wait`, `create_gateway_target_and_wait`, `update_gateway_target_and_wait`, `delete_gateway_target_and_wait`.
- **`create_knowledge_base_target(gateway_identifier, knowledge_base_id, name=None, ...)`** and **`create_agentic_retrieve_target(gateway_identifier, retrievers, model_arn, name=None, ...)`** - two purpose-built target constructors.
- **`get_gateway_by_name(name)`** and **`get_gateway_target_by_name(gateway_identifier, name)`** - lookup by name instead of ID.

Any other method name (`list_tools`, `call_tool`, `search_tools`, `create_target`, `create_from_openapi`, `create_from_lambda`, `enable_integration`, `connect_mcp_server`, `index_tools`) raises `AttributeError` - the client does not proxy tool calls, only resource management.

#### Create Gateway

```python
from bedrock_agentcore.gateway import GatewayClient

client = GatewayClient(region_name='us-east-1')

# Waits for the gateway to reach READY (or raises on FAILED)
gateway = client.create_gateway_and_wait(
    name="MyGateway",
    roleArn="arn:aws:iam::123456789012:role/GatewayRole",
    authorizerType="AWS_IAM",
    protocolType="MCP",
    protocolConfiguration={"mcp": {"searchType": "SEMANTIC"}},
)

gateway_id = gateway["gatewayId"]
gateway_arn = gateway["gatewayArn"]
gateway_url = gateway["gatewayUrl"]
```

#### Add Lambda Target

```python
# Add a Lambda function as a tool target
target = client.create_gateway_target_and_wait(
    gatewayIdentifier=gateway_id,
    name="WeatherTool",
    targetConfiguration={
        "mcp": {
            "lambda": {
                "lambdaArn": "arn:aws:lambda:us-east-1:123456789012:function:GetWeather",
                "toolSchema": {
                    "inlinePayload": [
                        {
                            "name": "get_weather",
                            "description": "Get current weather for a location",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "location": {"type": "string", "description": "City name"},
                                },
                                "required": ["location"],
                            },
                        }
                    ]
                },
            }
        }
    },
)
```

#### Add OpenAPI Target

```python
# Add a REST API via an OpenAPI spec staged in S3
target = client.create_gateway_target_and_wait(
    gatewayIdentifier=gateway_id,
    name="StockAPI",
    targetConfiguration={
        "mcp": {
            "openApiSchema": {
                "s3": {"uri": "s3://my-bucket/specs/stock-api.yaml"},
            }
        }
    },
    credentialProviderConfigurations=[
        {
            "credentialProviderType": "API_KEY",
            "credentialProvider": {
                "apiKeyCredentialProvider": {
                    "providerArn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:credential-provider/stock-api-key",
                }
            },
        }
    ],
)
```

#### Add a Knowledge Base Target

```python
# Purpose-built helper - not a generic targetConfiguration call
target = client.create_knowledge_base_target(
    gateway_identifier=gateway_id,
    knowledge_base_id="my-kb-id",
    name="docs-kb",
    description="Product documentation knowledge base",
)
```

#### List and Get Gateways

```python
# Pass-through to boto3 list_gateways/get_gateway
for gw in client.list_gateways(maxResults=50)["items"]:
    print(f"{gw['name']}: {gw['status']}")

gw = client.get_gateway(gatewayIdentifier=gateway_id)
print(gw["status"])  # CREATING, ACTIVE (or READY), FAILED

# Or look it up by name
gw = client.get_gateway_by_name("MyGateway")
```

### Calling Tools via MCP

Gateway has no data-plane boto3 API - agents call its tools by speaking MCP over HTTP against `gateway["gatewayUrl"]`. With Strands, use its built-in `MCPClient` over the `mcp` package's streamable-HTTP transport:

```python
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
    for tool in tools:
        print(tool.tool_name)

    result = mcp_client.call_tool_sync(
        tool_use_id="call-1",
        name="get_weather",
        arguments={"location": "Seattle"},
    )
```

For an `authorizerType='AWS_IAM'` gateway, sign the HTTP request with SigV4 instead of a bearer token (e.g. via `httpx` + `botocore.auth.SigV4Auth`, or `requests-auth-aws-sigv4`) rather than passing an `Authorization: Bearer` header.

Outside Strands, the raw `mcp` client SDK works the same way against any framework:

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
            result = await session.call_tool("get_weather", {"location": "Seattle"})
            return tools, result
```

---

## Using boto3 Directly

```python
import boto3

control_client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
```

#### CreateGateway

```python
response = control_client.create_gateway(
    name='MyGateway',
    description='Production gateway for agent tools',
    roleArn='arn:aws:iam::123456789012:role/GatewayRole',
    authorizerType='CUSTOM_JWT',
    authorizerConfiguration={
        'customJWTAuthorizer': {
            'discoveryUrl': 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_xxxxx/.well-known/openid-configuration',
            'allowedAudience': ['my-app-client-id'],
            'allowedClients': ['my-app-client-id']
        }
    },
    protocolType='MCP',
    protocolConfiguration={
        'mcp': {'searchType': 'SEMANTIC'}  # Enable semantic search
    },
    tags={
        'Environment': 'production'
    }
)

gateway_id = response['gatewayId']
gateway_arn = response['gatewayArn']
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Gateway name (1-48 chars) |
| `roleArn` | string | Yes | IAM execution role ARN |
| `authorizerType` | string | Yes | `AWS_IAM`, `CUSTOM_JWT`, `NONE`, or `AUTHENTICATE_ONLY` |
| `protocolType` | string | No | `MCP` (default) |
| `authorizerConfiguration` | object | Conditional | Required for `CUSTOM_JWT` - key is `customJWTAuthorizer` |
| `protocolConfiguration` | object | No | `{'mcp': {'searchType': 'SEMANTIC', ...}}` to enable semantic search |
| `description` | string | No | Description |
| `tags` | dict | No | Resource tags |

`authorizerType='IAM'` and top-level `searchConfiguration` do not exist - the values are `AWS_IAM` and `protocolConfiguration.mcp.searchType` respectively.

##### CreateGatewayTarget

Target configuration is nested under `targetConfiguration.mcp.<type>` - there is no flat `lambdaTargetConfiguration`/`openApiTargetConfiguration` key, and the Lambda tool schema is a list under `toolSchema.inlinePayload`, not a `{'tools': [...]}` wrapper.

```python
# Lambda target
response = control_client.create_gateway_target(
    gatewayIdentifier='gw-abc123xyz',
    name='CalculatorTool',
    targetConfiguration={
        'mcp': {
            'lambda': {
                'lambdaArn': 'arn:aws:lambda:us-east-1:123456789012:function:Calculator',
                'toolSchema': {
                    'inlinePayload': [
                        {
                            'name': 'calculate',
                            'description': 'Perform mathematical calculations',
                            'inputSchema': {
                                'type': 'object',
                                'properties': {
                                    'expression': {
                                        'type': 'string',
                                        'description': 'Mathematical expression to evaluate'
                                    }
                                },
                                'required': ['expression']
                            }
                        }
                    ]
                }
            }
        }
    }
)

target_id = response['targetId']
```

```python
# OpenAPI target
response = control_client.create_gateway_target(
    gatewayIdentifier='gw-abc123xyz',
    name='CRMTools',
    targetConfiguration={
        'mcp': {
            'openApiSchema': {
                's3': {'uri': 's3://my-specs-bucket/crm-api.yaml'}
            }
        }
    },
    credentialProviderConfigurations=[
        {
            'credentialProviderType': 'OAUTH',
            'credentialProvider': {
                'oauthCredentialProvider': {
                    'providerArn': 'arn:aws:bedrock-agentcore:us-east-1:123456789012:credential-provider/crm-oauth',
                    'scopes': ['api'],
                }
            }
        }
    ]
)
```

`credentialProviderArn` is not a field of the target configuration itself; outbound credentials are attached via the top-level `credentialProviderConfigurations` list, keyed by `credentialProviderType` (`OAUTH`, `API_KEY`, or `IAM`).

##### GetGateway

```python
response = control_client.get_gateway(
    gatewayIdentifier='gw-abc123xyz'
)

status = response['status']  # CREATING, ACTIVE, FAILED
endpoint = response['gatewayUrl']
```

##### ListGateways

```python
response = control_client.list_gateways(
    maxResults=50
)

for gateway in response['items']:
    print(f"{gateway['name']}: {gateway['status']}")
```

##### ListGatewayTargets

```python
response = control_client.list_gateway_targets(
    gatewayIdentifier='gw-abc123xyz'
)

for target in response['items']:
    print(f"Target: {target['name']} ({target['status']})")
```

##### DeleteGateway

```python
control_client.delete_gateway(
    gatewayIdentifier='gw-abc123xyz'
)
```

---

## Target Types

### Lambda Targets

Convert Lambda functions into MCP tools. `toolSchema` accepts inline tool definitions (`inlinePayload`, a list) or an S3-hosted schema (`s3`), not both.

```python
{
    'lambda': {
        'lambdaArn': 'arn:aws:lambda:us-east-1:123456789012:function:MyFunction',
        'toolSchema': {
            'inlinePayload': [
                {
                    'name': 'my_tool',
                    'description': 'What this tool does',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'param1': {'type': 'string'},
                            'param2': {'type': 'integer'}
                        },
                        'required': ['param1']
                    }
                }
            ]
        }
    }
}
```

**Lambda Handler Format:**

```python
def lambda_handler(event, context):
    """MCP tool handler."""
    tool_name = event.get('name')
    arguments = event.get('arguments', {})

    if tool_name == 'my_tool':
        result = process_request(arguments)
        return {
            'content': [
                {'type': 'text', 'text': json.dumps(result)}
            ]
        }

    return {
        'isError': True,
        'content': [{'type': 'text', 'text': f'Unknown tool: {tool_name}'}]
    }
```

### OpenAPI Targets

Convert REST APIs using OpenAPI specifications.

```python
{
    'openApiSchema': {
        's3': {'uri': 's3://my-bucket/api-spec.yaml'}
    }
}
```

Outbound credentials for the target go in the sibling `credentialProviderConfigurations` list on `CreateGatewayTarget`, not inside `openApiSchema` itself.

**OpenAPI Spec Requirements:**
- Valid OpenAPI 3.0+ specification
- Clear operation descriptions
- Well-defined request/response schemas
- `operationId` for each endpoint

### Smithy Targets

Use Smithy models for type-safe API integration.

```python
{
    'smithyModel': {
        's3': {'uri': 's3://my-bucket/model.smithy'}
    }
}
```

### MCP Server Targets

Connect to external MCP servers.

```python
{
    'mcpServer': {
        'endpoint': 'https://mcp.external.com',
        'listingMode': 'AUTOMATIC'
    }
}
```

### API Gateway Targets

Convert an Amazon API Gateway API into MCP tools.

```python
{
    'apiGateway': {
        # See the CreateGatewayTarget API reference for the full shape;
        # not yet exercised in this repo's examples.
    }
}
```

---

## 1-Click Integrations

Gateway ships a **connector** target type backed by an AWS-managed connector catalog (Salesforce, Slack, Jira, and similar SaaS services), instead of a `client.add_integration(...)` SDK call:

```python
response = control_client.create_gateway_target(
    gatewayIdentifier='gw-abc123xyz',
    name='SalesforceConnector',
    targetConfiguration={
        'mcp': {
            'connector': {
                'source': {
                    'connectorId': 'salesforce',  # see the console's connector catalog for valid IDs
                    'version': '1',
                },
            }
        }
    },
    credentialProviderConfigurations=[
        {
            'credentialProviderType': 'OAUTH',
            'credentialProvider': {
                'oauthCredentialProvider': {
                    'providerArn': 'arn:aws:bedrock-agentcore:us-east-1:123456789012:credential-provider/salesforce-oauth',
                    'scopes': ['api'],
                }
            }
        }
    ],
)
```

The set of valid `connectorId` values is AWS's connector catalog, browsable in the console; there is no boto3 `ListConnectors` operation to enumerate them programmatically, so treat any specific connector ID as illustrative rather than guaranteed current.

---

## Authentication

### Inbound Authentication

Verify agent/user identity before tool access. `authorizerType` is one of `AWS_IAM`, `CUSTOM_JWT`, `NONE`, or `AUTHENTICATE_ONLY`.

#### AWS IAM Authentication

```python
# Gateway with IAM auth
gateway = control_client.create_gateway(
    name='MyGateway',
    roleArn=role_arn,
    authorizerType='AWS_IAM',
    protocolType='MCP'
)
```

Requires SigV4 signing on requests.

#### Custom JWT Authentication

```python
# Gateway with JWT auth (Cognito, Okta, etc.)
gateway = control_client.create_gateway(
    name='MyGateway',
    roleArn=role_arn,
    authorizerType='CUSTOM_JWT',
    authorizerConfiguration={
        'customJWTAuthorizer': {
            'discoveryUrl': 'https://your-idp.com/.well-known/openid-configuration',
            'allowedAudience': ['your-client-id'],
            'allowedClients': ['your-client-id']
        }
    },
    protocolType='MCP'
)
```

`allowedAudience` is singular despite taking a list, and the config key is `customJWTAuthorizer` (capital JWT), not `customJwtAuthorizerConfig`.

### Outbound Authentication

Connect to backend services on behalf of users, via credential providers attached to a target's `credentialProviderConfigurations`.

#### OAuth 2.0

```python
# Create OAuth2 credential provider (a dedicated API, not a generic
# create_credential_provider call - see AgentCore Identity)
credential_provider = control_client.create_oauth2_credential_provider(
    name='SalesforceOAuth',
    credentialProviderVendor='SalesforceOauth2',
    oauth2ProviderConfigInput={
        'salesforceOauth2ProviderConfig': {
            'clientId': 'your-client-id',
            'clientSecret': 'your-client-secret',
        }
    }
)

# Reference it from a target
target = control_client.create_gateway_target(
    gatewayIdentifier=gateway_id,
    name='SalesforceTools',
    targetConfiguration={'mcp': {'openApiSchema': {'s3': {'uri': 's3://my-bucket/salesforce.yaml'}}}},
    credentialProviderConfigurations=[
        {
            'credentialProviderType': 'OAUTH',
            'credentialProvider': {
                'oauthCredentialProvider': {
                    'providerArn': credential_provider['credentialProviderArn'],
                    'scopes': ['api'],
                }
            }
        }
    ]
)
```

#### API Key

```python
# Create API key credential provider
credential_provider = control_client.create_api_key_credential_provider(
    name='WeatherAPIKey',
    apiKey='your-api-key',
)
```

See [AgentCore Identity](./04-identity.md) for the full credential-provider surface, including the real `credentialProviderVendor` enum.

---

## Code Examples

### Basic Gateway with Lambda Tool

```python
from bedrock_agentcore.gateway import GatewayClient

gateway_client = GatewayClient(region_name='us-east-1')

gateway = gateway_client.create_gateway_and_wait(
    name="ProductionGateway",
    roleArn=role_arn,
    authorizerType="AWS_IAM",
    protocolConfiguration={"mcp": {"searchType": "SEMANTIC"}},
)

# Add a Lambda target (assumes lambda_arn already deployed - see the Lambda
# handler format above for the function's expected event/response shape)
target = gateway_client.create_gateway_target_and_wait(
    gatewayIdentifier=gateway["gatewayId"],
    name="ProductTools",
    targetConfiguration={
        "mcp": {
            "lambda": {
                "lambdaArn": lambda_arn,
                "toolSchema": {
                    "inlinePayload": [
                        {
                            "name": "get_product",
                            "description": "Retrieve product details by ID",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "product_id": {"type": "string", "description": "Product ID"}
                                },
                                "required": ["product_id"],
                            },
                        }
                    ]
                },
            }
        }
    },
)

print(gateway["gatewayUrl"])
```

### Agent with Gateway Tools (Strands)

```python
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

model = BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0")

mcp_client = MCPClient(
    lambda: streamablehttp_client(
        gateway_url,
        headers={"Authorization": f"Bearer {bearer_token}"},
    )
)

with mcp_client:
    tools = mcp_client.list_tools_sync()

    # Strands' MCPAgentTool objects are usable directly as Strands tools
    agent = Agent(
        model=model,
        tools=tools,
        system_prompt="Use the available tools to help users.",
    )

    response = agent("What's the current weather in Seattle?")
    print(response)
```

### LangGraph with Gateway

```python
import asyncio
from langgraph.graph import StateGraph
from langchain_core.tools import StructuredTool
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def load_gateway_tools(gateway_url: str, bearer_token: str) -> list[StructuredTool]:
    """Fetch Gateway tools over MCP and wrap each as a LangChain tool."""
    async with streamablehttp_client(
        gateway_url, headers={"Authorization": f"Bearer {bearer_token}"}
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listing = await session.list_tools()

            async def call(name: str, **kwargs):
                async with streamablehttp_client(
                    gateway_url, headers={"Authorization": f"Bearer {bearer_token}"}
                ) as (r, w, _):
                    async with ClientSession(r, w) as s:
                        await s.initialize()
                        result = await s.call_tool(name, kwargs)
                        return result.content

            return [
                StructuredTool.from_function(
                    coroutine=lambda name=t.name, **kw: call(name, **kw),
                    name=t.name,
                    description=t.description or "",
                )
                for t in listing.tools
            ]


langchain_tools = asyncio.run(load_gateway_tools(gateway_url, bearer_token))

# Use in LangGraph
graph = StateGraph(AgentState)
# ... build graph with tools ...
```

Reopening a connection per call (as above) is simple but chattier than necessary; a production integration typically keeps one `ClientSession` open for the agent's lifetime instead.

---

## Integration Patterns

### With AgentCore Runtime

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

app = BedrockAgentCoreApp()

@app.entrypoint
async def main(request):
    prompt = request.get("prompt")
    bearer_token = request.get("bearer_token")

    mcp_client = MCPClient(
        lambda: streamablehttp_client(
            gateway_url, headers={"Authorization": f"Bearer {bearer_token}"}
        )
    )

    with mcp_client:
        tools = mcp_client.list_tools_sync()
        agent = Agent(model=model, tools=tools)
        response = agent(prompt)

    return {"response": str(response)}
```

### With AgentCore Identity

```python
from bedrock_agentcore.identity.auth import IdentityClient
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

identity = IdentityClient(region="us-east-1")

def call_tool_with_user_context(agent_identity_token: str, tool_name: str, arguments: dict):
    """Call a Gateway tool using the caller's delegated credentials."""

    # Get the user's OAuth token for a downstream service the tool needs
    token = identity.get_token(
        provider_name="salesforce",
        agent_identity_token=agent_identity_token,
        auth_flow="USER_FEDERATION",
        scopes=["api"],
    )

    mcp_client = MCPClient(
        lambda: streamablehttp_client(
            gateway_url, headers={"Authorization": f"Bearer {token}"}
        )
    )

    with mcp_client:
        return mcp_client.call_tool_sync(
            tool_use_id="call-1", name=tool_name, arguments=arguments
        )
```

---

## Best Practices

1. **Group related tools** - Create one target per logical group of tools (CRM, analytics, etc.).

2. **Enable semantic search** - Helps agents find the right tools when you have many (`protocolConfiguration.mcp.searchType='SEMANTIC'`).

3. **Write clear descriptions** - Tool descriptions are used for semantic search and agent understanding.

4. **Document your APIs** - Good OpenAPI specs produce better MCP tools.

5. **Use credential providers** - Never hardcode credentials; use AgentCore Identity.

6. **Test tools individually** - Verify each tool works before adding to gateway.

7. **Monitor usage** - Use CloudWatch metrics to track tool invocations.

8. **Handle errors gracefully** - Return proper error structures (`isError`, `content`) from Lambda handlers.

9. **Set appropriate timeouts** - Configure Lambda timeouts based on tool complexity.

10. **Version your APIs** - Use different targets for different API versions.

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ResourceNotFoundException` | Invalid gateway ID | Verify gateway exists and is `ACTIVE` |
| `ToolNotFound` (MCP error) | Tool name mismatch | Check tool name matches schema |
| `AccessDeniedException` | Invalid credentials or SigV4 signature | Verify credential provider setup / IAM signing |
| `ValidationException` | Malformed `targetConfiguration` | Check the nested `mcp.<type>` shape matches the API reference |
| Tool execution timeout | Backend too slow | Increase Lambda timeout |

### Debugging Tips

```bash
# Check gateway status
agentcore gateway get-mcp-gateway --id gw-abc123

# List targets
agentcore gateway list-mcp-gateway-targets --id gw-abc123

# Or via boto3
aws bedrock-agentcore-control get-gateway --gateway-identifier gw-abc123
aws bedrock-agentcore-control list-gateway-targets --gateway-identifier gw-abc123

# View Lambda target logs
aws logs tail /aws/lambda/MyToolFunction --follow
```

### Lambda Tool Not Working

1. Check the Lambda function exists and has correct permissions
2. Verify the tool schema (`toolSchema.inlinePayload`) matches the Lambda handler's expectations
3. Check the Lambda execution role can be assumed by Gateway
4. Review CloudWatch logs for Lambda errors

---

## Limits & Quotas

| Resource | Default Limit | Adjustable |
|----------|--------------|------------|
| Gateways per account | 50 | Yes |
| Targets per gateway | 100 | Yes |
| Tools per target | 50 | Yes |
| Total tools per gateway | 1000 | Yes |
| Request payload size | 6 MB | No |
| Response payload size | 6 MB | No |
| Tool execution timeout | 30 seconds | Yes |
| Semantic search results | 100 | No |
| Concurrent invocations | 1000 | Yes |

---

## Pricing

### MCP Operations

| Operation | Rate |
|-----------|------|
| Tool calls (`tools/call`) | Per request |
| Tool listing (`tools/list`) | Per request |

### Semantic Search

| Operation | Rate |
|-----------|------|
| Search queries | Per query |
| Tools indexed | Per tool/month |

### Cost Optimization Tips

1. **Batch tool calls** - Combine related calls when possible.
2. **Cache tool listings** - Tool lists change infrequently.
3. **Right-size targets** - Only expose needed tools.
4. **Monitor search usage** - Semantic search has separate costs.

---

## Related Services

- [AgentCore Runtime](./01-runtime.md) - Deploy agents with tool access
- [AgentCore Identity](./04-identity.md) - Credential management
- [AgentCore Policy](./07-policy.md) - Tool access control
- [AgentCore Observability](./08-observability.md) - Gateway monitoring
