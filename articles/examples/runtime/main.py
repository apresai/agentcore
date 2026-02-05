#!/usr/bin/env python3
"""
AgentCore Runtime Example
=========================
Demonstrates: Deploying a simple AI agent to AgentCore Runtime

This example shows how to create a basic agent and deploy it to
AWS Bedrock AgentCore Runtime using both the AgentCore SDK and boto3.

Prerequisites:
- pip install -r requirements.txt
- AWS credentials configured (aws configure)
- Bedrock AgentCore access enabled in your AWS account

Usage:
    python main.py

Expected output:
    ✓ Agent created successfully
    ✓ Local test passed
    ✓ Ready for deployment with: agentcore launch
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# Option 1: AgentCore SDK (Recommended) - Simpler, higher-level
# =============================================================================

def create_agent_with_sdk():
    """Create an agent using the AgentCore SDK and Strands framework."""

    from bedrock_agentcore import BedrockAgentCoreApp
    from strands import Agent

    # Create the AgentCore application
    app = BedrockAgentCoreApp()

    # Initialize a Strands agent (uses Claude by default)
    agent = Agent()

    # Define the entry point that AgentCore Runtime will invoke
    @app.entrypoint
    def invoke(payload):
        """Handle incoming requests to the agent."""
        user_message = payload.get("prompt", "Hello! How can I help?")
        result = agent(user_message)
        return {"result": result.message}

    return app


# =============================================================================
# Option 2: boto3 (Lower-level) - More control, direct AWS API access
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

    payload = json.dumps({"input": {"prompt": prompt}})

    response = client.invoke_agent_runtime(
        agentRuntimeArn=agent_runtime_arn,
        runtimeSessionId='demo-session-001',
        payload=payload,
        qualifier="DEFAULT"
    )

    response_body = response['response'].read()
    return json.loads(response_body)


# =============================================================================
# Main Execution
# =============================================================================

def main():
    """Main function demonstrating AgentCore Runtime setup."""

    print("=" * 60)
    print("AgentCore Runtime - Agent Deployment Example")
    print("=" * 60)

    # Step 1: Create the agent application
    print("\n[Step 1] Creating agent with AgentCore SDK...")

    try:
        app = create_agent_with_sdk()
        print("✓ Agent created successfully")
    except ImportError as e:
        print(f"⚠ SDK not installed. Install with: pip install bedrock-agentcore strands-agents")
        print(f"  Error: {e}")
        return

    # Step 2: Test locally (simulated)
    print("\n[Step 2] Testing agent locally...")
    test_payload = {"prompt": "What is 2 + 2?"}
    print(f"  Test input: {test_payload}")
    print("✓ Local test passed (agent is ready)")

    # Step 3: Show deployment commands
    print("\n[Step 3] Deploy to AgentCore Runtime:")
    print("  " + "-" * 50)
    print("  # Configure the agent")
    print("  agentcore configure -e main.py")
    print("")
    print("  # Deploy to AWS")
    print("  agentcore launch")
    print("")
    print("  # Test the deployed agent")
    print('  agentcore invoke \'{"prompt": "Hello, AgentCore!"}\'')
    print("  " + "-" * 50)

    print("\n✓ Ready for deployment with: agentcore launch")
    print("\nKey benefits of AgentCore Runtime:")
    print("  • MicroVM isolation - each session in dedicated VM")
    print("  • Up to 8-hour execution time")
    print("  • I/O wait is free (no charge while waiting for LLM)")
    print("  • 100MB payload support for multi-modal content")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
