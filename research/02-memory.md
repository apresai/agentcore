# AgentCore Memory

> Fully managed short-term and long-term memory service for context-aware, personalized AI agent conversations.

## Quick Reference

| CLI Command | Description |
|-------------|-------------|
| `agentcore memory create` | Create new memory resource |
| `agentcore memory list` | List all memories |
| `agentcore memory get` | Get memory details |
| `agentcore memory delete` | Delete memory resource |
| `agentcore memory status` | Get memory provisioning status |
| `agentcore memory show` | Show memory data (actors, sessions, events, records) |
| `agentcore memory browse` | Interactive TUI browser for memory content |

There is no `agentcore memory update-strategies` command. Strategies are set at `create` time via `--strategies` (a JSON string); updating them after creation goes through the `bedrock-agentcore-control` `update_memory` boto3 call's `memoryStrategies` parameter (there is no separate `UpdateMemoryStrategies` operation), not a dedicated CLI subcommand.

| SDK Client | Purpose |
|------------|---------|
| `MemoryClient` (AgentCore SDK) | Create memories/strategies, store events, retrieve long-term memories |
| `MemorySessionManager` / `MemorySession` (AgentCore SDK) | Per-session turn tracking, branching, long-term search |
| `bedrock-agentcore` (data plane) | Create events, retrieve/list memory records |
| `bedrock-agentcore-control` (control plane) | Manage memory resources |

| Key API | Description |
|---------|-------------|
| `CreateMemory` | Create memory resource |
| `CreateEvent` | Store conversation turn |
| `RetrieveMemoryRecords` | Semantic search long-term memory |
| `ListEvents` | Retrieve short-term events |
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
- How long raw events are retained (`eventExpiryDuration`, in **days**, 3-365)
- How it's secured (encryption)
- How raw interactions are transformed into insights (strategies)

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

Define how raw events are transformed into long-term memories. The real strategy types (both in the CLI's `--strategies` JSON and the SDK's `create_memory(strategies=...)`) are:
- **`semanticMemoryStrategy`** - Extracts factual information
- **`summaryMemoryStrategy`** - Session summaries
- **`userPreferenceMemoryStrategy`** - User preferences
- **`episodicMemoryStrategy`** - Structured episodes (scenario, intent, action, outcome)
- **`customMemoryStrategy`** - Prompt overrides on one of the above, or a fully self-managed extraction pipeline

Each has `name`, optional `description`, and `namespaces` (or `namespaceTemplates`). There is no `sessionSummaryMemoryStrategy` key or `maxRecentSessions` field - the strategy is named `summaryMemoryStrategy`, and controls like retention live at the memory-resource level (`eventExpiryDuration`), not per strategy.

---

## CLI Reference

### Installation

```bash
pip install bedrock-agentcore-starter-toolkit
```

> The starter toolkit's CLI now recommends `@aws/agentcore` (`npm install -g @aws/agentcore`) for new work; see [AgentCore Runtime](./01-runtime.md#installation) for the deprecation notice. This reference covers the Python starter toolkit (0.3.10) as installed today.

### agentcore memory create

Create a new memory resource. `NAME` is a required positional argument, not a `--name` flag.

```bash
agentcore memory create NAME [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--region`, `-r` | AWS region | session region |
| `--description`, `-d` | Description for the memory | None |
| `--event-expiry-days`, `-e` | Event retention, in days | 90 |
| `--strategies`, `-s` | JSON string of memory strategies | None |
| `--role-arn` | IAM role ARN for memory execution | auto-created |
| `--encryption-key-arn` | KMS key ARN for encryption | AWS managed |
| `--wait` / `--no-wait` | Wait for the memory to become `ACTIVE` | `--wait` |
| `--max-wait` | Maximum wait time (seconds) | 300 |

There is no `--name`, `--ttl`, or `--kms-key` flag - use the positional name, `--event-expiry-days` (days, not seconds), and `--encryption-key-arn`.

**Examples:**

```bash
# Basic memory (short-term only)
agentcore memory create CustomerSupport

# With a long-term strategy, waiting for ACTIVE
agentcore memory create CustomerSupport \
    --strategies '[{"semanticMemoryStrategy": {"name": "Facts"}}, {"userPreferenceMemoryStrategy": {"name": "Preferences"}}]' \
    --wait

# With custom retention and encryption
agentcore memory create SecureMemory \
    --event-expiry-days 30 \
    --encryption-key-arn arn:aws:kms:us-east-1:123456789012:key/abc123
```

### agentcore memory list

List all memory resources.

```bash
agentcore memory list [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--region`, `-r` | AWS region | - |
| `--max-results`, `-n` | Maximum results | 100 |

### agentcore memory get

Get details of a memory resource. `MEMORY_ID` is a required positional argument, not `--name`.

```bash
agentcore memory get MEMORY_ID [--region REGION]
```

### agentcore memory delete

Delete a memory resource. `MEMORY_ID` is positional.

```bash
agentcore memory delete MEMORY_ID [--wait] [--max-wait SECONDS]
```

### agentcore memory status / show / browse

```bash
# Provisioning status
agentcore memory status MEMORY_ID

# Inspect actors, sessions, events, and extracted records
agentcore memory show MEMORY_ID

# Interactive TUI browser
agentcore memory browse MEMORY_ID
```

---

## SDK Reference

### Using AgentCore SDK (Recommended)

The AgentCore SDK provides a high-level interface for memory operations. `MemoryClient` covers memory/strategy setup and short-term event storage; per-session turn tracking, branching, and long-term search go through `MemorySessionManager`/`MemorySession` instead.

```python
from bedrock_agentcore.memory import MemoryClient

client = MemoryClient(region_name='us-east-1')
```

#### Create Memory

```python
from bedrock_agentcore.memory import MemoryClient

client = MemoryClient(region_name='us-east-1')

# Create memory with short-term only (default event_expiry_days=90)
memory = client.create_memory(
    name="CustomerSupportMemory",
    description="Memory for customer support agent",
)

# Create memory with long-term strategies, waiting for ACTIVE
memory = client.create_memory_and_wait(
    name="CustomerSupportMemory",
    strategies=[
        {"summaryMemoryStrategy": {"name": "SessionSummarizer", "namespaces": ["summaries"]}},
        {"userPreferenceMemoryStrategy": {"name": "PreferenceLearner", "namespaces": ["preferences"]}},
        {"semanticMemoryStrategy": {"name": "FactExtractor", "namespaces": ["facts"]}},
    ],
)

memory_id = memory["memoryId"]
```

`event_expiry_days` (SDK) / `--event-expiry-days` (CLI) accepts **3-365 days**, not seconds - there is no `ttl`/TTL-in-seconds parameter on memory creation.

#### Create Event (Store Conversation)

`messages` is a list of `(text, role)` **tuples**, not `{"role": ..., "content": ...}` dicts. `role` is a plain string (`"USER"`, `"ASSISTANT"`, `"TOOL"`, or `"OTHER"` - see `bedrock_agentcore.memory.constants.MessageRole`).

```python
# Store a conversation turn
client.create_event(
    memory_id=memory_id,
    actor_id="user-123",
    session_id="session-456",
    messages=[
        ("I'd like to book a flight to Seattle", "USER"),
        ("I'd be happy to help you book a flight to Seattle. What dates are you looking at?", "ASSISTANT"),
        ("Next Friday, and I prefer window seats", "USER"),
        ("Got it! I'll look for window seats on flights to Seattle for next Friday.", "ASSISTANT"),
    ],
)
```

#### Retrieve Short-Term Memory

`MemoryClient` has no `get_events` method - use `list_events`.

```python
# Get recent conversation history
events = client.list_events(
    memory_id=memory_id,
    actor_id="user-123",
    session_id="session-456",
)

for event in events:
    # payload is a list of items, each with a 'conversational' or 'blob' key
    # (list_events is a thin wrapper over the raw ListEvents API)
    for item in event.get("payload", []):
        conv = item.get("conversational")
        if conv:
            print(f"{conv['role']}: {conv['content']['text']}")
```

For simple "last N turns" retrieval, `get_last_k_turns` is usually simpler than paging through `list_events`:

```python
turns = client.get_last_k_turns(
    memory_id=memory_id,
    actor_id="user-123",
    session_id="session-456",
    k=5,
)
```

#### Retrieve Long-Term Memory

`retrieve_memories` takes `namespace`/`namespace_path` and `top_k` - there is no `session_id` argument (long-term memory is keyed by actor/namespace, not session) and no `max_results` argument.

```python
# Semantic search across extracted memories
memories = client.retrieve_memories(
    memory_id=memory_id,
    namespace="preferences",
    query="What are the user's travel preferences?",
    actor_id="user-123",
    top_k=5,
)

for memory in memories:
    print(f"Memory: {memory['content']['text']}")
    print(f"Score: {memory['score']}")
```

#### List Memory Records

`MemoryClient` does not expose a `list_memory_records` convenience method; call the data-plane API directly for a raw listing.

```python
import boto3

data_client = boto3.client('bedrock-agentcore', region_name='us-east-1')

response = data_client.list_memory_records(
    memoryId=memory_id,
    namespace='preferences',
)

for record in response['memoryRecordSummaries']:
    print(f"ID: {record['memoryRecordId']}")
    print(f"Content: {record['content']['text']}")
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

`eventExpiryDuration` is **days** (3-365), not seconds, and is required.

```python
response = control_client.create_memory(
    name='CustomerSupportMemory',
    description='Memory for customer support',
    clientToken='unique-token-123',
    encryptionKeyArn='arn:aws:kms:us-east-1:123456789012:key/abc123',  # Optional
    eventExpiryDuration=90,  # Days, 3-365
    memoryStrategies=[
        {
            'summaryMemoryStrategy': {
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

# Raw boto3 output nests everything under a `memory` key - unlike the
# MemoryClient SDK wrapper, which normalizes it to top-level memoryId/memoryArn.
memory_id = response['memory']['id']
memory_arn = response['memory']['arn']
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Memory name (1-48 chars) |
| `eventExpiryDuration` | int | Yes | Event retention in days (3-365) |
| `description` | string | No | Description |
| `encryptionKeyArn` | string | No | Custom KMS key |
| `memoryStrategies` | list | No | Long-term strategies |

##### GetMemory

```python
response = control_client.get_memory(
    memoryId='mem-abc123xyz'
)

memory = response['memory']  # also nested, same as CreateMemory's output
status = memory['status']  # CREATING, ACTIVE, FAILED
strategies = memory['strategies']
```

##### ListMemories

```python
response = control_client.list_memories(
    maxResults=50
)

for memory in response['memories']:
    print(f"{memory['id']}: {memory['status']}")
```

##### UpdateMemory (adding/modifying/removing strategies)

There is no separate `UpdateMemoryStrategies` operation - strategy changes go through `UpdateMemory`'s `memoryStrategies` parameter, which itself nests `addMemoryStrategies`/`modifyMemoryStrategies`/`deleteMemoryStrategies` lists.

```python
response = control_client.update_memory(
    memoryId='mem-abc123xyz',
    memoryStrategies={
        'addMemoryStrategies': [
            {
                'summaryMemoryStrategy': {
                    'name': 'NewSummarizer',
                    'namespaces': ['new-summaries']
                }
            }
        ]
    }
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
    payload=[
        {'conversational': {'role': 'USER', 'content': {'text': 'Hello, I need help'}}},
        {'conversational': {'role': 'ASSISTANT', 'content': {'text': 'Hi! How can I help you today?'}}},
    ]
)

event_id = response['event']['eventId']
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `memoryId` | string | Yes | Memory resource ID |
| `actorId` | string | Yes | User/actor identifier |
| `payload` | list | Yes | List of event payload items |
| `eventTimestamp` | timestamp | Yes | When the event occurred |
| `sessionId` | string | No (API) | Session identifier - optional on the raw API, but required by the `MemoryClient.create_event()` SDK wrapper |

##### ListEvents

```python
response = data_client.list_events(
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
    namespace='preferences',
    searchCriteria={'searchQuery': 'travel preferences', 'topK': 10},
)

for record in response['memoryRecordSummaries']:
    print(f"Content: {record['content']['text']}")
    print(f"Score: {record['score']}")
    print(f"Namespaces: {record['namespaces']}")
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `memoryId` | string | Yes | Memory resource ID |
| `searchCriteria` | object | Yes | `{'searchQuery': ..., 'topK': ...}` |
| `namespace` | string | No | Filter by namespace |
| `maxResults` | int | No | Page size |

Note there is no `actorId` parameter on this API - namespace scoping (e.g. `/strategies/{id}/actors/{actorId}/`) is how records are scoped to a user.

##### ListMemoryRecords

List all extracted memory records.

```python
response = data_client.list_memory_records(
    memoryId='mem-abc123xyz',
    namespace='preferences'
)

for record in response['memoryRecordSummaries']:
    print(f"ID: {record['memoryRecordId']}")
    print(f"Strategy: {record['memoryStrategyId']}")
```

---

## Built-in Memory Strategies

### summaryMemoryStrategy

Creates condensed summaries of conversations within a session. (Not `sessionSummaryMemoryStrategy` - there is no `maxRecentSessions` field; namespace scoping and retention control what stays available.)

```python
{
    'summaryMemoryStrategy': {
        'name': 'SessionSummarizer',
        'namespaces': ['summaries'],
    }
}
```

**Use cases:**
- Quick context recall without re-processing entire history
- Session handoff between agents
- Audit trail of interactions

### userPreferenceMemoryStrategy

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

### semanticMemoryStrategy

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

### episodicMemoryStrategy

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

`customMemoryStrategy` does not take a free-form `modelId`/`extractionPrompt`/`consolidationPrompt` at the top level. It wraps a `configuration` that is either an **override** of one of the built-in strategies' extraction/consolidation prompts (`semanticOverride`, `summaryOverride`, `userPreferenceOverride`, `episodicOverride`), or a fully **`selfManagedConfiguration`** (see below) where you own the extraction pipeline entirely.

```python
from bedrock_agentcore.memory import MemoryClient

client = MemoryClient(region_name='us-east-1')

# Override the built-in semantic strategy's extraction prompt
memory = client.create_memory_and_wait(
    name="DomainMemory",
    strategies=[
        {
            "customMemoryStrategy": {
                "name": "ProductInterestTracker",
                "namespaces": ["products"],
                "configuration": {
                    "semanticOverride": {
                        "extraction": {
                            "appendToPrompt": (
                                "Also extract any products the user has shown interest in, "
                                "including level of interest (high/medium/low) and requirements mentioned."
                            ),
                            "modelId": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
                        }
                    }
                },
            }
        }
    ],
)
```

The exact fields inside `extraction`/`consolidation` (beyond `appendToPrompt` and `modelId`) are documented in the `CreateMemory` API reference; treat this example as illustrative of the shape rather than exhaustive.

---

## Self-Managed Strategies

For full control over extraction pipelines, use `customMemoryStrategy.configuration.selfManagedConfiguration`.

### Configuration

```python
{
    'customMemoryStrategy': {
        'name': 'CustomPipeline',
        'namespaces': ['custom'],
        'configuration': {
            'selfManagedConfiguration': {
                'triggerConditions': [
                    {'messageBasedTrigger': {'messageCount': 10}},
                ],
                'invocationConfiguration': {
                    'topicArn': 'arn:aws:sns:us-east-1:123456789012:memory-jobs',
                    'payloadDeliveryBucketName': 'my-bucket',
                },
                'historicalContextWindowSize': 100,
            }
        },
    }
}
```

`triggerConditions` also supports `tokenBasedTrigger` (`tokenCount`) and `timeBasedTrigger` (`idleSessionTimeout`) instead of, or alongside, `messageBasedTrigger`.

### Processing Pipeline

The Lambda subscribed to the SNS topic writes extracted records back with the data-plane `BatchCreateMemoryRecords` API - there is no singular `create_memory_record` call.

```python
import boto3
import json

def lambda_handler(event, context):
    """Process memory extraction job from SNS."""

    # Parse SNS message
    message = json.loads(event['Records'][0]['Sns']['Message'])

    s3_location = message['s3PayloadLocation']
    memory_id = message['memoryId']

    # Download payload from S3
    s3 = boto3.client('s3')
    payload = s3.get_object(
        Bucket=s3_location['bucket'],
        Key=s3_location['key']
    )

    data = json.loads(payload['Body'].read())

    # Extract memories using your logic
    records = extract_memories(data['events'])

    # Store back to AgentCore in a single batch call
    client = boto3.client('bedrock-agentcore')

    client.batch_create_memory_records(
        memoryId=memory_id,
        records=[
            {
                'namespaces': ['custom'],
                'content': {'text': record['content']},
                'metadata': record.get('metadata', {}),
            }
            for record in records
        ],
    )

    return {'statusCode': 200}

def extract_memories(events):
    """Your custom extraction logic."""
    records = []
    # Process events and extract insights
    return records
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
    turns = memory_client.get_last_k_turns(
        memory_id=memory_id,
        actor_id=user_id,
        session_id=session_id,
        k=10,
    )

    # get_last_k_turns returns List[List[Dict]] (a list of turns, each a list
    # of message dicts), which is not a Strands Messages list. Flatten it into
    # transcript text and hand that to the agent along with the new message.
    history = "\n".join(
        f"{m.get('role','')}: {m.get('content',{}).get('text','')}"
        for turn in turns for m in turn
    )
    response = agent(f"Conversation so far:\n{history}\n\nUser: {message}")

    # Store the exchange - messages are (text, role) tuples
    memory_client.create_event(
        memory_id=memory_id,
        actor_id=user_id,
        session_id=session_id,
        messages=[
            (message, "USER"),
            (response, "ASSISTANT"),
        ],
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
        namespace="preferences",
        query=message,
        actor_id=user_id,
        top_k=5,
    )

    facts = memory_client.retrieve_memories(
        memory_id=memory_id,
        namespace="facts",
        query=message,
        actor_id=user_id,
        top_k=5,
    )

    # Build personalized context
    context = "User preferences and known facts:\n"
    for pref in preferences:
        context += f"- {pref['content']['text']}\n"
    for fact in facts:
        context += f"- {fact['content']['text']}\n"

    # Get short-term history
    turns = memory_client.get_last_k_turns(
        memory_id=memory_id,
        actor_id=user_id,
        session_id=session_id,
        k=10,
    )

    # Create enhanced prompt
    system_prompt = f"""You are a helpful assistant with knowledge about this user.

{context}

Use this context to provide personalized responses."""

    # Agent.__call__ takes a positional prompt; the system prompt is a
    # property of the Agent, not a per-call keyword.
    agent.system_prompt = system_prompt
    response = agent(message)

    # Store interaction for future extraction
    memory_client.create_event(
        memory_id=memory_id,
        actor_id=user_id,
        session_id=session_id,
        messages=[
            (message, "USER"),
            (response, "ASSISTANT"),
        ],
    )

    return response
```

### Strands Agent with Memory Integration

There is no `bedrock_agentcore.memory.config.AgentCoreMemoryConfig` or `bedrock_agentcore.memory.session.AgentCoreMemorySessionManager` - Strands has no AgentCore-specific memory adapter. Use `MemorySessionManager` directly and pass its context into the agent's prompt.

```python
from strands import Agent
from strands.models import BedrockModel
from bedrock_agentcore.memory import MemoryClient, MemorySessionManager

# Create the memory resource once (e.g. during setup, not per-request)
memory_client = MemoryClient(region_name='us-east-1')
memory = memory_client.create_memory_and_wait(
    name="StrandsAgentMemory",
    strategies=[
        {"summaryMemoryStrategy": {"name": "SessionSummarizer", "namespaces": ["summaries"]}},
        {"userPreferenceMemoryStrategy": {"name": "PreferenceLearner", "namespaces": ["preferences"]}},
        {"semanticMemoryStrategy": {"name": "FactExtractor", "namespaces": ["facts"]}},
    ],
)

# Per-session turn tracking and long-term search go through MemorySessionManager
session_manager = MemorySessionManager(memory_id=memory["memoryId"], region_name="us-east-1")

model = BedrockModel(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    region_name="us-east-1"
)

agent = Agent(
    model=model,
    system_prompt="You are a helpful assistant that remembers user preferences.",
)

def chat(actor_id: str, session_id: str, message: str) -> str:
    memories = session_manager.search_long_term_memories(
        query=message, namespace_prefix=f"preferences/{actor_id}", top_k=5
    )
    context = "\n".join(m["content"]["text"] for m in memories)

    response = agent(f"Known preferences:\n{context}\n\nUser: {message}")

    session_manager.add_turns(
        actor_id=actor_id,
        session_id=session_id,
        messages=[(message, "USER"), (str(response), "ASSISTANT")],
    )
    return str(response)
```

### LangGraph with Memory Checkpointing

```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from bedrock_agentcore.memory import MemoryClient

memory_client = MemoryClient(region_name='us-east-1')

class AgentCoreCheckpointer(MemorySaver):
    """LangGraph checkpointer using AgentCore Memory."""

    def __init__(self, memory_id: str, actor_id: str):
        self.memory_id = memory_id
        self.actor_id = actor_id
        self.client = MemoryClient(region_name='us-east-1')

    def get(self, thread_id: str):
        """Get checkpoint from memory."""
        turns = self.client.get_last_k_turns(
            memory_id=self.memory_id,
            actor_id=self.actor_id,
            session_id=thread_id,
            k=1,
        )
        if turns:
            return turns[-1]
        return None

    def put(self, thread_id: str, checkpoint: dict):
        """Save checkpoint to memory."""
        self.client.create_event(
            memory_id=self.memory_id,
            actor_id=self.actor_id,
            session_id=thread_id,
            messages=[(str(checkpoint), "OTHER")],
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
        {"semanticMemoryStrategy": {"name": "FactExtractor", "namespaces": ["shared-facts"]}},
        {"summaryMemoryStrategy": {"name": "SessionSummarizer", "namespaces": ["handoffs"]}},
    ],
)

memory_id = shared_memory["memoryId"]

def agent_handoff(from_agent: str, to_agent: str, context: dict):
    """Hand off conversation between agents."""

    # Store handoff context as a system-style event
    memory_client.create_event(
        memory_id=memory_id,
        actor_id="system",
        session_id=context["session_id"],
        messages=[
            (
                f"Handoff from {from_agent} to {to_agent}: {context.get('summary', '')}",
                "OTHER",
            )
        ],
    )

def get_shared_context(query: str) -> list:
    """Get shared context for any agent."""

    facts = memory_client.retrieve_memories(
        memory_id=memory_id,
        namespace="shared-facts",
        query=query,
        actor_id="system",
    )

    return facts
```

---

## Integration Patterns

### With AgentCore Runtime

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient

memory_client = MemoryClient(region_name='us-east-1')
app = BedrockAgentCoreApp()

@app.entrypoint
async def main(request):
    user_id = request.get("user_id")
    session_id = request.get("session_id")
    message = request.get("prompt")

    # Retrieve context
    memories = memory_client.retrieve_memories(
        memory_id=MEMORY_ID,
        namespace=f"/facts/{user_id}",
        query=message,
    )

    # Generate response with context
    response = await generate_response(message, memories)

    # Store interaction
    memory_client.create_event(
        memory_id=MEMORY_ID,
        actor_id=user_id,
        session_id=session_id,
        messages=[
            (message, "USER"),
            (response, "ASSISTANT"),
        ],
    )

    return {"response": response}
```

### With AgentCore Observability

```python
from opentelemetry import trace
from bedrock_agentcore.memory import MemoryClient

tracer = trace.get_tracer(__name__)
memory_client = MemoryClient(region_name='us-east-1')

def retrieve_with_tracing(memory_id: str, actor_id: str, namespace: str, query: str):
    """Memory retrieval with observability."""

    with tracer.start_as_current_span("memory.retrieve") as span:
        span.set_attribute("memory.id", memory_id)
        span.set_attribute("memory.actor_id", actor_id)
        span.set_attribute("memory.query", query)

        memories = memory_client.retrieve_memories(
            memory_id=memory_id,
            namespace=namespace,
            query=query,
            actor_id=actor_id,
        )

        span.set_attribute("memory.result_count", len(memories))

        return memories
```

---

## Advanced Features

### Branching

There is no `create_branch`/`create_checkpoint`/`restore_checkpoint` on `MemoryClient` - real branching is `fork_conversation`, which creates a named branch from an existing event and adds new messages to it in one call.

```python
# Fork a new branch from a specific event
branch = memory_client.fork_conversation(
    memory_id=memory_id,
    actor_id=user_id,
    session_id=session_id,
    root_event_id="event-123",
    branch_name="alternative-path",
    new_messages=[("What if we tried option B?", "USER")],
)

# Inspect branches and their events
branches = memory_client.list_branches(memory_id=memory_id, actor_id=user_id, session_id=session_id)
branch_events = memory_client.list_branch_events(
    memory_id=memory_id, actor_id=user_id, session_id=session_id, branch_name="alternative-path"
)

# See the full tree of branches for a session
tree = memory_client.get_conversation_tree(memory_id=memory_id, actor_id=user_id, session_id=session_id)
```

`MemorySessionManager`/`MemorySession` expose the same `fork_conversation` and `list_branches` for session-scoped code, plus `merge_branch_context` to fold a branch's context back into the main line.

---

## Best Practices

1. **Design memory architecture intentionally** - Plan namespaces and strategies before implementation.

2. **Set retention deliberately** - `eventExpiryDuration` is 3-365 days; there is no separate short-term "TTL in seconds" knob.

3. **Focus on extracting relevant information** - Configure strategies to capture only what's needed.

4. **Implement memory operation rhythm** - Store events after each turn, retrieve before generating.

5. **Use meaningful namespaces** - Organize memories by type (preferences, facts, summaries).

6. **Implement proper security** - Use KMS encryption for sensitive data.

7. **Monitor memory usage** - Use CloudWatch metrics to track extraction and retrieval.

8. **Handle extraction latency** - Long-term memories are extracted asynchronously; plan for delays.

9. **Test with realistic data** - Validate strategies with production-like conversations.

10. **Consider multi-tenancy** - Use actor IDs and namespace scoping to isolate user data.

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ResourceNotFoundException` | Invalid memory ID | Verify memory exists and is `ACTIVE` |
| `ValidationException` | Invalid parameters (e.g. `eventExpiryDuration` out of 3-365 range) | Check event format and required fields |
| Extraction never runs | Not enough events, or strategy not `ACTIVE` | Check strategy status and event volume |
| `ThrottlingException` | Rate limit exceeded | Implement exponential backoff |

### Debugging Tips

```bash
# Check memory status
agentcore memory status mem-abc123xyz

# Inspect actors, sessions, events, and extracted records interactively
agentcore memory show mem-abc123xyz

# List events for debugging (boto3, not a fictional CLI subcommand)
aws bedrock-agentcore list-events \
    --memory-id mem-abc123 \
    --actor-id user-123 \
    --session-id session-456
```

### Strategy Not Extracting

1. Verify strategy status is `ACTIVE`
2. Check enough events exist to trigger extraction
3. Review CloudWatch logs for extraction errors
4. Ensure events have proper message format (`(text, role)` tuples via the SDK, or `payload` list items via boto3)

---

## Limits & Quotas

| Resource | Default Limit | Adjustable |
|----------|--------------|------------|
| Memories per account | 100 | Yes |
| Strategies per memory | 10 | Yes |
| Events per session | 10,000 | Yes |
| Memory records per actor | 100,000 | Yes |
| Event payload size | 256 KB | No |
| Event retention (`eventExpiryDuration`) | 3-365 days | N/A (bounded range, not a single max) |
| Retrieval results (max) | 100 | No |
| Concurrent extractions | 10 | Yes |

These per-resource limits have not been individually re-verified against the live AWS quota tables in this pass beyond `eventExpiryDuration` (confirmed 3-365 days from the `CreateMemory` API model); treat the others as carried forward from the prior version of this doc.

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

1. **Set appropriate retention** - Don't retain events longer than needed (`eventExpiryDuration`).
2. **Optimize retrieval** - Use namespaces to filter and reduce search scope.
3. **Batch events** - Combine multiple turns into single events when possible.
4. **Monitor extraction** - Track strategy costs in CloudWatch.

---

## Related Services

- [AgentCore Runtime](./01-runtime.md) - Deploy agents with memory
- [AgentCore Gateway](./03-gateway.md) - Tool integration
- [AgentCore Observability](./08-observability.md) - Memory monitoring
- [AgentCore Evaluations](./09-evaluations.md) - Evaluate memory effectiveness
