# AgentCore Framework Flexibility Example

This example demonstrates AgentCore's key advantage over Amazon Bedrock Agents: framework flexibility.

## What This Shows

With **Bedrock Agents**, you use its native framework only. With **AgentCore**, you can use:

- **Strands Agents** - AWS's simple, native framework
- **LangGraph** - Graph-based workflows for complex multi-step agents
- **CrewAI** - Role-based multi-agent collaboration
- **LlamaIndex** - Data-focused agents with strong RAG
- **Any custom framework** - Your own implementation

All deploy to AgentCore Runtime the same way.

## Running the Example

```bash
# Install dependencies
pip install -r requirements.txt

# Run the demo
python main.py
```

## Expected Output

```
==================================================
AgentCore Framework Flexibility Demo
==================================================

This demonstrates AgentCore's key advantage: framework flexibility.
Unlike Bedrock Agents, you can use any framework and switch without
changing your infrastructure.

1. Strands Agent (AWS native, simplest API):
----------------------------------------
   Prompt: What is the capital of France?
   Response: The capital of France is Paris.

2. LangGraph Agent (graph-based workflows):
----------------------------------------
   Prompt: What is the capital of France?
   Response: The capital of France is Paris.

==================================================
Key Takeaway:
==================================================

Both frameworks:
- Deploy to AgentCore Runtime the same way
- Get microVM session isolation automatically
- Use AgentCore Memory for context persistence
- Connect to tools via AgentCore Gateway
- Have full observability through CloudWatch

With Bedrock Agents, you're limited to its native framework.
With AgentCore, choose the framework that fits your use case.
```

## Decision Framework

Choose **Bedrock Agents** if:
- You want managed simplicity
- Standard patterns (support bot, RAG) fit your needs
- You don't need custom framework features
- Quick prototyping is the priority

Choose **AgentCore** if:
- You have an existing agent framework
- You need sessions longer than 15 minutes
- You want non-Bedrock models (OpenAI, Gemini)
- You need full code control
- Enterprise security (microVM isolation) is required

## Related Article

See `/articles/agentcore-vs-bedrock-agents-standard.md` for the full comparison.

## Prerequisites

- AWS account with Bedrock model access
- Python 3.10+
- AWS credentials configured
