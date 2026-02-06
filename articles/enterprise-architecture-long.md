# Enterprise Agent Platform Architecture with AgentCore

![AgentCore Gateway](images/gateway-article.webp)

Your organization has 15 teams building AI agents. Each team picked its own framework, rolled its own authentication, and hard-coded API integrations. Three months later you have 15 agents, 15 different security postures, 15 sets of duplicated credentials, and zero cross-team visibility. One agent has production access to Salesforce with an API key stored in plaintext. Another bypasses your IdP entirely. Nobody knows what tools any agent can actually invoke.

This is the enterprise agent sprawl problem, and it mirrors the microservices sprawl that platform engineering was created to solve a decade ago. The difference is that AI agents are non-deterministic. A container that misbehaves does the same wrong thing every time. An agent that misbehaves does something different each time, making the blast radius of poor governance unpredictable and potentially catastrophic.

The solution is the same pattern that worked for microservices: a centralized platform layer that provides shared infrastructure, consistent security, and unified governance while preserving team autonomy over agent logic. But the platform must account for agent-specific concerns that container orchestrators never had to handle: tool discovery across hundreds of enterprise APIs, persistent memory shared between cooperating agents, deterministic policy enforcement over non-deterministic behavior, and federated identity that flows from the human user through to the downstream service the agent calls on their behalf.

This article presents a reference architecture for an enterprise agent platform built on AWS Bedrock AgentCore. It covers four pillars: a centralized tool gateway for enterprise APIs, shared memory stores across agent teams, Cedar policy governance for multi-tenant isolation, and Identity service integration with enterprise IdPs like Okta and Microsoft Entra ID. The architecture is framework-agnostic, model-agnostic, and designed for organizations running agents at scale across multiple business units.

## The Solution

AgentCore provides nine modular services that compose into a platform layer for AI agents. For enterprise architecture, four services form the foundation:

- **Gateway** -- Centralized tool management that converts enterprise APIs, Lambda functions, and MCP servers into a unified MCP-compatible tool layer with authentication, semantic discovery, and policy enforcement at the boundary.
- **Memory** -- Short-term and long-term context management with shared memory stores that enable multi-agent coordination, session handoffs, and cross-team knowledge sharing.
- **Policy** -- Cedar-based deterministic access control that enforces tenant isolation, role-based tool restrictions, and hard limits at the Gateway boundary before any tool call executes.
- **Identity** -- Federated authentication with native support for Okta, Microsoft Entra ID, Amazon Cognito, and Auth0, providing both inbound authorization (who calls the agent) and outbound credential vending (what the agent can access on behalf of the user).

These four services, deployed on AgentCore Runtime with Observability for monitoring, give you a platform that multiple teams can build on without duplicating infrastructure or compromising security.

### Platform Architecture Overview

```
                         Enterprise Agent Platform
  ┌──────────────────────────────────────────────────────────────────┐
  │                                                                  │
  │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
  │   │ Team A   │  │ Team B   │  │ Team C   │  │ Team D   │       │
  │   │ Support  │  │ Sales    │  │ Finance  │  │ Ops/SRE  │       │
  │   │ Agent    │  │ Agent    │  │ Agent    │  │ Agent    │       │
  │   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
  │        │              │              │              │             │
  │   ┌────┴──────────────┴──────────────┴──────────────┴────┐       │
  │   │              AgentCore Runtime                       │       │
  │   │           (microVM per session)                      │       │
  │   └────┬──────────────┬──────────────┬──────────────┬────┘       │
  │        │              │              │              │             │
  │   ┌────▼────┐   ┌─────▼─────┐  ┌────▼────┐  ┌─────▼──────┐     │
  │   │ Gateway │   │  Memory   │  │ Policy  │  │  Identity  │     │
  │   │ (Tools) │   │ (Context) │  │ (Cedar) │  │ (Auth/IdP) │     │
  │   └────┬────┘   └───────────┘  └─────────┘  └─────┬──────┘     │
  │        │                                           │             │
  │   ┌────▼────────────────────────────────────────────▼────┐       │
  │   │              Enterprise Services                     │       │
  │   │  Salesforce │ Jira │ Slack │ Internal APIs │ DBs     │       │
  │   └─────────────────────────────────────────────────────-┘       │
  │                                                                  │
  │   ┌──────────────────────────────────────────────────────┐       │
  │   │              Observability (CloudWatch + OTEL)       │       │
  │   └──────────────────────────────────────────────────────┘       │
  │                                                                  │
  └──────────────────────────────────────────────────────────────────┘
```

Every agent, regardless of team or framework, connects to the same Gateway for tools, the same Memory stores for shared context, the same Policy engine for governance, and the same Identity service for authentication. Individual teams retain full control over their agent logic, framework choice, model selection, and prompt engineering.

## Prerequisites

### AWS Account Setup

- AWS account with Amazon Bedrock AgentCore access enabled
- IAM permissions: `bedrock-agentcore:*`, `bedrock:InvokeModel`, `iam:CreateRole`, `iam:AttachRolePolicy`, `lambda:CreateFunction`
- Region: us-east-1 (primary), us-west-2 (secondary recommended)

### Local Environment

- Python 3.10+
- AWS CLI v2 configured with appropriate credentials
- pip for package management

### Required Packages

```bash
# requirements.txt
boto3>=1.34.0
strands-agents>=0.1.0
bedrock-agentcore-sdk>=1.0.0
python-dotenv>=1.0.0
```

### Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install bedrock-agentcore-starter-toolkit
```

## Getting Started

This section walks through building the enterprise platform layer step by step: centralized gateway, shared memory, Cedar policies for tenant isolation, and federated identity. Each step produces infrastructure that multiple agent teams can share.

### Step 1: Initialize Platform Clients

All platform components use the same boto3 control plane and data plane clients. Set these up once.

```python
import boto3
import json
import time
import os
from datetime import datetime, timezone

REGION = os.getenv("AWS_REGION", "us-east-1")
ACCOUNT_ID = boto3.client("sts").get_caller_identity()["Account"]

# Control plane: manage resources (gateways, memories, policies)
control = boto3.client("bedrock-agentcore-control", region_name=REGION)

# Data plane: invoke tools, store events, retrieve memories
data = boto3.client("bedrock-agentcore", region_name=REGION)

# IAM for role management
iam = boto3.client("iam", region_name=REGION)

print(f"Account: {ACCOUNT_ID}")
print(f"Region: {REGION}")
```

### Step 2: Create the Centralized Enterprise Gateway

The Gateway is the heart of the platform. Instead of each team integrating APIs independently, every enterprise tool is registered once in a central Gateway. Agents discover and invoke tools through MCP, and authentication plus policy enforcement happens at the boundary.

#### Create the IAM Role

```python
def create_gateway_role(role_name: str) -> str:
    """Create IAM role for Gateway to invoke Lambda functions and access services."""
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        "aws:SourceAccount": ACCOUNT_ID
                    }
                },
            }
        ],
    }

    try:
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Gateway execution role for enterprise agent platform",
            Tags=[
                {"Key": "Platform", "Value": "enterprise-agents"},
                {"Key": "Component", "Value": "gateway"},
            ],
        )
        role_arn = response["Role"]["Arn"]
    except iam.exceptions.EntityAlreadyExistsException:
        role_arn = f"arn:aws:iam::{ACCOUNT_ID}:role/{role_name}"

    # Attach policy for Lambda invocation
    gateway_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["lambda:InvokeFunction"],
                "Resource": f"arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:*",
            },
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject"],
                "Resource": f"arn:aws:s3:::enterprise-agent-specs/*",
            },
        ],
    }

    iam.put_role_policy(
        RoleName=role_name,
        PolicyName="GatewayExecutionPolicy",
        PolicyDocument=json.dumps(gateway_policy),
    )

    # Wait for IAM propagation
    print(f"Gateway role created: {role_arn}")
    print("Waiting for IAM propagation...")
    time.sleep(10)
    return role_arn


gateway_role_arn = create_gateway_role("enterprise-agent-gateway-role")
```

#### Create the Gateway with JWT Authentication

For enterprise deployments, configure the Gateway with CUSTOM_JWT authentication so it validates tokens from your corporate IdP.

```python
def create_enterprise_gateway(
    name: str,
    role_arn: str,
    idp_discovery_url: str,
    allowed_audiences: list,
    allowed_clients: list,
) -> dict:
    """Create a centralized enterprise gateway with JWT auth and semantic search."""
    response = control.create_gateway(
        name=name,
        description="Centralized enterprise tool gateway for all agent teams",
        roleArn=role_arn,
        authorizerType="CUSTOM_JWT",
        authorizerConfiguration={
            "customJwtAuthorizerConfig": {
                "discoveryUrl": idp_discovery_url,
                "allowedAudiences": allowed_audiences,
                "allowedClients": allowed_clients,
            }
        },
        protocolType="MCP",
        searchConfiguration={"searchType": "SEMANTIC"},
        tags={
            "Platform": "enterprise-agents",
            "Environment": "production",
            "ManagedBy": "platform-team",
        },
    )

    gateway_id = response["gatewayId"]
    gateway_arn = response["gatewayArn"]
    print(f"Gateway created: {gateway_id}")

    # Wait for ACTIVE status
    for attempt in range(60):
        status_response = control.get_gateway(gatewayIdentifier=gateway_id)
        status = status_response["status"]
        if status == "ACTIVE":
            print(f"Gateway is ACTIVE")
            return {
                "gatewayId": gateway_id,
                "gatewayArn": gateway_arn,
                "status": status,
            }
        if status in ("FAILED", "CREATE_FAILED"):
            raise RuntimeError(f"Gateway creation failed: {status}")
        time.sleep(5)

    raise TimeoutError("Gateway did not become ACTIVE within timeout")


# Example: Configure with Okta as the enterprise IdP
# Replace with your actual Okta org URL and client IDs
gateway = create_enterprise_gateway(
    name="EnterprisePlatformGateway",
    role_arn=gateway_role_arn,
    idp_discovery_url="https://your-org.okta.com/.well-known/openid-configuration",
    allowed_audiences=["api://enterprise-agents"],
    allowed_clients=["0oa_your_okta_client_id"],
)

GATEWAY_ID = gateway["gatewayId"]
GATEWAY_ARN = gateway["gatewayArn"]
```

#### Register Enterprise Tool Targets

Each business unit's APIs are registered as Gateway targets. This is a one-time setup per API, after which any authorized agent can discover and use the tools.

```python
def add_lambda_target(gateway_id: str, target_name: str, lambda_arn: str, tools: list) -> dict:
    """Add a Lambda-backed tool target to the enterprise gateway."""
    response = control.create_gateway_target(
        gatewayIdentifier=gateway_id,
        name=target_name,
        targetConfiguration={
            "lambdaTargetConfiguration": {
                "lambdaArn": lambda_arn,
                "toolSchema": {"tools": tools},
            }
        },
    )
    print(f"Target added: {target_name} -> {lambda_arn}")
    return response


def add_openapi_target(
    gateway_id: str,
    target_name: str,
    spec_bucket: str,
    spec_key: str,
    endpoint_url: str,
    credential_provider_arn: str = None,
) -> dict:
    """Add an OpenAPI-backed tool target to the enterprise gateway."""
    target_config = {
        "openApiTargetConfiguration": {
            "openApiSpecificationS3Location": {
                "bucket": spec_bucket,
                "key": spec_key,
            },
            "endpointConfiguration": {"url": endpoint_url},
        }
    }

    if credential_provider_arn:
        target_config["openApiTargetConfiguration"][
            "credentialProviderArn"
        ] = credential_provider_arn

    response = control.create_gateway_target(
        gatewayIdentifier=gateway_id,
        name=target_name,
        targetConfiguration=target_config,
    )
    print(f"Target added: {target_name} -> {endpoint_url}")
    return response


# --- Register CRM tools (Salesforce via Lambda) ---
crm_tools = [
    {
        "name": "lookup_customer",
        "description": "Look up a customer by email, name, or account ID in Salesforce",
        "inputSchema": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Customer email address"},
                "account_id": {"type": "string", "description": "Salesforce account ID"},
                "name": {"type": "string", "description": "Customer name"},
            },
        },
    },
    {
        "name": "get_opportunities",
        "description": "Get sales opportunities for a customer account",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "Salesforce account ID",
                },
                "stage": {
                    "type": "string",
                    "description": "Filter by opportunity stage",
                    "enum": [
                        "Prospecting",
                        "Qualification",
                        "Proposal",
                        "Negotiation",
                        "Closed Won",
                        "Closed Lost",
                    ],
                },
            },
            "required": ["account_id"],
        },
    },
    {
        "name": "create_case",
        "description": "Create a support case in Salesforce",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string", "description": "Customer account ID"},
                "subject": {"type": "string", "description": "Case subject line"},
                "description": {"type": "string", "description": "Case description"},
                "priority": {
                    "type": "string",
                    "enum": ["Low", "Medium", "High", "Critical"],
                },
            },
            "required": ["account_id", "subject", "description"],
        },
    },
]

add_lambda_target(
    gateway_id=GATEWAY_ID,
    target_name="CRMTools",
    lambda_arn=f"arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:SalesforceBridge",
    tools=crm_tools,
)

# --- Register ticketing tools (Jira via Lambda) ---
ticketing_tools = [
    {
        "name": "create_ticket",
        "description": "Create a Jira ticket in the specified project",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_key": {"type": "string", "description": "Jira project key"},
                "summary": {"type": "string", "description": "Ticket summary"},
                "description": {"type": "string", "description": "Detailed description"},
                "issue_type": {
                    "type": "string",
                    "enum": ["Bug", "Task", "Story", "Epic"],
                },
                "priority": {
                    "type": "string",
                    "enum": ["Lowest", "Low", "Medium", "High", "Highest"],
                },
                "assignee": {"type": "string", "description": "Assignee username"},
            },
            "required": ["project_key", "summary", "issue_type"],
        },
    },
    {
        "name": "get_ticket",
        "description": "Get details of an existing Jira ticket",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "string", "description": "Jira ticket ID (e.g., PROJ-123)"},
            },
            "required": ["ticket_id"],
        },
    },
    {
        "name": "update_ticket",
        "description": "Update status, priority, or assignee of a Jira ticket",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "string", "description": "Jira ticket ID"},
                "status": {
                    "type": "string",
                    "enum": ["To Do", "In Progress", "In Review", "Done"],
                },
                "priority": {"type": "string"},
                "assignee": {"type": "string"},
                "comment": {"type": "string", "description": "Comment to add"},
            },
            "required": ["ticket_id"],
        },
    },
]

add_lambda_target(
    gateway_id=GATEWAY_ID,
    target_name="TicketingTools",
    lambda_arn=f"arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:JiraBridge",
    tools=ticketing_tools,
)

# --- Register internal API tools (REST via OpenAPI) ---
add_openapi_target(
    gateway_id=GATEWAY_ID,
    target_name="InternalAPIs",
    spec_bucket="enterprise-agent-specs",
    spec_key="internal-api-v2.yaml",
    endpoint_url="https://api.internal.example.com/v2",
)

# --- Register communication tools (Slack via Lambda) ---
comms_tools = [
    {
        "name": "send_message",
        "description": "Send a message to a Slack channel or user",
        "inputSchema": {
            "type": "object",
            "properties": {
                "channel": {"type": "string", "description": "Channel name or user ID"},
                "message": {"type": "string", "description": "Message text"},
            },
            "required": ["channel", "message"],
        },
    },
    {
        "name": "search_messages",
        "description": "Search for messages across Slack channels",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "channel": {"type": "string", "description": "Limit to specific channel"},
                "limit": {"type": "integer", "description": "Max results to return"},
            },
            "required": ["query"],
        },
    },
]

add_lambda_target(
    gateway_id=GATEWAY_ID,
    target_name="CommsTools",
    lambda_arn=f"arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:SlackBridge",
    tools=comms_tools,
)

print(f"\nEnterprise Gateway configured: {GATEWAY_ID}")
print("Targets: CRMTools, TicketingTools, InternalAPIs, CommsTools")
```

#### Verify Gateway Tools

Once targets are registered, any authorized agent can discover available tools through the MCP protocol.

```python
def list_gateway_tools(gateway_id: str) -> list:
    """List all tools available through the enterprise gateway."""
    response = data.invoke_gateway(
        gatewayIdentifier=gateway_id,
        method="tools/list",
        payload=json.dumps({}).encode(),
    )
    result = json.loads(response["payload"].read())
    tools = result.get("tools", [])
    print(f"Available tools ({len(tools)}):")
    for tool in tools:
        print(f"  - {tool['name']}: {tool.get('description', 'N/A')}")
    return tools


def search_gateway_tools(gateway_id: str, query: str, max_results: int = 5) -> list:
    """Semantic search for tools matching a natural language query."""
    response = data.search_gateway_tools(
        gatewayIdentifier=gateway_id,
        query=query,
        maxResults=max_results,
    )
    tools = response.get("tools", [])
    print(f"Search results for '{query}':")
    for tool in tools:
        print(f"  - {tool['name']} (score: {tool.get('relevanceScore', 'N/A')})")
    return tools


# List all enterprise tools
all_tools = list_gateway_tools(GATEWAY_ID)

# Semantic search -- agent asks "how do I create a support ticket?"
relevant_tools = search_gateway_tools(
    GATEWAY_ID, "create a support ticket for a customer issue"
)
```

### Multi-Tenant Gateway Architecture

In a multi-tenant deployment, you have two architecture options depending on your isolation requirements.

#### Option A: Shared Gateway with Policy Isolation

All tenants share a single Gateway. Cedar policies enforce tenant-level isolation at the tool-call boundary. This is simpler to manage and works well when tenants share the same tool catalog but need access restrictions.

```
            ┌──────────────────────────────┐
            │    Shared Enterprise Gateway  │
            │  ┌─────────────────────────┐  │
            │  │  Policy Engine (Cedar)  │  │
            │  │ ┌─────┐ ┌─────┐ ┌────┐ │  │
            │  │ │Tnt A│ │Tnt B│ │Tnt C│ │  │
            │  │ │Rules│ │Rules│ │Rules│ │  │
            │  │ └─────┘ └─────┘ └────┘ │  │
            │  └─────────────────────────┘  │
            │                               │
            │  ┌──────────────────────────┐ │
            │  │    Tool Targets          │ │
            │  │  CRM │ Jira │ Slack │ DB │ │
            │  └──────────────────────────┘ │
            └──────────────────────────────-┘
```

#### Option B: Per-Tenant Gateways

Each tenant gets its own Gateway with its own tool targets and policy engine. This provides stronger isolation but requires more management overhead. Use this when tenants have fundamentally different tool catalogs or strict regulatory requirements.

```
   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
   │  Tenant A GW     │  │  Tenant B GW     │  │  Tenant C GW     │
   │  ┌────────────┐  │  │  ┌────────────┐  │  │  ┌────────────┐  │
   │  │Policy Eng. │  │  │  │Policy Eng. │  │  │  │Policy Eng. │  │
   │  └────────────┘  │  │  └────────────┘  │  │  └────────────┘  │
   │  ┌────────────┐  │  │  ┌────────────┐  │  │  ┌────────────┐  │
   │  │ CRM │ Jira │  │  │  │ CRM │ API  │  │  │  │ DB  │ Slack│  │
   │  └────────────┘  │  │  └────────────┘  │  │  └────────────┘  │
   └─────────────────-┘  └─────────────────-┘  └─────────────────-┘
```

For most enterprises, Option A with Cedar policy isolation is the right starting point. Here is how to provision per-tenant gateways if you need Option B:

```python
def create_tenant_gateway(
    tenant_id: str,
    role_arn: str,
    idp_discovery_url: str,
    allowed_audiences: list,
    allowed_clients: list,
) -> dict:
    """Create an isolated gateway for a specific tenant."""
    response = control.create_gateway(
        name=f"Gateway-{tenant_id}",
        description=f"Isolated gateway for tenant {tenant_id}",
        roleArn=role_arn,
        authorizerType="CUSTOM_JWT",
        authorizerConfiguration={
            "customJwtAuthorizerConfig": {
                "discoveryUrl": idp_discovery_url,
                "allowedAudiences": allowed_audiences,
                "allowedClients": allowed_clients,
            }
        },
        protocolType="MCP",
        searchConfiguration={"searchType": "SEMANTIC"},
        tags={
            "Platform": "enterprise-agents",
            "TenantId": tenant_id,
            "IsolationModel": "per-tenant",
        },
    )

    gateway_id = response["gatewayId"]

    # Wait for ACTIVE
    for attempt in range(60):
        status_response = control.get_gateway(gatewayIdentifier=gateway_id)
        if status_response["status"] == "ACTIVE":
            break
        time.sleep(5)

    print(f"Tenant gateway created: {tenant_id} -> {gateway_id}")
    return {
        "tenantId": tenant_id,
        "gatewayId": gateway_id,
        "gatewayArn": response["gatewayArn"],
    }


class TenantGatewayRegistry:
    """Registry for managing per-tenant gateways in a multi-tenant platform."""

    def __init__(self):
        self.tenants = {}

    def register(self, tenant_id: str, gateway_id: str, gateway_arn: str):
        """Register a tenant's gateway."""
        self.tenants[tenant_id] = {
            "gatewayId": gateway_id,
            "gatewayArn": gateway_arn,
        }

    def get_gateway_id(self, tenant_id: str) -> str:
        """Get the gateway ID for a tenant."""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            raise ValueError(f"No gateway registered for tenant: {tenant_id}")
        return tenant["gatewayId"]

    def call_tool(self, tenant_id: str, tool_name: str, arguments: dict) -> dict:
        """Call a tool through the correct tenant gateway."""
        gateway_id = self.get_gateway_id(tenant_id)
        response = data.invoke_gateway(
            gatewayIdentifier=gateway_id,
            method="tools/call",
            payload=json.dumps(
                {"name": tool_name, "arguments": arguments}
            ).encode(),
        )
        return json.loads(response["payload"].read())


# Usage
registry = TenantGatewayRegistry()
registry.register("acme-corp", GATEWAY_ID, GATEWAY_ARN)
# registry.register("globex-inc", another_gateway_id, another_gateway_arn)
```

### Step 3: Create Shared Memory Stores

Enterprise agents rarely operate in isolation. A support agent escalates to a specialist agent. A sales agent hands off to a finance agent. A supervisor coordinates multiple worker agents. All of these patterns require shared context.

AgentCore Memory provides two levels of sharing: session-level short-term memory for within-conversation context, and long-term memory with configurable strategies for cross-session knowledge. By creating shared memory stores at the platform level, you enable these patterns across teams.

#### Platform Memory Architecture

```
  ┌──────────────────────────────────────────────────────┐
  │                   Memory Layer                       │
  │                                                      │
  │  ┌────────────────┐  ┌────────────────────────────┐  │
  │  │  Per-Agent      │  │  Shared Across Teams       │  │
  │  │  Memory Stores  │  │  Memory Stores             │  │
  │  │                 │  │                            │  │
  │  │ ┌────────────┐  │  │ ┌────────────────────────┐ │  │
  │  │ │ Support    │  │  │ │ Customer Knowledge     │ │  │
  │  │ │ Agent Mem  │  │  │ │ (all teams read/write) │ │  │
  │  │ └────────────┘  │  │ └────────────────────────┘ │  │
  │  │ ┌────────────┐  │  │ ┌────────────────────────┐ │  │
  │  │ │ Sales      │  │  │ │ Agent Handoff Context  │ │  │
  │  │ │ Agent Mem  │  │  │ │ (cross-agent sessions) │ │  │
  │  │ └────────────┘  │  │ └────────────────────────┘ │  │
  │  │ ┌────────────┐  │  │ ┌────────────────────────┐ │  │
  │  │ │ Finance    │  │  │ │ Incident Knowledge     │ │  │
  │  │ │ Agent Mem  │  │  │ │ (SRE team shared)      │ │  │
  │  │ └────────────┘  │  │ └────────────────────────┘ │  │
  │  └────────────────┘  └────────────────────────────┘  │
  └──────────────────────────────────────────────────────┘
```

#### Create Shared Memory Stores

```python
def create_platform_memory(
    name: str, description: str, strategies: list, ttl_seconds: int = 2592000
) -> dict:
    """Create a memory store for the platform layer.

    Args:
        name: Memory store name
        description: Human-readable description
        strategies: List of memory strategy configurations
        ttl_seconds: Short-term event TTL (default 30 days)
    """
    response = control.create_memory(
        name=name,
        description=description,
        eventExpiryDuration=ttl_seconds,
        memoryStrategies=strategies,
    )

    memory_id = response["memory"]["id"]
    print(f"Memory created: {name} -> {memory_id}")

    # Wait for ACTIVE
    for attempt in range(30):
        status_response = control.get_memory(memoryId=memory_id)
        if status_response.get("status") in ("ACTIVE", "READY"):
            print(f"Memory is ACTIVE: {name}")
            return {"memoryId": memory_id, "name": name}
        time.sleep(5)

    return {"memoryId": memory_id, "name": name}


# --- Shared Customer Knowledge Store ---
# All teams can read/write customer insights.
# Long-term strategies extract preferences and facts automatically.
customer_memory = create_platform_memory(
    name="EnterpriseCustomerKnowledge",
    description="Shared customer preferences and facts across all agent teams",
    strategies=[
        {
            "userPreferenceMemoryStrategy": {
                "name": "CustomerPreferences",
                "namespaces": ["preferences"],
            }
        },
        {
            "semanticMemoryStrategy": {
                "name": "CustomerFacts",
                "namespaces": ["facts"],
            }
        },
        {
            "sessionSummaryMemoryStrategy": {
                "name": "InteractionSummaries",
                "namespaces": ["summaries"],
                "maxRecentSessions": 20,
            }
        },
    ],
)

CUSTOMER_MEMORY_ID = customer_memory["memoryId"]

# --- Agent Handoff Context Store ---
# Used when one agent transfers a conversation to another.
handoff_memory = create_platform_memory(
    name="AgentHandoffContext",
    description="Shared context for agent-to-agent handoffs",
    strategies=[
        {
            "sessionSummaryMemoryStrategy": {
                "name": "HandoffSummaries",
                "namespaces": ["handoffs"],
                "maxRecentSessions": 50,
            }
        },
    ],
    ttl_seconds=86400,  # 24-hour TTL for handoff context
)

HANDOFF_MEMORY_ID = handoff_memory["memoryId"]

# --- Incident Knowledge Store ---
# SRE agents share incident patterns, runbooks, and resolution history.
incident_memory = create_platform_memory(
    name="IncidentKnowledge",
    description="Shared incident patterns and resolution history for SRE agents",
    strategies=[
        {
            "semanticMemoryStrategy": {
                "name": "IncidentPatterns",
                "namespaces": ["patterns", "runbooks"],
            }
        },
        {
            "episodicMemoryStrategy": {
                "name": "ResolutionHistory",
                "namespaces": ["resolutions"],
            }
        },
    ],
)

INCIDENT_MEMORY_ID = incident_memory["memoryId"]
```

#### Implement Shared Memory Operations

```python
class PlatformMemoryManager:
    """Manages shared memory operations across the enterprise platform."""

    def __init__(self, data_client):
        self.data = data_client
        self.stores = {}

    def register_store(self, name: str, memory_id: str):
        """Register a named memory store."""
        self.stores[name] = memory_id

    def store_interaction(
        self,
        store_name: str,
        actor_id: str,
        session_id: str,
        messages: list,
    ):
        """Store conversation events to a shared memory store."""
        memory_id = self.stores[store_name]
        self.data.create_event(
            memoryId=memory_id,
            actorId=actor_id,
            sessionId=session_id,
            eventTimestamp=datetime.now(timezone.utc),
            payload=[
                {"conversational": {"role": msg["role"], "content": {"text": msg["content"]}}}
                for msg in messages
            ],
        )

    def retrieve_context(
        self,
        store_name: str,
        actor_id: str,
        query: str,
        namespace: str = None,
        max_results: int = 10,
    ) -> list:
        """Semantic search across shared memory for relevant context."""
        memory_id = self.stores[store_name]
        kwargs = {
            "memoryId": memory_id,
            "namespace": namespace or "facts",
            "searchCriteria": {"searchQuery": query, "topK": max_results},
        }
        response = self.data.retrieve_memory_records(**kwargs)
        records = response.get("memoryRecords", [])
        return [
            {"content": r["content"]["text"], "score": r.get("score", 0)}
            for r in records
        ]

    def get_session_history(
        self, store_name: str, actor_id: str, session_id: str
    ) -> list:
        """Get short-term conversation history for a session."""
        memory_id = self.stores[store_name]
        response = self.data.get_events(
            memoryId=memory_id,
            actorId=actor_id,
            sessionId=session_id,
        )
        return response.get("events", [])

    def handoff_context(
        self,
        from_agent: str,
        to_agent: str,
        customer_id: str,
        session_id: str,
        summary: str,
        context: dict,
    ):
        """Store handoff context when transferring between agents."""
        memory_id = self.stores["handoffs"]
        self.data.create_event(
            memoryId=memory_id,
            actorId=customer_id,
            sessionId=session_id,
            eventTimestamp=datetime.now(timezone.utc),
            payload=[
                {
                    "conversational": {
                        "role": "SYSTEM",
                        "content": {
                            "text": json.dumps(
                                {
                                    "type": "agent_handoff",
                                    "from_agent": from_agent,
                                    "to_agent": to_agent,
                                    "summary": summary,
                                    "context": context,
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                }
                            )
                        },
                    }
                }
            ],
        )
        print(f"Handoff: {from_agent} -> {to_agent} for customer {customer_id}")


# Initialize the platform memory manager
memory_manager = PlatformMemoryManager(data)
memory_manager.register_store("customers", CUSTOMER_MEMORY_ID)
memory_manager.register_store("handoffs", HANDOFF_MEMORY_ID)
memory_manager.register_store("incidents", INCIDENT_MEMORY_ID)
```

#### Example: Cross-Agent Memory Sharing

```python
# Support agent stores customer interaction
memory_manager.store_interaction(
    store_name="customers",
    actor_id="customer-12345",
    session_id="support-session-001",
    messages=[
        {"role": "user", "content": "I want to upgrade my plan to Enterprise"},
        {
            "role": "assistant",
            "content": "I can help with that. Let me transfer you to our sales team.",
        },
    ],
)

# Support agent hands off to sales agent
memory_manager.handoff_context(
    from_agent="support-agent",
    to_agent="sales-agent",
    customer_id="customer-12345",
    session_id="support-session-001",
    summary="Customer wants to upgrade from Professional to Enterprise plan. "
    "Currently on annual billing. Has been a customer for 2 years.",
    context={
        "current_plan": "Professional",
        "desired_plan": "Enterprise",
        "billing_cycle": "annual",
        "tenure_years": 2,
    },
)

# Sales agent retrieves handoff context and customer knowledge
handoff = memory_manager.get_session_history(
    store_name="handoffs",
    actor_id="customer-12345",
    session_id="support-session-001",
)

customer_context = memory_manager.retrieve_context(
    store_name="customers",
    actor_id="customer-12345",
    query="plan preferences and upgrade history",
    namespace="preferences",
)

print("Handoff events:", len(handoff))
print("Customer context:", customer_context)
```

### Step 4: Cedar Policy Governance for Multi-Tenant Isolation

Cedar policies provide the deterministic enforcement layer. Every tool call flows through the Gateway's policy engine before execution. This is where you enforce tenant isolation, role-based access, and hard limits that no amount of prompt engineering can override.

#### Policy Architecture

```
  Agent Request
       │
       ▼
  ┌──────────┐     ┌─────────────────────────────┐
  │ Gateway  │────▶│ Policy Engine (Cedar)        │
  │          │     │                              │
  │          │     │  1. Tenant isolation rules   │
  │          │     │  2. Role-based access        │
  │          │     │  3. Parameter constraints    │
  │          │     │  4. Hard limits (forbid)     │
  │          │     │                              │
  │          │◀────│  Decision: ALLOW or DENY     │
  │          │     └─────────────────────────────-┘
  │          │
  │  ALLOW?  │──Yes──▶ Execute tool call
  │          │──No───▶ Return 403 Access Denied
  └──────────┘
```

#### Create Policy Engine and Attach to Gateway

```python
def create_platform_policy_engine(name: str, description: str) -> dict:
    """Create a policy engine for enterprise governance."""
    response = control.create_policy_engine(
        name=name,
        description=description,
    )

    engine_id = response["policyEngineId"]
    engine_arn = response["policyEngineArn"]
    print(f"Policy engine created: {engine_id}")

    # Wait for ACTIVE
    for attempt in range(30):
        status_response = control.get_policy_engine(policyEngineId=engine_id)
        if status_response["status"] == "ACTIVE":
            print("Policy engine is ACTIVE")
            return {"policyEngineId": engine_id, "policyEngineArn": engine_arn}
        time.sleep(5)

    return {"policyEngineId": engine_id, "policyEngineArn": engine_arn}


engine = create_platform_policy_engine(
    name="EnterprisePolicyEngine",
    description="Cedar policy engine for multi-tenant enterprise governance",
)

POLICY_ENGINE_ID = engine["policyEngineId"]
POLICY_ENGINE_ARN = engine["policyEngineArn"]

# Attach policy engine to the enterprise gateway
control.update_gateway(
    gatewayIdentifier=GATEWAY_ID,
    policyEngineConfiguration={
        "policyEngineArn": POLICY_ENGINE_ARN,
        "enforcementMode": "ENFORCE",
    },
)
print(f"Policy engine attached to gateway {GATEWAY_ID} in ENFORCE mode")
```

#### Define Cedar Policies for Tenant Isolation

The following policies implement multi-tenant isolation. Users can only access tools that their tenant is authorized for, and additional role-based restrictions apply within each tenant.

```python
def create_cedar_policy(engine_id: str, name: str, statement: str, description: str) -> dict:
    """Create a Cedar policy in the enterprise policy engine."""
    try:
        response = control.create_policy(
            policyEngineId=engine_id,
            name=name,
            description=description,
            validationMode="FAIL_ON_ANY_FINDINGS",
            definition={"cedar": {"statement": statement}},
        )
        print(f"Policy created: {name} -> {response['policyId']}")
        return response
    except control.exceptions.ValidationException as e:
        print(f"Validation error for {name}: {e}")
        raise


# --- Policy 1: Tenant A (Support team) can access CRM and ticketing tools ---
create_cedar_policy(
    engine_id=POLICY_ENGINE_ID,
    name="tenant_a_crm_access",
    description="Support team (Tenant A) can use CRM lookup and case creation tools",
    statement=f'''
permit(
    principal is AgentCore::OAuthUser,
    action in [
        AgentCore::Action::"CRMTools___lookup_customer",
        AgentCore::Action::"CRMTools___create_case",
        AgentCore::Action::"TicketingTools___create_ticket",
        AgentCore::Action::"TicketingTools___get_ticket",
        AgentCore::Action::"TicketingTools___update_ticket"
    ],
    resource == AgentCore::Gateway::"{GATEWAY_ARN}"
)
when {{
    principal.hasTag("tenant") &&
    principal.getTag("tenant") == "support-team"
}};
''',
)

# --- Policy 2: Tenant B (Sales team) can access CRM and opportunity tools ---
create_cedar_policy(
    engine_id=POLICY_ENGINE_ID,
    name="tenant_b_sales_access",
    description="Sales team (Tenant B) can use CRM and opportunity tools",
    statement=f'''
permit(
    principal is AgentCore::OAuthUser,
    action in [
        AgentCore::Action::"CRMTools___lookup_customer",
        AgentCore::Action::"CRMTools___get_opportunities",
        AgentCore::Action::"CommsTools___send_message",
        AgentCore::Action::"CommsTools___search_messages"
    ],
    resource == AgentCore::Gateway::"{GATEWAY_ARN}"
)
when {{
    principal.hasTag("tenant") &&
    principal.getTag("tenant") == "sales-team"
}};
''',
)

# --- Policy 3: Managers can access all tools within their tenant ---
create_cedar_policy(
    engine_id=POLICY_ENGINE_ID,
    name="manager_full_access",
    description="Managers have full tool access within their tenant scope",
    statement=f'''
permit(
    principal is AgentCore::OAuthUser,
    action,
    resource == AgentCore::Gateway::"{GATEWAY_ARN}"
)
when {{
    principal.hasTag("role") &&
    principal.getTag("role") == "manager"
}};
''',
)

# --- Policy 4: Hard limit -- nobody can delete customer records ---
create_cedar_policy(
    engine_id=POLICY_ENGINE_ID,
    name="forbid_customer_deletion",
    description="No user, regardless of role, can delete customer records",
    statement=f'''
forbid(
    principal,
    action == AgentCore::Action::"CRMTools___delete_customer",
    resource == AgentCore::Gateway::"{GATEWAY_ARN}"
);
''',
)

# --- Policy 5: High-value case creation requires senior role ---
create_cedar_policy(
    engine_id=POLICY_ENGINE_ID,
    name="high_priority_case_restriction",
    description="Only senior support or managers can create Critical priority cases",
    statement=f'''
forbid(
    principal is AgentCore::OAuthUser,
    action == AgentCore::Action::"CRMTools___create_case",
    resource == AgentCore::Gateway::"{GATEWAY_ARN}"
)
when {{
    context.input.priority == "Critical"
}}
unless {{
    principal.hasTag("role") &&
    (principal.getTag("role") == "senior-support" ||
     principal.getTag("role") == "manager")
}};
''',
)

# --- Policy 6: Read-only access for audit/compliance role ---
create_cedar_policy(
    engine_id=POLICY_ENGINE_ID,
    name="audit_readonly_access",
    description="Audit role can only read data, not create or modify",
    statement=f'''
permit(
    principal is AgentCore::OAuthUser,
    action in [
        AgentCore::Action::"CRMTools___lookup_customer",
        AgentCore::Action::"CRMTools___get_opportunities",
        AgentCore::Action::"TicketingTools___get_ticket",
        AgentCore::Action::"CommsTools___search_messages"
    ],
    resource == AgentCore::Gateway::"{GATEWAY_ARN}"
)
when {{
    principal.hasTag("role") &&
    principal.getTag("role") == "auditor"
}};
''',
)

print(f"\n6 Cedar policies created in engine {POLICY_ENGINE_ID}")
```

#### Generate Policies from Natural Language

For business stakeholders who cannot write Cedar directly, AgentCore supports natural language policy authoring.

```python
def generate_policy_from_natural_language(
    engine_id: str,
    gateway_arn: str,
    name: str,
    description: str,
) -> dict:
    """Generate a Cedar policy from a natural language description."""
    response = control.start_policy_generation(
        policyEngineId=engine_id,
        name=name,
        content={"text": description},
        resource={"gateway": {"gatewayArn": gateway_arn}},
    )

    generation_id = response["policyGenerationId"]
    print(f"Policy generation started: {generation_id}")

    # Poll for completion
    for attempt in range(30):
        result = control.get_policy_generation(
            policyEngineId=engine_id,
            policyGenerationId=generation_id,
        )
        status = result["status"]

        if status == "GENERATED":
            policies = result.get("generatedPolicies", [])
            print(f"Generated {len(policies)} policy option(s):")
            for i, policy in enumerate(policies):
                print(f"\n  Option {i + 1}:")
                print(f"  {policy['statement']}")
            return policies

        if status == "GENERATE_FAILED":
            print(f"Generation failed: {result.get('statusReasons')}")
            return None

        time.sleep(3)

    return None


# Example: business stakeholder describes a policy requirement
generated = generate_policy_from_natural_language(
    engine_id=POLICY_ENGINE_ID,
    gateway_arn=GATEWAY_ARN,
    name="InternRestrictions",
    description=(
        "Users tagged as interns should only be able to look up customer "
        "information and view ticket status. They should not be able to "
        "create, update, or delete anything."
    ),
)

# Review and create the best generated option
if generated:
    control.create_policy(
        policyEngineId=POLICY_ENGINE_ID,
        name="intern_readonly_policy",
        description="Intern role: read-only access to CRM and tickets",
        definition={"cedar": {"statement": generated[0]["statement"]}},
    )
    print("Generated policy created successfully")
```

### Step 5: Federated Identity with Okta and Entra ID

Enterprise authentication flows through corporate identity providers. AgentCore Identity integrates natively with Okta, Microsoft Entra ID, Amazon Cognito, and Auth0 for both inbound authorization (verifying who calls the agent) and outbound credential vending (letting the agent access services on behalf of the user).

#### Identity Architecture

```
  User (Browser / API Client)
       │
       │  JWT Token from Corporate IdP
       ▼
  ┌──────────────────────────────────────┐
  │  AgentCore Identity                  │
  │                                      │
  │  Inbound:                            │
  │  ┌──────┐ ┌────────┐ ┌──────────┐   │
  │  │ Okta │ │Entra ID│ │ Cognito  │   │
  │  └──┬───┘ └───┬────┘ └────┬─────┘   │
  │     │         │           │          │
  │     ▼         ▼           ▼          │
  │  ┌─────────────────────────────┐     │
  │  │  JWT Validation             │     │
  │  │  (OIDC Discovery URL)       │     │
  │  └─────────────────────────────┘     │
  │                                      │
  │  Outbound:                           │
  │  ┌──────────────────────────────┐    │
  │  │  Credential Providers        │    │
  │  │  ┌────────────┐ ┌─────────┐  │    │
  │  │  │ Salesforce │ │ Slack   │  │    │
  │  │  │ OAuth      │ │ OAuth   │  │    │
  │  │  └────────────┘ └─────────┘  │    │
  │  │  ┌────────────┐ ┌─────────┐  │    │
  │  │  │ GitHub     │ │ Custom  │  │    │
  │  │  │ API Key    │ │ OAuth   │  │    │
  │  │  └────────────┘ └─────────┘  │    │
  │  └──────────────────────────────┘    │
  └──────────────────────────────────────┘
```

#### Configure Inbound Authorization with Okta

When your enterprise uses Okta as the identity provider, configure the Gateway to validate Okta-issued JWTs.

```python
def configure_okta_inbound(
    okta_org_url: str,
    client_id: str,
    audience: str,
) -> dict:
    """Build Okta JWT authorizer configuration for Gateway inbound auth.

    Args:
        okta_org_url: Your Okta org URL (e.g., https://your-org.okta.com)
        client_id: Okta application client ID
        audience: Expected audience claim in the JWT
    """
    config = {
        "customJwtAuthorizerConfig": {
            "discoveryUrl": f"{okta_org_url}/.well-known/openid-configuration",
            "allowedAudiences": [audience],
            "allowedClients": [client_id],
        }
    }
    print(f"Okta inbound config ready: {okta_org_url}")
    return config


def configure_entra_id_inbound(
    tenant_id: str,
    client_id: str,
    audience: str,
) -> dict:
    """Build Microsoft Entra ID JWT authorizer configuration for Gateway inbound auth.

    Args:
        tenant_id: Azure AD / Entra ID tenant ID
        client_id: Application registration client ID
        audience: Expected audience claim (usually api://your-app-id)
    """
    config = {
        "customJwtAuthorizerConfig": {
            "discoveryUrl": (
                f"https://login.microsoftonline.com/{tenant_id}"
                "/v2.0/.well-known/openid-configuration"
            ),
            "allowedAudiences": [audience],
            "allowedClients": [client_id],
        }
    }
    print(f"Entra ID inbound config ready: tenant {tenant_id}")
    return config


# Example: Okta configuration
okta_config = configure_okta_inbound(
    okta_org_url="https://your-org.okta.com",
    client_id="0oa_your_okta_client_id",
    audience="api://enterprise-agents",
)

# Example: Microsoft Entra ID configuration
entra_config = configure_entra_id_inbound(
    tenant_id="your-azure-tenant-id",
    client_id="your-entra-app-client-id",
    audience="api://enterprise-agents",
)
```

#### Create Outbound Credential Providers

Agents need credentials to access downstream services on behalf of users. AgentCore Identity stores and manages these credentials securely.

```python
def create_oauth2_credential_provider(
    name: str,
    vendor: str,
    client_id: str,
    client_secret: str,
    custom_config: dict = None,
) -> dict:
    """Create an OAuth2 credential provider for outbound service access."""
    kwargs = {
        "name": name,
        "credentialProviderVendor": vendor,
    }

    if vendor == "CustomOauth2" and custom_config:
        kwargs["oauth2ProviderConfigInput"] = {
            "customOauth2ProviderConfig": {
                "clientId": client_id,
                "clientSecret": client_secret,
                "authorizeEndpoint": custom_config["authorize_url"],
                "tokenEndpoint": custom_config["token_url"],
                "issuer": custom_config["issuer"],
                "scopes": custom_config.get("scopes", []),
            }
        }
    else:
        kwargs["oauth2ProviderConfigInput"] = {
            "includedOauth2ProviderConfig": {
                "clientId": client_id,
                "clientSecret": client_secret,
            }
        }

    response = control.create_credential_provider(**kwargs)
    provider_arn = response["credentialProviderArn"]
    print(f"Credential provider created: {name} -> {provider_arn}")
    return {"name": name, "arn": provider_arn}


def create_api_key_provider(name: str, api_key: str) -> dict:
    """Create an API key credential provider."""
    response = control.create_credential_provider(
        name=name,
        credentialProviderVendor="ApiKey",
        apiKeyProviderConfigInput={"apiKey": api_key},
    )
    provider_arn = response["credentialProviderArn"]
    print(f"API key provider created: {name} -> {provider_arn}")
    return {"name": name, "arn": provider_arn}


# --- Salesforce OAuth provider ---
sf_provider = create_oauth2_credential_provider(
    name="EnterpriseSalesforceOAuth",
    vendor="SalesforceOauth2",
    client_id="your-salesforce-connected-app-client-id",
    client_secret="your-salesforce-connected-app-secret",
)

# --- Slack OAuth provider ---
slack_provider = create_oauth2_credential_provider(
    name="EnterpriseSlackOAuth",
    vendor="SlackOauth2",
    client_id="your-slack-app-client-id",
    client_secret="your-slack-app-client-secret",
)

# --- Jira API key provider ---
jira_provider = create_api_key_provider(
    name="EnterpriseJiraAPIKey",
    api_key="your-jira-api-token",
)

# --- Custom internal API OAuth provider ---
internal_provider = create_oauth2_credential_provider(
    name="InternalAPIOAuth",
    vendor="CustomOauth2",
    client_id="internal-api-client-id",
    client_secret="internal-api-client-secret",
    custom_config={
        "authorize_url": "https://auth.internal.example.com/oauth/authorize",
        "token_url": "https://auth.internal.example.com/oauth/token",
        "issuer": "https://auth.internal.example.com",
        "scopes": ["read", "write"],
    },
)
```

#### Implement User-Delegated Tool Access

When an agent calls a tool on behalf of a user, Identity provides the user's credentials to the downstream service. The agent never sees or stores the user's tokens directly.

```python
class PlatformIdentityManager:
    """Manages identity and credential flows for the enterprise platform."""

    def __init__(self, data_client, control_client):
        self.data = data_client
        self.control = control_client
        self.providers = {}

    def register_provider(self, service_name: str, provider_arn: str):
        """Register a credential provider for a downstream service."""
        self.providers[service_name] = provider_arn

    def get_user_token(
        self, service_name: str, user_jwt: str, scopes: list = None
    ) -> dict:
        """Get a service-specific token for a user via OAuth2 delegation.

        The user's JWT from the corporate IdP is exchanged for a
        service-specific token without the agent ever seeing raw credentials.
        """
        provider_arn = self.providers.get(service_name)
        if not provider_arn:
            raise ValueError(f"No provider registered for: {service_name}")

        kwargs = {
            "credentialProviderArn": provider_arn,
            "workloadIdentityToken": user_jwt,
        }
        if scopes:
            kwargs["scopes"] = scopes

        response = self.data.get_resource_oauth2_access_token(**kwargs)
        return {
            "accessToken": response["accessToken"],
            "tokenType": response.get("tokenType", "Bearer"),
            "expiresIn": response.get("expiresIn"),
        }

    def get_api_key(self, service_name: str) -> str:
        """Get an API key for a service (not user-delegated)."""
        provider_arn = self.providers.get(service_name)
        if not provider_arn:
            raise ValueError(f"No provider registered for: {service_name}")

        response = self.data.get_api_key_credential(
            credentialProviderArn=provider_arn,
        )
        return response["apiKey"]

    def call_tool_as_user(
        self,
        gateway_id: str,
        tool_name: str,
        arguments: dict,
        user_jwt: str,
        service_name: str,
    ) -> dict:
        """Call a Gateway tool with user-delegated credentials.

        This is the recommended pattern for enterprise agents:
        the user's identity flows through to the downstream service.
        """
        # Get service token for this user
        token = self.get_user_token(service_name, user_jwt)

        # Call tool through gateway with bearer token
        response = self.data.invoke_gateway(
            gatewayIdentifier=gateway_id,
            method="tools/call",
            payload=json.dumps(
                {"name": tool_name, "arguments": arguments}
            ).encode(),
            # The bearer token is passed to the downstream service
        )
        return json.loads(response["payload"].read())


# Initialize the identity manager
identity_manager = PlatformIdentityManager(data, control)
identity_manager.register_provider("salesforce", sf_provider["arn"])
identity_manager.register_provider("slack", slack_provider["arn"])
identity_manager.register_provider("jira", jira_provider["arn"])
identity_manager.register_provider("internal", internal_provider["arn"])
```

### Step 6: Build a Platform-Aware Agent

With the platform layer in place, individual agent teams build their agents using shared infrastructure. Here is a support agent that uses all four platform services.

```python
from strands import Agent, tool
from strands.models import BedrockModel

# --- Tools that use the platform layer ---

@tool
def remember_customer(customer_id: str, query: str) -> str:
    """Search shared customer knowledge for relevant context.

    Args:
        customer_id: Customer identifier
        query: What to search for in customer history
    """
    results = memory_manager.retrieve_context(
        store_name="customers",
        actor_id=customer_id,
        query=query,
        namespace="preferences",
    )
    if results:
        return "Known about this customer:\n" + "\n".join(
            f"- {r['content']}" for r in results
        )
    return "No prior context found for this customer."


@tool
def check_handoff_context(customer_id: str, session_id: str) -> str:
    """Check if another agent handed off this conversation with context.

    Args:
        customer_id: Customer identifier
        session_id: Current session ID
    """
    events = memory_manager.get_session_history(
        store_name="handoffs",
        actor_id=customer_id,
        session_id=session_id,
    )
    if events:
        return f"Handoff context found: {json.dumps(events[-1], default=str)}"
    return "No handoff context. This is a new conversation."


@tool
def call_enterprise_tool(tool_name: str, arguments: dict) -> str:
    """Call any enterprise tool through the centralized gateway.

    Available tools: lookup_customer, get_opportunities, create_case,
    create_ticket, get_ticket, update_ticket, send_message, search_messages.

    Args:
        tool_name: Name of the enterprise tool to call
        arguments: Tool arguments as a dictionary
    """
    response = data.invoke_gateway(
        gatewayIdentifier=GATEWAY_ID,
        method="tools/call",
        payload=json.dumps({"name": tool_name, "arguments": arguments}).encode(),
    )
    result = json.loads(response["payload"].read())
    return json.dumps(result, default=str)


@tool
def store_customer_interaction(customer_id: str, session_id: str, summary: str) -> str:
    """Store a summary of this interaction in shared customer knowledge.

    Args:
        customer_id: Customer identifier
        session_id: Current session ID
        summary: Summary of the interaction for future reference
    """
    memory_manager.store_interaction(
        store_name="customers",
        actor_id=customer_id,
        session_id=session_id,
        messages=[{"role": "assistant", "content": summary}],
    )
    return f"Interaction stored for customer {customer_id}"


@tool
def escalate_to_agent(
    target_agent: str, customer_id: str, session_id: str, reason: str, context: dict
) -> str:
    """Escalate or hand off this conversation to another agent team.

    Args:
        target_agent: Target agent name (e.g., "sales-agent", "finance-agent")
        customer_id: Customer identifier
        session_id: Current session ID
        reason: Reason for the handoff
        context: Relevant context to pass along
    """
    memory_manager.handoff_context(
        from_agent="support-agent",
        to_agent=target_agent,
        customer_id=customer_id,
        session_id=session_id,
        summary=reason,
        context=context,
    )
    return f"Escalated to {target_agent}. Handoff context stored."


# --- Create the platform-aware agent ---
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
    region_name=REGION,
)

support_agent = Agent(
    model=model,
    tools=[
        remember_customer,
        check_handoff_context,
        call_enterprise_tool,
        store_customer_interaction,
        escalate_to_agent,
    ],
    system_prompt="""You are an enterprise customer support agent running on the
AgentCore platform. You have access to shared enterprise tools and customer
knowledge.

Operating procedures:
1. ALWAYS check for handoff context first -- another agent may have started this
   conversation.
2. Search shared customer knowledge to personalize the interaction.
3. Use enterprise tools (CRM, ticketing, messaging) through the centralized gateway.
4. Store a brief summary of every interaction for future reference.
5. If the customer needs sales, finance, or SRE assistance, escalate with full
   context using the handoff tool.
6. You cannot create Critical priority cases unless you have senior-support or
   manager role. Inform the customer and escalate if needed.
7. Never attempt to delete customer records.""",
)
```

### Step 7: Deploy to Runtime

Package the platform-aware agent for deployment on AgentCore Runtime.

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()


@app.entrypoint()
async def handle_request(request):
    """Handle incoming support requests with full platform integration."""
    customer_id = request.get("customer_id", "unknown")
    session_id = request.get("session_id", "default")
    prompt = request.get("prompt", "")

    # Enrich the prompt with platform context
    context_prompt = (
        f"[Customer: {customer_id} | Session: {session_id}]\n{prompt}"
    )

    response = support_agent(context_prompt)

    return {
        "response": str(response),
        "customer_id": customer_id,
        "session_id": session_id,
    }


if __name__ == "__main__":
    app.run()
```

Deploy and invoke:

```bash
# Deploy the agent
agentcore deploy --name enterprise-support-agent --memory 2048 --timeout 3600

# Invoke with a customer request
agentcore invoke '{
    "customer_id": "CUST-12345",
    "session_id": "sess-001",
    "prompt": "I was talking to someone about upgrading my plan. Can you help?"
}'
```

## Advanced Usage

### Platform Orchestrator Pattern

For large enterprises, a platform orchestrator routes requests to the appropriate specialized agent based on the request type. Each specialized agent runs on the same platform layer.

```python
class PlatformOrchestrator:
    """Routes requests to specialized agents using shared platform infrastructure."""

    def __init__(self, gateway_id: str, memory_manager: PlatformMemoryManager):
        self.gateway_id = gateway_id
        self.memory = memory_manager
        self.agents = {}

    def register_agent(self, name: str, agent_runtime_arn: str, capabilities: list):
        """Register a specialized agent with the orchestrator."""
        self.agents[name] = {
            "arn": agent_runtime_arn,
            "capabilities": capabilities,
        }

    def route_request(self, request: dict) -> str:
        """Route a request to the best-matching agent."""
        prompt = request.get("prompt", "")
        customer_id = request.get("customer_id")

        # Check for existing handoff context
        if request.get("session_id"):
            handoffs = self.memory.get_session_history(
                store_name="handoffs",
                actor_id=customer_id,
                session_id=request["session_id"],
            )
            if handoffs:
                # Route to the target agent from the handoff
                last_handoff = handoffs[-1]
                target = json.loads(
                    last_handoff.get("payload", [{}])[0]
                    .get("conversational", {})
                    .get("content", {})
                    .get("text", "{}")
                ).get("to_agent", "support-agent")
                return target

        # Keyword-based routing (replace with LLM classification for production)
        prompt_lower = prompt.lower()
        if any(w in prompt_lower for w in ["buy", "upgrade", "pricing", "plan", "quote"]):
            return "sales-agent"
        if any(w in prompt_lower for w in ["invoice", "billing", "refund", "payment"]):
            return "finance-agent"
        if any(w in prompt_lower for w in ["outage", "incident", "down", "error", "alert"]):
            return "sre-agent"

        return "support-agent"

    def invoke_agent(self, agent_name: str, request: dict) -> dict:
        """Invoke a specialized agent through Runtime."""
        agent_config = self.agents.get(agent_name)
        if not agent_config:
            raise ValueError(f"Unknown agent: {agent_name}")

        response = data.invoke_agent_runtime(
            agentRuntimeId=agent_config["arn"],
            payload=json.dumps(request).encode(),
        )
        return json.loads(response["payload"].read())


# Set up the orchestrator
orchestrator = PlatformOrchestrator(GATEWAY_ID, memory_manager)
orchestrator.register_agent(
    "support-agent",
    "arn:aws:bedrock-agentcore:us-east-1:123456789012:agent-runtime/support-v2",
    capabilities=["customer-lookup", "ticketing", "case-management"],
)
orchestrator.register_agent(
    "sales-agent",
    "arn:aws:bedrock-agentcore:us-east-1:123456789012:agent-runtime/sales-v1",
    capabilities=["opportunity-management", "quoting", "proposals"],
)
orchestrator.register_agent(
    "sre-agent",
    "arn:aws:bedrock-agentcore:us-east-1:123456789012:agent-runtime/sre-v1",
    capabilities=["incident-response", "runbooks", "monitoring"],
)
```

### Observability for the Platform

Monitor the entire platform through a unified observability layer.

```python
import boto3

cloudwatch = boto3.client("cloudwatch", region_name=REGION)
logs = boto3.client("logs", region_name=REGION)


def create_platform_dashboard():
    """Create a CloudWatch dashboard for the enterprise agent platform."""
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "properties": {
                    "title": "Gateway Tool Invocations",
                    "metrics": [
                        [
                            "AWS/BedrockAgentCore",
                            "GatewayInvocations",
                            "GatewayId",
                            GATEWAY_ID,
                        ]
                    ],
                    "period": 300,
                    "stat": "Sum",
                },
            },
            {
                "type": "metric",
                "properties": {
                    "title": "Policy Decisions (Allow/Deny)",
                    "metrics": [
                        [
                            "AWS/BedrockAgentCore",
                            "PolicyAllowCount",
                            "GatewayId",
                            GATEWAY_ID,
                        ],
                        [
                            "AWS/BedrockAgentCore",
                            "PolicyDenyCount",
                            "GatewayId",
                            GATEWAY_ID,
                        ],
                    ],
                    "period": 300,
                    "stat": "Sum",
                },
            },
            {
                "type": "metric",
                "properties": {
                    "title": "Memory Operations",
                    "metrics": [
                        ["AWS/BedrockAgentCore", "MemoryCreateEvents"],
                        ["AWS/BedrockAgentCore", "MemoryRetrievals"],
                    ],
                    "period": 300,
                    "stat": "Sum",
                },
            },
            {
                "type": "metric",
                "properties": {
                    "title": "Agent Session Duration (p50/p99)",
                    "metrics": [
                        [
                            "AWS/BedrockAgentCore",
                            "SessionDuration",
                            {"stat": "p50"},
                        ],
                        [
                            "AWS/BedrockAgentCore",
                            "SessionDuration",
                            {"stat": "p99"},
                        ],
                    ],
                    "period": 300,
                },
            },
        ],
    }

    cloudwatch.put_dashboard(
        DashboardName="EnterpriseAgentPlatform",
        DashboardBody=json.dumps(dashboard_body),
    )
    print("Platform dashboard created: EnterpriseAgentPlatform")


def create_policy_denial_alarm():
    """Alert when policy denials spike -- may indicate misconfiguration or attack."""
    cloudwatch.put_metric_alarm(
        AlarmName="EnterprisePlatform-PolicyDenialSpike",
        MetricName="PolicyDenyCount",
        Namespace="AWS/BedrockAgentCore",
        Statistic="Sum",
        Period=300,
        EvaluationPeriods=1,
        Threshold=50,
        ComparisonOperator="GreaterThanThreshold",
        Dimensions=[{"Name": "GatewayId", "Value": GATEWAY_ID}],
        AlarmActions=[
            f"arn:aws:sns:{REGION}:{ACCOUNT_ID}:platform-alerts"
        ],
        AlarmDescription=(
            "Policy denials exceeded 50 in 5 minutes. "
            "Investigate for misconfiguration or unauthorized access attempts."
        ),
    )
    print("Policy denial alarm created")


create_platform_dashboard()
create_policy_denial_alarm()
```

### Testing Policies Before Enforcement

Always test Cedar policies in LOG_ONLY mode before switching to ENFORCE in production.

```python
def test_policy_rollout(gateway_id: str, engine_arn: str, test_cases: list):
    """Test policies in LOG_ONLY mode, then promote to ENFORCE if all pass."""

    # Step 1: Switch to LOG_ONLY
    print("Switching to LOG_ONLY mode...")
    control.update_gateway(
        gatewayIdentifier=gateway_id,
        policyEngineConfiguration={
            "policyEngineArn": engine_arn,
            "enforcementMode": "LOG_ONLY",
        },
    )
    time.sleep(10)  # Wait for propagation

    # Step 2: Run test cases
    results = []
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        try:
            response = data.invoke_gateway(
                gatewayIdentifier=gateway_id,
                method="tools/call",
                payload=json.dumps(
                    {"name": test["tool"], "arguments": test["arguments"]}
                ).encode(),
            )
            result = json.loads(response["payload"].read())
            actual = "ALLOW"
        except Exception as e:
            actual = "DENY" if "403" in str(e) or "Access" in str(e) else "ERROR"
            result = str(e)

        passed = actual == test["expected"]
        results.append({"name": test["name"], "passed": passed, "actual": actual})
        print(f"  Expected: {test['expected']}, Actual: {actual} -> {'PASS' if passed else 'FAIL'}")

    # Step 3: Promote to ENFORCE if all pass
    all_passed = all(r["passed"] for r in results)
    if all_passed:
        print(f"\nAll {len(results)} tests passed. Switching to ENFORCE mode...")
        control.update_gateway(
            gatewayIdentifier=gateway_id,
            policyEngineConfiguration={
                "policyEngineArn": engine_arn,
                "enforcementMode": "ENFORCE",
            },
        )
        print("Policies are now enforced in production.")
    else:
        failed = [r for r in results if not r["passed"]]
        print(f"\n{len(failed)} test(s) failed. Remaining in LOG_ONLY mode.")
        for f in failed:
            print(f"  FAILED: {f['name']} (got {f['actual']})")

    return results


# Define test cases for policy validation
policy_test_cases = [
    {
        "name": "Support team can lookup customer",
        "tool": "lookup_customer",
        "arguments": {"email": "test@example.com"},
        "expected": "ALLOW",
    },
    {
        "name": "Support team can create standard case",
        "tool": "create_case",
        "arguments": {
            "account_id": "ACC-001",
            "subject": "Test",
            "description": "Testing",
            "priority": "Medium",
        },
        "expected": "ALLOW",
    },
    {
        "name": "Non-senior cannot create critical case",
        "tool": "create_case",
        "arguments": {
            "account_id": "ACC-001",
            "subject": "Urgent",
            "description": "Critical test",
            "priority": "Critical",
        },
        "expected": "DENY",
    },
]

# Run the test suite
# test_policy_rollout(GATEWAY_ID, POLICY_ENGINE_ARN, policy_test_cases)
```

## Key Benefits

### Shared Infrastructure, Independent Teams

Each team deploys their own agent with their own framework and model choices. The platform layer provides Gateway, Memory, Policy, and Identity as shared services. No team duplicates API integrations, credential management, or policy enforcement.

### Deterministic Security at Scale

Cedar policies enforce access control at the Gateway boundary. When a policy says deny, the tool call is blocked before execution. This is not probabilistic prompt-based filtering. It is deterministic, auditable, and immune to prompt injection.

### Federated Identity Without Custom Code

Okta, Entra ID, and Cognito integrate natively through OIDC discovery URLs. User identity flows from the corporate IdP through the agent to the downstream service. Agents never store or manage credentials directly.

### Cross-Agent Knowledge Sharing

Shared memory stores enable patterns that are impossible with isolated agents: customer knowledge that follows the customer across teams, incident patterns that inform future responses, and handoff context that preserves conversation continuity.

### Consumption-Based Cost Model

AgentCore charges for actual resource usage with I/O wait time free. Agents spend 30-70% of their time waiting for LLM responses and API calls, and you pay nothing for CPU during that wait. No over-provisioning, no capacity planning, no idle resource waste.

## Pricing

### Enterprise Platform Cost Estimate

For an enterprise platform handling 1,000,000 monthly interactions across multiple agent teams:

| Component | Configuration | Monthly Cost |
|-----------|--------------|-------------|
| **Runtime** | 1M sessions, 90s avg, 70% I/O wait, 2GB mem | ~$3,500 |
| **Gateway** | 3M tool calls + 1M searches, 200 tools indexed | ~$1,300 |
| **Memory** | 1M short-term events, 100K long-term records, 200K retrievals | ~$475 |
| **Identity** | Free via Runtime | $0 |
| **Policy** | 3M authorization requests (Preview: free) | $75 (post-preview) |
| **Observability** | 2TB span data, 1TB logs | ~$1,200 |
| **Total** | | **~$6,550/month** |

**Cost per interaction**: ~$0.0066

Compare this to the self-hosted alternative: 10+ EC2 instances, load balancers, NAT gateways, ECS/EKS management, credential vaults, policy engines, custom memory stores, and the engineering team to operate all of it. Conservative estimates put that at $15,000-25,000/month in infrastructure alone, plus $20,000+/month in engineering time.

### Free Tier

New AWS customers receive **$200 in Free Tier credits** across all AgentCore services. Policy and Evaluations are currently free during preview.

### Cost Optimization

1. **Maximize I/O wait**: Design agents to offload computation to the LLM (already separately billed) rather than doing CPU-intensive local processing.
2. **Cache tool lists**: Call `ListTools` once per session, not per tool invocation.
3. **Use Identity through Runtime/Gateway**: Identity is free when accessed through these services.
4. **Right-size memory TTL**: Set short-term event expiry based on actual session patterns.
5. **Sample Observability**: Use 10-20% trace sampling in production, 100% only in development.

## Next Steps

Start with a single Gateway and one agent team. Register your most-used enterprise APIs as tool targets and verify the pattern works. Add Memory for customer context continuity, then Policy for governance. Identity integration comes last since it requires coordination with your IdP team.

The progression:

1. **Week 1**: Gateway with 3-5 enterprise tools, one pilot agent team
2. **Week 2**: Memory stores for customer knowledge and agent handoffs
3. **Week 3**: Cedar policies for role-based access and tenant isolation (start in LOG_ONLY)
4. **Week 4**: Identity integration with Okta or Entra ID, promote policies to ENFORCE
5. **Month 2+**: Onboard additional agent teams, expand tool catalog, add Observability dashboards

Each step adds value independently. You do not need the entire platform to realize benefits from any single component.

---

**Documentation**: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/

**Samples**: https://github.com/awslabs/amazon-bedrock-agentcore-samples/

**Pricing**: https://aws.amazon.com/bedrock/agentcore/pricing/

#AWS #AI #AgentCore #Enterprise #Architecture #Tutorial
