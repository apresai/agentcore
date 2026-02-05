# AgentCore Memory Example

Runnable example demonstrating short-term and long-term memory from the article:
[Memory Article](../../memory-standard.md)

## Prerequisites

- AWS account with Bedrock AgentCore access
- Python 3.10+ installed
- AWS credentials configured (`aws configure`)

## Setup

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set region (optional, defaults to us-east-1)
export AWS_REGION=us-east-1
```

## Run

```bash
python main.py
```

## Expected Output

```
✓ AgentCore clients initialized

Creating memory: MemoryExample_1234567890...
✓ Memory created: MemoryExample_1234567890-xxxxx
Waiting for memory to become active (this may take 2-3 minutes)...
  Status: CREATING...
  Status: CREATING...
✓ Memory is active

Storing conversation event...
✓ Event stored successfully

Retrieving short-term memory...
✓ Short-term events retrieved: 1 event(s)
  - USER: I prefer window seats and vegetarian meals on flig...
  - ASSISTANT: I've noted your preferences: window seats and vege...

Checking for long-term memories (async extraction)...
  (Long-term extraction is async - memories will appear after processing)

✓ Memory working successfully!

Memory ID: MemoryExample_1234567890-xxxxx
Use this ID to retrieve memories in future sessions.

Cleaning up: Deleting memory MemoryExample_1234567890...
✓ Memory deleted successfully
```

## What This Demonstrates

1. **Memory Creation** - Creating a memory resource with a preference extraction strategy
2. **Short-Term Storage** - Storing conversation events with the proper payload format
3. **Short-Term Retrieval** - Getting recent conversation history within a session
4. **Long-Term Extraction** - How preferences are extracted asynchronously
5. **Cleanup** - Proper resource deletion

## API Notes

- Memory names must be alphanumeric with underscores only, starting with a letter
- Event expiry duration is in days (min 3, max 365)
- Roles must be uppercase: `USER`, `ASSISTANT`, `TOOL`, `OTHER`
- Payload uses the `conversational` wrapper with `content.text` structure
- Memory creation takes 2-3 minutes to become ACTIVE

## Learn More

- [AgentCore Memory Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)
- [GitHub Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples/)
