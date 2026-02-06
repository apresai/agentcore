#!/usr/bin/env python3
"""
AgentCore Runtime Example
=========================
Demonstrates: Deploying a simple AI agent to AgentCore Runtime

This example shows how to create a basic agent and deploy it to
AWS Bedrock AgentCore Runtime using the AgentCore SDK and Strands framework.

Prerequisites:
- pip install -r requirements.txt
- AWS credentials configured (aws configure)
- Bedrock model access enabled (Claude or other model)

Usage:
    # Deploy to AgentCore Runtime
    agentcore configure -e main.py -n runtime_demo -dt direct_code_deploy -ni
    agentcore deploy
    agentcore invoke '{"prompt": "What is 6 * 7?"}'

    # Local demo (tests agent + shows deployment instructions)
    python main.py --demo
"""

import os
import sys
import json

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

# Create the agent (lightweight — no API calls at import time)
agent = Agent(
    system_prompt=(
        "You are Deep Thought, the second greatest computer in the Universe "
        "of Time and Space. You answer questions helpfully and concisely, "
        "with occasional references to the number 42."
    )
)

# Wrap in AgentCore app for Runtime deployment
app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload, context):
    """Handle incoming requests to the deployed agent."""
    user_message = payload.get("prompt", "Hello!")
    result = agent(user_message)
    return {
        "result": result.message,
        "session_id": context.session_id,
    }


# =============================================================================
# boto3 Alternative (Lower-level API access)
# =============================================================================

def deploy_with_boto3(agent_name: str, role_arn: str, container_uri: str):
    """Deploy an agent using boto3 for more control over the process."""
    import boto3

    region = os.getenv("AWS_REGION", "us-east-1")
    client = boto3.client('bedrock-agentcore-control', region_name=region)

    response = client.create_agent_runtime(
        agentRuntimeName=agent_name,
        agentRuntimeArtifact={
            'containerConfiguration': {
                'containerUri': container_uri
            }
        },
        networkConfiguration={"networkMode": "PUBLIC"},
        roleArn=role_arn
    )
    return response


def invoke_with_boto3(agent_runtime_arn: str, prompt: str):
    """Invoke a deployed agent using boto3."""
    import boto3

    region = os.getenv("AWS_REGION", "us-east-1")
    client = boto3.client('bedrock-agentcore', region_name=region)

    response = client.invoke_agent_runtime(
        agentRuntimeArn=agent_runtime_arn,
        runtimeSessionId='demo-session-001',
        payload=json.dumps({"input": {"prompt": prompt}}),
        qualifier="DEFAULT"
    )

    return json.loads(response['response'].read())


# =============================================================================
# Local demo mode (--demo flag)
# =============================================================================

def run_demo():
    """Run a local demo — creates agent, tests it, shows deployment steps."""

    print("=" * 60)
    print("AgentCore Runtime - Deep Thought")
    print("=" * 60)
    print()
    print("  +-----------------------------------------------+")
    print("  |          DEEP THOUGHT COMPUTING ...            |")
    print('  |  "The Answer to the Great Question ...         |')
    print('  |   of Life, the Universe and Everything ...     |')
    print('  |   Is ... Forty-two."                           |')
    print("  +-----------------------------------------------+")
    print()
    print("  After 7.5 million years of computation, Deep Thought")
    print("  delivered The Answer. AgentCore Runtime does it in seconds.")

    # Step 1: Agent already created at module level
    print("\n[Step 1] Creating agent with Strands framework...")
    print("✓ Agent created successfully")

    # Step 2: Test the agent locally
    print("\n[Step 2] Testing agent locally...")
    test_prompt = "What is the answer to life, the universe, and everything? Reply with just the number."
    print(f"  Input:  \"{test_prompt}\"")

    try:
        response = agent(test_prompt)
        if hasattr(response, 'message'):
            content = response.message.get('content', [])
            if content and isinstance(content, list):
                result_text = content[0].get('text', str(response))
            else:
                result_text = str(content)
        else:
            result_text = str(response)
        print(f"  Output: \"{result_text.strip()}\"")
        print("✓ Local test passed")
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        print("  (Ensure AWS credentials are configured and Bedrock model access is enabled)")
        return

    # Step 3: Show deployment commands
    print("\n[Step 3] Creating AgentCore app...")
    print("✓ AgentCore app created")

    print("\n[Step 4] Deploy to AgentCore Runtime:")
    print("  " + "-" * 50)
    print("  # Configure the agent")
    print("  agentcore configure -e main.py -n runtime_demo -dt direct_code_deploy -ni")
    print("")
    print("  # Deploy to AWS")
    print("  agentcore deploy")
    print("")
    print("  # Invoke your deployed agent")
    print("  agentcore invoke '{\"prompt\": \"Hello, AgentCore!\"}'")
    print("  " + "-" * 50)

    print("\n✓ Ready for deployment!")
    print("\nKey benefits of AgentCore Runtime:")
    print("  • MicroVM isolation - each session gets its own universe")
    print("  • Up to 8 hours of execution (7.5M years, condensed)")
    print("  • I/O wait is FREE (Deep Thought didn't have that luxury)")
    print("  • 100MB payload support for multi-modal content")
    print()
    print('  "I think the problem, to be quite honest with you, is that')
    print("   you've never actually known what the Question is.\"")
    print("                                    - Deep Thought")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    if "--demo" in sys.argv:
        run_demo()
    else:
        # Default: start the AgentCore server (for deployment + local dev)
        app.run()
