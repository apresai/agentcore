# AgentCore Gateway Example

Demonstrates creating an MCP Gateway using AWS Bedrock AgentCore.

## What This Shows

- Creating a Gateway resource with real AWS APIs
- Setting up IAM roles for Gateway
- Understanding the MCP endpoint configuration
- Proper resource cleanup

## Prerequisites

- AWS account with Bedrock AgentCore access
- AWS credentials configured (`aws configure`)
- Python 3.10+
- IAM permissions for:
  - `bedrock-agentcore:*`
  - `iam:CreateRole`
  - `iam:DeleteRole`

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Expected Output

```
============================================================
AgentCore Gateway Demo
============================================================

[Step 1] Creating Gateway...
  Waiting for IAM role to propagate...
✓ IAM role ready: agentcore-gateway-demo-xxxxx
✓ Gateway created: demo-gateway-xxxxx
  Waiting for Gateway to become ready...
✓ Gateway is READY

[Step 2] Gateway configuration:
  - Gateway ID: demo-gateway-xxxxx
  - Endpoint: https://demo-gateway-xxxxx.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp
  - Protocol: MCP (Model Context Protocol)
  - Auth: None (demo) - use IAM or JWT in production

[Info] Next steps to add tools:
  1. Create a Lambda function or API endpoint
  2. Create an API Key credential provider (for external APIs)
  3. Add a Gateway Target with tool schema
  4. Invoke tools via MCP protocol

✓ Gateway working successfully!

[Step 3] Cleaning up...
✓ Gateway deleted
✓ IAM role deleted

============================================================
Gateway Benefits:
  • Unified access: All tools via MCP protocol
  • Any backend: Lambda, REST APIs, external MCP servers
  • Semantic search: Find tools by natural language
  • Built-in auth: OAuth, JWT, API keys handled for you
  • 1-click integrations: Salesforce, Slack, Jira, GitHub
============================================================
```

## Key Concepts

### MCP Protocol

Gateway exposes tools via Model Context Protocol (MCP):
- `tools/list` - Enumerate available tools
- `tools/call` - Invoke a tool with arguments

### Target Types

| Type | Use Case |
|------|----------|
| Lambda | Custom logic, calculations |
| OpenAPI | Existing REST APIs |
| MCP Server | External MCP endpoints |
| Smithy | Type-safe API models |

### Adding Tools

To add tools to your Gateway, use the AgentCore CLI:

```bash
# Add a Lambda function as a tool
agentcore gateway create-mcp-gateway-target \
    --gateway-id <your-gateway-id> \
    --name MyCalculator \
    --type lambda \
    --lambda-arn arn:aws:lambda:us-east-1:123456789012:function:Calculator
```

## Learn More

- [Gateway Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)
- [MCP Protocol Spec](https://modelcontextprotocol.io/)
- [AgentCore Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples/)
