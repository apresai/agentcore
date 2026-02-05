# Policy

> Cedar-based deterministic access control for AI agents

**Status: Preview** (No charges during preview)

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

### Create Policy from Natural Language

```python
from bedrock_agentcore.policy import PolicyClient

policy = PolicyClient()

# Describe policy in plain English
policy.create_from_description(
    gateway_id="my-gateway",
    description="""
    Allow agents to read customer data only if:
    - The requesting user owns the customer record, OR
    - The requesting user is a support agent

    Deny all write operations on customer data except:
    - Support agents can update contact information
    - Managers can update any field
    """
)
```

### Create Cedar Policy Directly

```python
# Write Cedar policy
policy.create_from_cedar(
    gateway_id="my-gateway",
    policy="""
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
)
```

### Test Policy

```python
# Test policy before deploying
result = policy.test(
    policy_id="my-policy",
    test_cases=[
        {
            "principal": {"user_id": "user-123", "groups": ["support-agents"]},
            "action": "read",
            "resource": {"type": "customer", "id": "cust-456"},
            "expected": "ALLOW"
        },
        {
            "principal": {"user_id": "user-123", "groups": []},
            "action": "write",
            "resource": {"type": "customer", "id": "cust-456"},
            "expected": "DENY"
        }
    ]
)

print(f"Tests passed: {result.passed}/{result.total}")
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

```python
# Policies automatically apply to Gateway tools
gateway.invoke_tool(
    tool_name="get_customer",
    input={"customer_id": "cust-123"},
    # Context automatically includes:
    # - User identity from Identity service
    # - Agent identity
    # - Request parameters
)

# Policy evaluates before tool executes
# If DENY, tool call is blocked with reason
```

## Monitoring

```python
# View policy decisions in CloudWatch
decisions = policy.list_decisions(
    policy_id="my-policy",
    start_time=datetime.now() - timedelta(hours=1)
)

for decision in decisions:
    print(f"{decision.timestamp}: {decision.action} - {decision.result}")
    if decision.result == "DENY":
        print(f"  Reason: {decision.reason}")
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

**No charges during Preview.**

## Related

- [Detailed Research](../../research/07-policy.md)
- [Cedar Language Reference](https://www.cedarpolicy.com/)
- [Policy Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html)
