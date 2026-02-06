#!/usr/bin/env python3
"""
AgentCore Framework Flexibility Example
=======================================
Demonstrates: How AgentCore supports multiple agent frameworks
Article: /articles/agentcore-vs-bedrock-agents-standard.md

This example shows the same simple agent implemented with different frameworks,
all deployable to AgentCore Runtime. This is a key differentiator from
Bedrock Agents, which requires its native framework.

Theme: Multiple Perspectives from Hitchhiker's Guide to the Galaxy
- Ford Prefect's Approach (Strands): Simple, practical, field-tested
- Zaphod Beeblebrox's Approach (LangGraph): Complex, flashy, graph-based

Prerequisites:
- pip install -r requirements.txt
- AWS credentials configured
- Bedrock model access enabled

Usage:
    python main.py

Expected output:
    === AgentCore Framework Flexibility Demo ===

    Ford Prefect's Approach (Strands):
       [Agent response using Strands]

    Zaphod Beeblebrox's Approach (LangGraph):
       [Agent response using LangGraph]

    Both frameworks deploy to AgentCore Runtime the same way!
"""

import os

# Optional: load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


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
            model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
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
        model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
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
    print("=" * 60)
    print("AgentCore Framework Flexibility - Multiple Perspectives")
    print("=" * 60)
    print()
    print('  "The History of every major Galactic Civilization tends to')
    print('   pass through three distinct and recognizable phases..."')
    print()
    print("  Different researchers, different methods, same Universe.")
    print("  AgentCore lets you choose your approach. Bedrock Agents doesn't.")
    print()

    test_prompt = "What is the meaning of life? Answer in one sentence."

    # Test Strands - Ford Prefect's approach
    print("Ford Prefect's Approach (Strands - simple, practical, field-tested):")
    print("-" * 60)
    print("  Ford knows: the best research tool is the simplest one.")
    print("  Strands is AWS-native, minimal API, gets the job done.")
    try:
        strands_response = strands_agent_example(test_prompt)
        print(f"   Prompt:   \"{test_prompt}\"")
        print(f"   Response: {strands_response}")
        print("  ✓ Ford Prefect would approve - simple and effective.")
    except ImportError as e:
        print(f"   [Strands not installed: {e}]")
    except Exception as e:
        print(f"   [Error: {e}]")
    print()

    # Test LangGraph - Zaphod's approach
    print("Zaphod Beeblebrox's Approach (LangGraph - complex, flashy, graph-based):")
    print("-" * 60)
    print("  Zaphod needs two heads for this: state graphs, typed dicts,")
    print("  node pipelines. Overkill? Maybe. But it looks impressive.")
    try:
        langgraph_response = langgraph_agent_example(test_prompt)
        print(f"   Prompt:   \"{test_prompt}\"")
        print(f"   Response: {langgraph_response}")
        print("  ✓ Zaphod would approve - flashy and graph-based.")
    except ImportError as e:
        print(f"   [LangGraph not installed: {e}]")
    except Exception as e:
        print(f"   [Error: {e}]")
    print()

    print("=" * 60)
    print("The Hitchhiker's Key Takeaway:")
    print("=" * 60)
    print("""
Both approaches reach the same destination:
  • Deploy to AgentCore Runtime the same way
  • Get microVM session isolation automatically
  • Use AgentCore Memory for context persistence
  • Connect to tools via AgentCore Gateway
  • Have full observability through CloudWatch

  Ford Prefect (Strands): "Keep it simple. Carry a towel."
  Zaphod Beeblebrox (LangGraph): "If it's worth doing, do it with style."

With Bedrock Agents, you're stuck with one approach.
With AgentCore, be Ford or Zaphod - your choice.
""")


def show_deployment_comparison():
    """
    Show how deployment differs between Bedrock Agents and AgentCore.
    """
    print("=" * 60)
    print("Deployment Comparison - Two Entries in the Guide")
    print("=" * 60)

    bedrock_agents_approach = """
Bedrock Agents - Guide Entry: "Mostly harmless."
  (Configuration-based, like ordering from a set menu)
  1. Create agent in console or via API
  2. Define action groups (tools)
  3. Connect knowledge bases
  4. Configure prompts and guardrails
  5. Deploy (fully managed)

  Pros: Simple, no infrastructure code
  Cons: Limited to Bedrock framework and models
"""

    agentcore_approach = """
AgentCore - Guide Entry: "A hoopy frood who really knows where his towel is."
  (Code-first, like writing your own Guide entry)
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
    print("=" * 60)
    print("AgentCore vs Bedrock Agents - A Tale of Two Approaches")
    print("=" * 60)
    print()
    print('  "There is an art to flying, or rather a knack. The knack')
    print('   lies in learning how to throw yourself at the ground')
    print('   and miss."')
    print()
    print("  There is also an art to choosing an agent framework.")
    print("  AgentCore lets you choose. Bedrock Agents does not.")
    print()

    # Show the deployment comparison
    show_deployment_comparison()

    # Run the framework demonstrations
    demonstrate_framework_flexibility()

    # Closing
    print("=" * 60)
    print()
    print('  "Time is an illusion. Lunchtime doubly so."')
    print("  But framework lock-in? That's very real.")
    print("  Choose AgentCore. Choose freedom.")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
