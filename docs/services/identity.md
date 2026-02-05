# Identity

> Secure authentication and credential management for AI agents

## Overview

AgentCore Identity solves the complex problem of how AI agents authenticate and authorize access to resources. It provides secure authentication, authorization, and credential management that enables agents to access AWS resources and third-party services on behalf of users.

## Authentication Flows

```
Inbound (User → Agent):
┌──────┐     ┌─────┐     ┌─────┐     ┌──────────────┐     ┌─────────────────┐
│ User │ ──► │ IdP │ ──► │ JWT │ ──► │ AgentCore    │ ──► │ Verified        │
│      │     │     │     │     │     │ Identity     │     │ Session         │
└──────┘     └─────┘     └─────┘     └──────────────┘     └─────────────────┘

Outbound (Agent → Tool):
┌───────┐     ┌──────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────┐
│ Agent │ ──► │ Identity │ ──► │ Credential  │ ──► │ OAuth/API    │ ──► │ External │
│       │     │          │     │ Vault       │     │ Key          │     │ Service  │
└───────┘     └──────────┘     └─────────────┘     └──────────────┘     └──────────┘
```

## Supported Identity Providers

| Provider | Configuration |
|----------|---------------|
| **Amazon Cognito** | Native integration |
| **Okta** | OIDC/SAML |
| **Microsoft Entra ID** | OIDC/SAML |
| **Auth0** | OIDC |
| **Any OIDC-compliant** | Custom configuration |

## Quick Start

### Configure Inbound Authentication

```python
from bedrock_agentcore.identity import IdentityClient

identity = IdentityClient()

# Configure JWT authorizer
identity.configure_authorizer(
    agent_id="my-agent",
    authorizer_type="jwt",
    config={
        "issuer": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_xxxxx",
        "audience": "my-client-id"
    }
)
```

### Store Outbound Credentials

```python
# Store OAuth credentials for external service
identity.store_credential(
    agent_id="my-agent",
    credential_name="salesforce",
    credential_type="oauth2",
    config={
        "client_id": "...",
        "client_secret_arn": "arn:aws:secretsmanager:...",
        "token_url": "https://login.salesforce.com/services/oauth2/token"
    }
)
```

### Use Credentials in Agent

```python
# Credentials are automatically injected when calling tools
# No need to handle tokens in your code

# Via Gateway
gateway.invoke_tool(
    tool_name="salesforce_get_account",
    input={"account_id": "123"}
)
# Identity automatically provides OAuth token
```

## Key Features

| Feature | Description |
|---------|-------------|
| **Workload Identity** | Agent-specific identity attributes |
| **IdP Integration** | No user migration required |
| **JWT Authorization** | Verify inbound requests |
| **Credential Vault** | Secure storage for outbound auth |
| **Token Refresh** | Automatic credential management |

## Pricing

- Per credential request (free when accessed through Runtime/Gateway)

## Related

- [Detailed Research](../../research/04-identity.md)
- [Identity Developer Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html)
