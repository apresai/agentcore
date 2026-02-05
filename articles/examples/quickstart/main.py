#!/usr/bin/env python3
"""
AgentCore Quickstart Example
============================
Demonstrates: Your first AI agent deployed to AgentCore in 5 minutes

This is the minimal code needed to create an agent that can be deployed
to AWS Bedrock AgentCore Runtime.

Prerequisites:
    pip install -r requirements.txt
    aws configure  # Set up AWS credentials

Usage:
    # Test locally
    agentcore dev
    agentcore invoke --dev "Hello, agent!"

    # Deploy to AWS
    agentcore launch
    agentcore invoke '{"prompt": "Hello from the cloud!"}'

Expected output:
    ✓ Agent deployed: arn:aws:bedrock-agentcore:us-east-1:123456789:runtime/my-first-agent
    ✓ Response: {"result": "Hello! I'm your AI assistant..."}
"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent

# =============================================================================
# Create the Agent
# =============================================================================

# Initialize the AgentCore application wrapper
app = BedrockAgentCoreApp()

# Create a Strands agent (uses Claude via Amazon Bedrock by default)
agent = Agent(
    system_prompt="You are a helpful assistant. Be concise and friendly."
)


# =============================================================================
# Define the Entry Point
# =============================================================================

@app.entrypoint
def invoke(payload, context):
    """
    Entry point that AgentCore Runtime calls when your agent is invoked.

    Args:
        payload: Dict containing the request data (e.g., {"prompt": "Hello!"})
        context: AgentCore context with session info

    Returns:
        Dict with the response to send back to the caller
    """
    # Extract the user's message from the payload
    user_message = payload.get("prompt", "Hello! How can I help you today?")

    # Invoke the agent and get the response
    result = agent(user_message)

    # Return the result
    return {
        "result": result.message,
        "session_id": context.session_id
    }


# =============================================================================
# Run the Application
# =============================================================================

if __name__ == "__main__":
    # This starts the local development server when running directly
    # In production, AgentCore Runtime handles the server
    app.run()
