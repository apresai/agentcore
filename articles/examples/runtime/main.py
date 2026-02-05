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
    python main.py

Expected output:
    ✓ Agent created successfully
    ✓ Local test passed: "42"
    ✓ Ready for deployment
"""

import os
import json

# Optional: load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


# =============================================================================
# AgentCore Runtime Agent
# =============================================================================

def create_agent():
    """Create an agent using the Strands framework."""
    from strands import Agent
    return Agent()


def create_agentcore_app(agent):
    """Wrap the agent in a BedrockAgentCoreApp for deployment."""
    from bedrock_agentcore import BedrockAgentCoreApp

    app = BedrockAgentCoreApp()

    @app.entrypoint
    def invoke(payload):
        """Handle incoming requests to the agent."""
        user_message = payload.get("prompt", "Hello!")
        result = agent(user_message)
        return {"result": result.message}

    return app


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
# Main Execution
# =============================================================================

def main():
    """Main function demonstrating AgentCore Runtime setup."""

    print("=" * 60)
    print("AgentCore Runtime - Agent Deployment Example")
    print("=" * 60)

    # Step 1: Create the agent
    print("\n[Step 1] Creating agent with Strands framework...")
    try:
        agent = create_agent()
        print("✓ Agent created successfully")
    except ImportError as e:
        print(f"✗ Missing dependencies. Install with:")
        print(f"  pip install bedrock-agentcore strands-agents")
        print(f"  Error: {e}")
        return

    # Step 2: Test the agent locally
    print("\n[Step 2] Testing agent locally...")
    test_prompt = "What is the answer to life, the universe, and everything? Reply with just the number."
    print(f"  Input:  \"{test_prompt}\"")

    try:
        response = agent(test_prompt)
        # Extract text from response
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

    # Step 3: Create AgentCore app for deployment
    print("\n[Step 3] Creating AgentCore app...")
    try:
        app = create_agentcore_app(agent)
        print("✓ AgentCore app created")
    except ImportError as e:
        print(f"  ✗ bedrock-agentcore not installed: {e}")
        return

    # Step 4: Show deployment commands
    print("\n[Step 4] Deploy to AgentCore Runtime:")
    print("  " + "-" * 50)
    print("  # Initialize AgentCore project")
    print("  agentcore init")
    print("")
    print("  # Deploy to AWS")
    print("  agentcore deploy")
    print("")
    print("  # Invoke your deployed agent")
    print('  agentcore invoke "Hello, AgentCore!"')
    print("  " + "-" * 50)

    print("\n✓ Ready for deployment!")
    print("\nKey benefits of AgentCore Runtime:")
    print("  • MicroVM isolation - each session runs in dedicated VM")
    print("  • Up to 8-hour execution time for complex tasks")
    print("  • I/O wait is FREE (no charge while waiting for LLM)")
    print("  • 100MB payload support for multi-modal content")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
