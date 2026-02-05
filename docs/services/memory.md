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

### Create a Memory Session

```python
from bedrock_agentcore.memory import MemoryClient

memory = MemoryClient()

# Create session for short-term memory
session = memory.create_session(
    agent_id="my-agent",
    user_id="user-123"
)

print(f"Session ID: {session.session_id}")
```

### Add Messages (Short-Term)

```python
# Add conversation messages
session.add_message(
    role="user",
    content="My name is Alice and I work at Acme Corp."
)

session.add_message(
    role="assistant",
    content="Nice to meet you, Alice! How can I help you today?"
)

# Later in conversation, retrieve context
messages = session.get_messages()
# Agent knows user is Alice from Acme Corp
```

### Store Facts (Long-Term)

```python
# Store explicit facts
memory.store_fact(
    agent_id="my-agent",
    user_id="user-123",
    fact="User prefers formal communication style"
)

memory.store_fact(
    agent_id="my-agent",
    user_id="user-123",
    fact="User's timezone is PST"
)

# Retrieve facts in future sessions
facts = memory.get_facts(
    agent_id="my-agent",
    user_id="user-123"
)

for fact in facts:
    print(f"- {fact.content}")
```

### Automatic Insight Extraction

```python
# Enable automatic extraction
session = memory.create_session(
    agent_id="my-agent",
    user_id="user-123",
    extract_insights=True  # Automatically extracts facts
)

# During conversation, insights are auto-extracted
session.add_message(
    role="user",
    content="I'm allergic to peanuts, so please avoid any recommendations with nuts."
)

# System automatically extracts and stores:
# "User is allergic to peanuts"
```

---

## boto3 Alternative

```python
import boto3

memory = boto3.client('bedrock-agentcore-memory')

# Create session
response = memory.create_session(
    agentId='my-agent',
    userId='user-123'
)
session_id = response['sessionId']

# Add message
memory.put_message(
    sessionId=session_id,
    role='user',
    content='Hello!'
)

# Get messages
messages = memory.get_messages(sessionId=session_id)

# Store long-term fact
memory.put_memory_record(
    agentId='my-agent',
    userId='user-123',
    content='User prefers email communication'
)
```

---

## Framework Integration

### Strands

```python
from strands import Agent
from strands.models import BedrockModel
from strands.memory import AgentCoreMemory

model = BedrockModel(model_id="anthropic.claude-3-sonnet-20240229-v1:0")

# Configure memory
memory = AgentCoreMemory(
    agent_id="my-agent",
    short_term=True,
    long_term=True
)

agent = Agent(
    model=model,
    memory=memory,
    system_prompt="You are a helpful assistant."
)

# Memory is automatically managed
response = agent.run(
    "My name is Alice",
    user_id="user-123"
)
```

### LangGraph

```python
from langgraph.checkpoint.agentcore import AgentCoreMemorySaver

# Use as checkpoint saver
memory_saver = AgentCoreMemorySaver(agent_id="my-agent")

app = workflow.compile(checkpointer=memory_saver)

# State is automatically persisted
config = {"configurable": {"thread_id": "user-123"}}
response = app.invoke({"messages": [...]}, config)
```

### LlamaIndex

```python
from llama_index.storage.chat_store.agentcore import AgentCoreChatStore

chat_store = AgentCoreChatStore(agent_id="my-agent")

# Use with chat engine
chat_engine = index.as_chat_engine(
    chat_store=chat_store,
    chat_mode="context"
)
```

---

## Shared Memory Patterns

### Multi-Agent Collaboration

```python
# Create shared memory store
memory = MemoryClient()

shared_store = memory.create_memory_store(
    name="customer-context",
    shared=True
)

# Agent A writes
session_a = memory.create_session(
    agent_id="support-agent",
    user_id="user-123",
    memory_store_id=shared_store.id
)
session_a.add_message(role="user", content="I have a billing issue")

# Agent B reads same context
session_b = memory.create_session(
    agent_id="billing-agent",
    user_id="user-123",
    memory_store_id=shared_store.id
)
# Agent B sees the billing issue from Agent A's session
```

---

## Best Practices

### 1. Scope Memory Appropriately

| Pattern | When to Use |
|---------|-------------|
| User-scoped | Personal preferences, history |
| Session-scoped | Single task context |
| Shared store | Multi-agent workflows |

### 2. Clean Up Old Sessions

```python
# Delete old sessions to manage costs
memory.delete_session(session_id=old_session_id)
```

### 3. Use Semantic Search for Retrieval

```python
# Search long-term memory semantically
relevant_facts = memory.search_facts(
    agent_id="my-agent",
    user_id="user-123",
    query="travel preferences",
    limit=5
)
```

### 4. Handle Memory Gracefully

```python
# Check if memory exists before assuming
facts = memory.get_facts(agent_id="my-agent", user_id="user-123")

if not facts:
    # New user, no prior context
    system_prompt = "You are a helpful assistant."
else:
    # Build context from facts
    context = "\n".join([f.content for f in facts])
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
> Delete old sessions to avoid unnecessary storage costs.

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
