#!/usr/bin/env python3
"""
AgentCore Framework Flexibility Example
=======================================
Demonstrates: How AgentCore supports multiple agent frameworks
Article: /articles/agentcore-vs-bedrock-agents-standard.md

This example shows the same simple agent implemented with different frameworks,
all deployable to AgentCore Runtime. This is a key differentiator from
Bedrock Agents, which requires its native framework.

Prerequisites:
- pip install -r requirements.txt
- AWS credentials configured
- Bedrock model access enabled

Usage:
    python main.py

Expected output:
    === AgentCore Framework Flexibility Demo ===

    1. Strands Agent Response:
       [Agent response using Strands]

    2. LangGraph Agent Response:
       [Agent response using LangGraph]

    Both frameworks deploy to AgentCore Runtime the same way!
"""

import os
from dotenv import load_dotenv

load_dotenv()


def strands_agent_example(prompt: str) -> str:
    """
    Example using Strands Agents - AWS's native agent framework.
    Simplest path to AgentCore deployment.
    """
    from strands import Agent
    from strands.models import BedrockModel

    # Strands provides clean, minimal API
    agent = Agent(
        model=BedrockModel(
            model_id="anthropic.claude-3-haiku-20240307-v1:0",
            region_name=os.getenv("AWS_REGION", "us-east-1")
        ),
        system_prompt="You are a helpful assistant. Keep responses brief (1-2 sentences)."
    )

    # Simple invocation
    response = agent(prompt)
    return str(response)


def langgraph_agent_example(prompt: str) -> str:
    """
    Example using LangGraph - for complex, multi-step workflows.
    Best for stateful, graph-based agent logic.
    """
    from langchain_aws import ChatBedrock
    from langgraph.graph import StateGraph, START, END
    from typing import TypedDict, Annotated
    import operator

    # Define state for the graph
    class AgentState(TypedDict):
        messages: Annotated[list, operator.add]
        response: str

    # Initialize Bedrock model through LangChain
    llm = ChatBedrock(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_kwargs={"max_tokens": 256}
    )

    # Define the agent node
    def agent_node(state: AgentState) -> AgentState:
        messages = state["messages"]
        # Add system message for brief responses
        from langchain_core.messages import SystemMessage, HumanMessage
        full_messages = [
            SystemMessage(content="You are a helpful assistant. Keep responses brief (1-2 sentences)."),
            HumanMessage(content=messages[-1])
        ]
        response = llm.invoke(full_messages)
        return {"messages": [], "response": response.content}

    # Build the graph
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_edge(START, "agent")
    graph.add_edge("agent", END)

    # Compile and run
    app = graph.compile()
    result = app.invoke({"messages": [prompt], "response": ""})
    return result["response"]


def demonstrate_framework_flexibility():
    """
    Demonstrate that AgentCore supports multiple frameworks.

    Key point: All these frameworks deploy to AgentCore Runtime
    with the same microVM isolation, memory, and observability.
    Bedrock Agents only supports its native framework.
    """
    print("=" * 50)
    print("AgentCore Framework Flexibility Demo")
    print("=" * 50)
    print()
    print("This demonstrates AgentCore's key advantage: framework flexibility.")
    print("Unlike Bedrock Agents, you can use any framework and switch without")
    print("changing your infrastructure.")
    print()

    test_prompt = "What is the capital of France?"

    # Test Strands
    print("1. Strands Agent (AWS native, simplest API):")
    print("-" * 40)
    try:
        strands_response = strands_agent_example(test_prompt)
        print(f"   Prompt: {test_prompt}")
        print(f"   Response: {strands_response}")
    except ImportError as e:
        print(f"   [Strands not installed: {e}]")
    except Exception as e:
        print(f"   [Error: {e}]")
    print()

    # Test LangGraph
    print("2. LangGraph Agent (graph-based workflows):")
    print("-" * 40)
    try:
        langgraph_response = langgraph_agent_example(test_prompt)
        print(f"   Prompt: {test_prompt}")
        print(f"   Response: {langgraph_response}")
    except ImportError as e:
        print(f"   [LangGraph not installed: {e}]")
    except Exception as e:
        print(f"   [Error: {e}]")
    print()

    print("=" * 50)
    print("Key Takeaway:")
    print("=" * 50)
    print("""
Both frameworks:
- Deploy to AgentCore Runtime the same way
- Get microVM session isolation automatically
- Use AgentCore Memory for context persistence
- Connect to tools via AgentCore Gateway
- Have full observability through CloudWatch

With Bedrock Agents, you're limited to its native framework.
With AgentCore, choose the framework that fits your use case.
""")


def show_deployment_comparison():
    """
    Show how deployment differs between Bedrock Agents and AgentCore.
    """
    print("=" * 50)
    print("Deployment Comparison")
    print("=" * 50)

    bedrock_agents_approach = """
Bedrock Agents (configuration-based):
1. Create agent in console or via API
2. Define action groups (tools)
3. Connect knowledge bases
4. Configure prompts and guardrails
5. Deploy (fully managed)

Pros: Simple, no infrastructure code
Cons: Limited to Bedrock framework and models
"""

    agentcore_approach = """
AgentCore (code-first):
1. Write agent in your preferred framework
2. Package code (zip or container)
3. Deploy to AgentCore Runtime:

   agentcore create my-agent
   agentcore deploy my-agent
   agentcore invoke my-agent "Hello!"

4. Add Gateway tools, Memory, Identity as needed

Pros: Any framework, any model, full control
Cons: More setup, requires agent code
"""

    print(bedrock_agents_approach)
    print(agentcore_approach)


def main():
    """Main function to run the demonstration."""
    print()
    print("This example shows AgentCore's framework flexibility -")
    print("a key differentiator from Amazon Bedrock Agents.")
    print()

    # Show the deployment comparison
    show_deployment_comparison()

    # Run the framework demonstrations
    demonstrate_framework_flexibility()


if __name__ == "__main__":
    main()
