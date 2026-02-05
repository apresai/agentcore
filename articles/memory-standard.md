Your AI agent forgets everything after each session. Here's the fix:

![AgentCore Memory](images/memory-article.webp)

Every conversation starts from zero. User mentions they prefer window seats? Gone. They told you their budget last week? Forgotten. Without memory, your agents can't build relationships or learn from interactions.

AgentCore Memory solves this with two memory types working together: **short-term memory** maintains context within a session (so "What about tomorrow?" knows you're still talking about Seattle weather), while **long-term memory** automatically extracts and stores preferences, facts, and summaries across sessions.

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

### Create Memory and Store Events

```python
import boto3
from datetime import datetime, timezone

# Initialize clients
control = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
data = boto3.client('bedrock-agentcore', region_name='us-east-1')

# Create memory with preference extraction
response = control.create_memory(
    name="CustomerMemory",
    eventExpiryDuration=7,  # days
    memoryStrategies=[{
        'userPreferenceMemoryStrategy': {
            'name': 'PreferenceLearner',
            'namespaces': ['preferences']
        }
    }]
)
memory_id = response['memory']['id']

# Store a conversation (short-term memory)
data.create_event(
    memoryId=memory_id,
    actorId="user_123",
    sessionId="session_456",
    eventTimestamp=datetime.now(timezone.utc),
    payload=[
        {'conversational': {'role': 'USER', 'content': {'text': 'I prefer window seats'}}},
        {'conversational': {'role': 'ASSISTANT', 'content': {'text': 'Got it!'}}}
    ]
)

# Retrieve conversation history
events = data.list_events(
    memoryId=memory_id,
    actorId="user_123",
    sessionId="session_456"
)
print(f"Events: {len(events['events'])}")
```

### Retrieve Long-Term Memories

```python
# Semantic search across extracted preferences (async extraction)
records = data.retrieve_memory_records(
    memoryId=memory_id,
    namespace="preferences",
    searchCriteria={'searchQuery': "travel preferences", 'topK': 5}
)

for record in records.get('memoryRecords', []):
    print(f"Remembered: {record['content']['text']}")
```

## Running the Example

```bash
cd articles/examples/memory
pip install -r requirements.txt
python main.py
```

Expected output:
```
✓ Memory created: MemoryExample_xxx
✓ Event stored successfully
✓ Short-term events retrieved: 1 event(s)
  - USER: I prefer window seats...
✓ Memory working successfully!
```

## Key Benefits

- **Zero infrastructure**: Fully managed storage, extraction, and retrieval
- **Automatic extraction**: Long-term memories are extracted asynchronously without extra code
- **Semantic search**: Find relevant memories using natural language queries

## Common Patterns

Teams typically use Memory for customer support agents that recall past issues, booking assistants that remember preferences, and multi-agent systems where specialized agents share context through a common memory store.

## Next Steps

Start with short-term memory for session context, then add long-term strategies as you identify what your agent should remember across sessions.

📚 Documentation: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html
💻 Full runnable example: `articles/examples/memory/`
🔧 GitHub samples: https://github.com/awslabs/amazon-bedrock-agentcore-samples/

#AWS #AI #AgentCore #Memory #Developers
