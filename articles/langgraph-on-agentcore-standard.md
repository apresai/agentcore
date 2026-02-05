Your LangGraph agents deserve production infrastructure. Here's how to deploy them — without managing a single server:

![AgentCore Runtime](images/runtime-article.webp)

LangGraph gives you graph-based orchestration: define nodes for reasoning, tool use, and decision-making, connect them with conditional edges, and let the framework handle execution flow. It is one of the most popular ways to build structured AI agents. But running LangGraph in production means Kubernetes clusters, scaling policies, session management, and security isolation — infrastructure that has nothing to do with your agent logic.

**AgentCore Runtime** eliminates that entire layer. Deploy your LangGraph agent with the CLI, get microVM isolation per session, and run graph executions for up to 8 hours. Add AgentCore Memory for state persistence across sessions. Your graph logic stays exactly the same.

## Prerequisites

- AWS account with Bedrock AgentCore access
- Python 3.10+ installed
- boto3 SDK (`pip install boto3`)
- AWS credentials configured

## Environment Setup

```bash
# Install dependencies
pip install boto3 langgraph langchain-aws bedrock-agentcore-starter-toolkit

# Set environment variables
export AWS_REGION=us-east-1
```

## Implementation

### Build a LangGraph Agent with State Persistence

```python
import json
import boto3
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_aws import ChatBedrock
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient

# --- State Definition ---

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    research_notes: str
    iteration: int

# --- Graph Nodes ---

model = ChatBedrock(
    model_id="anthropic.claude-sonnet-4-20250514",
    region_name="us-east-1"
)

memory_client = MemoryClient(region_name="us-east-1")
MEMORY_ID = "mem-langgraph-agent"

def research(state: AgentState) -> dict:
    """Gather information based on the user query."""
    prompt = f"Research the following topic and provide key findings:\n{state['messages'][-1].content}"
    response = model.invoke([{"role": "user", "content": prompt}])
    return {
        "messages": [response],
        "research_notes": response.content,
        "iteration": state.get("iteration", 0) + 1
    }

def analyze(state: AgentState) -> dict:
    """Analyze research findings and produce a final answer."""
    prompt = (
        f"Based on these research notes, provide a clear analysis:\n"
        f"{state['research_notes']}\n\n"
        f"Original question: {state['messages'][0].content}"
    )
    response = model.invoke([{"role": "user", "content": prompt}])
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    """Route to analysis after enough research iterations."""
    if state.get("iteration", 0) >= 2:
        return "analyze"
    return "research"

# --- Build Graph ---

graph = StateGraph(AgentState)
graph.add_node("research", research)
graph.add_node("analyze", analyze)

graph.set_entry_point("research")
graph.add_conditional_edges("research", should_continue, {
    "research": "research",
    "analyze": "analyze"
})
graph.add_edge("analyze", END)

agent = graph.compile()

# --- AgentCore Runtime Wrapper ---

app = BedrockAgentCoreApp()

@app.entrypoint()
async def main(request):
    user_id = request.get("user_id", "default")
    session_id = request.get("session_id", "default")
    prompt = request.get("prompt", "")

    # Retrieve past context from AgentCore Memory
    memories = memory_client.retrieve_memories(
        memory_id=MEMORY_ID,
        actor_id=user_id,
        query=prompt,
        namespace="research",
        max_results=5
    )
    context = "\n".join([m["content"] for m in memories])

    # Prepend context if available
    full_prompt = f"Previous context:\n{context}\n\nNew query: {prompt}" if context else prompt

    # Execute the graph
    result = agent.invoke({
        "messages": [{"role": "user", "content": full_prompt}],
        "research_notes": "",
        "iteration": 0
    })

    response_text = result["messages"][-1].content

    # Persist interaction to Memory
    memory_client.create_event(
        memory_id=MEMORY_ID,
        actor_id=user_id,
        session_id=session_id,
        messages=[
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": response_text}
        ]
    )

    return {"response": response_text}

if __name__ == "__main__":
    app.run()
```

### Deploy with the AgentCore CLI

```bash
# Scaffold a LangGraph project
agentcore create --framework langgraph --model-provider bedrock --name research-agent

# Test locally before deploying
agentcore dev

# Invoke the local dev server
agentcore invoke --dev '{"prompt": "Explain graph-based agent architectures"}'

# Deploy to AgentCore Runtime
agentcore deploy --region us-east-1 --memory 1024 --timeout 28800

# Invoke the deployed agent
agentcore invoke '{"prompt": "Compare ReAct vs plan-and-execute patterns"}'

# Continue a session
agentcore invoke --session-id sess-001 '{"prompt": "Go deeper on plan-and-execute"}'

# Check deployment status
agentcore status --name research-agent
```

### Create Memory for Cross-Session Persistence

```python
import boto3

control = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

# Create memory with research-oriented strategies
response = control.create_memory(
    name='LangGraphAgentMemory',
    memoryStrategies=[
        {
            'sessionSummaryMemoryStrategy': {
                'name': 'ResearchSummarizer',
                'namespaces': ['research']
            }
        },
        {
            'semanticMemoryStrategy': {
                'name': 'FactExtractor',
                'namespaces': ['facts']
            }
        }
    ]
)
memory_id = response['memoryId']
print(f"Memory created: {memory_id}")
```

## Running the Example

```bash
cd articles/examples/langgraph
pip install -r requirements.txt
python main.py
```

Expected output:
```
Starting AgentCore dev server on port 8080...
Agent ready. Invoke with: agentcore invoke --dev '{"prompt": "your question"}'
```

## Key Benefits

- **Zero infrastructure**: No Kubernetes, no scaling config, no container management. Deploy with `agentcore deploy`
- **8-hour execution**: Long-running research graphs, multi-step analysis, and iterative refinement without timeout constraints
- **MicroVM isolation**: Each session runs in a dedicated microVM with isolated CPU, memory, and filesystem
- **Free I/O wait**: You are not charged while the graph waits for LLM responses, only for active compute
- **State persistence**: AgentCore Memory preserves research context and user interactions across sessions

## Common Patterns

Teams use LangGraph on AgentCore for research agents that iterate through gather-analyze-synthesize cycles over hours, multi-step workflows with conditional branching based on intermediate results, and supervisor architectures where a coordinator graph dispatches to specialized sub-agents. The 8-hour execution window makes LangGraph particularly effective for deep analysis tasks that would timeout on Lambda or short-lived containers.

## Next Steps

Start with a simple two-node graph deployed via the CLI. Add conditional edges as your workflow grows. Integrate Memory when you need cross-session context. Use `agentcore dev` for rapid local iteration before deploying.

Documentation: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/
LangGraph docs: https://langchain-ai.github.io/langgraph/
GitHub samples: https://github.com/awslabs/amazon-bedrock-agentcore-samples/

#AWS #AI #AgentCore #LangGraph #Developers
