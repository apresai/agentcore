Deploy Strands agents to production with memory and tools -- no infrastructure required.

![AgentCore Runtime](images/runtime-article.webp)

Ford Prefect survived fifteen years on Earth by knowing one thing: keep it simple, and always know where your towel is. Strands takes the same approach to agent frameworks -- minimal code, production ready, no unnecessary complications. It is, in the parlance of the Guide, a hoopy frood that really knows where its towel is.

But even Ford needed a ship off the planet. Hosting, memory, and tool wiring are still on you.

**AgentCore** handles it. Serverless microVMs, Memory for persistence, Gateway for tools -- one SDK.

## Prerequisites

- AWS account with Bedrock model access
- Python 3.10+
- `pip install bedrock-agentcore bedrock-agentcore-starter-toolkit strands-agents`

## Quick Start

```python
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient

model = BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0")
memory = MemoryClient()
# Gateway exposes tools over MCP -- connect with a standard MCP client
mcp_client = MCPClient(lambda: streamablehttp_client("YOUR_GATEWAY_URL"))
mcp_client.start()
agent = Agent(model=model, tools=mcp_client.list_tools_sync())
app = BedrockAgentCoreApp()

@app.entrypoint
async def invoke(request):
    prompt = request.get("prompt", "Hello!")
    user_id = request.get("user_id", "default")
    memories = memory.retrieve_memories(
        memory_id="mem-your-id", namespace=f"/actor/{user_id}/", query=prompt)
    context = "\n".join([m["content"] for m in memories])
    result = agent(f"Context:\n{context}\n\n{prompt}" if context else prompt)
    memory.create_event(memory_id="mem-your-id", actor_id=user_id,
        session_id="s1", messages=[(prompt, "USER"), (str(result), "ASSISTANT")])
    return {"response": str(result)}

if __name__ == "__main__":
    app.run()
```

## How to Run

Three commands. That is it. Ford would approve -- he always said the best technology is the kind you do not have to think about, like a really good towel.

```bash
agentcore create --agent-framework Strands --project-name myagent --memory STM_AND_LTM
agentcore deploy
agentcore invoke '{"prompt": "What tools do you have?"}'
```

**Key benefit**: Strands has first-class AgentCore support -- the simplest path to production. I/O wait is free, every request is microVM-isolated.

The Guide's entry on Strands would probably read: "Mostly harmless. Extremely useful." And honestly, that is the highest compliment a framework can get.

[View complete example on GitHub](https://github.com/apresai/agentcore/tree/main/articles/examples/overview/)

Docs: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/

#AWS #AI #AgentCore #Strands #Developers
