# AgentCore Identity

## Overview

Amazon Bedrock AgentCore Identity is an identity and credential management service designed specifically for AI agents and automated workloads.

## Core Capabilities

- **Secure authentication**
- **Authorization**
- **Credential management**

Enables agents and tools to access AWS resources and third-party services on behalf of users while maintaining strict security controls and audit trails.

## Architecture

Agent identities are implemented as **workload identities** with specialized attributes that enable agent-specific capabilities while maintaining compatibility with industry-standard workload identity patterns.

## Integration Points

Natively integrates with:
- AgentCore Runtime
- AgentCore Gateway

## Supported Identity Providers

- Amazon Cognito
- Okta
- Microsoft Azure Entra ID
- Auth0
- Any IdP with standard workload identity patterns

## Key Features

### Workload Identities
Manage identities specifically designed for AI agents and automated workloads.

### Inbound JWT Authorizer
Configure JWT-based authorization for incoming requests.

### Credential Providers
Manage outbound credentials for accessing third-party services.

### Provider Setup
Configure various identity providers for seamless integration.

## Pricing

- **No additional charges** when used through AgentCore Runtime or Gateway
- Otherwise: charged per request from agent to AgentCore Identity for OAuth token or API key
