# AgentCore Identity

> Identity and credential management service for AI agents with IdP integration, OAuth flows, and secure credential vending.

## Quick Reference

| CLI Command | Description |
|-------------|-------------|
| `agentcore identity setup-aws-jwt` | Configure AWS JWT authorizer |
| `agentcore identity setup-cognito` | Set up Cognito integration |
| `agentcore identity create-credential-provider` | Create credential provider |
| `agentcore identity list-providers` | List credential providers |

| SDK Client | Purpose |
|------------|---------|
| `IdentityClient` (AgentCore SDK) | High-level identity operations |
| `bedrock-agentcore` (data plane) | Token exchange, credential retrieval |
| `bedrock-agentcore-control` (control plane) | Manage identity resources |

| Key API | Description |
|---------|-------------|
| `CreateWorkloadIdentity` | Create agent identity |
| `CreateCredentialProvider` | Configure outbound credentials |
| `GetResourceOauth2AccessToken` | Get OAuth token for service |
| `GetApiKeyCredential` | Get API key for service |

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

Agent identities implemented as **workload identities** with specialized attributes for agent-specific capabilities while maintaining compatibility with industry-standard patterns.

```python
# Workload identity structure
{
    "workloadIdentityId": "wi-abc123xyz",
    "workloadIdentityArn": "arn:aws:bedrock-agentcore:...:workload-identity/wi-abc123",
    "name": "CustomerSupportAgent",
    "type": "AGENT",
    "attributes": {
        "agentRuntimeArn": "arn:aws:bedrock-agentcore:...:agent/...",
        "capabilities": ["crm", "email", "calendar"]
    }
}
```

### Credential Providers

Configure connections to external services:
- **OAuth2 providers** - For services with OAuth (Salesforce, Slack, Google)
- **API Key providers** - For services with static keys
- **Custom providers** - For specialized authentication

### Inbound Authorization

Verify who can invoke your agents:
- **JWT authorizer** - Validate tokens from IdPs (Cognito, Okta, Entra ID)
- **IAM authorizer** - AWS SigV4 signing
- **Custom authorizer** - Your own validation logic

### Outbound Authorization

How agents access external services:
- **User delegation** - Act on behalf of authenticated users
- **Service account** - Use pre-configured service credentials
- **Token exchange** - Convert user tokens to service tokens

---

## CLI Reference

### Installation

```bash
pip install bedrock-agentcore-starter-toolkit
```

### agentcore identity setup-aws-jwt

Configure JWT-based inbound authorization.

```bash
agentcore identity setup-aws-jwt [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--discovery-url` | OIDC discovery URL | Required |
| `--audience` | Expected audience claim | Required |
| `--client-id` | Client ID for validation | Required |
| `--gateway-id` | Gateway to configure | Optional |

**Examples:**

```bash
# Configure with Cognito
agentcore identity setup-aws-jwt \
    --discovery-url https://cognito-idp.us-east-1.amazonaws.com/us-east-1_xxxxx/.well-known/openid-configuration \
    --audience my-app-client-id \
    --client-id my-app-client-id

# Configure with Okta
agentcore identity setup-aws-jwt \
    --discovery-url https://my-org.okta.com/.well-known/openid-configuration \
    --audience api://my-agent \
    --client-id 0oaxxxxxxxx
```

### agentcore identity setup-cognito

Quick setup with Amazon Cognito.

```bash
agentcore identity setup-cognito [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--user-pool-id` | Cognito User Pool ID | Required |
| `--client-id` | App client ID | Required |
| `--region` | AWS region | us-east-1 |

**Example:**

```bash
agentcore identity setup-cognito \
    --user-pool-id us-east-1_AbCdEfGhI \
    --client-id 1abc2def3ghi4jkl5mno
```

### agentcore identity create-credential-provider

Create an outbound credential provider.

```bash
agentcore identity create-credential-provider [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--name` | Provider name | Required |
| `--type` | oauth2, api_key | Required |
| `--vendor` | Pre-built vendor (salesforce, slack, github) | Optional |
| `--client-id` | OAuth client ID | For oauth2 |
| `--client-secret` | OAuth client secret | For oauth2 |
| `--api-key` | API key value | For api_key |

**Examples:**

```bash
# Salesforce OAuth
agentcore identity create-credential-provider \
    --name SalesforceProvider \
    --type oauth2 \
    --vendor salesforce \
    --client-id YOUR_CLIENT_ID \
    --client-secret YOUR_CLIENT_SECRET

# GitHub with API key
agentcore identity create-credential-provider \
    --name GitHubProvider \
    --type api_key \
    --vendor github \
    --api-key ghp_xxxxxxxxxxxx

# Custom OAuth provider
agentcore identity create-credential-provider \
    --name CustomAPI \
    --type oauth2 \
    --authorize-url https://api.example.com/oauth/authorize \
    --token-url https://api.example.com/oauth/token \
    --client-id YOUR_CLIENT_ID \
    --client-secret YOUR_CLIENT_SECRET
```

### agentcore identity list-providers

List all credential providers.

```bash
agentcore identity list-providers

# Output
NAME                TYPE      VENDOR        STATUS
SalesforceProvider  oauth2    salesforce    ACTIVE
GitHubProvider      api_key   github        ACTIVE
CustomAPI           oauth2    custom        ACTIVE
```

---

## SDK Reference

### Using AgentCore SDK

```python
from bedrock_agentcore.identity import IdentityClient

client = IdentityClient(region_name='us-east-1')
```

#### Create Workload Identity

```python
from bedrock_agentcore.identity import IdentityClient

client = IdentityClient(region_name='us-east-1')

# Create identity for agent
identity = client.create_workload_identity(
    name="CustomerSupportAgent",
    description="Identity for customer support agent",
    agent_runtime_arn="arn:aws:bedrock-agentcore:...:agent/my-agent"
)

identity_id = identity["workloadIdentityId"]
```

#### Create OAuth2 Credential Provider

```python
# Pre-built Salesforce provider
provider = client.create_credential_provider(
    name="SalesforceProvider",
    vendor="SalesforceOauth2",
    oauth2_config={
        "clientId": "your-client-id",
        "clientSecret": "your-client-secret"
    }
)

# Custom OAuth2 provider
provider = client.create_credential_provider(
    name="CustomAPIProvider",
    vendor="CustomOauth2",
    oauth2_config={
        "clientId": "your-client-id",
        "clientSecret": "your-client-secret",
        "authorizeEndpoint": "https://api.example.com/oauth/authorize",
        "tokenEndpoint": "https://api.example.com/oauth/token",
        "issuer": "https://api.example.com"
    }
)

provider_arn = provider["credentialProviderArn"]
```

#### Create API Key Credential Provider

```python
# API key provider
provider = client.create_credential_provider(
    name="WeatherAPIKey",
    vendor="ApiKey",
    api_key_config={
        "apiKey": "your-api-key",
        "headerName": "X-API-Key"
    }
)
```

#### Get OAuth2 Access Token

```python
# Get token for user to access Salesforce
token = client.get_resource_oauth2_access_token(
    credential_provider_arn=provider_arn,
    user_id="user-123",
    scopes=["api", "refresh_token"]
)

access_token = token["accessToken"]
expires_at = token["expiresAt"]
```

#### Get API Key

```python
# Get API key for service
credential = client.get_api_key_credential(
    credential_provider_arn=provider_arn
)

api_key = credential["apiKey"]
```

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
    description='Identity for customer support agent',
    workloadIdentityType='AGENT',
    agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:123456789012:agent/my-agent',
    tags={
        'Environment': 'production'
    }
)

identity_id = response['workloadIdentityId']
identity_arn = response['workloadIdentityArn']
```

##### CreateCredentialProvider

```python
# OAuth2 provider (Salesforce)
response = control_client.create_credential_provider(
    name='SalesforceProvider',
    credentialProviderVendor='SalesforceOauth2',
    oauth2ProviderConfigInput={
        'includedOauth2ProviderConfig': {
            'clientId': 'your-client-id',
            'clientSecret': 'your-client-secret'
        }
    }
)

provider_arn = response['credentialProviderArn']
```

```python
# OAuth2 provider (Custom)
response = control_client.create_credential_provider(
    name='CustomAPIProvider',
    credentialProviderVendor='CustomOauth2',
    oauth2ProviderConfigInput={
        'customOauth2ProviderConfig': {
            'clientId': 'your-client-id',
            'clientSecret': 'your-client-secret',
            'authorizeEndpoint': 'https://api.example.com/oauth/authorize',
            'tokenEndpoint': 'https://api.example.com/oauth/token',
            'issuer': 'https://api.example.com',
            'scopes': ['read', 'write']
        }
    }
)
```

```python
# API Key provider
response = control_client.create_credential_provider(
    name='WeatherAPIKey',
    credentialProviderVendor='ApiKey',
    apiKeyProviderConfigInput={
        'apiKey': 'your-api-key'
    }
)
```

**Supported OAuth2 Vendors:**

| Vendor | Configuration Key |
|--------|-------------------|
| Salesforce | `SalesforceOauth2` |
| Slack | `SlackOauth2` |
| GitHub | `GitHubOauth2` |
| Google | `GoogleOauth2` |
| Microsoft | `MicrosoftOauth2` |
| Okta | `OktaOauth2` |
| Twitch | `TwitchOauth2` |
| LinkedIn | `LinkedInOauth2` |
| Reddit | `RedditOauth2` |
| Spotify | `SpotifyOauth2` |
| Zendesk | `ZendeskOauth2` |
| Custom | `CustomOauth2` |

##### GetCredentialProvider

```python
response = control_client.get_credential_provider(
    credentialProviderArn='arn:aws:bedrock-agentcore:...:credential-provider/cp-abc123'
)

status = response['status']  # CREATING, ACTIVE, FAILED
vendor = response['credentialProviderVendor']
```

##### ListCredentialProviders

```python
response = control_client.list_credential_providers(
    maxResults=50
)

for provider in response['credentialProviderSummaries']:
    print(f"{provider['name']}: {provider['credentialProviderVendor']}")
```

##### DeleteCredentialProvider

```python
control_client.delete_credential_provider(
    credentialProviderArn='arn:aws:bedrock-agentcore:...:credential-provider/cp-abc123'
)
```

#### Data Plane APIs

##### GetResourceOauth2AccessToken

```python
# Get OAuth access token for a user
response = data_client.get_resource_oauth2_access_token(
    credentialProviderArn='arn:aws:bedrock-agentcore:...:credential-provider/salesforce',
    workloadIdentityToken='user-jwt-token',  # User's identity token
    scopes=['api', 'refresh_token']
)

access_token = response['accessToken']
token_type = response['tokenType']
expires_in = response['expiresIn']
```

##### GetApiKeyCredential

```python
# Get API key
response = data_client.get_api_key_credential(
    credentialProviderArn='arn:aws:bedrock-agentcore:...:credential-provider/weather-api'
)

api_key = response['apiKey']
```

---

## Supported Identity Providers

### Amazon Cognito

```python
# Configure Cognito as inbound authorizer
authorizer_config = {
    'customJwtAuthorizerConfig': {
        'discoveryUrl': 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_xxxxx/.well-known/openid-configuration',
        'allowedAudiences': ['your-app-client-id'],
        'allowedClients': ['your-app-client-id']
    }
}
```

### Okta

```python
# Configure Okta as inbound authorizer
authorizer_config = {
    'customJwtAuthorizerConfig': {
        'discoveryUrl': 'https://your-org.okta.com/.well-known/openid-configuration',
        'allowedAudiences': ['api://my-agent'],
        'allowedClients': ['0oaxxxxxxxxxxxxxxxx']
    }
}
```

### Microsoft Entra ID (Azure AD)

```python
# Configure Entra ID as inbound authorizer
authorizer_config = {
    'customJwtAuthorizerConfig': {
        'discoveryUrl': 'https://login.microsoftonline.com/{tenant-id}/v2.0/.well-known/openid-configuration',
        'allowedAudiences': ['api://my-agent'],
        'allowedClients': ['your-client-id']
    }
}
```

### Auth0

```python
# Configure Auth0 as inbound authorizer
authorizer_config = {
    'customJwtAuthorizerConfig': {
        'discoveryUrl': 'https://your-tenant.auth0.com/.well-known/openid-configuration',
        'allowedAudiences': ['https://my-agent.example.com'],
        'allowedClients': ['your-client-id']
    }
}
```

---

## OAuth 2.0 Flows

### Authorization Code Flow (3LO)

For user delegation with consent.

```python
from bedrock_agentcore.identity import IdentityClient

client = IdentityClient()

# Step 1: Generate authorization URL
auth_url = client.get_authorization_url(
    credential_provider_arn=provider_arn,
    redirect_uri="https://your-app.com/callback",
    scopes=["api", "refresh_token"],
    state="random-state-string"
)

# Step 2: User visits auth_url and grants consent
# Step 3: Handle callback with authorization code

# Step 4: Exchange code for tokens
tokens = client.complete_authorization(
    credential_provider_arn=provider_arn,
    authorization_code=code,
    redirect_uri="https://your-app.com/callback"
)

access_token = tokens["accessToken"]
refresh_token = tokens["refreshToken"]
```

### Client Credentials Flow (2LO)

For machine-to-machine authentication.

```python
# Get token using service credentials
token = client.get_client_credentials_token(
    credential_provider_arn=provider_arn,
    scopes=["read", "write"]
)

access_token = token["accessToken"]
```

### Token Refresh

```python
# Refresh an expired token
new_token = client.refresh_token(
    credential_provider_arn=provider_arn,
    refresh_token=refresh_token
)
```

---

## Code Examples

### Agent with User-Delegated Access

```python
from strands import Agent
from bedrock_agentcore.identity import IdentityClient
from bedrock_agentcore.gateway import GatewayClient

identity = IdentityClient()
gateway = GatewayClient(gateway_id="gw-abc123")

def create_agent_with_user_context(user_token: str):
    """Create agent that acts on behalf of user."""

    # Get Salesforce token for this user
    sf_token = identity.get_resource_oauth2_access_token(
        credential_provider_arn="arn:aws:...:credential-provider/salesforce",
        workload_identity_token=user_token,
        scopes=["api"]
    )

    # Configure agent to use this token
    agent = Agent(
        model=model,
        tools=[
            lambda args: gateway.call_tool(
                tool_name=args["name"],
                arguments=args["arguments"],
                bearer_token=sf_token["accessToken"]
            )
        ],
        system_prompt="You are a sales assistant with access to the user's Salesforce data."
    )

    return agent

# Usage
agent = create_agent_with_user_context(user_jwt)
response = agent("Find my recent opportunities")
```

### OAuth Callback Handler

```python
from flask import Flask, request, redirect
from bedrock_agentcore.identity import IdentityClient

app = Flask(__name__)
identity = IdentityClient()

@app.route("/auth/start")
def start_auth():
    """Initiate OAuth flow."""
    auth_url = identity.get_authorization_url(
        credential_provider_arn=SALESFORCE_PROVIDER_ARN,
        redirect_uri="https://myapp.com/auth/callback",
        scopes=["api", "refresh_token"],
        state=generate_state_token()
    )
    return redirect(auth_url)

@app.route("/auth/callback")
def auth_callback():
    """Handle OAuth callback."""
    code = request.args.get("code")
    state = request.args.get("state")

    # Verify state
    if not verify_state_token(state):
        return "Invalid state", 400

    # Complete authorization
    tokens = identity.complete_authorization(
        credential_provider_arn=SALESFORCE_PROVIDER_ARN,
        authorization_code=code,
        redirect_uri="https://myapp.com/auth/callback"
    )

    # Store tokens for user
    store_user_tokens(get_current_user(), tokens)

    return redirect("/dashboard")
```

### Multi-Service Agent

```python
from bedrock_agentcore.identity import IdentityClient
from bedrock_agentcore.gateway import GatewayClient

identity = IdentityClient()

class MultiServiceAgent:
    """Agent with access to multiple services."""

    def __init__(self, user_token: str):
        self.user_token = user_token
        self.providers = {
            "salesforce": "arn:aws:...:credential-provider/salesforce",
            "slack": "arn:aws:...:credential-provider/slack",
            "jira": "arn:aws:...:credential-provider/jira"
        }

    def get_service_token(self, service: str) -> str:
        """Get access token for a service."""
        provider_arn = self.providers.get(service)
        if not provider_arn:
            raise ValueError(f"Unknown service: {service}")

        token = identity.get_resource_oauth2_access_token(
            credential_provider_arn=provider_arn,
            workload_identity_token=self.user_token
        )
        return token["accessToken"]

    def call_service(self, service: str, action: str, params: dict):
        """Call a service action with proper credentials."""
        token = self.get_service_token(service)

        # Use gateway with service-specific token
        return gateway.call_tool(
            tool_name=f"{service}_{action}",
            arguments=params,
            bearer_token=token
        )

# Usage
agent = MultiServiceAgent(user_jwt)
result = agent.call_service("salesforce", "get_opportunities", {"limit": 10})
```

### Secure Credential Caching

```python
import time
from functools import lru_cache
from bedrock_agentcore.identity import IdentityClient

identity = IdentityClient()

class TokenCache:
    """Cache tokens with expiration."""

    def __init__(self):
        self.cache = {}

    def get_token(self, user_id: str, provider_arn: str) -> str:
        """Get cached token or fetch new one."""
        cache_key = f"{user_id}:{provider_arn}"

        # Check cache
        if cache_key in self.cache:
            token_data = self.cache[cache_key]
            if time.time() < token_data["expires_at"] - 60:  # 1 min buffer
                return token_data["access_token"]

        # Fetch new token
        token = identity.get_resource_oauth2_access_token(
            credential_provider_arn=provider_arn,
            user_id=user_id
        )

        # Cache it
        self.cache[cache_key] = {
            "access_token": token["accessToken"],
            "expires_at": time.time() + token["expiresIn"]
        }

        return token["accessToken"]

    def invalidate(self, user_id: str, provider_arn: str):
        """Invalidate cached token."""
        cache_key = f"{user_id}:{provider_arn}"
        self.cache.pop(cache_key, None)

token_cache = TokenCache()
```

---

## Integration Patterns

### With AgentCore Runtime

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.identity import IdentityClient

identity = IdentityClient()
app = BedrockAgentCoreApp()

@app.entrypoint()
async def main(request):
    # Extract user token from request
    user_token = request.get("bearer_token")

    if not user_token:
        return {"error": "Authentication required"}

    # Validate token
    try:
        user_info = identity.validate_token(user_token)
    except Exception:
        return {"error": "Invalid token"}

    # Get service tokens for this user
    sf_token = identity.get_resource_oauth2_access_token(
        credential_provider_arn=SF_PROVIDER_ARN,
        workload_identity_token=user_token
    )

    # Process request with user context
    response = await process_with_credentials(
        request["prompt"],
        sf_token=sf_token["accessToken"],
        user_id=user_info["sub"]
    )

    return {"response": response}
```

### With AgentCore Gateway

```python
from bedrock_agentcore.gateway import GatewayClient
from bedrock_agentcore.identity import IdentityClient

identity = IdentityClient()
gateway = GatewayClient(gateway_id="gw-abc123")

def call_tool_as_user(user_id: str, tool_name: str, arguments: dict):
    """Call gateway tool with user's credentials."""

    # Determine which provider the tool needs
    tool_config = gateway.get_tool_config(tool_name)
    provider_arn = tool_config.get("credentialProviderArn")

    if provider_arn:
        # Get user's token for this service
        token = identity.get_resource_oauth2_access_token(
            credential_provider_arn=provider_arn,
            user_id=user_id
        )
        bearer_token = token["accessToken"]
    else:
        bearer_token = None

    # Call tool
    return gateway.call_tool(
        tool_name=tool_name,
        arguments=arguments,
        bearer_token=bearer_token
    )
```

---

## Security Best Practices

1. **Never store secrets in code** - Use credential providers for all credentials.

2. **Use user delegation** - Let users authorize access rather than using service accounts when possible.

3. **Limit scopes** - Request only the OAuth scopes your agent needs.

4. **Rotate credentials** - Set up automatic rotation for API keys.

5. **Audit access** - Use CloudTrail to monitor credential usage.

6. **Use short-lived tokens** - Prefer short expiration times with refresh tokens.

7. **Validate tokens** - Always verify JWT tokens before trusting claims.

8. **Implement PKCE** - Use Proof Key for Code Exchange for public clients.

9. **Secure callbacks** - Protect OAuth callback endpoints against CSRF.

10. **Encrypt at rest** - Use KMS encryption for stored credentials.

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `InvalidToken` | Expired or malformed JWT | Check token expiration, validate format |
| `ProviderNotFound` | Invalid provider ARN | Verify provider exists and is ACTIVE |
| `AuthorizationFailed` | User hasn't granted consent | Initiate OAuth flow for user |
| `TokenRefreshFailed` | Invalid refresh token | Re-authenticate user |
| `ScopeNotGranted` | Missing required scope | Request scope during authorization |
| `ClientError` | Invalid client credentials | Verify client ID/secret |

### Debugging Tips

```bash
# Check provider status
aws bedrock-agentcore-control get-credential-provider \
    --credential-provider-arn arn:aws:...:credential-provider/my-provider

# List all providers
aws bedrock-agentcore-control list-credential-providers

# Check CloudTrail for auth events
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=EventName,AttributeValue=GetResourceOauth2AccessToken
```

### OAuth Flow Issues

1. **Verify redirect URI** - Must exactly match registered URI
2. **Check client credentials** - Verify with OAuth provider
3. **Review scopes** - Ensure scopes are enabled in provider
4. **Check state parameter** - Must match for security
5. **Validate discovery URL** - Ensure OIDC discovery is accessible

---

## Limits & Quotas

| Resource | Default Limit | Adjustable |
|----------|--------------|------------|
| Credential providers per account | 100 | Yes |
| Workload identities per account | 100 | Yes |
| OAuth tokens per user per provider | 10 | No |
| Token requests per second | 100 | Yes |
| API key providers | 50 | Yes |

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
