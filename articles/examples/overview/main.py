#!/usr/bin/env python3
"""
AgentCore Overview Example
==========================
Demonstrates: Creating a basic AI agent with AWS Bedrock AgentCore

This example shows the minimal code needed to create an agent that can be
deployed to AWS Bedrock AgentCore Runtime. It demonstrates:
- Creating an agent using the Strands framework
- Wrapping it with BedrockAgentCoreApp for deployment
- Handling requests and returning responses

Prerequisites:
    pip install -r requirements.txt
    aws configure  # Set up AWS credentials
    # Enable model access in Amazon Bedrock console

Usage:
    # Test locally
    python main.py

    # Deploy to AWS (after testing)
    agentcore configure -e main.py
    agentcore launch
    agentcore invoke '{"prompt": "What is AgentCore?"}'

Expected output:
    ============================================================
    AgentCore Overview - Basic Agent Example
    ============================================================

    [Step 1] Creating agent with Strands framework...
    Agent created successfully

    [Step 2] Testing agent locally...
    Input:  "What is AWS Bedrock AgentCore? Answer in one sentence."
    Output: "AWS Bedrock AgentCore is a modular platform for building,
            deploying, and operating AI agents securely at enterprise scale."
    Local test passed

    [Step 3] Ready for deployment!
    Run these commands to deploy:
      agentcore configure -e main.py
      agentcore launch
      agentcore invoke '{"prompt": "Hello!"}'

    ============================================================
"""

import os
import sys

# Optional: load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

from strands import Agent
from bedrock_agentcore.runtime import BedrockAgentCoreApp


# =============================================================================
# AgentCore Runtime Agent — deployable entrypoint
# =============================================================================

# Create agent at module level (lightweight — no API calls at import time)
agent = Agent(
    system_prompt=(
        "You are a helpful AI assistant with expertise in AWS services. "
        "You provide accurate, concise information about AWS Bedrock AgentCore. "
        "When asked about AgentCore, explain its capabilities clearly."
    )
)

# Wrap in AgentCore app for Runtime deployment
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload, context):
    """Entry point that AgentCore Runtime calls when your agent is invoked."""
    user_message = payload.get("prompt", "Hello! How can I help you?")
    result = agent(user_message)
    return {
        "result": result.message,
        "session_id": context.session_id
    }


# =============================================================================
# Alternative: Direct boto3 API (for advanced use cases)
# =============================================================================

def invoke_deployed_agent(agent_runtime_arn: str, prompt: str):
    """
    Invoke a deployed agent using boto3.

    Use this when you want programmatic access to a deployed agent from
    another application or service.

    Args:
        agent_runtime_arn: The ARN of the deployed agent runtime
        prompt: The user's message to send to the agent

    Returns:
        dict: The agent's response
    """
    import json
    import uuid
    import boto3

    region = os.getenv("AWS_REGION", "us-east-1")
    client = boto3.client('bedrock-agentcore', region_name=region)

    response = client.invoke_agent_runtime(
        agentRuntimeArn=agent_runtime_arn,
        runtimeSessionId=str(uuid.uuid4()),
        payload=json.dumps({"prompt": prompt}).encode(),
        qualifier="DEFAULT"
    )

    # Read and parse the response
    content = []
    for chunk in response.get("response", []):
        content.append(chunk.decode('utf-8'))

    return json.loads(''.join(content))


# =============================================================================
# Main Execution
# =============================================================================

def main():
    """Run a local demo — creates agent, tests it, shows deployment steps."""
    print("=" * 60)
    print("AgentCore Overview - Basic Agent Example")
    print("=" * 60)

    print("\n[Step 1] Creating agent with Strands framework...")
    print("Agent created successfully")

    print("\n[Step 2] Testing agent locally...")
    test_prompt = "What is AWS Bedrock AgentCore? Answer in one sentence."
    print(f'Input:  "{test_prompt}"')

    try:
        response = agent(test_prompt)
        result_text = str(response.message) if hasattr(response, 'message') else str(response)
        print(f'Output: "{result_text.strip()}"')
        print("Local test passed")
    except Exception as e:
        print(f"Test failed: {e}")
        return

    print("\n[Step 3] Ready for deployment!")
    print("Run these commands to deploy:")
    print("-" * 40)
    print("  agentcore configure -e main.py -n overview_demo -dt direct_code_deploy -ni")
    print("  agentcore deploy")
    print('  agentcore invoke \'{"prompt": "Hello!"}\'')
    print("-" * 40)

    print("\nAgentCore provides:")
    print("  - MicroVM isolation: Each session runs in dedicated VM")
    print("  - 8-hour execution: Long-running tasks supported")
    print("  - Free I/O wait: No charge while waiting for LLM")
    print("  - Framework agnostic: LangGraph, CrewAI, custom code")
    print("  - Model agnostic: Claude, GPT, Gemini, Nova, Llama")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    if "--demo" in sys.argv:
        main()
    else:
        # Default: start the AgentCore server (for deployment + local dev)
        app.run()
