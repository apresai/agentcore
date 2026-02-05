# AgentCore Runtime Example

Runnable example demonstrating how to deploy an AI agent to AWS Bedrock AgentCore Runtime.

**Article**: [runtime-short.md](../../runtime-short.md)

## What This Demonstrates

- Creating an agent with the AgentCore SDK
- Using the Strands agent framework
- Deploying to serverless microVM infrastructure
- Both SDK and boto3 approaches

## Prerequisites

- Python 3.10+
- AWS account with Bedrock AgentCore access enabled
- AWS credentials configured (`aws configure`)
- Region: us-east-1, us-west-2, ap-southeast-2, or eu-central-1

## Setup

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure AWS (if not already done)
aws configure
```

## Run

```bash
# Run the example locally
python main.py
```

## Expected Output

```
============================================================
AgentCore Runtime - Agent Deployment Example
============================================================

[Step 1] Creating agent with AgentCore SDK...
✓ Agent created successfully

[Step 2] Testing agent locally...
  Test input: {'prompt': 'What is 2 + 2?'}
✓ Local test passed (agent is ready)

[Step 3] Deploy to AgentCore Runtime:
  --------------------------------------------------
  # Configure the agent
  agentcore configure -e main.py

  # Deploy to AWS
  agentcore launch

  # Test the deployed agent
  agentcore invoke '{"prompt": "Hello, AgentCore!"}'
  --------------------------------------------------

✓ Ready for deployment with: agentcore launch

Key benefits of AgentCore Runtime:
  • MicroVM isolation - each session in dedicated VM
  • Up to 8-hour execution time
  • I/O wait is free (no charge while waiting for LLM)
  • 100MB payload support for multi-modal content

============================================================
```

## Deploy to AWS

After running `main.py` locally, deploy to AgentCore:

```bash
# Configure your agent
agentcore configure -e main.py

# Deploy to AgentCore Runtime
agentcore launch

# Invoke your deployed agent
agentcore invoke '{"prompt": "Tell me a joke"}'
```

## Learn More

- [AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [GitHub Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples)
- [AgentCore Product Page](https://aws.amazon.com/bedrock/agentcore/)
