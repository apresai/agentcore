# Building a Customer Support Agent with AgentCore

Your support bot forgets everything between sessions. Customers repeat themselves. Agents can't access your CRM. AgentCore solves this by combining **Runtime** (serverless hosting), **Memory** (conversation context), and **Gateway** (tool integration).

## Architecture

```
         Customer --> Runtime (Agent) --> Memory + Gateway
                                             |         |
                                      Preferences   CRM/Tickets
```

- **Runtime**: Deploys agents with microVM isolation per session
- **Memory**: Short-term (session) + long-term (preferences) context
- **Gateway**: Converts Lambda/APIs into MCP tools

## Prerequisites

```bash
pip install boto3 strands-agents
export AWS_REGION=us-east-1
```

## Step 1: Create Gateway with Tools

Register CRM and ticket tools with Gateway:

```python
import boto3

control = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

# Create gateway
gateway = control.create_gateway(name='SupportGateway', authorizerType='IAM', protocolType='MCP')
gateway_id = gateway['gatewayId']

# Add CRM lookup tool
control.create_gateway_target(
    gatewayId=gateway_id,
    name='CRMTools',
    targetConfiguration={
        'lambdaTargetConfiguration': {
            'lambdaArn': 'arn:aws:lambda:us-east-1:123456789012:function:lookup-customer',
            'toolSchema': {'tools': [{
                'name': 'lookup_customer',
                'description': 'Look up customer by email',
                'inputSchema': {'type': 'object', 'properties': {'email': {'type': 'string'}}, 'required': ['email']}
            }]}
        }
    }
)
```

## Step 2: Create Memory

Set up memory with preference extraction:

```python
memory = control.create_memory(
    name='SupportMemory',
    eventExpiryDuration=7,
    memoryStrategies=[{
        'userPreferenceMemoryStrategy': {'name': 'CustomerPreferences', 'namespaces': ['preferences']}
    }]
)
memory_id = memory['memory']['id']
```

## Step 3: Build the Agent

Create a Strands agent with Gateway tools and Memory integration:

```python
from strands import Agent
from strands.models import BedrockModel
from strands.tools import tool
from datetime import datetime, timezone

data_client = boto3.client('bedrock-agentcore', region_name='us-east-1')

@tool
def lookup_customer(email: str) -> str:
    """Look up customer by email."""
    response = data_client.invoke_gateway(
        gatewayId=GATEWAY_ID, method='tools/call',
        payload=json.dumps({'name': 'lookup_customer', 'arguments': {'email': email}}).encode()
    )
    return json.loads(response['payload'].read())['content'][0]['text']

model = BedrockModel(model_id="anthropic.claude-sonnet-4-20250514")
agent = Agent(model=model, tools=[lookup_customer], system_prompt="You are a helpful support agent.")

def chat_with_memory(email: str, session_id: str, message: str) -> str:
    # Retrieve preferences
    prefs = data_client.retrieve_memory_records(
        memoryId=MEMORY_ID, namespace="preferences",
        searchCriteria={'searchQuery': email, 'topK': 3}
    )

    # Get response with context
    response = str(agent(f"Customer prefs: {prefs}\n\n{message}"))

    # Store interaction
    data_client.create_event(
        memoryId=MEMORY_ID, actorId=email, sessionId=session_id,
        eventTimestamp=datetime.now(timezone.utc),
        payload=[
            {'conversational': {'role': 'USER', 'content': {'text': message}}},
            {'conversational': {'role': 'ASSISTANT', 'content': {'text': response}}}
        ]
    )
    return response
```

## Step 4: Deploy to Runtime

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint()
async def main(request):
    return {"response": chat_with_memory(
        request["customer_email"], request["session_id"], request["message"]
    )}
```

```bash
agentcore deploy --name customer-support-agent
```

## Testing

```bash
cd articles/examples/customer-support
pip install -r requirements.txt
python main.py
```

Expected output:
```
Customer: Hi, I'm alice@example.com with an order issue
Agent: Hello Alice! I see you're a premium customer. How can I help?

Customer: Can you create a ticket?
Agent: I've created ticket TKT-1234. Our team will review within 24 hours.
```

## Next Steps

- **Add Policy**: Restrict tools by customer tier
- **Add Observability**: Enable CloudWatch tracing
- **Scale**: Route to specialized agents using Gateway semantic search

## Key Takeaways

- **Runtime** handles deployment and isolation
- **Memory** provides session context and learned preferences
- **Gateway** converts APIs into agent-accessible tools

Full runnable example: `articles/examples/customer-support/`
Docs: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/
