# Memory

> Short-term and long-term context management for stateful AI agents

## Overview

AgentCore Memory addresses the fundamental challenge of statelessness in AI agents. Without memory, agents treat each interaction as isolated, with no knowledge of previous conversations. Memory provides the capability for agents to build coherent understanding over time.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Memory Service                           │
├─────────────────────────────┬───────────────────────────────────┤
│      Short-Term Memory      │       Long-Term Memory            │
│                             │                                   │
│  • Turn-by-turn context     │  • Cross-session insights         │
│  • Session duration         │  • Permanent storage              │
│  • Multi-turn continuity    │  • User preferences               │
│                             │  • Learned facts                  │
│  "What about tomorrow?"     │  "I prefer window seats"          │
│  (knows you asked about     │  (remembered from 3 months ago)   │
│   Seattle weather)          │                                   │
└─────────────────────────────┴───────────────────────────────────┘
```

## Key Features

### Short-Term Memory

Captures turn-by-turn interactions within a single session.

**Example**:
```
User: What's the weather in Seattle?
Agent: It's 65°F and partly cloudy in Seattle today.

User: What about tomorrow?
       ^^^^^^^^^^^^^^^^
       Short-term memory provides context that
       "tomorrow" refers to Seattle weather
```

### Long-Term Memory

Automatically extracts and stores key insights across sessions.

**Example**:
```
Session 1 (January):
User: I always prefer window seats when I fly.

Session 2 (March):
Agent: I've booked you a window seat on the flight.
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
       Long-term memory recalled preference from January
```

### Shared Memory Stores

Memory stores can be shared across multiple agents:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Shared Memory Store                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Agent A   │  │   Agent B   │  │   Agent C   │            │
│  │  (Support)  │  │  (Booking)  │  │  (Billing)  │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                │                    │
│         └────────────────┼────────────────┘                    │
│                          │                                     │
│                          ▼                                     │
│              ┌─────────────────────┐                          │
│              │   Shared Context    │                          │
│              │                     │                          │
│              │  • User preferences │                          │
│              │  • Conversation     │                          │
│              │  • Transaction      │                          │
│              └─────────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Memory Types Comparison

| Aspect | Short-Term | Long-Term |
|--------|------------|-----------|
| **Scope** | Single session | Cross-session |
| **Persistence** | Session duration | Permanent |
| **Content** | Messages, context | Facts, preferences |
| **Extraction** | Manual/automatic | Automatic |
| **Use case** | Multi-turn conversations | Personalization |

---

## Quick Start

There is no `create_session()`/`add_message()`/`get_messages()`/`store_fact()`/`get_facts()`. Create a memory resource once (with a long-term strategy if you want automatic fact extraction), then record and retrieve conversation turns directly against it.

### Create a Memory Resource

```python
from bedrock_agentcore.memory import MemoryClient

memory = MemoryClient(region_name="us-east-1")

# Waits for the memory to reach ACTIVE. A semanticMemoryStrategy is what
# gives you automatic long-term fact extraction below.
mem = memory.create_memory_and_wait(
    name="MyAgentMemory",
    strategies=[
        {"semanticMemoryStrategy": {"name": "FactExtractor", "namespaces": ["facts"]}},
    ],
)

memory_id = mem["memoryId"]
```

### Add Messages (Short-Term)

`messages` is a list of `(text, role)` tuples, not `role=`/`content=` keyword calls:

```python
# Store a conversation turn
memory.create_event(
    memory_id=memory_id,
    actor_id="user-123",
    session_id="session-abc",
    messages=[
        ("My name is Alice and I work at Acme Corp.", "USER"),
        ("Nice to meet you, Alice! How can I help you today?", "ASSISTANT"),
    ],
)

# Later in the conversation, retrieve recent turns
turns = memory.get_last_k_turns(
    memory_id=memory_id,
    actor_id="user-123",
    session_id="session-abc",
    k=5,
)
# Agent knows user is Alice from Acme Corp
```

### Retrieve Facts (Long-Term)

Long-term facts aren't stored with an explicit `store_fact()` call - the `semanticMemoryStrategy` attached above extracts them automatically from events. Retrieve them with a semantic query:

```python
memories = memory.retrieve_memories(
    memory_id=memory_id,
    namespace="facts",
    query="communication preferences and timezone",
    actor_id="user-123",
    top_k=5,
)

for record in memories:
    print(f"- {record['content']['text']}")
```

### Automatic Insight Extraction

There is no `extract_insights=True` flag - extraction is enabled by attaching a long-term strategy (`semanticMemoryStrategy`, `userPreferenceMemoryStrategy`, `summaryMemoryStrategy`, or `episodicMemoryStrategy`) when the memory is created, as shown above. Once attached, insights are extracted automatically from every event:

```python
memory.create_event(
    memory_id=memory_id,
    actor_id="user-123",
    session_id="session-abc",
    messages=[
        ("I'm allergic to peanuts, so please avoid any recommendations with nuts.", "USER"),
    ],
)

# The FactExtractor strategy extracts and stores something like:
# "User is allergic to peanuts" - retrievable later via retrieve_memories()
```

---

## boto3 Alternative

`bedrock-agentcore-memory` isn't a real botocore service - memory events live on the `bedrock-agentcore` data-plane client, and the memory resource itself is created via `bedrock-agentcore-control`. There is no `create_session`/`put_message`/`get_messages`/`put_memory_record` operation on either.

```python
import boto3

control_client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
data_client = boto3.client('bedrock-agentcore', region_name='us-east-1')

# Create the memory resource (raw output nests everything under a `memory` key)
response = control_client.create_memory(
    name='CustomerSupportMemory',
    eventExpiryDuration=90,  # days, 3-365, required
)
memory_id = response['memory']['id']

# Store a conversation turn
data_client.create_event(
    memoryId=memory_id,
    actorId='user-123',
    sessionId='session-abc',
    eventTimestamp='2024-01-15T10:30:00Z',
    payload=[{'conversational': {'role': 'USER', 'content': {'text': 'Hello!'}}}],
)

# List recent events
events = data_client.list_events(
    memoryId=memory_id,
    actorId='user-123',
    sessionId='session-abc',
)
```

---

## Framework Integration

There is no `strands.memory.AgentCoreMemory`, `langgraph.checkpoint.agentcore.AgentCoreMemorySaver`, or `llama_index.storage.chat_store.agentcore.AgentCoreChatStore` - none of these frameworks ship an AgentCore-specific memory adapter. Wire memory in directly with `MemoryClient`/`MemorySessionManager` instead.

### Strands

```python
from strands import Agent
from strands.models import BedrockModel
from bedrock_agentcore.memory import MemoryClient, MemorySessionManager

# Create the memory resource once (e.g. during setup, not per-request)
memory_client = MemoryClient(region_name="us-east-1")
memory = memory_client.create_memory_and_wait(
    name="StrandsAgentMemory",
    strategies=[
        {"userPreferenceMemoryStrategy": {"name": "PreferenceLearner", "namespaces": ["preferences"]}},
    ],
)

# Per-session turn tracking and long-term search go through MemorySessionManager
session_manager = MemorySessionManager(memory_id=memory["memoryId"], region_name="us-east-1")

model = BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0", region_name="us-east-1")
agent = Agent(model=model, system_prompt="You are a helpful assistant.")

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

### LangGraph

LangGraph's own `BaseCheckpointSaver` is the extension point - back it with `MemoryClient` rather than reaching for a nonexistent AgentCore-provided saver:

```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from bedrock_agentcore.memory import MemoryClient

class AgentCoreCheckpointer(MemorySaver):
    """LangGraph checkpointer backed by AgentCore Memory."""

    def __init__(self, memory_id: str, actor_id: str):
        self.memory_id = memory_id
        self.actor_id = actor_id
        self.client = MemoryClient(region_name="us-east-1")

    def get(self, thread_id: str):
        turns = self.client.get_last_k_turns(
            memory_id=self.memory_id,
            actor_id=self.actor_id,
            session_id=thread_id,
            k=1,
        )
        return turns[-1] if turns else None

    def put(self, thread_id: str, checkpoint: dict):
        self.client.create_event(
            memory_id=self.memory_id,
            actor_id=self.actor_id,
            session_id=thread_id,
            messages=[(str(checkpoint), "OTHER")],
        )

checkpointer = AgentCoreCheckpointer(memory_id="mem-abc123xyz", actor_id="user-123")

graph = StateGraph(AgentState)
# ... build graph ...
agent = graph.compile(checkpointer=checkpointer)
```

---

## Shared Memory Patterns

### Multi-Agent Collaboration

There is no `create_memory_store(shared=True)` - a single memory resource shared by multiple agents *is* the shared store, since events and long-term facts are keyed by `actor_id`/namespace, not by agent:

```python
from bedrock_agentcore.memory import MemoryClient

memory = MemoryClient(region_name="us-east-1")

shared_memory = memory.create_memory_and_wait(
    name="TeamSharedMemory",
    strategies=[
        {"semanticMemoryStrategy": {"name": "FactExtractor", "namespaces": ["shared-facts"]}},
    ],
)
memory_id = shared_memory["memoryId"]

# Agent A writes to the shared session
memory.create_event(
    memory_id=memory_id,
    actor_id="user-123",
    session_id="session-abc",
    messages=[("I have a billing issue", "USER")],
)

# Agent B reads the same session
turns = memory.get_last_k_turns(
    memory_id=memory_id,
    actor_id="user-123",
    session_id="session-abc",
    k=5,
)
# Agent B sees the billing issue from Agent A's turn
```

---

## Best Practices

### 1. Scope Memory Appropriately

| Pattern | When to Use |
|---------|-------------|
| User-scoped | Personal preferences, history |
| Session-scoped | Single task context |
| Shared store | Multi-agent workflows |

### 2. Set an Appropriate Event Expiry

There is no per-session `delete_session()` - short-term events age out automatically based on `eventExpiryDuration` (3-365 days, set when the memory is created). Pick a value that matches how long conversations need to stay in short-term memory:

```python
memory.create_memory_and_wait(
    name="MyAgentMemory",
    event_expiry_days=30,
    strategies=[...],
)
```

### 3. Use Semantic Search for Retrieval

```python
# Search long-term memory semantically - there is no search_facts() method
relevant_facts = memory.retrieve_memories(
    memory_id=memory_id,
    namespace="preferences",
    query="travel preferences",
    actor_id="user-123",
    top_k=5,
)
```

### 4. Handle Memory Gracefully

```python
# Check if any facts exist before assuming - there is no get_facts() method
facts = memory.retrieve_memories(
    memory_id=memory_id,
    namespace="facts",
    query="user context",
    actor_id="user-123",
)

if not facts:
    # New user, no prior context
    system_prompt = "You are a helpful assistant."
else:
    # Build context from facts
    context = "\n".join(f["content"]["text"] for f in facts)
    system_prompt = f"You are a helpful assistant. User context:\n{context}"
```

---

## Pricing

| Operation | Cost |
|-----------|------|
| Short-term message | Per event |
| Long-term record | Per record stored |
| Search/retrieval | Per operation |

> [!TIP]
> Set `event_expiry_days` to the shortest retention that fits your use case - there's no manual per-session delete, so this is what keeps short-term storage costs down.

---

## When to Use Memory

| Scenario | Recommendation |
|----------|----------------|
| Multi-turn conversations | ✅ Short-term memory |
| User personalization | ✅ Long-term memory |
| Multi-agent workflows | ✅ Shared memory stores |
| Stateless single queries | Skip memory |

---

## Related Services

| Service | Integration |
|---------|-------------|
| [Runtime](runtime.md) | Hosts agents that use memory |
| [Identity](identity.md) | User identity for memory scoping |
| [Observability](observability.md) | Track memory operations |

---

## Resources

- [Memory Developer Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)
- [Detailed Research](../../research/02-memory.md)
- [Memory Examples](../../articles/examples/memory/)
