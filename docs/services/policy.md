# Policy

> Cedar-based deterministic access control for AI agents

**Status: GA** (generally available 2026-03-03)

## Overview

AgentCore Policy enables developers to define and enforce security controls for AI agent interactions with tools. It creates a protective boundary around agent operations, ensuring agents operate within defined boundaries and business rules.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Agent Request                            │
│            "Get customer data for user-123"                     │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AgentCore Policy                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Policy Evaluation                      │   │
│  │                                                          │   │
│  │  Principal: agent-123                                    │   │
│  │  Action: get_customer                                    │   │
│  │  Resource: customer-data                                 │   │
│  │  Context: user_id=user-456                              │   │
│  │                                                          │   │
│  │  Policy: permit if user owns the data                   │   │
│  │                                                          │   │
│  │  Result: ✓ ALLOW                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│                    Allow request                                │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Gateway Tool                                │
│                  get_customer(user-123)                         │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

| Feature | Description |
|---------|-------------|
| **Cedar Language** | AWS's open-source policy language |
| **Natural Language** | Describe rules in plain English |
| **Gateway Integration** | Intercepts all tool requests |
| **Fine-Grained** | Rules based on identity, params, context |
| **Deterministic** | Consistent enforcement regardless of agent |

## Quick Start

`bedrock_agentcore.policy` exports `PolicyEngineClient`, not `PolicyClient`. Policies belong to a **policy engine** (create one first), and its methods take `policy_engine_id=`, not `gateway_id=` - attaching that engine to a gateway is a separate step.

### Create a Policy Engine

```python
from bedrock_agentcore.policy import PolicyEngineClient

policy = PolicyEngineClient(region_name="us-east-1")

engine = policy.create_or_get_policy_engine(name="CustomerDataPolicyEngine")
engine_id = engine["policyEngineId"]
```

### Create Policy from Natural Language

There is no `create_from_description()` - natural-language authoring is `generate_and_create_policy()`, which generates Cedar from the description and creates the policy in one step:

```python
policy.generate_and_create_policy(
    policy_engine_id=engine_id,
    generation_name="customer-data-access-gen",
    policy_name="customer-data-access",
    resource={"arn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/gw-abc123"},
    content={
        "rawText": """
        Allow agents to read customer data only if:
        - The requesting user owns the customer record, OR
        - The requesting user is a support agent

        Deny all write operations on customer data except:
        - Support agents can update contact information
        - Managers can update any field
        """
    },
)
```

### Create Cedar Policy Directly

There is no `create_from_cedar()` - write Cedar through `create_or_get_policy()`'s `definition={"cedar": {"statement": ...}}`:

```python
policy.create_or_get_policy(
    policy_engine_id=engine_id,
    name="customer-data-read-write",
    definition={
        "cedar": {
            "statement": """
            // Allow users to read their own data
            permit(
                principal,
                action == Action::"read",
                resource
            ) when {
                resource.owner == principal.user_id
            };

            // Allow support agents to read any customer
            permit(
                principal in Group::"support-agents",
                action == Action::"read",
                resource in ResourceType::"customer"
            );

            // Deny write by default
            forbid(
                principal,
                action == Action::"write",
                resource
            ) unless {
                principal in Group::"managers"
            };
            """
        }
    },
)
```

### Test Policy Before Enforcing

There is no `policy.test()` method - test by attaching the engine to the gateway in `LOG_ONLY` mode, calling the gateway's tools for real, and checking the responses, then flip to `ENFORCE` once satisfied:

```python
def set_policy_mode(control_client, gateway_id: str, engine_arn: str, mode: str):
    """UpdateGateway is not a sparse patch: name, roleArn and authorizerType are
    required on every call, so read the current configuration back first."""
    gw = control_client.get_gateway(gatewayIdentifier=gateway_id)
    kwargs = {
        "gatewayIdentifier": gateway_id,
        "name": gw["name"],
        "roleArn": gw["roleArn"],
        "authorizerType": gw["authorizerType"],
        "policyEngineConfiguration": {"arn": engine_arn, "mode": mode},
    }
    if gw.get("authorizerConfiguration"):
        kwargs["authorizerConfiguration"] = gw["authorizerConfiguration"]
    return control_client.update_gateway(**kwargs)


import boto3

control_client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

# Attach in LOG_ONLY mode - decisions are logged but never block a call
set_policy_mode(control_client, "gw-abc123", engine["policyEngineArn"], "LOG_ONLY")

# ... call the gateway's tools over MCP and check the responses ...

# Once satisfied, switch to enforcement
set_policy_mode(control_client, "gw-abc123", engine["policyEngineArn"], "ENFORCE")
```

## Cedar Policy Examples

### Role-Based Access

```cedar
// Only admins can delete
permit(
    principal in Group::"admins",
    action == Action::"delete",
    resource
);
```

### Parameter-Based Rules

```cedar
// Limit transaction amounts
permit(
    principal,
    action == Action::"transfer",
    resource
) when {
    context.amount <= 1000
};

// Large transfers need manager approval
permit(
    principal in Group::"managers",
    action == Action::"transfer",
    resource
) when {
    context.amount > 1000 && context.amount <= 10000
};
```

### Time-Based Rules

```cedar
// Only allow during business hours
permit(
    principal,
    action == Action::"process_order",
    resource
) when {
    context.hour >= 9 && context.hour <= 17
};
```

### Data Classification

```cedar
// Restrict PII access
forbid(
    principal,
    action,
    resource in ResourceType::"pii"
) unless {
    principal.has_pii_training == true
};
```

## Natural Language → Cedar

The system converts descriptions to Cedar:

```
Input:  "Only support agents can refund orders over $100"

Output:
    permit(
        principal in Group::"support-agents",
        action == Action::"refund",
        resource in ResourceType::"order"
    ) when {
        context.amount > 100
    };
```

## Integration with Gateway

Once a policy engine is attached in `ENFORCE` mode, every MCP tool call through that gateway is evaluated automatically - there is no per-call opt-in and, since Gateway has no data-plane boto3 API, no `gateway.invoke_tool()` call to attach the policy to in the first place (see [AgentCore Gateway](gateway.md)). Denied calls come back as MCP errors to the caller:

```python
set_policy_mode(control_client, "gw-abc123", engine["policyEngineArn"], "ENFORCE")

# Every subsequent call_tool() over MCP against this gateway is now
# evaluated against the attached policy engine before the target executes.
```

## Monitoring

There is no `policy.list_decisions()` - decisions are logged to CloudWatch, queried like any other log group:

```python
import time
import boto3
import json

logs_client = boto3.client('logs', region_name='us-east-1')

response = logs_client.filter_log_events(
    logGroupName='/aws/bedrock-agentcore/policy-decisions',
    filterPattern='{ $.decision = "DENY" }',
    startTime=int((time.time() - 3600) * 1000),
    limit=100,
)

for event in response['events']:
    log = json.loads(event['message'])
    print(f"{log['timestamp']}: {log['action']} - {log['decision']}")
    if log['decision'] == 'DENY':
        print(f"  Reason: {log.get('reason', 'N/A')}")
```

## Use Cases

| Use Case | Policy Approach |
|----------|-----------------|
| Data access control | Resource ownership rules |
| Transaction limits | Parameter-based rules |
| Compliance | Mandatory access controls |
| Multi-tenant | Tenant isolation rules |
| Audit requirements | Logging all decisions |

## Pricing

Billed per one million user input tokens processed for authorization requests during agent execution.

## Related

- [Detailed Research](../../research/07-policy.md)
- [Cedar Language Reference](https://www.cedarpolicy.com/)
- [Policy Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html)
