Deploy your first AI agent in 5 minutes. **DON'T PANIC.**

![AgentCore Getting Started](images/getting-started-article.webp)

No containers. No Kubernetes. No infrastructure headaches. If *The Hitchhiker's Guide to the Galaxy* had an entry on deploying AI agents, it would probably just say: "Mostly Harmless — when done correctly."

**Amazon Bedrock AgentCore** is a serverless platform for running AI agents at enterprise scale. Each session runs in an isolated microVM, your code deploys with 4 commands, and you only pay for actual compute (not while waiting for LLM responses).

## Prerequisites

- AWS account with credentials configured (`aws configure`)
- Python 3.10+

## Deploy Your First Agent

```bash
# 1. Install the AgentCore CLI and toolkit
pip install bedrock-agentcore bedrock-agentcore-starter-toolkit strands-agents

# 2. Create a new agent project
agentcore create my-first-agent

# 3. Deploy to AWS
cd my-first-agent
agentcore launch

# 4. Talk to your agent
agentcore invoke '{"prompt": "Hello! What can you do?"}'
```

That's it. Your agent is live. Four commands. Even Ford Prefect could manage it, and he once spent fifteen years trying to get a single entry in the Guide updated.

## What Just Happened?

- **Created** a Python agent using the Strands framework
- **Deployed** to serverless infrastructure via AWS CodeBuild (no Docker needed locally)
- **Invoked** your agent through the AgentCore Runtime API

The agent runs in a dedicated microVM with isolated CPU, memory, and filesystem. Sessions can run up to 8 hours. You're not charged during I/O wait time. Much like the Guide itself, AgentCore is more popular than the *Encyclopaedia Galactica* — and slightly cheaper.

## Next Steps

- Add **Memory** for conversation history: `agentcore memory create`
- Connect **Tools** via Gateway: `agentcore gateway create-mcp-gateway`
- Enable **Observability** for tracing in CloudWatch

Remember: a hoopy frood always knows where their towel is, and a hoopy developer always knows where their agent is deployed. In this case, it's AgentCore Runtime, and it just took you less time than ordering a Pan Galactic Gargle Blaster.

Docs: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/
Code: `articles/examples/quickstart/`

#AWS #AI #AgentCore #Agents
