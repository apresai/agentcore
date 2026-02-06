Amazon Bedrock Agents or AgentCore? Here's how to decide:

![AgentCore vs Bedrock Agents](images/comparison-article.webp)

In *The Hitchhiker's Guide to the Galaxy*, Earth's entry was famously reduced to two words: "Mostly Harmless." Accurate, perhaps, but not exactly comprehensive. AWS has a similar problem with AI agents -- two offerings, two levels of depth, and picking the wrong one means rebuilding later.

**Amazon Bedrock Agents** is the "Mostly Harmless" entry: configuration-based, concise, gets the job done for simple cases. Define agents, connect action groups and knowledge bases, deploy without code. Best for managed simplicity.

**Amazon Bedrock AgentCore** is the full Guide entry -- thorough, flexible, and prepared for anything the galaxy throws at you. Code-first: bring any framework (LangGraph, Strands, CrewAI), any model (Claude, Nova, GPT-4), deploy to isolated microVMs. Best for flexibility and control.

## Comparison Table

| Aspect | Bedrock Agents | AgentCore |
|--------|----------------|-----------|
| **Framework** | Bedrock-native | Any (LangGraph, Strands, custom) |
| **Models** | Bedrock models | Any provider |
| **Customization** | Config-based | Full code control |
| **Execution Time** | Lambda limits | Up to 8 hours |
| **Tool Integration** | Action groups | MCP Gateway |
| **Memory** | 30-day max | Configurable |
| **Session Isolation** | Standard | MicroVM per session |
| **Pricing** | Per-invocation | Consumption-based |

## When to Choose AgentCore

Much like the actual *Hitchhiker's Guide* -- with its thousand or so pages on the drinking customs of Betelgeuse -- AgentCore covers territory that the short entry simply cannot.

**Framework flexibility**: Your team uses LangGraph, CrewAI, or a custom framework. AgentCore runs any Python-based agent. Being locked to one framework is like being stuck on one planet -- fine until you need to go somewhere interesting.

**Long-running workloads**: Research agents or complex reasoning exceeding standard timeouts. AgentCore supports 8-hour sessions.

**Multi-model architectures**: Use Claude for reasoning, Haiku for speed, GPT-4 for specialized tasks in one agent.

**Enterprise security**: MicroVM isolation ensures complete session separation. Integrates with Okta, Entra ID.

## When to Choose Bedrock Agents

**Rapid prototyping**: Get agents running in hours through console configuration.

**Standard patterns**: Customer support, RAG, simple automation where managed defaults work.

**Minimal infrastructure**: Fully managed means no runtime or scaling concerns.

## Decision Framework

```
START: Existing agent framework?
  YES --> AgentCore (bring your framework)
  NO  --> Need sessions > 15 minutes?
            YES --> AgentCore
            NO  --> Need non-Bedrock models?
                      YES --> AgentCore
                      NO  --> Bedrock Agents (managed)
```

## Framework Flexibility Example

AgentCore lets you swap frameworks without changing infrastructure:

```python
# Strands Agents (AWS native)
from strands import Agent
from strands.models import BedrockModel
agent = Agent(model=BedrockModel("us.anthropic.claude-haiku-4-5-20251001-v1:0"))

# LangGraph (graph-based workflows)
from langgraph.graph import StateGraph
graph = StateGraph(AgentState)

# CrewAI (role-based collaboration)
from crewai import Agent, Crew
researcher = Agent(role="Researcher", ...)
```

All three deploy to AgentCore Runtime the same way.

## Migration Path

Upgrading from "Mostly Harmless" to the full entry is easier than you might expect.

**Bedrock Agents to AgentCore**: Export action groups, convert to MCP tools via Gateway. Expect 2-4 weeks for complex agents.

**Self-hosted to AgentCore**: Keep your framework code unchanged. Replace infrastructure (ECS, Lambda orchestration) with AgentCore Runtime.

## Recommendation

Start with Bedrock Agents if you're new to AI agents. Move to AgentCore when you hit limitations: framework lock-in, timeout constraints, or multi-model needs.

Most production deployments eventually need AgentCore's flexibility. The galaxy is a big place, and "Mostly Harmless" only gets you so far -- sooner or later, you will want the full Guide.

## Running the Example

```bash
cd articles/examples/comparison
pip install -r requirements.txt
python main.py
```

## Resources

- Documentation: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/
- Bedrock Agents: https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html
- Full example: `articles/examples/comparison/`

#AWS #AI #AgentCore #BedrockAgents
