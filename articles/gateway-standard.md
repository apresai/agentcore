Your agents need tools. Here's how to give them thousands — without writing integration code:

![AgentCore Gateway](images/gateway-article.webp)

Every AI agent eventually needs to do something real — query a database, file a ticket, send a message. That means integrating APIs. For one or two tools, you write custom code. For ten, you build a framework. For hundreds across your enterprise? You need a Babel Fish. In *The Hitchhiker's Guide to the Galaxy*, the Babel Fish is a small, leech-like creature that, when placed in your ear, instantly translates any language in the universe. AgentCore Gateway is the Babel Fish for your agent's tool problem — except instead of translating Vogon poetry (mercifully), it translates APIs.

AgentCore Gateway converts your existing APIs, Lambda functions, and MCP servers into a unified tool layer that any agent can discover and invoke through the **Model Context Protocol (MCP)**. OpenAPI spec in, MCP tools out. Lambda function in, MCP tools out. Like the Babel Fish performing its miraculous universal translation, Gateway handles authentication, protocol translation, and semantic tool discovery — so you focus on agent logic, not plumbing.

## Prerequisites

- AWS account with Bedrock AgentCore access
- Python 3.10+ installed
- boto3 SDK (`pip install boto3`)
- AWS credentials configured

## Environment Setup

```bash
# Install dependencies
pip install boto3 python-dotenv

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
data = boto3.client('bedrock-agentcore', region_name='us-east-1')
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
    authorizerType='IAM',
    protocolType='MCP',
    searchConfiguration={'searchType': 'SEMANTIC'}
)
gateway_id = gateway['gatewayId']
print(f"✓ Gateway created: {gateway_id}")

# Add a Lambda function as an MCP tool
target = control.create_gateway_target(
    gatewayIdentifier=gateway_id,
    name='OrderLookup',
    targetConfiguration={
        'lambdaTargetConfiguration': {
            'lambdaArn': f'arn:aws:lambda:us-east-1:{account_id}:function:OrderLookup',
            'toolSchema': {
                'tools': [{
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
)
print(f"✓ Lambda target added: {target['targetId']}")
```

### Invoke Tools via MCP Protocol

```python
# List all available tools
response = data.invoke_gateway(
    gatewayIdentifier=gateway_id,
    method='tools/list',
    payload=json.dumps({}).encode()
)
tools = json.loads(response['payload'].read())
for tool in tools.get('tools', []):
    print(f"  Tool: {tool['name']} - {tool['description']}")

# Call a tool through the gateway
result = data.invoke_gateway(
    gatewayIdentifier=gateway_id,
    method='tools/call',
    payload=json.dumps({
        'name': 'lookup_order',
        'arguments': {'order_id': 'ORD-12345'}
    }).encode()
)
print(f"✓ Tool result: {json.loads(result['payload'].read())}")
```

### Semantic Tool Discovery

```python
# When you have hundreds of tools, let agents search by intent
results = data.search_gateway_tools(
    gatewayIdentifier=gateway_id,
    query='find customer order information',
    maxResults=5
)

for tool in results.get('tools', []):
    print(f"  {tool['name']}: {tool['description']} (score: {tool['relevanceScore']})")
```

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
- **Scale to thousands**: Up to 1,000 tools per gateway with 100 targets, semantic search keeps agents efficient. The Babel Fish merely handled every spoken language in the universe — Gateway handles REST, GraphQL, Lambda, and MCP, which is arguably a more hostile ecosystem.

## Common Patterns

Teams typically start with a single gateway per environment, adding Lambda targets for internal services and OpenAPI targets for external APIs. As tool counts grow, semantic search becomes critical — agents query for relevant tools by intent rather than maintaining static tool lists. For SaaS integrations, 1-click connectors for Salesforce, Slack, and Jira eliminate OAuth implementation entirely.

## Next Steps

Start with a gateway and one Lambda target to validate the flow. Add semantic search when your tool count exceeds what fits comfortably in a single prompt. Use 1-click integrations for SaaS tools instead of building custom connectors. Douglas Adams once wrote that the Babel Fish, by effectively removing all barriers to communication, caused more and bloodier wars than anything else in the history of creation. Fortunately, Gateway just causes fewer integration meetings — which is the opposite of war, and nearly as satisfying.

📚 Documentation: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html
💻 Full runnable example: `articles/examples/gateway/`
🔧 GitHub samples: https://github.com/awslabs/amazon-bedrock-agentcore-samples/

#AWS #AI #AgentCore #Gateway #MCP #Developers
