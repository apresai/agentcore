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

# Optional: load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


# =============================================================================
# Agent Creation
# =============================================================================

def create_agent():
    """
    Create an agent using the Strands framework.

    Strands is AWS's open-source agent framework, providing the simplest path
    to AgentCore deployment. By default, it uses Claude via Amazon Bedrock.

    Returns:
        Agent: A configured Strands agent ready for use
    """
    from strands import Agent

    # Create agent with a system prompt
    # The system prompt defines the agent's personality and capabilities
    agent = Agent(
        system_prompt="""You are a helpful AI assistant with expertise in AWS services.
You provide accurate, concise information about AWS Bedrock AgentCore.
When asked about AgentCore, explain its capabilities clearly."""
    )

    return agent


def create_agentcore_app(agent):
    """
    Wrap the agent in a BedrockAgentCoreApp for deployment.

    BedrockAgentCoreApp provides the infrastructure integration:
    - Handles incoming HTTP/WebSocket requests
    - Manages session lifecycle
    - Provides context about the runtime environment

    Args:
        agent: A Strands agent (or any callable that processes prompts)

    Returns:
        BedrockAgentCoreApp: An application ready for deployment
    """
    from bedrock_agentcore.runtime import BedrockAgentCoreApp

    # Initialize the AgentCore application
    app = BedrockAgentCoreApp()

    @app.entrypoint
    def invoke(payload, context):
        """
        Entry point that AgentCore Runtime calls when your agent is invoked.

        Args:
            payload: Dict containing the request data
                     Expected format: {"prompt": "user message here"}
            context: AgentCore context with session information
                     - context.session_id: Unique identifier for this session
                     - context.runtime_id: The runtime this agent is deployed to

        Returns:
            Dict with the response to send back to the caller
        """
        # Extract the user's message from the payload
        user_message = payload.get("prompt", "Hello! How can I help you?")

        # Invoke the agent and get the response
        result = agent(user_message)

        # Return the result
        # The 'result' field contains the agent's response
        # The 'session_id' helps track conversations across multiple calls
        return {
            "result": result.message,
            "session_id": context.session_id
        }

    return app


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
    """
    Main function demonstrating AgentCore agent creation and testing.

    This function:
    1. Creates an agent using Strands
    2. Tests it locally with a sample prompt
    3. Shows deployment commands for AgentCore Runtime
    """
    print("=" * 60)
    print("AgentCore Overview - Basic Agent Example")
    print("=" * 60)

    # Step 1: Create the agent
    print("\n[Step 1] Creating agent with Strands framework...")
    try:
        agent = create_agent()
        print("Agent created successfully")
    except ImportError as e:
        print(f"Missing dependencies. Install with:")
        print(f"  pip install bedrock-agentcore strands-agents")
        print(f"Error: {e}")
        return

    # Step 2: Test the agent locally
    print("\n[Step 2] Testing agent locally...")
    test_prompt = "What is AWS Bedrock AgentCore? Answer in one sentence."
    print(f'Input:  "{test_prompt}"')

    try:
        response = agent(test_prompt)
        # Extract the message from the response
        result_text = str(response.message) if hasattr(response, 'message') else str(response)
        print(f'Output: "{result_text.strip()}"')
        print("Local test passed")
    except Exception as e:
        print(f"Test failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Run 'aws configure' to set up credentials")
        print("  2. Enable model access in Amazon Bedrock console")
        print("  3. Check you're in a supported region (us-east-1, us-west-2)")
        return

    # Step 3: Show deployment commands
    print("\n[Step 3] Ready for deployment!")
    print("Run these commands to deploy:")
    print("-" * 40)
    print("  agentcore configure -e main.py")
    print("  agentcore launch")
    print('  agentcore invoke \'{"prompt": "Hello!"}\'')
    print("-" * 40)

    # Show key AgentCore benefits
    print("\nAgentCore provides:")
    print("  - MicroVM isolation: Each session runs in dedicated VM")
    print("  - 8-hour execution: Long-running tasks supported")
    print("  - Free I/O wait: No charge while waiting for LLM")
    print("  - Framework agnostic: LangGraph, CrewAI, custom code")
    print("  - Model agnostic: Claude, GPT, Gemini, Nova, Llama")

    print("\n" + "=" * 60)


# =============================================================================
# AgentCore Runtime Entry Point
# =============================================================================

# This section runs when the file is executed directly
# In production, AgentCore Runtime imports this module and calls the entrypoint

if __name__ == "__main__":
    # When running locally for testing
    main()

    # Uncomment below to start the local development server
    # This mimics how AgentCore Runtime will run your agent
    # agent = create_agent()
    # app = create_agentcore_app(agent)
    # app.run()
