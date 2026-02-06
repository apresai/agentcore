# AgentCore LangGraph Example

Demonstrates deploying a LangGraph agent to AWS Bedrock AgentCore Runtime with Memory integration.

## What This Shows

- Building a research agent with LangGraph's StateGraph
- Deploying to AgentCore Runtime with `agentcore deploy`
- Integrating AgentCore Memory for cross-session persistence
- Conditional graph routing based on iteration count

## Prerequisites

- AWS account with Bedrock AgentCore access
- AWS credentials configured (`aws configure`)
- Python 3.10+
- IAM permissions for:
  - `bedrock-agentcore:*`
  - `bedrock:InvokeModel`

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
# Test locally
python main.py

# Deploy to AgentCore Runtime
agentcore create --framework langgraph --model-provider bedrock --name research-agent
agentcore deploy --region us-east-1
agentcore invoke '{"prompt": "Explain graph-based agent architectures"}'
```

## Expected Output

```
============================================================
AgentCore LangGraph Agent
============================================================

[Step 1] Building LangGraph research agent...
✓ Graph compiled: research -> analyze -> END

[Step 2] Testing locally...
  Input: "Explain the benefits of graph-based agent orchestration"
  Executing graph...
✓ Research completed (2 iterations)
✓ Analysis generated

[Step 3] Ready for deployment:
  agentcore deploy --region us-east-1

============================================================
```

## Key Concepts

### LangGraph + AgentCore

| LangGraph Provides | AgentCore Provides |
|--------------------|--------------------|
| Graph-based orchestration | Serverless hosting (microVMs) |
| Conditional routing | Auto-scaling to zero |
| State management | Memory persistence |
| Tool integration | Gateway for MCP tools |

### Graph Structure

```
research -> (should_continue?) -> research (loop)
                               -> analyze -> END
```

## Learn More

- [AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [AgentCore Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples/)
