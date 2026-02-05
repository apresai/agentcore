# AgentCore Memory

> Fully managed short-term and long-term memory service for context-aware, personalized AI agent conversations.

## Quick Reference

| CLI Command | Description |
|-------------|-------------|
| `agentcore memory create` | Create new memory resource |
| `agentcore memory list` | List all memories |
| `agentcore memory get` | Get memory details |
| `agentcore memory delete` | Delete memory resource |
| `agentcore memory update-strategies` | Update long-term strategies |

| SDK Client | Purpose |
|------------|---------|
| `MemoryClient` (AgentCore SDK) | High-level memory operations |
| `bedrock-agentcore` (data plane) | Create events, retrieve memories |
| `bedrock-agentcore-control` (control plane) | Manage memory resources |

| Key API | Description |
|---------|-------------|
| `CreateMemory` | Create memory resource |
| `CreateEvent` | Store conversation turn |
| `RetrieveMemoryRecords` | Semantic search long-term memory |
| `GetEvents` | Retrieve short-term events |
| `ListMemoryRecords` | List extracted memories |

---

## Overview

Amazon Bedrock AgentCore Memory is a fully managed service that gives AI agents the ability to remember past interactions, enabling intelligent, context-aware, and personalized conversations.

## The Problem It Solves

Without memory, AI agents are **stateless** - each interaction is treated as new with no knowledge of previous conversations. AgentCore Memory allows agents to build a coherent understanding of users over time.

---

## Core Concepts

### Memory Resource

A memory resource is a logical container that encapsulates both raw events and processed long-term memories. It defines:
- How long data is retained
- How it's secured (encryption)
- How raw interactions are transformed into insights

### Short-Term Memory

Captures **turn-by-turn interactions** within a single session:
- Maintains immediate conversation context
- Stores raw events as immutable records
- Organized by actor and session
- No need for users to repeat information

**Example**: User asks "What's the weather in Seattle?" then follows with "What about tomorrow?" - the agent understands "tomorrow" refers to Seattle weather.

### Long-Term Memory

**Automatically extracts and stores key insights** across sessions:
- User preferences and choices
- Important facts and knowledge
- Session summaries
- Extracted asynchronously using memory strategies

**Example**: Customer mentions preference for window seats during flight booking. In future interactions, agent proactively offers window seats.

### Memory Strategies

Define how raw events are transformed into long-term memories:
- **Built-in strategies**: Pre-configured extraction patterns
- **Custom strategies**: Your own extraction logic
- **Self-managed strategies**: Full control over pipelines

---

## CLI Reference

### Installation

```bash
pip install bedrock-agentcore-starter-toolkit
```

### agentcore memory create

Create a new memory resource.

```bash
agentcore memory create [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--name` | Memory name | Required |
| `--region` | AWS region | us-east-1 |
| `--strategies` | Long-term strategies (comma-separated) | None |
| `--ttl` | Short-term memory TTL (seconds) | 86400 |
| `--kms-key` | Custom KMS key ARN | AWS managed |

**Examples:**

```bash
# Basic memory (short-term only)
agentcore memory create --name CustomerSupport

# With long-term strategies
agentcore memory create \
    --name CustomerSupport \
    --strategies SessionSummarizer,PreferenceLearner,FactExtractor

# With custom TTL and encryption
agentcore memory create \
    --name SecureMemory \
    --ttl 3600 \
    --kms-key arn:aws:kms:us-east-1:123456789012:key/abc123
```

### agentcore memory list

List all memory resources.

```bash
agentcore memory list [OPTIONS]

# Output format
NAME                STATUS    STRATEGIES
CustomerSupport     ACTIVE    SessionSummarizer, PreferenceLearner
SecureMemory        ACTIVE    None
```

### agentcore memory get

Get details of a memory resource.

```bash
agentcore memory get --name CustomerSupport
```

### agentcore memory delete

Delete a memory resource.

```bash
agentcore memory delete --name CustomerSupport --force
```

### agentcore memory update-strategies

Add or update long-term memory strategies.

```bash
agentcore memory update-strategies \
    --name CustomerSupport \
    --add SessionSummarizer
```

---

## SDK Reference

### Using AgentCore SDK (Recommended)

The AgentCore SDK provides a high-level interface for memory operations.

```python
from bedrock_agentcore.memory import MemoryClient

client = MemoryClient(region_name='us-east-1')
```

#### Create Memory

```python
from bedrock_agentcore.memory import MemoryClient

client = MemoryClient(region_name='us-east-1')

# Create memory with short-term only
memory = client.create_memory(
    name="CustomerSupportMemory",
    description="Memory for customer support agent"
)

# Create memory with long-term strategies
memory = client.create_memory_and_wait(
    name="CustomerSupportMemory",
    strategies=[
        {
            "strategyName": "SessionSummarizer",
            "namespaces": ["summaries"]
        },
        {
            "strategyName": "PreferenceLearner",
            "namespaces": ["preferences"]
        },
        {
            "strategyName": "FactExtractor",
            "namespaces": ["facts"]
        }
    ]
)

memory_id = memory["memoryId"]
```

#### Create Event (Store Conversation)

```python
# Store a conversation turn
client.create_event(
    memory_id=memory_id,
    actor_id="user-123",
    session_id="session-456",
    messages=[
        {"role": "user", "content": "I'd like to book a flight to Seattle"},
        {"role": "assistant", "content": "I'd be happy to help you book a flight to Seattle. What dates are you looking at?"},
        {"role": "user", "content": "Next Friday, and I prefer window seats"},
        {"role": "assistant", "content": "Got it! I'll look for window seats on flights to Seattle for next Friday."}
    ]
)
```

#### Retrieve Short-Term Memory

```python
# Get recent conversation history
events = client.get_events(
    memory_id=memory_id,
    actor_id="user-123",
    session_id="session-456"
)

for event in events:
    for msg in event["messages"]:
        print(f"{msg['role']}: {msg['content']}")
```

#### Retrieve Long-Term Memory

```python
# Semantic search across extracted memories
memories = client.retrieve_memories(
    memory_id=memory_id,
    actor_id="user-123",
    query="What are the user's travel preferences?",
    namespace="preferences",
    max_results=5
)

for memory in memories:
    print(f"Memory: {memory['content']}")
    print(f"Score: {memory['score']}")
```

#### List Memory Records

```python
# List all extracted memory records
records = client.list_memory_records(
    memory_id=memory_id,
    actor_id="user-123",
    namespace="preferences"
)

for record in records:
    print(f"ID: {record['memoryRecordId']}")
    print(f"Content: {record['content']}")
```

### Using boto3 Directly

For lower-level control, use boto3 directly.

```python
import boto3

# Control plane client
control_client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

# Data plane client
data_client = boto3.client('bedrock-agentcore', region_name='us-east-1')
```

#### Control Plane APIs

##### CreateMemory

```python
response = control_client.create_memory(
    name='CustomerSupportMemory',
    description='Memory for customer support',
    clientToken='unique-token-123',
    encryptionKeyArn='arn:aws:kms:us-east-1:123456789012:key/abc123',  # Optional
    eventExpiryDuration=86400,  # Short-term TTL in seconds
    memoryStrategies=[
        {
            'sessionSummaryMemoryStrategy': {
                'maxRecentSessions': 10,
                'name': 'SessionSummarizer',
                'namespaces': ['summaries']
            }
        },
        {
            'userPreferenceMemoryStrategy': {
                'name': 'PreferenceLearner',
                'namespaces': ['preferences']
            }
        },
        {
            'semanticMemoryStrategy': {
                'name': 'FactExtractor',
                'namespaces': ['facts']
            }
        }
    ]
)

memory_id = response['memoryId']
memory_arn = response['memoryArn']
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Memory name (1-48 chars) |
| `description` | string | No | Description |
| `eventExpiryDuration` | int | No | Short-term TTL (seconds) |
| `encryptionKeyArn` | string | No | Custom KMS key |
| `memoryStrategies` | list | No | Long-term strategies |

##### GetMemory

```python
response = control_client.get_memory(
    memoryId='mem-abc123xyz'
)

status = response['status']  # CREATING, ACTIVE, FAILED
strategies = response['memoryStrategies']
```

##### ListMemories

```python
response = control_client.list_memories(
    maxResults=50
)

for memory in response['memorySummaries']:
    print(f"{memory['name']}: {memory['status']}")
```

##### UpdateMemoryStrategies

```python
response = control_client.update_memory_strategies(
    memoryId='mem-abc123xyz',
    strategies=[
        {
            'sessionSummaryMemoryStrategy': {
                'name': 'NewSummarizer',
                'namespaces': ['new-summaries']
            }
        }
    ]
)
```

##### DeleteMemory

```python
control_client.delete_memory(
    memoryId='mem-abc123xyz'
)
```

#### Data Plane APIs

##### CreateEvent

```python
response = data_client.create_event(
    memoryId='mem-abc123xyz',
    actorId='user-123',
    sessionId='session-456',
    eventTimestamp='2024-01-15T10:30:00Z',
    payload={
        'messages': [
            {'role': 'user', 'content': 'Hello, I need help'},
            {'role': 'assistant', 'content': 'Hi! How can I help you today?'}
        ]
    }
)

event_id = response['eventId']
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `memoryId` | string | Yes | Memory resource ID |
| `actorId` | string | Yes | User/actor identifier |
| `sessionId` | string | Yes | Session identifier |
| `payload` | object | Yes | Event data (messages) |
| `eventTimestamp` | string | No | ISO 8601 timestamp |

##### GetEvents

```python
response = data_client.get_events(
    memoryId='mem-abc123xyz',
    actorId='user-123',
    sessionId='session-456',
    maxResults=100
)

for event in response['events']:
    print(f"Event ID: {event['eventId']}")
    print(f"Timestamp: {event['eventTimestamp']}")
```

##### RetrieveMemoryRecords

Semantic search across long-term memories.

```python
response = data_client.retrieve_memory_records(
    memoryId='mem-abc123xyz',
    actorId='user-123',
    query='travel preferences',
    namespace='preferences',
    maxResults=10
)

for record in response['memoryRecords']:
    print(f"Content: {record['content']}")
    print(f"Score: {record['score']}")
    print(f"Namespace: {record['namespace']}")
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `memoryId` | string | Yes | Memory resource ID |
| `actorId` | string | Yes | User/actor identifier |
| `query` | string | Yes | Search query |
| `namespace` | string | No | Filter by namespace |
| `maxResults` | int | No | Maximum results (default: 10) |

##### ListMemoryRecords

List all extracted memory records.

```python
response = data_client.list_memory_records(
    memoryId='mem-abc123xyz',
    actorId='user-123',
    namespace='preferences'
)

for record in response['memoryRecords']:
    print(f"ID: {record['memoryRecordId']}")
    print(f"Strategy: {record['strategyId']}")
```

---

## Built-in Memory Strategies

### SessionSummaryMemoryStrategy

Creates condensed summaries of conversations within a session.

```python
{
    'sessionSummaryMemoryStrategy': {
        'name': 'SessionSummarizer',
        'namespaces': ['summaries'],
        'maxRecentSessions': 10  # How many sessions to keep
    }
}
```

**Use cases:**
- Quick context recall without re-processing entire history
- Session handoff between agents
- Audit trail of interactions

### UserPreferenceMemoryStrategy

Identifies and extracts user preferences, choices, and styles.

```python
{
    'userPreferenceMemoryStrategy': {
        'name': 'PreferenceLearner',
        'namespaces': ['preferences']
    }
}
```

**Use cases:**
- Personalized recommendations
- Proactive suggestions
- User profiling

### SemanticMemoryStrategy

Extracts factual information and contextual knowledge.

```python
{
    'semanticMemoryStrategy': {
        'name': 'FactExtractor',
        'namespaces': ['facts']
    }
}
```

**Use cases:**
- Knowledge base building
- Context enrichment
- Fact verification

### EpisodicMemoryStrategy

Captures interactions as structured episodes with scenarios, intents, actions, and outcomes.

```python
{
    'episodicMemoryStrategy': {
        'name': 'EpisodeTracker',
        'namespaces': ['episodes']
    }
}
```

**Use cases:**
- Learning from past experiences
- Pattern recognition
- Adaptive behavior

---

## Custom Memory Strategies

Create custom strategies for domain-specific extraction.

```python
from bedrock_agentcore.memory import MemoryClient

client = MemoryClient(region_name='us-east-1')

# Create memory with custom strategy
memory = client.create_memory_and_wait(
    name="DomainMemory",
    strategies=[
        {
            "customMemoryStrategy": {
                "name": "ProductInterestTracker",
                "namespaces": ["products"],
                "modelId": "anthropic.claude-sonnet-4-20250514",
                "extractionPrompt": """
                    Analyze the conversation and extract any products
                    the user has shown interest in. Include:
                    - Product name
                    - Level of interest (high/medium/low)
                    - Any specific requirements mentioned

                    Conversation: {conversation}
                """,
                "consolidationPrompt": """
                    Merge these product interests, updating interest levels
                    and combining requirements for the same products.

                    Existing: {existing}
                    New: {new}
                """
            }
        }
    ]
)
```

---

## Self-Managed Strategies

For full control over extraction pipelines.

### Setup Requirements

1. **S3 bucket** - For batched event payloads
2. **SNS topic** - For job notifications
3. **IAM role** - For AgentCore access

### Configuration

```python
{
    'selfManagedMemoryStrategy': {
        'name': 'CustomPipeline',
        'namespaces': ['custom'],
        'triggerConfiguration': {
            'eventCount': 10,  # Trigger after N events
            'timeWindow': 3600  # Or after N seconds
        },
        'payloadDelivery': {
            's3Bucket': 'my-bucket',
            's3Prefix': 'memory-payloads/',
            'snsTopicArn': 'arn:aws:sns:us-east-1:123456789012:memory-jobs'
        },
        'historicalContextWindow': 100
    }
}
```

### Processing Pipeline

```python
import boto3
import json

def lambda_handler(event, context):
    """Process memory extraction job from SNS."""

    # Parse SNS message
    message = json.loads(event['Records'][0]['Sns']['Message'])

    s3_location = message['s3PayloadLocation']
    job_id = message['jobId']
    memory_id = message['memoryId']

    # Download payload from S3
    s3 = boto3.client('s3')
    payload = s3.get_object(
        Bucket=s3_location['bucket'],
        Key=s3_location['key']
    )

    data = json.loads(payload['Body'].read())

    # Extract memories using your logic
    memories = extract_memories(data['events'])

    # Store back to AgentCore
    client = boto3.client('bedrock-agentcore')

    for memory in memories:
        client.create_memory_record(
            memoryId=memory_id,
            actorId=data['actorId'],
            namespace='custom',
            content=memory['content'],
            metadata=memory['metadata']
        )

    return {'statusCode': 200}

def extract_memories(events):
    """Your custom extraction logic."""
    memories = []
    # Process events and extract insights
    return memories
```

---

## Code Examples

### Basic Short-Term Memory

```python
from bedrock_agentcore.memory import MemoryClient
from strands import Agent

# Initialize clients
memory_client = MemoryClient(region_name='us-east-1')
memory_id = "mem-abc123xyz"

def chat_with_memory(user_id: str, session_id: str, message: str) -> str:
    """Chat with short-term memory context."""

    # Get recent conversation history
    events = memory_client.get_events(
        memory_id=memory_id,
        actor_id=user_id,
        session_id=session_id
    )

    # Build conversation context
    history = []
    for event in events:
        for msg in event.get("messages", []):
            history.append(msg)

    # Add current message
    history.append({"role": "user", "content": message})

    # Get agent response
    response = agent.chat(history)

    # Store the exchange
    memory_client.create_event(
        memory_id=memory_id,
        actor_id=user_id,
        session_id=session_id,
        messages=[
            {"role": "user", "content": message},
            {"role": "assistant", "content": response}
        ]
    )

    return response
```

### Long-Term Memory with Personalization

```python
from bedrock_agentcore.memory import MemoryClient

memory_client = MemoryClient(region_name='us-east-1')
memory_id = "mem-abc123xyz"

def personalized_chat(user_id: str, session_id: str, message: str) -> str:
    """Chat with personalized long-term memory."""

    # Retrieve relevant long-term memories
    preferences = memory_client.retrieve_memories(
        memory_id=memory_id,
        actor_id=user_id,
        query=message,
        namespace="preferences",
        max_results=5
    )

    facts = memory_client.retrieve_memories(
        memory_id=memory_id,
        actor_id=user_id,
        query=message,
        namespace="facts",
        max_results=5
    )

    # Build personalized context
    context = "User preferences and known facts:\n"
    for pref in preferences:
        context += f"- {pref['content']}\n"
    for fact in facts:
        context += f"- {fact['content']}\n"

    # Get short-term history
    events = memory_client.get_events(
        memory_id=memory_id,
        actor_id=user_id,
        session_id=session_id
    )

    # Create enhanced prompt
    system_prompt = f"""You are a helpful assistant with knowledge about this user.

{context}

Use this context to provide personalized responses."""

    # Generate response
    response = agent.chat(
        messages=[{"role": "user", "content": message}],
        system_prompt=system_prompt
    )

    # Store interaction for future extraction
    memory_client.create_event(
        memory_id=memory_id,
        actor_id=user_id,
        session_id=session_id,
        messages=[
            {"role": "user", "content": message},
            {"role": "assistant", "content": response}
        ]
    )

    return response
```

### Strands Agent with Memory Integration

```python
from strands import Agent
from strands.models import BedrockModel
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.session import AgentCoreMemorySessionManager

# Initialize memory
memory_client = MemoryClient(region_name='us-east-1')

# Create memory with strategies
memory = memory_client.create_memory_and_wait(
    name="StrandsAgentMemory",
    strategies=[
        {"strategyName": "SessionSummarizer", "namespaces": ["summaries"]},
        {"strategyName": "PreferenceLearner", "namespaces": ["preferences"]},
        {"strategyName": "FactExtractor", "namespaces": ["facts"]}
    ]
)

# Configure memory for agent
memory_config = AgentCoreMemoryConfig(
    memory_id=memory["memoryId"],
    region_name="us-east-1"
)

session_manager = AgentCoreMemorySessionManager(memory_config)

# Create model
model = BedrockModel(
    model_id="anthropic.claude-sonnet-4-20250514",
    region_name="us-east-1"
)

# Create agent with memory
agent = Agent(
    model=model,
    memory=session_manager,
    system_prompt="You are a helpful assistant that remembers user preferences."
)

# Use the agent
response = agent("I prefer dark mode and minimal notifications")
print(response)

response = agent("What are my preferences?")  # Agent recalls from memory
print(response)
```

### LangGraph with Memory Checkpointing

```python
from langgraph.graph import StateGraph
from langgraph.checkpoint import MemorySaver
from bedrock_agentcore.memory import MemoryClient

memory_client = MemoryClient(region_name='us-east-1')

class AgentCoreCheckpointer(MemorySaver):
    """LangGraph checkpointer using AgentCore Memory."""

    def __init__(self, memory_id: str, actor_id: str):
        self.memory_id = memory_id
        self.actor_id = actor_id
        self.client = MemoryClient()

    def get(self, thread_id: str):
        """Get checkpoint from memory."""
        events = self.client.get_events(
            memory_id=self.memory_id,
            actor_id=self.actor_id,
            session_id=thread_id
        )
        if events:
            return events[-1].get("checkpoint")
        return None

    def put(self, thread_id: str, checkpoint: dict):
        """Save checkpoint to memory."""
        self.client.create_event(
            memory_id=self.memory_id,
            actor_id=self.actor_id,
            session_id=thread_id,
            messages=[{"role": "system", "content": "checkpoint"}],
            metadata={"checkpoint": checkpoint}
        )

# Use with LangGraph
checkpointer = AgentCoreCheckpointer(
    memory_id="mem-abc123xyz",
    actor_id="user-123"
)

graph = StateGraph(AgentState)
# ... build graph ...
agent = graph.compile(checkpointer=checkpointer)
```

### Multi-Agent Shared Memory

```python
from bedrock_agentcore.memory import MemoryClient

memory_client = MemoryClient(region_name='us-east-1')

# Shared memory for agent team
shared_memory = memory_client.create_memory_and_wait(
    name="TeamSharedMemory",
    strategies=[
        {"strategyName": "FactExtractor", "namespaces": ["shared-facts"]},
        {"strategyName": "SessionSummarizer", "namespaces": ["handoffs"]}
    ]
)

memory_id = shared_memory["memoryId"]

def agent_handoff(from_agent: str, to_agent: str, context: dict):
    """Hand off conversation between agents."""

    # Store handoff context
    memory_client.create_event(
        memory_id=memory_id,
        actor_id="system",
        session_id=context["session_id"],
        messages=[
            {
                "role": "system",
                "content": f"Handoff from {from_agent} to {to_agent}",
                "metadata": {
                    "from_agent": from_agent,
                    "to_agent": to_agent,
                    "reason": context.get("reason"),
                    "summary": context.get("summary")
                }
            }
        ]
    )

def get_shared_context(session_id: str, query: str) -> list:
    """Get shared context for any agent."""

    facts = memory_client.retrieve_memories(
        memory_id=memory_id,
        actor_id="system",
        query=query,
        namespace="shared-facts"
    )

    return facts
```

---

## Integration Patterns

### With AgentCore Runtime

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient

memory_client = MemoryClient()
app = BedrockAgentCoreApp()

@app.entrypoint()
async def main(request):
    user_id = request.get("user_id")
    session_id = request.get("session_id")
    message = request.get("prompt")

    # Retrieve context
    memories = memory_client.retrieve_memories(
        memory_id=MEMORY_ID,
        actor_id=user_id,
        query=message
    )

    # Generate response with context
    response = await generate_response(message, memories)

    # Store interaction
    memory_client.create_event(
        memory_id=MEMORY_ID,
        actor_id=user_id,
        session_id=session_id,
        messages=[
            {"role": "user", "content": message},
            {"role": "assistant", "content": response}
        ]
    )

    return {"response": response}
```

### With AgentCore Observability

```python
from opentelemetry import trace
from bedrock_agentcore.memory import MemoryClient

tracer = trace.get_tracer(__name__)
memory_client = MemoryClient()

def retrieve_with_tracing(memory_id: str, actor_id: str, query: str):
    """Memory retrieval with observability."""

    with tracer.start_as_current_span("memory.retrieve") as span:
        span.set_attribute("memory.id", memory_id)
        span.set_attribute("memory.actor_id", actor_id)
        span.set_attribute("memory.query", query)

        memories = memory_client.retrieve_memories(
            memory_id=memory_id,
            actor_id=actor_id,
            query=query
        )

        span.set_attribute("memory.result_count", len(memories))

        return memories
```

---

## Advanced Features

### Branching

Create alternative conversation paths from a specific point.

```python
# Create a branch from a specific event
branch = memory_client.create_branch(
    memory_id=memory_id,
    actor_id=user_id,
    session_id=session_id,
    from_event_id="event-123",
    branch_name="alternative-path"
)

# Continue conversation on branch
memory_client.create_event(
    memory_id=memory_id,
    actor_id=user_id,
    session_id=branch["branchSessionId"],
    messages=[{"role": "user", "content": "What if we tried option B?"}]
)
```

### Checkpointing

Save and mark specific states for later reference.

```python
# Create checkpoint
checkpoint = memory_client.create_checkpoint(
    memory_id=memory_id,
    actor_id=user_id,
    session_id=session_id,
    checkpoint_name="before-decision",
    metadata={"state": "awaiting-confirmation"}
)

# Later, restore to checkpoint
memory_client.restore_checkpoint(
    memory_id=memory_id,
    actor_id=user_id,
    checkpoint_id=checkpoint["checkpointId"]
)
```

---

## Best Practices

1. **Design memory architecture intentionally** - Plan namespaces and strategies before implementation.

2. **Use appropriate TTL settings** - Set short-term TTL based on session patterns (hours to days).

3. **Focus on extracting relevant information** - Configure strategies to capture only what's needed.

4. **Implement memory operation rhythm** - Store events after each turn, retrieve before generating.

5. **Use meaningful namespaces** - Organize memories by type (preferences, facts, summaries).

6. **Implement proper security** - Use KMS encryption for sensitive data.

7. **Monitor memory usage** - Use CloudWatch metrics to track extraction and retrieval.

8. **Handle extraction latency** - Long-term memories are extracted asynchronously; plan for delays.

9. **Test with realistic data** - Validate strategies with production-like conversations.

10. **Consider multi-tenancy** - Use actor IDs to isolate user data.

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `MemoryNotFound` | Invalid memory ID | Verify memory exists and is ACTIVE |
| `ActorNotFound` | No events for actor | Create events before retrieving |
| `StrategyFailed` | Extraction error | Check CloudWatch logs for details |
| `QuotaExceeded` | Too many memories | Delete old records or request increase |
| `ValidationError` | Invalid parameters | Check event format and required fields |

### Debugging Tips

```bash
# Check memory status
agentcore memory get --name MyMemory

# View extraction logs
aws logs tail /aws/bedrock-agentcore/memories/<memory_id> --follow

# List events for debugging
aws bedrock-agentcore get-events \
    --memory-id mem-abc123 \
    --actor-id user-123 \
    --session-id session-456
```

### Strategy Not Extracting

1. Verify strategy status is ACTIVE
2. Check enough events exist to trigger extraction
3. Review CloudWatch logs for extraction errors
4. Ensure events have proper message format

---

## Limits & Quotas

| Resource | Default Limit | Adjustable |
|----------|--------------|------------|
| Memories per account | 100 | Yes |
| Strategies per memory | 10 | Yes |
| Events per session | 10,000 | Yes |
| Memory records per actor | 100,000 | Yes |
| Event payload size | 256 KB | No |
| Short-term TTL (max) | 30 days | No |
| Retrieval results (max) | 100 | No |
| Concurrent extractions | 10 | Yes |

---

## Pricing

### Short-Term Memory

| Operation | Rate |
|-----------|------|
| Event creation | Per event |
| Event retrieval | Per request |

### Long-Term Memory

| Operation | Rate |
|-----------|------|
| Memory record storage | Per record/month |
| Retrieval (semantic search) | Per request |
| Strategy extraction | Per extraction job |

### Cost Optimization Tips

1. **Set appropriate TTL** - Don't store short-term events longer than needed.
2. **Optimize retrieval** - Use namespaces to filter and reduce search scope.
3. **Batch events** - Combine multiple turns into single events when possible.
4. **Monitor extraction** - Track strategy costs in CloudWatch.

---

## Related Services

- [AgentCore Runtime](./01-runtime.md) - Deploy agents with memory
- [AgentCore Gateway](./03-gateway.md) - Tool integration
- [AgentCore Observability](./08-observability.md) - Memory monitoring
- [AgentCore Evaluations](./09-evaluations.md) - Evaluate memory effectiveness
