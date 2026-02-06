Your OpenAI Agents SDK code works locally. Now deploy it to production with security, scaling, and model flexibility.

![AgentCore Runtime](images/runtime-article.webp)

Switching spacecraft mid-flight sounds impossible, but any seasoned galactic hitchhiker will tell you it is mostly a matter of knowing which airlock to use. The OpenAI Agents SDK provides a clean API for building agents, but production deployment means managing infrastructure yourself -- and you are locked to one ship's engines. Time to transfer to a better vessel.

**AgentCore Runtime** deploys your OpenAI SDK agents to serverless infrastructure with microVM isolation and lets you swap in any model, including Bedrock models like Claude and Nova. Same crew, different ship, vastly better hyperspace drive.

## Prerequisites

- AWS account with Bedrock AgentCore access
- Python 3.10+
- Packages: `bedrock-agentcore`, `openai-agents`, `litellm`

## Quick Start

```python
# OpenAI Agents SDK on AgentCore — with Bedrock models
from agents import Agent, Runner
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Switch models by changing one string: "gpt-4o" → Bedrock Claude
agent = Agent(
    name="assistant",
    instructions="You are a helpful assistant running on AWS.",
    model="bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
)

app = BedrockAgentCoreApp()

@app.entrypoint()
async def invoke(request):
    prompt = request.get("prompt", "Hello!")
    result = await Runner.run(agent, prompt)
    return {"response": result.final_output}

if __name__ == "__main__":
    app.run()
```

## How to Run

```bash
pip install bedrock-agentcore openai-agents litellm

# Test locally
python main.py

# Deploy to AWS
agentcore configure -e main.py
agentcore launch
agentcore invoke '{"prompt": "What can you do?"}'
```

**Key benefit**: Write once with OpenAI Agents SDK, deploy anywhere. Switch between GPT-4o, Claude, Nova, or Llama by changing one string -- no other code changes required. As any interstellar traveler knows, the best migrations are the ones where you do not have to repack your luggage.

Next steps: add Gateway for enterprise API tools and Memory for conversation persistence. DON'T PANIC -- your agent code survives the jump intact.

Docs: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/

#AWS #AI #AgentCore #OpenAI #Developers
