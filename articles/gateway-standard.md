Your agents need tools. Here's how to give them thousands — without writing integration code:

![AgentCore Gateway](images/gateway-article.webp)

Every AI agent eventually needs to do something real — query a database, file a ticket, send a message. That means integrating APIs. For one or two tools, you write custom code. For ten, you build a framework. For hundreds across your enterprise? You need a Babel Fish. In *The Hitchhiker's Guide to the Galaxy*, the Babel Fish is a small, leech-like creature that, when placed in your ear, instantly translates any language in the universe. AgentCore Gateway is the Babel Fish for your agent's tool problem — except instead of translating Vogon poetry (mercifully), it translates APIs.

AgentCore Gateway converts your existing APIs, Lambda functions, and MCP servers into a unified tool layer that any agent can discover and invoke through the **Model Context Protocol (MCP)**. OpenAPI spec in, MCP tools out. Lambda function in, MCP tools out. Like the Babel Fish performing its miraculous universal translation, Gateway handles authentication, protocol translation, and semantic tool discovery — so you focus on agent logic, not plumbing.

## Prerequisites

- AWS account with Bedrock AgentCore access
- Python 3.10+ installed
- boto3 SDK and Strands Agents (`pip install boto3 strands-agents`)
- AWS credentials configured

## Environment Setup

```bash
# Install dependencies
pip install boto3 strands-agents

# Set environment variables
export AWS_REGION=us-east-1
```

## Implementation

### Create a Gateway and Add Tools

```python
import boto3
import json
import time

# Initialize clients
control = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
sts = boto3.client('sts')

account_id = sts.get_caller_identity()['Account']

# Create IAM role for Gateway
iam = boto3.client('iam')
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}
role = iam.create_role(
    RoleName="gateway-demo-role",
    AssumeRolePolicyDocument=json.dumps(trust_policy)
)
time.sleep(10)  # Wait for IAM propagation

# Create gateway with semantic search enabled
gateway = control.create_gateway(
    name="ProductionGateway",
    description="Unified tool gateway for all agent tools",
    roleArn=role['Role']['Arn'],
    authorizerType='AWS_IAM',
    protocolType='MCP',
    protocolConfiguration={'mcp': {'searchType': 'SEMANTIC'}}
)
gateway_id = gateway['gatewayId']
print(f"✓ Gateway created: {gateway_id}")

# Add a Lambda function as an MCP tool
target = control.create_gateway_target(
    gatewayIdentifier=gateway_id,
    name='OrderLookup',
    targetConfiguration={
        'mcp': {
            'lambda': {
                'lambdaArn': f'arn:aws:lambda:us-east-1:{account_id}:function:OrderLookup',
                'toolSchema': {
                    'inlinePayload': [{
                        'name': 'lookup_order',
                        'description': 'Look up order status by order ID',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'order_id': {'type': 'string', 'description': 'Order ID'}
                            },
                            'required': ['order_id']
                        }
                    }]
                }
            }
        }
    }
)
print(f"✓ Lambda target added: {target['targetId']}")
```

### Invoke Tools via MCP Protocol

There is no boto3 "invoke gateway" call -- Gateway is itself an MCP server. Once a target is `READY`, agents talk to it directly over the Model Context Protocol at the gateway's endpoint, using any MCP client:

```python
# Confirm the target is ready, then fetch the gateway's MCP endpoint
targets = control.list_gateway_targets(gatewayIdentifier=gateway_id)
for t in targets['items']:
    print(f"  Target: {t['name']} ({t['status']})")

gw = control.get_gateway(gatewayIdentifier=gateway_id)
print(f"✓ MCP endpoint: {gw['gatewayUrl']}")
```

```python
# Any MCP client can now list and call tools against gatewayUrl.
# With authorizerType='AWS_IAM', requests must be SigV4-signed;
# with 'CUSTOM_JWT', a bearer token is used instead.
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

mcp_client = MCPClient(lambda: streamablehttp_client(gw['gatewayUrl']))
with mcp_client:
    for tool in mcp_client.list_tools_sync():
        print(f"  Tool: {tool.tool_name}")
    result = mcp_client.call_tool_sync(
        tool_use_id="lookup-1", name="lookup_order",
        arguments={"order_id": "ORD-12345"})
    print(f"✓ Tool result: {result}")
```

### Semantic Tool Discovery

Semantic search is a Gateway-side capability you turn on when you create the gateway (`protocolConfiguration={'mcp': {'searchType': 'SEMANTIC'}}`, above) -- there is no separate boto3 search call. With it enabled, the gateway itself ranks tool results by intent when an agent lists tools through MCP, so you do not maintain a static tool list as your target count grows.

## Running the Example

```bash
cd articles/examples/gateway
pip install -r requirements.txt
python main.py
```

Expected output:
```
✓ Gateway created: gw-abc123xyz
✓ Gateway is READY
✓ Gateway working successfully!
```

## Four Ways to Add Tools

| Target Type | Source | Use Case |
|-------------|--------|----------|
| **Lambda** | AWS Lambda functions | Custom business logic, database queries |
| **OpenAPI** | REST API specs | Existing APIs with OpenAPI/Swagger docs |
| **MCP Server** | External MCP servers | Third-party MCP-compatible services |
| **1-Click** | Salesforce, Slack, Jira, GitHub, Zendesk | SaaS integrations with managed OAuth |

## Key Benefits

- **Zero integration code**: Drop in an OpenAPI spec or Lambda ARN — Gateway generates MCP tools automatically
- **Semantic discovery**: Agents find the right tools from thousands using natural language search, reducing prompt size and latency
- **Built-in auth**: Inbound (IAM, JWT, OAuth) and outbound (OAuth, API keys) authentication handled at the gateway layer
- **Scale to thousands**: Up to 1,000 tools per target with 100 targets per gateway, semantic search keeps agents efficient. The Babel Fish merely handled every spoken language in the universe — Gateway handles REST, GraphQL, Lambda, and MCP, which is arguably a more hostile ecosystem.

## Common Patterns

Teams typically start with a single gateway per environment, adding Lambda targets for internal services and OpenAPI targets for external APIs. As tool counts grow, semantic search becomes critical — agents query for relevant tools by intent rather than maintaining static tool lists. For SaaS integrations, 1-click connectors for Salesforce, Slack, and Jira eliminate OAuth implementation entirely.

## Next Steps

Start with a gateway and one Lambda target to validate the flow. Add semantic search when your tool count exceeds what fits comfortably in a single prompt. Use 1-click integrations for SaaS tools instead of building custom connectors. Douglas Adams once wrote that the Babel Fish, by effectively removing all barriers to communication, caused more and bloodier wars than anything else in the history of creation. Fortunately, Gateway just causes fewer integration meetings — which is the opposite of war, and nearly as satisfying.

📚 Documentation: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html
💻 Full runnable example: `articles/examples/gateway/` | [View complete example on GitHub](https://github.com/apresai/agentcore/tree/main/articles/examples/gateway/)
🔧 GitHub samples: https://github.com/awslabs/amazon-bedrock-agentcore-samples/

#AWS #AI #AgentCore #Gateway #MCP #Developers
