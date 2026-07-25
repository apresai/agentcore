# AgentCore Identity

> Identity and credential management service for AI agents with IdP integration, OAuth flows, and secure credential vending.

## Quick Reference

| CLI Command | Description |
|-------------|-------------|
| `agentcore identity setup-aws-jwt` | Set up AWS IAM JWT federation for M2M auth (no secrets) |
| `agentcore identity setup-cognito` | Create Cognito user pools for Identity auth |
| `agentcore identity create-credential-provider` | Create an OAuth2 credential provider for outbound auth |
| `agentcore identity list-credential-providers` | List configured credential providers |
| `agentcore identity create-workload-identity` | Create a workload identity for your agent |
| `agentcore identity update-workload-identity` | Update workload identity callback URLs |
| `agentcore identity get-cognito-inbound-token` | Get a Cognito access token for Runtime inbound auth |
| `agentcore identity list-aws-jwt` | List AWS IAM JWT federation configuration |
| `agentcore identity cleanup` | Clean up Identity resources for an agent |

There is no `agentcore identity list-providers` - the real command is `list-credential-providers`.

| SDK Client | Purpose |
|------------|---------|
| `IdentityClient` (`bedrock_agentcore.identity.auth`) | Workload identities, credential providers, token retrieval |
| `requires_access_token` / `requires_api_key` / `requires_iam_access_token` decorators | Inject a token/API key into a tool function before it runs |
| `bedrock-agentcore` (data plane) | Token exchange, credential retrieval |
| `bedrock-agentcore-control` (control plane) | Manage identity resources |

| Key API | Description |
|---------|-------------|
| `CreateWorkloadIdentity` | Create agent identity |
| `CreateOauth2CredentialProvider` / `CreateApiKeyCredentialProvider` | Configure outbound credentials |
| `GetResourceOauth2Token` | Get OAuth token for a service |
| `GetResourceApiKey` | Get API key for a service |

There is no unified `CreateCredentialProvider` or `GetResourceOauth2AccessToken`/`GetApiKeyCredential` API - OAuth2 and API-key credential providers are separate operation families end to end (create/get/list/update/delete), and the data-plane token calls are `GetResourceOauth2Token` and `GetResourceApiKey`.

---

## Overview

Amazon Bedrock AgentCore Identity is an identity and credential management service designed specifically for AI agents and automated workloads. It enables agents and tools to securely access AWS resources and third-party services on behalf of users while maintaining strict security controls and audit trails.

## The Problem It Solves

AI agents need credentials to access external services (Salesforce, Slack, GitHub), but managing these credentials securely is complex:
- Storing and rotating secrets
- Handling OAuth flows
- Mapping user permissions to agent actions
- Maintaining audit trails

AgentCore Identity handles all of this automatically.

---

## Core Concepts

### Workload Identity

Agent identities implemented as **workload identities**. The real `CreateWorkloadIdentity` shape is much smaller than a generic resource record - just a name, its ARN, and the OAuth2 return URLs it's allowed to redirect to:

```python
# Real CreateWorkloadIdentity / IdentityClient.create_workload_identity output
{
    "name": "CustomerSupportAgent",
    "workloadIdentityArn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:workload-identity/CustomerSupportAgent",
    "allowedResourceOauth2ReturnUrls": ["http://localhost:8081/oauth2/callback"],
}
```

There is no `workloadIdentityId`, `type`, `attributes.agentRuntimeArn`, or `attributes.capabilities` field on this resource - it does not carry a description, a type enum, or arbitrary attributes.

### Credential Providers

Configure connections to external services:
- **OAuth2 providers** - For services with OAuth (Salesforce, Slack, Google, ...) via `CreateOauth2CredentialProvider`
- **API Key providers** - For services with static keys via `CreateApiKeyCredentialProvider`

These are two separate API families (create/get/list/update/delete each), not variants of one `CreateCredentialProvider` call.

### Inbound Authorization

Verify who can invoke your agents:
- **JWT authorizer** - Validate tokens from IdPs (Cognito, Okta, Entra ID)
- **IAM authorizer** - AWS SigV4 signing
- **Custom authorizer** - Your own validation logic

### Outbound Authorization

How agents access external services:
- **User delegation (`USER_FEDERATION`)** - Act on behalf of authenticated users, with consent
- **Machine-to-machine (`M2M`)** - Use pre-configured service credentials, no user in the loop
- **Token exchange (`ON_BEHALF_OF_TOKEN_EXCHANGE`)** - Convert one token type into another
- **AWS IAM JWT federation** - Get an STS-signed JWT with no client secret at all, for services that trust AWS as an OIDC issuer

---

## CLI Reference

### Installation

```bash
pip install bedrock-agentcore-starter-toolkit
```

> See [AgentCore Runtime](./01-runtime.md#installation) for the starter toolkit's `@aws/agentcore` deprecation notice.

### agentcore identity setup-aws-jwt

Set up AWS IAM JWT federation for M2M authentication - no client secrets, the JWT is signed by AWS STS. Run it once per audience; running it again with a new `--audience` adds that audience (idempotent).

```bash
agentcore identity setup-aws-jwt [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--audience`, `-a` | Audience URL for the JWT (required) | - |
| `--signing-algorithm`, `-s` | `ES384` or `RS256` | `ES384` |
| `--duration`, `-d` | Default token duration, seconds (60-3600) | 300 |
| `--region`, `-r` | AWS region | - |

**Examples:**

```bash
agentcore identity setup-aws-jwt --audience https://api.example.com

# Add another audience later (idempotent)
agentcore identity setup-aws-jwt --audience https://api2.example.com

agentcore identity setup-aws-jwt --audience https://legacy-api.example.com --signing-algorithm RS256
```

There is no `--discovery-url` or `--client-id` flag - this command is for AWS-signed JWTs, not for configuring an external IdP as your inbound authorizer.

### agentcore identity setup-cognito

Create two Cognito user pools: a Runtime pool for agent inbound JWT auth, and an Identity pool for agent outbound OAuth. Configuration is saved for use by subsequent commands.

```bash
agentcore identity setup-cognito [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--region`, `-r` | AWS region | configured region |
| `--auth-flow` | `user` (`USER_FEDERATION`) or `m2m` (client credentials) | `user` |

There is no `--user-pool-id` or `--client-id` flag - this command creates the pools for you; it does not attach to existing ones.

### agentcore identity create-credential-provider

Create an OAuth2 credential provider (3LO support). Prints AgentCore's callback URL, which you must register with your IdP.

```bash
agentcore identity create-credential-provider [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--name`, `-n` | Provider name (required) | - |
| `--type`, `-t` | `cognito`, `github`, `google`, or `salesforce` (required) | - |
| `--client-id` | OAuth client ID (required) | - |
| `--client-secret` | OAuth client secret (required) | - |
| `--discovery-url` | OAuth discovery URL (required for `cognito`) | - |
| `--cognito-pool-id` | Cognito pool ID, to auto-update its callback URLs | - |
| `--region`, `-r` | AWS region | - |

There is no `api_key` provider type or `--api-key` flag on this command - it is OAuth2-only. `--type` only accepts `cognito`, `github`, `google`, `salesforce` here (the boto3 `credentialProviderVendor` enum is much larger - see "Supported OAuth2 Vendors" below - but the CLI only wires up these four).

**Examples:**

```bash
# Cognito provider, auto-updating callback URLs
agentcore identity create-credential-provider --name MyCognito --type cognito \
    --client-id abc123 --client-secret xyz789 \
    --discovery-url https://cognito-idp.us-west-2.amazonaws.com/us-west-2_xxx/.well-known/openid-configuration \
    --cognito-pool-id us-west-2_xxx

# GitHub provider
agentcore identity create-credential-provider --name MyGitHub --type github \
    --client-id abc123 --client-secret xyz789
```

### agentcore identity list-credential-providers

```bash
agentcore identity list-credential-providers
```

Reads from the local `.bedrock_agentcore.yaml` config, not a live account-wide listing call.

### agentcore identity create-workload-identity

Creates the workload identity your agent needs before it can obtain OAuth2 tokens, with the callback URLs OAuth providers may redirect to.

```bash
agentcore identity create-workload-identity [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--name`, `-n` | Workload identity name | auto-generated |
| `--return-urls` | Comma-separated OAuth return URLs | none |
| `--region`, `-r` | AWS region | - |

```bash
agentcore identity create-workload-identity --name MyAgent \
    --return-urls http://localhost:8081/oauth2/callback,https://prod.example.com/callback
```

---

## SDK Reference

### IdentityClient

`IdentityClient` is defined in `bedrock_agentcore.services.identity` and re-exported from `bedrock_agentcore.identity.auth` - it is **not** exported from the `bedrock_agentcore.identity` package root (`bedrock_agentcore.identity.__all__` only lists the `requires_access_token`/`requires_api_key` decorators). Its constructor takes a positional `region`, not `region_name`.

```python
from bedrock_agentcore.identity.auth import IdentityClient

client = IdentityClient(region="us-east-1")
```

Its real methods: `create_workload_identity`, `update_workload_identity`, `get_workload_identity`, `create_oauth2_credential_provider`, `create_api_key_credential_provider`, `get_token`, `get_api_key`, `get_workload_access_token`, `complete_resource_token_auth`, plus the payments-credential-provider family (`create_payment_credential_provider`, `get_payment_credential_provider`, `list_payment_credential_providers`, `update_payment_credential_provider`, `delete_payment_credential_provider`). There is no `get_resource_oauth2_access_token`, `get_api_key_credential`, `get_authorization_url`, `complete_authorization`, `get_client_credentials_token`, `refresh_token`, or `validate_token` method.

#### Create Workload Identity

```python
from bedrock_agentcore.identity.auth import IdentityClient

client = IdentityClient(region="us-east-1")

# name and allowed_resource_oauth_2_return_urls are the only real inputs -
# there is no description or agent_runtime_arn parameter.
identity = client.create_workload_identity(
    name="CustomerSupportAgent",
    allowed_resource_oauth_2_return_urls=["https://myapp.com/auth/callback"],
)

identity_arn = identity["workloadIdentityArn"]
```

#### Create Credential Providers

`create_oauth2_credential_provider`/`create_api_key_credential_provider` take a single `req` dict of keyword arguments that pass straight through to the matching boto3 control-plane call - there is no unified `create_credential_provider`.

```python
# OAuth2 provider (Salesforce)
provider = client.create_oauth2_credential_provider({
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

# API key provider
provider = client.create_api_key_credential_provider({
    "name": "WeatherAPIKey",
    "apiKey": "your-api-key",
})
```

#### Get an OAuth2 Access Token

`get_token` requires an `agent_identity_token` (the workload's own identity token, not a user ID) and an explicit `auth_flow`. There is no separate `get_authorization_url`/`complete_authorization` pair for the SDK client - for `USER_FEDERATION`, pass `on_auth_url` and `get_token` handles presenting the URL and waiting for consent internally.

```python
access_token = client.get_token(
    provider_name="salesforce",
    scopes=["api", "refresh_token"],
    agent_identity_token=agent_identity_token,
    auth_flow="USER_FEDERATION",
    on_auth_url=lambda url: print(f"Authorize this agent: {url}"),
)
```

#### Get an API Key

```python
api_key = client.get_api_key(
    provider_name="weather-api",
    agent_identity_token=agent_identity_token,
)
```

### Decorators (Recommended for Tool Functions)

For tools called from an agent framework, the decorators are the primary recommended pattern - they fetch the token and inject it as a keyword argument before the function body runs, rather than requiring manual `IdentityClient` calls inside every tool.

#### OAuth2 (`requires_access_token`)

```python
from bedrock_agentcore.identity import requires_access_token

@requires_access_token(
    provider_name="salesforce",
    scopes=["api"],
    auth_flow="USER_FEDERATION",
    on_auth_url=lambda url: print(f"Authorize this agent: {url}"),
)
def get_opportunities(query: str, *, access_token: str) -> str:
    """Call Salesforce with the injected access token."""
    import requests
    response = requests.get(
        "https://your-instance.salesforce.com/services/data/v59.0/query",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"q": query},
    )
    return response.text
```

#### API Key (`requires_api_key`)

```python
from bedrock_agentcore.identity import requires_api_key

@requires_api_key(provider_name="weather-api")
def get_weather(location: str, *, api_key: str) -> str:
    import requests
    response = requests.get(
        "https://api.weather.example.com/current",
        headers={"X-API-Key": api_key},
        params={"location": location},
    )
    return response.text
```

#### AWS-Signed JWT, No Secrets (`requires_iam_access_token`)

For M2M auth against a service that trusts AWS as an OIDC issuer - obtains a JWT from AWS STS (`GetWebIdentityToken`), no client secret anywhere. Requires `agentcore identity setup-aws-jwt` (or the equivalent IAM API call) to have enabled federation for the audience first.

```python
from bedrock_agentcore.identity.auth import requires_iam_access_token

@requires_iam_access_token(
    audience=["https://api.example.com"],
    signing_algorithm="ES384",
    duration_seconds=300,
)
def call_external_api(query: str, *, access_token: str) -> str:
    """Call external API with AWS JWT authentication."""
    import requests
    response = requests.get(
        "https://api.example.com/data",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"q": query},
    )
    return response.text
```

`requires_iam_access_token` is not exported from `bedrock_agentcore.identity.__all__` either - import it from `bedrock_agentcore.identity.auth`.

### Using boto3 Directly

```python
import boto3

# Control plane
control_client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

# Data plane
data_client = boto3.client('bedrock-agentcore', region_name='us-east-1')
```

#### Control Plane APIs

##### CreateWorkloadIdentity

```python
response = control_client.create_workload_identity(
    name='CustomerSupportAgent',
    allowedResourceOauth2ReturnUrls=['https://myapp.com/auth/callback'],
    tags={
        'Environment': 'production'
    }
)

identity_arn = response['workloadIdentityArn']
```

There is no `description`, `workloadIdentityType`, or `agentRuntimeArn` parameter, and the response has no `workloadIdentityId` field.

##### CreateOauth2CredentialProvider / CreateApiKeyCredentialProvider

```python
# OAuth2 provider (Salesforce)
response = control_client.create_oauth2_credential_provider(
    name='SalesforceProvider',
    credentialProviderVendor='SalesforceOauth2',
    oauth2ProviderConfigInput={
        'salesforceOauth2ProviderConfig': {
            'clientId': 'your-client-id',
            'clientSecret': 'your-client-secret'
        }
    }
)

provider_arn = response['credentialProviderArn']
```

```python
# OAuth2 provider (Custom)
response = control_client.create_oauth2_credential_provider(
    name='CustomAPIProvider',
    credentialProviderVendor='CustomOauth2',
    oauth2ProviderConfigInput={
        'customOauth2ProviderConfig': {
            'clientId': 'your-client-id',
            'clientSecret': 'your-client-secret',
            'oauthDiscovery': {
                'authorizationServerMetadata': {
                    'issuer': 'https://api.example.com',
                    'authorizationEndpoint': 'https://api.example.com/oauth/authorize',
                    'tokenEndpoint': 'https://api.example.com/oauth/token',
                }
            },
        }
    }
)
```

```python
# API Key provider
response = control_client.create_api_key_credential_provider(
    name='WeatherAPIKey',
    apiKey='your-api-key'
)
```

There is a single `create_credential_provider`-shaped call in neither the SDK nor boto3 - `CreateOauth2CredentialProvider` and `CreateApiKeyCredentialProvider` are always separate operations, and `apiKeyProviderConfigInput` is not a field (the API key itself is a top-level `apiKey` parameter).

**Supported OAuth2 Vendors** (`credentialProviderVendor`, from the `CreateOauth2CredentialProvider` API model - 25 values total, this is a representative subset, not exhaustive):

| Vendor | Configuration Key |
|--------|-------------------|
| Salesforce | `SalesforceOauth2` |
| Slack | `SlackOauth2` |
| GitHub | `GithubOauth2` |
| Google | `GoogleOauth2` |
| Microsoft | `MicrosoftOauth2` |
| Okta | `OktaOauth2` |
| Twitch | `TwitchOauth2` |
| LinkedIn | `LinkedinOauth2` |
| Reddit | `RedditOauth2` |
| Spotify | `SpotifyOauth2` |
| Atlassian | `AtlassianOauth2` |
| Auth0 | `Auth0Oauth2` |
| Cognito | `CognitoOauth2` |
| Custom | `CustomOauth2` |

`GitHubOauth2` and `LinkedInOauth2` are not valid values - the real keys are `GithubOauth2` and `LinkedinOauth2` (lowercase "hub"/"in"). There is no `ZendeskOauth2` vendor.

##### GetOauth2CredentialProvider / GetApiKeyCredentialProvider

```python
response = control_client.get_oauth2_credential_provider(
    name='my-provider'
)

status = response['status']  # CREATING, ACTIVE, FAILED
vendor = response['credentialProviderVendor']
```

##### ListOauth2CredentialProviders / ListApiKeyCredentialProviders

```python
response = control_client.list_oauth2_credential_providers(
    maxResults=50
)

for provider in response['credentialProviders']:
    print(f"{provider['name']}: {provider['credentialProviderVendor']}")
```

##### DeleteOauth2CredentialProvider / DeleteApiKeyCredentialProvider

```python
control_client.delete_oauth2_credential_provider(
    name='my-provider'
)
```

These operations are addressed by `name`, not by `credentialProviderArn` - unlike Gateway resources, credential providers use name as their primary identifier in the API.

#### Data Plane APIs

##### GetResourceOauth2Token

Not `GetResourceOauth2AccessToken`. Requires the caller's own `workloadIdentityToken` and an explicit `oauth2Flow`.

```python
response = data_client.get_resource_oauth2_token(
    workloadIdentityToken='workload-jwt-token',
    resourceCredentialProviderName='salesforce',
    scopes=['api', 'refresh_token'],
    oauth2Flow='USER_FEDERATION',
)

access_token = response['accessToken']
session_status = response['sessionStatus']
```

##### GetResourceApiKey

Not `GetApiKeyCredential`.

```python
response = data_client.get_resource_api_key(
    workloadIdentityToken='workload-jwt-token',
    resourceCredentialProviderName='weather-api',
)

api_key = response['apiKey']
```

---

## Supported Identity Providers

### Amazon Cognito

```python
# Configure Cognito as inbound authorizer on a Gateway (authorizerConfiguration.customJWTAuthorizer)
authorizer_config = {
    'customJWTAuthorizer': {
        'discoveryUrl': 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_xxxxx/.well-known/openid-configuration',
        'allowedAudience': ['your-app-client-id'],
        'allowedClients': ['your-app-client-id']
    }
}
```

### Okta

```python
authorizer_config = {
    'customJWTAuthorizer': {
        'discoveryUrl': 'https://your-org.okta.com/.well-known/openid-configuration',
        'allowedAudience': ['api://my-agent'],
        'allowedClients': ['0oaxxxxxxxxxxxxxxxx']
    }
}
```

### Microsoft Entra ID (Azure AD)

```python
authorizer_config = {
    'customJWTAuthorizer': {
        'discoveryUrl': 'https://login.microsoftonline.com/{tenant-id}/v2.0/.well-known/openid-configuration',
        'allowedAudience': ['api://my-agent'],
        'allowedClients': ['your-client-id']
    }
}
```

### Auth0

```python
authorizer_config = {
    'customJWTAuthorizer': {
        'discoveryUrl': 'https://your-tenant.auth0.com/.well-known/openid-configuration',
        'allowedAudience': ['https://my-agent.example.com'],
        'allowedClients': ['your-client-id']
    }
}
```

`customJWTAuthorizer` and `allowedAudience` (singular) are the real keys used inside a Gateway's `authorizerConfiguration` - see [AgentCore Gateway](./03-gateway.md#authentication).

---

## OAuth 2.0 Flows

The SDK exposes these as `auth_flow` values on `get_token` / `requires_access_token`, not as separate `get_authorization_url`/`complete_authorization`/`get_client_credentials_token`/`refresh_token` methods.

### User Federation (3LO, with consent)

```python
from bedrock_agentcore.identity.auth import IdentityClient

client = IdentityClient(region="us-east-1")

access_token = client.get_token(
    provider_name="salesforce",
    scopes=["api", "refresh_token"],
    agent_identity_token=agent_identity_token,
    auth_flow="USER_FEDERATION",
    on_auth_url=lambda url: notify_user_to_authorize(url),
    callback_url="https://your-app.com/callback",  # must be pre-registered on the workload identity
)
```

`get_token` handles presenting the authorization URL (via `on_auth_url`) and polling for completion internally; there is no separate step to "exchange a code" from application code. `complete_resource_token_auth(session_uri, user_identifier)` exists for the case where your own callback handler needs to explicitly signal that a redirect came back, but it is not the common path.

### Machine-to-Machine (2LO)

```python
access_token = client.get_token(
    provider_name="internal-service",
    scopes=["read", "write"],
    agent_identity_token=agent_identity_token,
    auth_flow="M2M",
)
```

### Force Re-authentication

```python
access_token = client.get_token(
    provider_name="salesforce",
    scopes=["api"],
    agent_identity_token=agent_identity_token,
    auth_flow="USER_FEDERATION",
    force_authentication=True,  # ignore any cached token in the vault
)
```

There is no standalone `refresh_token` method - AgentCore Identity's token vault refreshes tokens transparently on the next `get_token` call.

---

## Code Examples

### Agent Tool with User-Delegated Access

```python
from strands import Agent
from bedrock_agentcore.identity import requires_access_token

@requires_access_token(
    provider_name="salesforce",
    scopes=["api"],
    auth_flow="USER_FEDERATION",
    on_auth_url=lambda url: print(f"Authorize this agent: {url}"),
)
def salesforce_search(query: str, *, access_token: str) -> str:
    """Search Salesforce records with the injected access token."""
    import requests
    response = requests.get(
        "https://your-instance.salesforce.com/services/data/v59.0/search",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"q": query},
    )
    return response.text

agent = Agent(
    model=model,
    tools=[salesforce_search],
    system_prompt="You are a sales assistant with access to the user's Salesforce data.",
)

response = agent("Find my recent opportunities")
```

### Multi-Service Agent

```python
from bedrock_agentcore.identity.auth import IdentityClient

identity = IdentityClient(region="us-east-1")

class MultiServiceAgent:
    """Agent with access to multiple services via named credential providers."""

    def __init__(self, agent_identity_token: str):
        self.agent_identity_token = agent_identity_token
        self.providers = {
            "salesforce": "salesforce",
            "slack": "slack",
            "jira": "jira",
        }

    def get_service_token(self, service: str) -> str:
        """Get an access token for a service."""
        provider_name = self.providers.get(service)
        if not provider_name:
            raise ValueError(f"Unknown service: {service}")

        return identity.get_token(
            provider_name=provider_name,
            agent_identity_token=self.agent_identity_token,
            auth_flow="USER_FEDERATION",
        )

# Usage
agent = MultiServiceAgent(agent_identity_token)
token = agent.get_service_token("salesforce")
```

### Secure Token Caching

AgentCore Identity's own token vault already caches and refreshes tokens for you (`get_token` returns a cached token unless `force_authentication=True`), so most agents don't need a second cache layer. If you do add one on top (e.g. to avoid a network round trip per call), key it by `(agent_identity_token, provider_name)` and treat AgentCore's vault as the source of truth, not the local cache.

```python
import time
from bedrock_agentcore.identity.auth import IdentityClient

identity = IdentityClient(region="us-east-1")

class TokenCache:
    """Optional short-lived local cache in front of the AgentCore Identity vault."""

    def __init__(self, ttl_seconds: int = 60):
        self.ttl_seconds = ttl_seconds
        self.cache: dict[str, tuple[str, float]] = {}

    def get_token(self, agent_identity_token: str, provider_name: str) -> str:
        cache_key = f"{provider_name}:{hash(agent_identity_token)}"

        cached = self.cache.get(cache_key)
        if cached and time.time() < cached[1]:
            return cached[0]

        token = identity.get_token(
            provider_name=provider_name,
            agent_identity_token=agent_identity_token,
            auth_flow="M2M",
        )

        self.cache[cache_key] = (token, time.time() + self.ttl_seconds)
        return token

token_cache = TokenCache()
```

---

## Integration Patterns

### With AgentCore Runtime

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.identity.auth import IdentityClient

identity = IdentityClient(region="us-east-1")
app = BedrockAgentCoreApp()

@app.entrypoint
async def main(request):
    # The agent's own identity token, used to call AgentCore Identity on its behalf
    agent_identity_token = request.get("agent_identity_token")

    if not agent_identity_token:
        return {"error": "Authentication required"}

    # Get a service token for this workload
    sf_token = identity.get_token(
        provider_name="salesforce",
        agent_identity_token=agent_identity_token,
        auth_flow="M2M",
    )

    # Process request with the service token
    response = await process_with_credentials(
        request["prompt"],
        sf_token=sf_token,
    )

    return {"response": response}
```

### With AgentCore Gateway

```python
from bedrock_agentcore.identity.auth import IdentityClient
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

identity = IdentityClient(region="us-east-1")

def call_tool_as_user(agent_identity_token: str, provider_name: str, tool_name: str, arguments: dict):
    """Call a Gateway tool with the caller's delegated credentials."""

    token = identity.get_token(
        provider_name=provider_name,
        agent_identity_token=agent_identity_token,
        auth_flow="USER_FEDERATION",
    )

    mcp_client = MCPClient(
        lambda: streamablehttp_client(
            gateway_url, headers={"Authorization": f"Bearer {token}"}
        )
    )

    with mcp_client:
        return mcp_client.call_tool_sync(tool_use_id="call-1", name=tool_name, arguments=arguments)
```

See [AgentCore Gateway](./03-gateway.md#calling-tools-via-mcp) - Gateway has no data-plane boto3 API of its own, so tool calls always go over MCP, with the bearer token obtained here.

---

## Security Best Practices

1. **Never store secrets in code** - Use credential providers for all credentials.

2. **Use user delegation** - Let users authorize access (`USER_FEDERATION`) rather than machine credentials (`M2M`) when possible.

3. **Limit scopes** - Request only the OAuth scopes your agent needs.

4. **Prefer AWS-signed JWTs where supported** - `requires_iam_access_token` needs no client secret at all for services that trust AWS as an OIDC issuer.

5. **Audit access** - Use CloudTrail to monitor credential usage.

6. **Let the vault refresh tokens** - `get_token` refreshes transparently; reach for `force_authentication=True` only when you must invalidate a cached token.

7. **Register callback URLs precisely** - `callback_url` must be pre-registered on the workload identity; there is no wildcard matching.

8. **Secure callback endpoints** - Protect any endpoint that receives OAuth redirects against CSRF, and verify `custom_state` if you set one.

9. **Encrypt at rest** - Use KMS encryption for stored credentials where supported.

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `RequiresUserConsentException` | User hasn't granted consent yet | Handle `on_auth_url` and have the user complete authorization |
| `ResourceNotFoundException` | Invalid provider name | Verify the provider exists and is `ACTIVE` |
| `AccessDeniedException` | Missing IAM permissions | Verify the execution role can call Identity APIs |
| `ValidationException` | Invalid parameters (e.g. malformed `oauth2ProviderConfigInput`) | Check the vendor-specific config shape |
| `RuntimeError` from `requires_iam_access_token` | AWS IAM JWT federation not enabled for the audience | Run `agentcore identity setup-aws-jwt --audience ...` first |

### Debugging Tips

```bash
# List locally configured credential providers
agentcore identity list-credential-providers

# Check a provider directly via boto3 (addressed by name, not ARN)
aws bedrock-agentcore-control get-oauth2-credential-provider --name my-provider
aws bedrock-agentcore-control get-api-key-credential-provider --name my-provider

# Check CloudTrail for auth events
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=EventName,AttributeValue=GetResourceOauth2Token
```

### OAuth Flow Issues

1. **Verify the callback URL** - Must exactly match what's registered on the workload identity
2. **Check client credentials** - Verify with the OAuth provider
3. **Review scopes** - Ensure scopes are enabled with the provider
4. **Check `custom_state`** - If set, must round-trip unchanged through the callback
5. **Validate the discovery URL** - Ensure OIDC discovery is reachable (for `CUSTOM_JWT` inbound auth / `CustomOauth2` outbound providers)

---

## Limits & Quotas

| Resource | Default Limit | Adjustable |
|----------|--------------|------------|
| Credential providers per account | 100 | Yes |
| Workload identities per account | 100 | Yes |
| OAuth tokens per user per provider | 10 | No |
| Token requests per second | 100 | Yes |
| API key providers | 50 | Yes |

These per-resource limits have not been individually re-verified against the live AWS quota tables in this pass; treat them as carried forward from the prior version of this doc.

---

## Pricing

| Operation | Rate |
|-----------|------|
| Token requests | Per request |
| Credential provider storage | Per provider/month |

**Note**: No additional charges when used through AgentCore Runtime or Gateway.

---

## Related Services

- [AgentCore Runtime](./01-runtime.md) - Authentication for agents
- [AgentCore Gateway](./03-gateway.md) - Credential injection for tools
- [AgentCore Policy](./07-policy.md) - Authorization policies
- [AgentCore Observability](./08-observability.md) - Auth event monitoring
