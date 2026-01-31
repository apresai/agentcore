# AgentCore Runtime

## Overview

Amazon Bedrock AgentCore Runtime provides a secure, serverless, purpose-built hosting environment for deploying and running AI agents or tools.

## Key Features

### Framework Agnostic
Transform any local agent code to cloud-native deployments with a few lines of code. Works with LangGraph, Strands, CrewAI, or custom agents.

### Model Flexibility
Works with any LLM: Amazon Bedrock models, Anthropic Claude, Google Gemini, OpenAI, etc.

### Protocol Support
- Model Context Protocol (MCP)
- Agent to Agent (A2A)

### Session Isolation
Each user session runs in a **dedicated microVM** with:
- Isolated CPU, memory, and filesystem
- Complete separation between user sessions
- Memory sanitization after session completion
- Deterministic security for non-deterministic AI processes

### Extended Execution Time
- Real-time interactions
- Long-running workloads up to **8 hours**
- Multi-agent collaboration support
- Extended problem-solving sessions

### Consumption-Based Pricing
- Charges only for resources actually consumed
- Dynamic provisioning (no right-sizing required)
- CPU billing aligned with active processing
- **I/O wait periods typically free** (when waiting for LLM responses)
- 1-second minimum billing
- 128MB minimum memory billing

### Built-in Authentication
Powered by AgentCore Identity:
- Integration with corporate IdPs (Okta, Microsoft Entra ID, Amazon Cognito)
- End users authenticate only to authorized agents
- Outbound OAuth flows for third-party services (Slack, Zoom, GitHub)
- API key support

### Agent-Specific Observability
- Captures agent reasoning steps
- Tool invocations tracking
- Model interactions logging
- Clear visibility into decision-making processes
- Debugging and auditing capabilities

### Enhanced Payload Handling
- Process **100MB payloads**
- Multi-modal support (text, images, audio, video)
- Rich media content handling
- Large dataset processing

### Bidirectional Streaming
- HTTP API calls
- Persistent WebSocket connections
- Real-time feedback
- Maintained conversation context

## Deployment Options

1. **Code Upload**: Deploy Python code as a zip file
2. **Containers**: Container-based deployments

## SDK Integration

Single, comprehensive SDK providing:
- Runtime access
- Memory integration
- Tools access
- Gateway connectivity

## Key Topics

- Session management
- Async and long-running agents
- Response streaming
- Custom headers
- Inbound/Outbound authentication
- Versioning and endpoints
- Troubleshooting
