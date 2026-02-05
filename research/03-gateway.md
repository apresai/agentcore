# AgentCore Gateway

> Convert APIs, Lambda functions, and services into MCP-compatible tools with unified access, semantic search, and built-in authentication.

## Quick Reference

| CLI Command | Description |
|-------------|-------------|
| `agentcore gateway create-mcp-gateway` | Create new gateway |
| `agentcore gateway create-mcp-gateway-target` | Add target to gateway |
| `agentcore gateway list` | List all gateways |
| `agentcore gateway delete` | Delete gateway |

| SDK Client | Purpose |
|------------|---------|
| `GatewayClient` (AgentCore SDK) | High-level gateway operations |
| `bedrock-agentcore` (data plane) | Call tools, list tools |
| `bedrock-agentcore-control` (control plane) | Manage gateway resources |

| Key API | Description |
|---------|-------------|
| `CreateGateway` | Create gateway resource |
| `CreateGatewayTarget` | Add tool target |
| `ListTools` | List available MCP tools |
| `CallTool` | Invoke MCP tool |
| `Ping` | Health check |

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

Targets define how the gateway routes requests to specific tools:
- **Lambda targets** - AWS Lambda functions
- **OpenAPI targets** - REST APIs with OpenAPI specs
- **Smithy targets** - APIs defined with Smithy models
- **MCP Server targets** - External MCP servers

### Tool Discovery

Gateway supports intelligent tool discovery:
- **ListTools** - Enumerate all available tools
- **Semantic search** - Find tools by natural language description
- Agents dynamically select appropriate tools based on context

### Authentication

Gateway handles dual-sided security:
- **Inbound auth** - Verify agent/user identity (OAuth, JWT, IAM)
- **Outbound auth** - Connect to backend services (OAuth, API keys)

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
| `--name` | Gateway name | Required |
| `--region` | AWS region | us-east-1 |
| `--enable-semantic-search` | Enable semantic tool discovery | false |
| `--role-arn` | Custom IAM role ARN | auto-created |
| `--authorizer-type` | Auth type (IAM, CUSTOM_JWT, NONE) | IAM |

**Examples:**

```bash
# Basic gateway with IAM auth
agentcore gateway create-mcp-gateway --name MyGateway --region us-east-1

# With semantic search
agentcore gateway create-mcp-gateway \
    --name MyGateway \
    --region us-east-1 \
    --enable-semantic-search

# With custom role
agentcore gateway create-mcp-gateway \
    --name MyGateway \
    --role-arn arn:aws:iam::123456789012:role/MyGatewayRole
```

### agentcore gateway create-mcp-gateway-target

Add a target to an existing gateway.

```bash
agentcore gateway create-mcp-gateway-target [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--gateway-id` | Gateway ID | Required |
| `--name` | Target name | Required |
| `--type` | Target type (lambda, openapi, smithy, mcp) | Required |
| `--lambda-arn` | Lambda function ARN | For lambda type |
| `--openapi-spec` | Path to OpenAPI spec | For openapi type |
| `--endpoint-url` | API endpoint URL | For openapi/mcp type |

**Examples:**

```bash
# Lambda target
agentcore gateway create-mcp-gateway-target \
    --gateway-id gw-abc123 \
    --name WeatherTool \
    --type lambda \
    --lambda-arn arn:aws:lambda:us-east-1:123456789012:function:GetWeather

# OpenAPI target
agentcore gateway create-mcp-gateway-target \
    --gateway-id gw-abc123 \
    --name StockAPI \
    --type openapi \
    --openapi-spec ./openapi.yaml \
    --endpoint-url https://api.example.com

# External MCP server
agentcore gateway create-mcp-gateway-target \
    --gateway-id gw-abc123 \
    --name ExternalMCP \
    --type mcp \
    --endpoint-url https://mcp.example.com
```

### agentcore gateway list

List all gateways.

```bash
agentcore gateway list

# Output
NAME          STATUS    TARGETS    SEMANTIC_SEARCH
MyGateway     ACTIVE    3          enabled
TestGateway   ACTIVE    1          disabled
```

### agentcore gateway delete

Delete a gateway.

```bash
agentcore gateway delete --gateway-id gw-abc123 --force
```

---

## SDK Reference

### Using AgentCore SDK (Recommended)

```python
from bedrock_agentcore.gateway import GatewayClient

client = GatewayClient(region_name='us-east-1')
```

#### Create Gateway

```python
from bedrock_agentcore.gateway import GatewayClient

client = GatewayClient(region_name='us-east-1')

# Create basic gateway
gateway = client.create_gateway(
    name="MyGateway",
    authorizer_type="IAM",
    enable_semantic_search=True
)

gateway_id = gateway["gatewayId"]
gateway_arn = gateway["gatewayArn"]
```

#### Add Lambda Target

```python
# Add Lambda function as tool
target = client.create_target(
    gateway_id=gateway_id,
    name="WeatherTool",
    target_type="lambda",
    lambda_config={
        "functionArn": "arn:aws:lambda:us-east-1:123456789012:function:GetWeather",
        "toolSchema": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                    "units": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    }
)
```

#### Add OpenAPI Target

```python
# Add REST API via OpenAPI spec
target = client.create_target(
    gateway_id=gateway_id,
    name="StockAPI",
    target_type="openapi",
    openapi_config={
        "specificationS3Location": {
            "bucket": "my-bucket",
            "key": "specs/stock-api.yaml"
        },
        "endpointUrl": "https://api.stocks.example.com",
        "authConfig": {
            "type": "API_KEY",
            "credentialProviderArn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:credential-provider/stock-api-key"
        }
    }
)
```

#### List Tools

```python
# Get all available tools from gateway
tools = client.list_tools(gateway_id=gateway_id)

for tool in tools:
    print(f"Tool: {tool['name']}")
    print(f"Description: {tool['description']}")
    print(f"Input schema: {tool['inputSchema']}")
```

#### Call Tool

```python
# Invoke a tool through the gateway
result = client.call_tool(
    gateway_id=gateway_id,
    tool_name="get_weather",
    arguments={"location": "Seattle", "units": "fahrenheit"}
)

print(f"Result: {result['content']}")
```

#### Semantic Search for Tools

```python
# Find tools by natural language query
tools = client.search_tools(
    gateway_id=gateway_id,
    query="How can I get stock prices?",
    max_results=5
)

for tool in tools:
    print(f"Tool: {tool['name']} (score: {tool['score']})")
```

### Using boto3 Directly

```python
import boto3

# Control plane
control_client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

# Data plane
data_client = boto3.client('bedrock-agentcore', region_name='us-east-1')
```

#### Control Plane APIs

##### CreateGateway

```python
response = control_client.create_gateway(
    name='MyGateway',
    description='Production gateway for agent tools',
    roleArn='arn:aws:iam::123456789012:role/GatewayRole',
    authorizerType='CUSTOM_JWT',
    authorizerConfiguration={
        'customJwtAuthorizerConfig': {
            'discoveryUrl': 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_xxxxx/.well-known/openid-configuration',
            'allowedAudiences': ['my-app-client-id'],
            'allowedClients': ['my-app-client-id']
        }
    },
    protocolType='MCP',
    searchConfiguration={
        'searchType': 'SEMANTIC'  # Enable semantic search
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
| `authorizerType` | string | Yes | IAM, CUSTOM_JWT, or NONE |
| `protocolType` | string | Yes | MCP (default) |
| `authorizerConfiguration` | object | Conditional | Required for CUSTOM_JWT |
| `searchConfiguration` | object | No | Enable semantic search |
| `description` | string | No | Description |
| `tags` | dict | No | Resource tags |

##### CreateGatewayTarget

```python
# Lambda target
response = control_client.create_gateway_target(
    gatewayId='gw-abc123xyz',
    name='CalculatorTool',
    targetConfiguration={
        'lambdaTargetConfiguration': {
            'lambdaArn': 'arn:aws:lambda:us-east-1:123456789012:function:Calculator',
            'toolSchema': {
                'tools': [
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
)

target_id = response['targetId']
```

```python
# OpenAPI target
response = control_client.create_gateway_target(
    gatewayId='gw-abc123xyz',
    name='CRMTools',
    targetConfiguration={
        'openApiTargetConfiguration': {
            'openApiSpecificationS3Location': {
                'bucket': 'my-specs-bucket',
                'key': 'crm-api.yaml'
            },
            'endpointConfiguration': {
                'url': 'https://crm.example.com/api/v1'
            },
            'credentialProviderArn': 'arn:aws:bedrock-agentcore:us-east-1:123456789012:credential-provider/crm-oauth'
        }
    }
)
```

##### GetGateway

```python
response = control_client.get_gateway(
    gatewayId='gw-abc123xyz'
)

status = response['status']  # CREATING, ACTIVE, FAILED
endpoint = response['gatewayEndpoint']
```

##### ListGateways

```python
response = control_client.list_gateways(
    maxResults=50
)

for gateway in response['gatewaySummaries']:
    print(f"{gateway['name']}: {gateway['status']}")
```

##### ListGatewayTargets

```python
response = control_client.list_gateway_targets(
    gatewayId='gw-abc123xyz'
)

for target in response['targetSummaries']:
    print(f"Target: {target['name']} ({target['targetType']})")
```

##### DeleteGateway

```python
control_client.delete_gateway(
    gatewayId='gw-abc123xyz'
)
```

#### Data Plane APIs

##### ListTools (MCP)

```python
import json

# List all tools via MCP protocol
response = data_client.invoke_gateway(
    gatewayId='gw-abc123xyz',
    method='tools/list',
    payload=json.dumps({}).encode()
)

result = json.loads(response['payload'].read())
for tool in result['tools']:
    print(f"Tool: {tool['name']}")
```

##### CallTool (MCP)

```python
# Call a tool via MCP protocol
response = data_client.invoke_gateway(
    gatewayId='gw-abc123xyz',
    method='tools/call',
    payload=json.dumps({
        'name': 'get_weather',
        'arguments': {
            'location': 'Seattle',
            'units': 'celsius'
        }
    }).encode()
)

result = json.loads(response['payload'].read())
print(f"Result: {result['content']}")
```

##### Semantic Search

```python
# Search for tools by description
response = data_client.search_gateway_tools(
    gatewayId='gw-abc123xyz',
    query='find stock prices and financial data',
    maxResults=10
)

for tool in response['tools']:
    print(f"{tool['name']}: {tool['description']} (score: {tool['relevanceScore']})")
```

---

## Target Types

### Lambda Targets

Convert Lambda functions into MCP tools.

```python
{
    'lambdaTargetConfiguration': {
        'lambdaArn': 'arn:aws:lambda:us-east-1:123456789012:function:MyFunction',
        'toolSchema': {
            'tools': [
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
    'openApiTargetConfiguration': {
        'openApiSpecificationS3Location': {
            'bucket': 'my-bucket',
            'key': 'api-spec.yaml'
        },
        'endpointConfiguration': {
            'url': 'https://api.example.com'
        },
        'credentialProviderArn': 'arn:aws:bedrock-agentcore:...:credential-provider/my-creds'
    }
}
```

**OpenAPI Spec Requirements:**
- Valid OpenAPI 3.0+ specification
- Clear operation descriptions
- Well-defined request/response schemas
- operationId for each endpoint

### Smithy Targets

Use Smithy models for type-safe API integration.

```python
{
    'smithyTargetConfiguration': {
        'smithyModelS3Location': {
            'bucket': 'my-bucket',
            'key': 'model.smithy'
        },
        'endpointConfiguration': {
            'url': 'https://api.example.com'
        }
    }
}
```

### MCP Server Targets

Connect to external MCP servers.

```python
{
    'mcpServerTargetConfiguration': {
        'mcpServerUrl': 'https://mcp.external.com',
        'transportType': 'HTTP_SSE',
        'authConfiguration': {
            'type': 'BEARER_TOKEN',
            'credentialProviderArn': 'arn:aws:bedrock-agentcore:...:credential-provider/mcp-token'
        }
    }
}
```

---

## 1-Click Integrations

Pre-built integrations for popular services:

| Service | Description |
|---------|-------------|
| **Salesforce** | CRM operations, leads, opportunities |
| **Slack** | Messaging, channels, users |
| **Jira** | Issue tracking, projects |
| **Asana** | Task management, projects |
| **Zendesk** | Support tickets, customers |
| **GitHub** | Repositories, issues, PRs |
| **Google Workspace** | Drive, Calendar, Gmail |

### Enable Integration

```python
from bedrock_agentcore.gateway import GatewayClient

client = GatewayClient()

# Add Salesforce integration
target = client.add_integration(
    gateway_id=gateway_id,
    integration="salesforce",
    credential_provider_arn="arn:aws:bedrock-agentcore:...:credential-provider/salesforce-oauth"
)
```

---

## Authentication

### Inbound Authentication

Verify agent/user identity before tool access.

#### IAM Authentication

```python
# Gateway with IAM auth (default)
gateway = control_client.create_gateway(
    name='MyGateway',
    roleArn=role_arn,
    authorizerType='IAM',
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
        'customJwtAuthorizerConfig': {
            'discoveryUrl': 'https://your-idp.com/.well-known/openid-configuration',
            'allowedAudiences': ['your-client-id'],
            'allowedClients': ['your-client-id'],
            'allowedScopes': ['tools:read', 'tools:write']
        }
    },
    protocolType='MCP'
)
```

### Outbound Authentication

Connect to backend services on behalf of users.

#### OAuth 2.0

```python
# Create OAuth credential provider
credential_provider = control_client.create_credential_provider(
    name='SalesforceOAuth',
    credentialProviderVendor='SalesforceOauth2',
    oauth2ProviderConfigInput={
        'clientId': 'your-client-id',
        'clientSecret': 'your-client-secret',
        'authorizationUrl': 'https://login.salesforce.com/services/oauth2/authorize',
        'tokenUrl': 'https://login.salesforce.com/services/oauth2/token',
        'scopes': ['api', 'refresh_token']
    }
)

# Use in target
target = control_client.create_gateway_target(
    gatewayId=gateway_id,
    name='SalesforceTools',
    targetConfiguration={
        'openApiTargetConfiguration': {
            # ...
            'credentialProviderArn': credential_provider['credentialProviderArn']
        }
    }
)
```

#### API Key

```python
# Create API key credential provider
credential_provider = control_client.create_credential_provider(
    name='WeatherAPIKey',
    credentialProviderVendor='ApiKey',
    apiKeyProviderConfigInput={
        'apiKey': 'your-api-key',
        'headerName': 'X-API-Key'  # or 'Authorization'
    }
)
```

---

## Code Examples

### Basic Gateway with Lambda Tool

```python
from bedrock_agentcore.gateway import GatewayClient
import boto3

# Create gateway
gateway_client = GatewayClient(region_name='us-east-1')

gateway = gateway_client.create_gateway(
    name="ProductionGateway",
    authorizer_type="IAM",
    enable_semantic_search=True
)

# Create Lambda function for tool
lambda_code = '''
import json

def handler(event, context):
    tool_name = event.get('name')
    args = event.get('arguments', {})

    if tool_name == 'get_product':
        product_id = args.get('product_id')
        # Fetch product from database
        product = {"id": product_id, "name": "Widget", "price": 29.99}
        return {
            "content": [{"type": "text", "text": json.dumps(product)}]
        }

    return {"isError": True, "content": [{"type": "text", "text": "Unknown tool"}]}
'''

# Add Lambda target
target = gateway_client.create_target(
    gateway_id=gateway["gatewayId"],
    name="ProductTools",
    target_type="lambda",
    lambda_config={
        "functionArn": lambda_arn,
        "toolSchema": {
            "tools": [{
                "name": "get_product",
                "description": "Retrieve product details by ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string", "description": "Product ID"}
                    },
                    "required": ["product_id"]
                }
            }]
        }
    }
)

# Use the gateway
result = gateway_client.call_tool(
    gateway_id=gateway["gatewayId"],
    tool_name="get_product",
    arguments={"product_id": "PROD-123"}
)

print(result)
```

### Agent with Gateway Tools

```python
from strands import Agent
from strands.models import BedrockModel
from strands.tools import tool
from bedrock_agentcore.gateway import GatewayClient

# Initialize
model = BedrockModel(model_id="anthropic.claude-sonnet-4-20250514")
gateway = GatewayClient(gateway_id="gw-abc123xyz")

# Get tools from gateway
gateway_tools = gateway.list_tools()

# Create dynamic tool wrapper
@tool
def gateway_tool(tool_name: str, arguments: dict) -> str:
    """Execute a tool from the gateway.

    Args:
        tool_name: Name of the tool to execute
        arguments: Arguments to pass to the tool
    """
    result = gateway.call_tool(tool_name=tool_name, arguments=arguments)
    return result["content"]

# Create agent with gateway tools
agent = Agent(
    model=model,
    tools=[gateway_tool],
    system_prompt=f"""You have access to these tools via the gateway:
{chr(10).join([f"- {t['name']}: {t['description']}" for t in gateway_tools])}

Use gateway_tool() to call any of these tools."""
)

# Use agent
response = agent("What's the current weather in Seattle?")
print(response)
```

### LangGraph with Gateway

```python
from langgraph.graph import StateGraph
from langchain_core.tools import StructuredTool
from bedrock_agentcore.gateway import GatewayClient

gateway = GatewayClient(gateway_id="gw-abc123xyz")

# Convert gateway tools to LangChain tools
def create_langchain_tools():
    tools = []
    for gateway_tool in gateway.list_tools():
        def make_tool_func(name):
            def tool_func(**kwargs):
                return gateway.call_tool(tool_name=name, arguments=kwargs)
            return tool_func

        tool = StructuredTool.from_function(
            func=make_tool_func(gateway_tool["name"]),
            name=gateway_tool["name"],
            description=gateway_tool["description"]
        )
        tools.append(tool)
    return tools

langchain_tools = create_langchain_tools()

# Use in LangGraph
graph = StateGraph(AgentState)
# ... build graph with tools ...
```

### Multi-Gateway Setup

```python
from bedrock_agentcore.gateway import GatewayClient

# Create specialized gateways
crm_gateway = GatewayClient(gateway_id="gw-crm")
analytics_gateway = GatewayClient(gateway_id="gw-analytics")
internal_gateway = GatewayClient(gateway_id="gw-internal")

class MultiGatewayRouter:
    """Route tool calls to appropriate gateway."""

    def __init__(self):
        self.gateways = {
            "crm": crm_gateway,
            "analytics": analytics_gateway,
            "internal": internal_gateway
        }
        self.tool_mapping = self._build_mapping()

    def _build_mapping(self):
        mapping = {}
        for category, gateway in self.gateways.items():
            for tool in gateway.list_tools():
                mapping[tool["name"]] = category
        return mapping

    def call_tool(self, tool_name: str, arguments: dict):
        category = self.tool_mapping.get(tool_name)
        if not category:
            raise ValueError(f"Unknown tool: {tool_name}")

        gateway = self.gateways[category]
        return gateway.call_tool(tool_name=tool_name, arguments=arguments)

router = MultiGatewayRouter()
result = router.call_tool("get_customer", {"customer_id": "123"})
```

### Gateway with Policy Engine

```python
from bedrock_agentcore.gateway import GatewayClient
import boto3

control = boto3.client('bedrock-agentcore-control')

# Create gateway with policy engine
gateway = control.create_gateway(
    name='SecureGateway',
    roleArn=role_arn,
    authorizerType='CUSTOM_JWT',
    authorizerConfiguration={...},
    protocolType='MCP',
    policyEngineConfiguration={
        'policyEngineArn': 'arn:aws:bedrock-agentcore:us-east-1:123456789012:policy-engine/pe-abc123',
        'enforcementMode': 'ENFORCE'  # or 'LOG_ONLY'
    }
)
```

---

## Integration Patterns

### With AgentCore Runtime

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.gateway import GatewayClient

gateway = GatewayClient(gateway_id="gw-abc123xyz")
app = BedrockAgentCoreApp()

@app.entrypoint()
async def main(request):
    prompt = request.get("prompt")

    # Get relevant tools
    tools = gateway.search_tools(query=prompt, max_results=5)

    # Agent decides which tools to use
    tool_calls = agent.plan_tool_calls(prompt, tools)

    # Execute tools
    results = []
    for call in tool_calls:
        result = gateway.call_tool(
            tool_name=call["name"],
            arguments=call["arguments"]
        )
        results.append(result)

    # Generate response with tool results
    response = agent.generate(prompt, tool_results=results)

    return {"response": response}
```

### With AgentCore Identity

```python
from bedrock_agentcore.gateway import GatewayClient
from bedrock_agentcore.identity import IdentityClient

identity = IdentityClient()
gateway = GatewayClient(gateway_id="gw-abc123xyz")

def call_tool_with_user_context(user_id: str, tool_name: str, arguments: dict):
    """Call tool with user's credentials."""

    # Get user's OAuth token
    token = identity.get_resource_token(
        user_id=user_id,
        credential_provider_arn="arn:aws:bedrock-agentcore:...:credential-provider/salesforce"
    )

    # Call tool with token
    result = gateway.call_tool(
        tool_name=tool_name,
        arguments=arguments,
        bearer_token=token["accessToken"]
    )

    return result
```

---

## Best Practices

1. **Group related tools** - Create one target per logical group of tools (CRM, analytics, etc.).

2. **Enable semantic search** - Helps agents find the right tools when you have many.

3. **Write clear descriptions** - Tool descriptions are used for semantic search and agent understanding.

4. **Document your APIs** - Good OpenAPI specs produce better MCP tools.

5. **Use credential providers** - Never hardcode credentials; use AgentCore Identity.

6. **Test tools individually** - Verify each tool works before adding to gateway.

7. **Monitor usage** - Use CloudWatch metrics to track tool invocations.

8. **Handle errors gracefully** - Return proper error structures from Lambda handlers.

9. **Set appropriate timeouts** - Configure Lambda timeouts based on tool complexity.

10. **Version your APIs** - Use different targets for different API versions.

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `GatewayNotFound` | Invalid gateway ID | Verify gateway exists and is ACTIVE |
| `ToolNotFound` | Tool name mismatch | Check tool name matches schema |
| `AuthorizationError` | Invalid credentials | Verify credential provider setup |
| `TargetError` | Backend service error | Check Lambda logs or API health |
| `SchemaValidation` | Invalid arguments | Verify arguments match input schema |
| `Timeout` | Tool execution too slow | Increase Lambda timeout |

### Debugging Tips

```bash
# Check gateway status
aws bedrock-agentcore-control get-gateway --gateway-id gw-abc123

# List targets
aws bedrock-agentcore-control list-gateway-targets --gateway-id gw-abc123

# View Lambda logs
aws logs tail /aws/lambda/MyToolFunction --follow

# Test tool directly
agentcore gateway test-tool \
    --gateway-id gw-abc123 \
    --tool-name get_weather \
    --arguments '{"location": "Seattle"}'
```

### Lambda Tool Not Working

1. Check Lambda function exists and has correct permissions
2. Verify tool schema matches Lambda handler expectations
3. Check Lambda execution role can be assumed by Gateway
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
| ListTools | Per request |
| CallTool | Per request |
| Ping | Per request |

### Semantic Search

| Operation | Rate |
|-----------|------|
| Search queries | Per query |
| Tools indexed | Per tool/month |

### Cost Optimization Tips

1. **Batch tool calls** - Combine related calls when possible.
2. **Cache ListTools** - Tool lists change infrequently.
3. **Right-size targets** - Only expose needed tools.
4. **Monitor search usage** - Semantic search has separate costs.

---

## Related Services

- [AgentCore Runtime](./01-runtime.md) - Deploy agents with tool access
- [AgentCore Identity](./04-identity.md) - Credential management
- [AgentCore Policy](./07-policy.md) - Tool access control
- [AgentCore Observability](./08-observability.md) - Gateway monitoring
