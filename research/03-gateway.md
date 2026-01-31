# AgentCore Gateway

## Overview

Amazon Bedrock AgentCore Gateway provides an easy and secure way to build, deploy, discover, and connect to tools at scale. It converts APIs, Lambda functions, and services into **Model Context Protocol (MCP)-compatible tools**.

## The Problem It Solves

AI agents need tools to perform real-world tasks (querying databases, sending messages, analyzing documents). Gateway eliminates weeks of custom code development, infrastructure provisioning, and security implementation.

## Key Benefits

### Simplify Tool Development
- Transform enterprise resources into agent-ready tools with a few lines of code
- Eliminate months of custom integration code
- Focus on building differentiated agent capabilities

### Unified Access
- Single, secure endpoint for all tools
- Combine multiple tool sources (APIs, Lambda functions)
- Build and scale agent workflows faster

### Intelligent Tool Discovery
- Contextual search as tool collections grow
- Built-in **semantic search** capabilities
- Agents find right tools based on task context

### Comprehensive Authentication
- **Inbound authentication**: Verify agent identity
- **Outbound authentication**: Connect to tools
- Handle OAuth flows, token refresh, secure credential storage

### Framework Compatibility
Works with:
- CrewAI
- LangGraph
- LlamaIndex
- Strands Agents

### Serverless Infrastructure
- Fully managed with automatic scaling
- Built-in observability and auditing

## Supported Input Types

- OpenAPI specifications
- Smithy
- AWS Lambda functions

## Key Capabilities

| Capability | Description |
|------------|-------------|
| **Security Guard** | OAuth authorization for valid users/agents |
| **Translation** | Converts agent requests (MCP) into API/Lambda invocations |
| **Composition** | Combines multiple APIs/functions into single MCP endpoint |
| **Secure Credential Exchange** | Handles credential injection per tool |
| **Semantic Tool Selection** | Search across tools to find appropriate ones for context |
| **Infrastructure Manager** | Serverless solution with observability and auditing |

## 1-Click Integrations

Pre-built integrations available for:
- Salesforce
- Slack
- Jira
- Asana
- Zendesk

## Pricing

Billing based on:
- Number of MCP operations (ListTools, CallTool, Ping)
- Search queries
- Tools indexed for semantic search
