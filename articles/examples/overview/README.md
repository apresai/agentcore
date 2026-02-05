# AgentCore Overview Example

A minimal example demonstrating how to create and deploy an AI agent with AWS Bedrock AgentCore.

## What This Example Shows

- Creating an agent using the Strands framework
- Wrapping it with BedrockAgentCoreApp for deployment
- Testing locally before deploying to AWS
- Invoking a deployed agent programmatically

## Prerequisites

1. **AWS Account**: With Bedrock AgentCore access
2. **AWS CLI**: Configured with credentials (`aws configure`)
3. **Python 3.10+**: Required for AgentCore SDK
4. **Model Access**: Enable Claude or another model in Amazon Bedrock console

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Test locally
python main.py

# Deploy to AWS
agentcore configure -e main.py
agentcore launch
agentcore invoke '{"prompt": "What is AgentCore?"}'
```

## Files

| File | Description |
|------|-------------|
| `main.py` | Agent code with local testing and deployment |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |

## Expected Output

```
============================================================
AgentCore Overview - Basic Agent Example
============================================================

[Step 1] Creating agent with Strands framework...
Agent created successfully

[Step 2] Testing agent locally...
Input:  "What is AWS Bedrock AgentCore? Answer in one sentence."
Output: "AWS Bedrock AgentCore is a modular platform for building,
        deploying, and operating AI agents securely at enterprise scale."
Local test passed

[Step 3] Ready for deployment!
Run these commands to deploy:
----------------------------------------
  agentcore configure -e main.py
  agentcore launch
  agentcore invoke '{"prompt": "Hello!"}'
----------------------------------------

AgentCore provides:
  - MicroVM isolation: Each session runs in dedicated VM
  - 8-hour execution: Long-running tasks supported
  - Free I/O wait: No charge while waiting for LLM
  - Framework agnostic: LangGraph, CrewAI, custom code
  - Model agnostic: Claude, GPT, Gemini, Nova, Llama

============================================================
```

## Key Concepts

### BedrockAgentCoreApp

The wrapper that enables deployment to AgentCore Runtime:

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload, context):
    # payload: {"prompt": "user message"}
    # context: session_id, runtime_id, etc.
    return {"result": "agent response"}
```

### Strands Agent

AWS's open-source framework for building agents:

```python
from strands import Agent

agent = Agent(
    system_prompt="You are a helpful assistant."
)

response = agent("Hello!")
print(response.message)
```

## Next Steps

- Add Memory for conversation context
- Add Gateway for tool integration
- Add Identity for user authentication
- Add Observability for tracing

## Documentation

- [AgentCore Developer Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [GitHub Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples/)
