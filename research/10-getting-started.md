# Getting Started with AgentCore

## Prerequisites

- Python 3.10 or newer
- AWS account with AgentCore permissions

## Quickstart (Under 5 Minutes)

### Step 0: Install the AgentCore CLI

```bash
pip install bedrock-agentcore-starter-toolkit
```

Verify Python version:
```bash
python3 --version
```

### Step 1: Create Your Agent

```bash
agentcore create
```

This command:
- Bootstraps a simple agent (choose framework: Strands, LangGraph, OpenAI Agents SDK, or Google ADK)
- Uses a foundation model (Amazon Bedrock, OpenAI, Gemini, Claude, Nova, Llama, Mistral)
- Produces Python project or IaC-ready code (Terraform or CDK)
- Automatically creates Gateway, Memory, and enables Observability
- Configures role, entrypoint, requirements, and auth model

### Optional: Test Locally

Start local dev server:
```bash
agentcore dev
```

In a separate terminal, test the agent:
```bash
agentcore invoke --dev "Hello!"
```

### Step 2: Deploy Your Agent

```bash
agentcore deploy
```

This command:
- Consolidates Python code into a zip file
- Deploys to AgentCore Runtime
- Configures CloudWatch logging

### Step 3: Invoke Your Agent

```bash
agentcore invoke '{"prompt": "tell me a joke"}'
```

If you see a joke, your agent is running!

## Next Steps

After your first agent:

1. **Add Memory**: Enable context-aware conversations
2. **Enable Browser**: Interact with web pages
3. **Connect Gateway**: Securely connect tools and APIs
4. **Explore Examples**: [GitHub Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples/)

## Available Interfaces

### AgentCore Starter Toolkit (CLI)
- Create agent projects
- Deploy agents
- Import existing agents
- Manage gateways, memory, configuration
- Observability and evaluations

### AgentCore Python SDK
- Python primitives for agent development
- Built-in support for runtime, memory, tools, identity, evaluations

### AWS SDK
- For operations not covered by AgentCore Python SDK
- Integration with other AWS services

### AgentCore MCP Server
- Works with MCP clients (Kiro, Cursor, Claude Code, Amazon Q CLI)
- Simplifies local → production deployment

### Console & AWS CLI
- Create and manage AgentCore services
- Test agents

## IAM Permissions

Refer to [IAM Permissions for AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-permissions.html) for required permissions.
