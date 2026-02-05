# AgentCore Quickstart Example

Your first AI agent deployed to AWS in 5 minutes.

**Article**: [getting-started-short.md](../../getting-started-short.md)

## What This Demonstrates

- Minimal code to create an AgentCore-compatible agent
- Local development and testing with `agentcore dev`
- One-command deployment to AWS
- Invoking your deployed agent

## Prerequisites

- Python 3.10+
- AWS account with Bedrock AgentCore access enabled
- AWS credentials configured (`aws configure`)
- Region: us-east-1, us-west-2, ap-southeast-2, or eu-central-1

## Quick Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Test Locally

```bash
# Start the local development server
agentcore dev

# In another terminal, test your agent
agentcore invoke --dev "What is AgentCore?"
```

## Deploy to AWS

```bash
# Deploy to AgentCore Runtime (builds in AWS CodeBuild - no Docker needed)
agentcore launch

# Invoke your deployed agent
agentcore invoke '{"prompt": "Hello from the cloud!"}'
```

## Expected Output

### Local Testing
```
Starting local AgentCore development server on http://localhost:8080
```

### Deployment
```
Building agent with AWS CodeBuild...
Deploying to AgentCore Runtime...
✓ Agent deployed: arn:aws:bedrock-agentcore:us-east-1:123456789:runtime/my-first-agent
```

### Invocation
```json
{
  "result": "Hello! I'm your AI assistant running on AgentCore. How can I help you today?",
  "session_id": "abc123-def456"
}
```

## Next Steps

After deploying your first agent:

1. **Add Memory** for conversation context:
   ```bash
   agentcore memory create my-memory
   ```

2. **Connect Tools** via Gateway:
   ```bash
   agentcore gateway create-mcp-gateway --name my-gateway
   ```

3. **View Logs** in CloudWatch:
   - Log group: `/aws/bedrock-agentcore/runtimes/{agent-id}-DEFAULT`

## Code Structure

```
quickstart/
├── main.py           # Agent code with @app.entrypoint
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

When you run `agentcore launch`, the toolkit:
1. Creates a `.bedrock_agentcore.yaml` config file
2. Builds a container via AWS CodeBuild (ARM64 for Graviton)
3. Pushes to ECR
4. Deploys to AgentCore Runtime
5. Returns the agent ARN for invocation

## Learn More

- [AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [GitHub Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples)
- [AgentCore Product Page](https://aws.amazon.com/bedrock/agentcore/)
