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

`IdentityClient` isn't exported from `bedrock_agentcore.identity` directly - it lives in `bedrock_agentcore.identity.auth`, and its constructor takes a positional `region`. It has no `configure_authorizer()` or `store_credential()` method; its real surface is workload identity and credential-provider management (`create_workload_identity`, `create_oauth2_credential_provider`, `create_api_key_credential_provider`, `get_token`, `get_api_key`, and the payments-credential-provider family).

### Configure Inbound Authentication

Inbound JWT verification is configured on the *Gateway* (or Runtime), not through a standalone Identity call - it's the `authorizerConfiguration.customJWTAuthorizer` block passed to `create_gateway`:

```python
from bedrock_agentcore.gateway import GatewayClient

gateway = GatewayClient(region_name="us-east-1")

gw = gateway.create_gateway_and_wait(
    name="MyGateway",
    roleArn="arn:aws:iam::123456789012:role/GatewayRole",
    authorizerType="CUSTOM_JWT",
    authorizerConfiguration={
        "customJWTAuthorizer": {
            "discoveryUrl": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_xxxxx/.well-known/openid-configuration",
            "allowedAudience": ["my-client-id"],
            "allowedClients": ["my-client-id"],
        }
    },
    protocolType="MCP",
)
```

### Store Outbound Credentials

Outbound credentials go through a dedicated `create_oauth2_credential_provider`/`create_api_key_credential_provider` call - there is no generic `store_credential()`:

```python
from bedrock_agentcore.identity.auth import IdentityClient

identity = IdentityClient(region="us-east-1")

provider = identity.create_oauth2_credential_provider({
    "name": "SalesforceProvider",
    "credentialProviderVendor": "SalesforceOauth2",
    "oauth2ProviderConfigInput": {
        "salesforceOauth2ProviderConfig": {
            "clientId": "your-client-id",
            "clientSecret": "your-client-secret",
        }
    },
})

provider_arn = provider["credentialProviderArn"]
```

### Use Credentials in Agent

Tool functions pull the token in automatically via the `requires_access_token` decorator - there's no `gateway.invoke_tool()` method (Gateway has no data-plane boto3 API; agents call tools over MCP - see [AgentCore Gateway](gateway.md)):

```python
from bedrock_agentcore.identity import requires_access_token

@requires_access_token(
    provider_name="salesforce",
    scopes=["api"],
    auth_flow="USER_FEDERATION",
    on_auth_url=lambda url: print(f"Authorize this agent: {url}"),
)
def get_salesforce_account(account_id: str, *, access_token: str) -> dict:
    """access_token is injected by the decorator before the body runs."""
    import requests
    response = requests.get(
        "https://your-instance.salesforce.com/services/data/v59.0/query",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"q": f"SELECT Id FROM Account WHERE Id = '{account_id}'"},
    )
    return response.json()
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
