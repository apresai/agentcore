# Building a Customer Support Agent with AgentCore

![AgentCore Customer Support](images/memory-article.webp)

## The Problem

Your support team handles 500 tickets a day. Every interaction starts cold — the agent doesn't know that this customer called three times last week about the same billing issue, prefers email communication, and has a premium account. The customer repeats themselves. The agent asks redundant questions. Resolution time balloons.

Building a production support agent requires solving four problems simultaneously: context persistence across sessions, secure access to CRM and ticketing tools, real-time quality monitoring, and deterministic guardrails to prevent the agent from doing things like issuing unauthorized refunds. Most teams attempt this with a single framework and end up with a brittle monolith.

This tutorial builds a customer support agent using four AgentCore services working together: **Memory** for customer context, **Gateway** for CRM tool integration, **Observability** for monitoring, and **Runtime** for deployment.

## Prerequisites

### AWS Account Setup

- AWS account with Bedrock AgentCore access enabled
- IAM permissions: `bedrock-agentcore:*`, `bedrock:InvokeModel`
- Region: us-east-1

### Local Environment

- Python 3.10+
- pip for package management

### Required Packages

```bash
# requirements.txt
boto3>=1.34.0
strands-agents>=0.1.0
bedrock-agentcore-sdk>=1.0.0
python-dotenv>=1.0.0
```

## Getting Started

### Step 1: Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Configure Credentials

```python
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
control = boto3.client('bedrock-agentcore-control', region_name=REGION)
data = boto3.client('bedrock-agentcore', region_name=REGION)
```

### Step 3: Create Memory for Customer Context

The support agent needs two types of memory: short-term for the current conversation and long-term for customer preferences and history.

```python
from datetime import datetime, timezone

# Create memory with preference extraction
memory_response = control.create_memory(
    name="CustomerSupportMemory",
    description="Stores customer interactions and preferences",
    eventExpiryDuration=30,  # Keep events for 30 days
    memoryStrategies=[
        {
            'userPreferenceMemoryStrategy': {
                'name': 'CustomerPreferences',
                'namespaces': ['preferences', 'issues']
            }
        },
        {
            'semanticMemoryStrategy': {
                'name': 'InteractionHistory',
                'namespaces': ['history'],
                'description': 'Stores summaries of past support interactions'
            }
        }
    ]
)
memory_id = memory_response['memory']['id']
print(f"✓ Memory created: {memory_id}")
```

### Step 4: Set Up Gateway for CRM Tools

Connect your CRM and ticketing systems through Gateway so the agent can look up customers, check order status, and create tickets.

```python
import json
import time

iam = boto3.client('iam')
sts = boto3.client('sts')
account_id = sts.get_caller_identity()['Account']

# Create IAM role for Gateway
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}
role = iam.create_role(
    RoleName="support-agent-gateway-role",
    AssumeRolePolicyDocument=json.dumps(trust_policy)
)
time.sleep(10)

# Create gateway
gateway = control.create_gateway(
    name="SupportAgentGateway",
    description="CRM and ticketing tools for support agent",
    roleArn=role['Role']['Arn'],
    authorizerType='IAM',
    protocolType='MCP',
    searchConfiguration={'searchType': 'SEMANTIC'}
)
gateway_id = gateway['gatewayId']
print(f"✓ Gateway created: {gateway_id}")

# Wait for gateway to be active
for _ in range(60):
    status = control.get_gateway(gatewayIdentifier=gateway_id)['status']
    if status in ('ACTIVE', 'READY'):
        break
    time.sleep(2)
print(f"✓ Gateway is {status}")
```

### Step 5: Add CRM Tools to Gateway

```python
# Add customer lookup tool (Lambda target)
control.create_gateway_target(
    gatewayIdentifier=gateway_id,
    name='CustomerTools',
    targetConfiguration={
        'lambdaTargetConfiguration': {
            'lambdaArn': f'arn:aws:lambda:us-east-1:{account_id}:function:CustomerLookup',
            'toolSchema': {
                'tools': [
                    {
                        'name': 'lookup_customer',
                        'description': 'Look up customer by email or account ID',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'email': {'type': 'string', 'description': 'Customer email'},
                                'account_id': {'type': 'string', 'description': 'Account ID'}
                            }
                        }
                    },
                    {
                        'name': 'get_order_status',
                        'description': 'Get status of a customer order',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'order_id': {'type': 'string', 'description': 'Order ID'}
                            },
                            'required': ['order_id']
                        }
                    },
                    {
                        'name': 'create_support_ticket',
                        'description': 'Create a new support ticket for the customer',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'customer_id': {'type': 'string'},
                                'subject': {'type': 'string'},
                                'description': {'type': 'string'},
                                'priority': {'type': 'string', 'enum': ['low', 'medium', 'high']}
                            },
                            'required': ['customer_id', 'subject', 'description']
                        }
                    }
                ]
            }
        }
    }
)
print("✓ Customer tools added to gateway")
```

### Step 6: Build the Agent

```python
from strands import Agent, tool
from strands.models import BedrockModel

# Create tools that use Memory and Gateway
@tool
def remember_customer(customer_id: str, session_id: str, query: str) -> str:
    """Retrieve what we know about this customer from past interactions.

    Args:
        customer_id: The customer's account ID
        session_id: Current session ID
        query: What to search for in memory
    """
    # Search long-term memories
    records = data.retrieve_memory_records(
        memoryId=memory_id,
        namespace="preferences",
        searchCriteria={'searchQuery': query, 'topK': 5}
    )

    memories = []
    for record in records.get('memoryRecords', []):
        memories.append(record['content']['text'])

    if memories:
        return "Known about this customer:\n" + "\n".join(f"- {m}" for m in memories)
    return "No prior history found for this customer."

@tool
def store_interaction(customer_id: str, session_id: str, summary: str) -> str:
    """Store a summary of this interaction for future reference.

    Args:
        customer_id: The customer's account ID
        session_id: Current session ID
        summary: Summary of the interaction
    """
    data.create_event(
        memoryId=memory_id,
        actorId=customer_id,
        sessionId=session_id,
        eventTimestamp=datetime.now(timezone.utc),
        payload=[
            {'conversational': {'role': 'ASSISTANT', 'content': {'text': summary}}}
        ]
    )
    return f"✓ Interaction stored for customer {customer_id}"

@tool
def call_crm_tool(tool_name: str, arguments: dict) -> str:
    """Call a CRM tool through the Gateway.

    Args:
        tool_name: Name of the CRM tool (lookup_customer, get_order_status, create_support_ticket)
        arguments: Arguments for the tool
    """
    response = data.invoke_gateway(
        gatewayIdentifier=gateway_id,
        method='tools/call',
        payload=json.dumps({
            'name': tool_name,
            'arguments': arguments
        }).encode()
    )
    return json.loads(response['payload'].read())

# Initialize the agent
model = BedrockModel(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    region_name=REGION
)

support_agent = Agent(
    model=model,
    tools=[remember_customer, store_interaction, call_crm_tool],
    system_prompt="""You are a customer support agent. Follow these rules:
1. Always check customer memory first to personalize the interaction
2. Use CRM tools to look up accounts, orders, and create tickets
3. Store important details about each interaction for future reference
4. Be empathetic but efficient
5. Never process refunds over $500 without noting it requires manager approval
6. Always confirm actions before executing them"""
)
```

### Step 7: Deploy to Runtime

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint()
async def handle_request(request):
    customer_id = request.get("customer_id", "unknown")
    session_id = request.get("session_id", "default")
    prompt = request.get("prompt", "")

    # Enrich prompt with customer context
    context_prompt = f"[Customer ID: {customer_id}, Session: {session_id}]\n{prompt}"

    response = support_agent(context_prompt)
    return {"response": str(response)}

if __name__ == "__main__":
    app.run()
```

Deploy with the CLI:

```bash
agentcore deploy --name customer-support-agent --memory 1024 --timeout 3600
```

### Step 8: Run It

```bash
# Deploy
agentcore deploy

# Invoke
agentcore invoke '{"customer_id": "CUST-123", "session_id": "sess-001", "prompt": "I need help with my order ORD-456"}'

# Expected output:
# ✓ Agent deployed: customer-support-agent
# ✓ Response: "Let me look up your order and check our records..."
```

## Architecture Overview

```
Customer Request
       |
       v
  [AgentCore Runtime]
  (microVM isolation)
       |
  [Support Agent]
   /    |    \
  v     v     v
Memory  Gateway  Observability
  |       |         |
  v       v         v
Preferences  CRM/Tickets  CloudWatch
& History    & Orders     Dashboards
```

## Key Benefits

### Context That Persists
Memory stores customer preferences and interaction summaries automatically. When a customer calls back, the agent knows their history without them repeating it.

### Secure Tool Access
Gateway provides MCP-compatible access to CRM tools with authentication handled at the infrastructure layer. The agent calls tools through a unified interface.

### Production Monitoring
Observability traces every agent decision, tool call, and response. Set up CloudWatch alarms for error rates, latency spikes, and unusual patterns.

## Troubleshooting

**Issue: Memory returns empty results**
Solution: Long-term memory extraction is asynchronous. Wait a few minutes after storing events before querying long-term records.

**Issue: Gateway tool calls fail with AuthorizationError**
Solution: Verify the Gateway IAM role has permission to invoke the Lambda functions.

**Issue: Agent responses are slow**
Solution: Check if semantic search is adding latency. Reduce `topK` in memory retrieval or cache tool lists.

## Next Steps

Start with Memory and a single Gateway tool to validate the pattern. Add CRM integrations incrementally. Use Observability to identify which customer queries take longest and optimize those paths first.

📚 **Documentation**: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/
💻 **Full runnable code**: `articles/examples/memory/`
🔧 **GitHub samples**: https://github.com/awslabs/amazon-bedrock-agentcore-samples/

#AWS #AI #AgentCore #CustomerSupport #Memory #Tutorial
