# AgentCore Policy

> Define and enforce deterministic security controls for AI agent interactions using Cedar policies with natural language authoring support.

## Quick Reference

| CLI Command | Description |
|-------------|-------------|
| `agentcore policy create-engine` | Create new policy engine |
| `agentcore policy create` | Create Cedar policy |
| `agentcore policy generate` | Generate policy from natural language |
| `agentcore policy list` | List policies in engine |
| `agentcore policy delete` | Delete policy |

| SDK Client | Purpose |
|------------|---------|
| `PolicyClient` (AgentCore SDK) | High-level policy operations |
| `bedrock-agentcore-control` (boto3) | Control plane API access |

| Key API | Description |
|---------|-------------|
| `CreatePolicyEngine` | Create policy engine container |
| `CreatePolicy` | Create Cedar policy in engine |
| `StartPolicyGeneration` | Convert natural language to Cedar |
| `GetPolicyGeneration` | Get generated policy results |
| `UpdateGateway` | Attach policy engine to gateway |
| `ListPolicies` | List policies in engine |
| `DeletePolicy` | Remove policy from engine |
| `DeletePolicyEngine` | Delete policy engine |

---

## Overview

Amazon Bedrock AgentCore Policy enables developers to define and enforce security controls for AI agent interactions with tools by creating a protective boundary around agent operations.

AI agents dynamically adapt to solve complex problems, but this flexibility introduces security challenges:
- Agents may misinterpret business rules
- Agents may act outside intended authority
- Need deterministic control without slowing agents down

AgentCore Policy addresses these challenges by intercepting all agent traffic through Gateways and evaluating each request against defined policies **before** allowing tool access.

---

## Core Concepts

### Policy Engine

A policy engine is a container that stores and evaluates Cedar policies. Key characteristics:

- **Collection of policies** - Groups related policies for evaluation
- **Gateway association** - Each Gateway can have at most one policy engine, but multiple Gateways can share the same engine
- **Intercepts requests** - Evaluates all agent requests at the gateway boundary
- **Deterministic decisions** - Provides consistent allow/deny decisions

```python
# Policy engine lifecycle
# CREATING -> ACTIVE -> UPDATING -> DELETING
# Failure states: CREATE_FAILED, UPDATE_FAILED, DELETE_FAILED
```

### Cedar Language

Cedar is AWS's open-source language for writing and enforcing authorization policies. It provides:

- **Human-readable syntax** - Easy to write and review
- **Formal verification** - Analyzable for correctness
- **High performance** - Millisecond-level evaluation
- **Fine-grained control** - Attribute-based access control (ABAC)

### Enforcement Modes

Policy engines support two enforcement modes:

| Mode | Behavior | Use Case |
|------|----------|----------|
| `ENFORCE` | Evaluates and enforces decisions (allow/deny) | Production deployment |
| `LOG_ONLY` | Evaluates and logs decisions without enforcement | Testing, validation, gradual rollout |

### Schema Validation

The policy engine generates a Cedar schema from the Gateway's tool definitions:

- **Tool schemas** - Available tools and their input parameters
- **Data types** - Expected parameter types and constraints
- **Validation** - Policies are checked against schema during creation

### Default-Deny Model

Cedar follows a default-deny authorization model:

1. **Everything denied by default** - If no policies match, access is denied
2. **Forbid-wins semantics** - If any forbid policy matches, result is DENY
3. **Permit required** - At least one permit policy must match for ALLOW

---

## CLI Reference

### Installation

```bash
pip install bedrock-agentcore-starter-toolkit
```

### agentcore policy create-engine

Create a new policy engine.

```bash
agentcore policy create-engine [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--name` | Policy engine name | Required |
| `--description` | Human-readable description | None |
| `--region` | AWS region | us-east-1 |

**Examples:**

```bash
# Basic policy engine
agentcore policy create-engine --name RefundPolicyEngine

# With description
agentcore policy create-engine \
    --name RefundPolicyEngine \
    --description "Policy engine for refund governance"
```

### agentcore policy create

Create a Cedar policy in a policy engine.

```bash
agentcore policy create [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--engine-id` | Policy engine ID | Required |
| `--name` | Policy name | Required |
| `--statement` | Cedar policy statement | Required |
| `--description` | Policy description | None |
| `--validation-mode` | FAIL_ON_ANY_FINDINGS or IGNORE_ALL_FINDINGS | FAIL_ON_ANY_FINDINGS |

**Examples:**

```bash
# Create refund limit policy
agentcore policy create \
    --engine-id pe-abc123xyz \
    --name refund_limit_policy \
    --description "Allow refunds under $1000" \
    --statement 'permit(principal, action == AgentCore::Action::"RefundTool__process_refund", resource) when { context.input.amount < 1000 };'

# With lenient validation
agentcore policy create \
    --engine-id pe-abc123xyz \
    --name test_policy \
    --validation-mode IGNORE_ALL_FINDINGS \
    --statement 'permit(principal, action, resource);'
```

### agentcore policy generate

Generate Cedar policy from natural language.

```bash
agentcore policy generate [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--engine-id` | Policy engine ID | Required |
| `--name` | Generation request name | Required |
| `--description` | Natural language policy description | Required |
| `--gateway-arn` | Target gateway ARN | Required |

**Examples:**

```bash
# Generate from natural language
agentcore policy generate \
    --engine-id pe-abc123xyz \
    --name AllowSmallRefunds \
    --description "Allow any user to process refunds under $500" \
    --gateway-arn arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/gw-xyz

# More complex policy
agentcore policy generate \
    --engine-id pe-abc123xyz \
    --name ManagerOnlyLargeRefunds \
    --description "Only users with the manager role can process refunds over $1000" \
    --gateway-arn arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/gw-xyz
```

### agentcore policy list

List policies in a policy engine.

```bash
agentcore policy list --engine-id pe-abc123xyz

# Output
NAME                    STATUS    CREATED
refund_limit_policy     ACTIVE    2025-01-15T10:30:00Z
manager_override        ACTIVE    2025-01-15T11:00:00Z
```

### agentcore policy delete

Delete a policy.

```bash
agentcore policy delete --engine-id pe-abc123xyz --policy-id pol-def456
```

### agentcore policy attach

Attach policy engine to gateway.

```bash
agentcore policy attach \
    --gateway-id gw-abc123 \
    --engine-arn arn:aws:bedrock-agentcore:us-east-1:123456789012:policy-engine/pe-abc123xyz \
    --mode ENFORCE
```

---

## SDK Reference

### Using AgentCore SDK (Recommended)

```python
from bedrock_agentcore_starter_toolkit.operations.policy.client import PolicyClient

client = PolicyClient(region_name='us-east-1')
```

#### Create Policy Engine

```python
from bedrock_agentcore_starter_toolkit.operations.policy.client import PolicyClient

client = PolicyClient(region_name='us-east-1')

# Create or get existing policy engine
engine = client.create_or_get_policy_engine(
    name="RefundPolicyEngine",
    description="Policy engine for refund governance"
)

engine_id = engine["policyEngineId"]
engine_arn = engine["policyEngineArn"]
print(f"Policy Engine: {engine_id}")
```

#### Create Cedar Policy

```python
# Define Cedar policy statement
cedar_statement = '''
permit(
    principal is AgentCore::OAuthUser,
    action == AgentCore::Action::"RefundTool__process_refund",
    resource == AgentCore::Gateway::"arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/gw-abc123"
)
when {
    context.input.amount < 1000
};
'''

# Create policy
policy = client.create_or_get_policy(
    policy_engine_id=engine_id,
    name="refund_limit_policy",
    description="Allow refunds under $1000",
    definition={"cedar": {"statement": cedar_statement}}
)

print(f"Policy ID: {policy['policyId']}")
print(f"Status: {policy['status']}")
```

#### Attach to Gateway

```python
from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient

gateway_client = GatewayClient(region_name='us-east-1')

# Attach policy engine in ENFORCE mode
gateway_client.update_gateway_policy_engine(
    gateway_identifier="gw-abc123",
    policy_engine_arn=engine_arn,
    mode="ENFORCE"  # or "LOG_ONLY" for testing
)
```

### Using boto3 Directly

```python
import boto3

client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
```

#### Control Plane APIs

##### CreatePolicyEngine

```python
response = client.create_policy_engine(
    name='RefundPolicyEngine',
    description='Policy engine for refund governance'
)

engine_id = response['policyEngineId']
engine_arn = response['policyEngineArn']
status = response['status']  # CREATING -> ACTIVE
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Engine name (1-48 chars, alphanumeric + underscore) |
| `description` | string | No | Description (1-4,096 chars) |
| `clientToken` | string | No | Idempotency token |

##### GetPolicyEngine

```python
response = client.get_policy_engine(
    policyEngineId='pe-abc123xyz'
)

status = response['status']
if status == 'ACTIVE':
    print("Policy engine ready")
```

##### CreatePolicy

```python
cedar_statement = '''
permit(
    principal,
    action == AgentCore::Action::"RefundTool__process_refund",
    resource
)
when {
    context.input.amount < 1000
};
'''

response = client.create_policy(
    policyEngineId='pe-abc123xyz',
    name='refund_limit_policy',
    description='Allow refunds under $1000',
    validationMode='FAIL_ON_ANY_FINDINGS',
    definition={
        'cedar': {
            'statement': cedar_statement
        }
    }
)

policy_id = response['policyId']
policy_arn = response['policyArn']
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `policyEngineId` | string | Yes | Policy engine ID |
| `name` | string | Yes | Policy name (1-48 chars) |
| `definition` | object | Yes | Cedar policy definition |
| `validationMode` | string | No | FAIL_ON_ANY_FINDINGS (default) or IGNORE_ALL_FINDINGS |
| `description` | string | No | Policy description |

##### StartPolicyGeneration

```python
response = client.start_policy_generation(
    policyEngineId='pe-abc123xyz',
    name='NLPolicy',
    content={
        'text': 'Allow any user to process refunds under $500'
    },
    resource={
        'gateway': {
            'gatewayArn': 'arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/gw-abc123'
        }
    }
)

generation_id = response['policyGenerationId']
status = response['status']  # GENERATING -> GENERATED
```

##### GetPolicyGeneration

```python
response = client.get_policy_generation(
    policyEngineId='pe-abc123xyz',
    policyGenerationId='pg-xyz789'
)

if response['status'] == 'GENERATED':
    # Review generated policies
    for policy in response['generatedPolicies']:
        print(f"Option: {policy['statement']}")
        print(f"Findings: {policy['findings']}")
```

##### ListPolicies

```python
response = client.list_policies(
    policyEngineId='pe-abc123xyz',
    maxResults=50
)

for policy in response['policySummaries']:
    print(f"{policy['name']}: {policy['status']}")
```

##### UpdatePolicy

```python
response = client.update_policy(
    policyEngineId='pe-abc123xyz',
    policyId='pol-def456',
    definition={
        'cedar': {
            'statement': 'permit(principal, action, resource) when { context.input.amount < 500 };'
        }
    }
)
```

##### DeletePolicy

```python
client.delete_policy(
    policyEngineId='pe-abc123xyz',
    policyId='pol-def456'
)
```

##### DeletePolicyEngine

```python
client.delete_policy_engine(
    policyEngineId='pe-abc123xyz'
)
```

##### UpdateGateway (Attach Policy Engine)

```python
response = client.update_gateway(
    gatewayId='gw-abc123',
    policyEngineConfiguration={
        'policyEngineArn': 'arn:aws:bedrock-agentcore:us-east-1:123456789012:policy-engine/pe-abc123xyz',
        'enforcementMode': 'ENFORCE'  # or 'LOG_ONLY'
    }
)
```

---

## Cedar Policy Language

### Basic Syntax

Cedar policies follow this structure:

```cedar
effect(
    principal [constraint],
    action [constraint],
    resource [constraint]
)
[when { conditions }]
[unless { conditions }];
```

### Effects: permit and forbid

```cedar
// Allow access
permit(principal, action, resource);

// Deny access
forbid(principal, action, resource);
```

### Principal Constraints

Specify who the policy applies to:

```cedar
// Any authenticated user
principal is AgentCore::OAuthUser

// Specific user by tag
principal.hasTag("username") && principal.getTag("username") == "john"

// User with specific role
principal.hasTag("role") && principal.getTag("role") == "manager"

// Any principal (wildcard)
principal
```

### Action Constraints

Specify which operations the policy applies to:

```cedar
// Specific tool action
action == AgentCore::Action::"ToolName__method_name"

// Multiple actions
action in [
    AgentCore::Action::"RefundTool__process_refund",
    AgentCore::Action::"RefundTool__check_status"
]

// Any action (wildcard)
action
```

### Resource Constraints

Specify which gateway the policy applies to:

```cedar
// Specific gateway
resource == AgentCore::Gateway::"arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/gw-abc123"

// Any resource (wildcard)
resource
```

### Conditions with `when` and `unless`

```cedar
// Allow when condition is true
permit(principal, action, resource)
when {
    context.input.amount < 1000
};

// Allow unless condition is true
permit(principal, action, resource)
unless {
    context.input.category == "restricted"
};
```

### Context and Input Parameters

Access tool input parameters through `context.input`:

```cedar
// Numeric comparison
context.input.amount < 1000
context.input.quantity >= 1 && context.input.quantity <= 100

// String comparison
context.input.region == "us-east-1"
context.input.status in ["pending", "approved"]

// Boolean check
context.input.is_priority == true

// Nested object access
context.input.customer.tier == "premium"
```

### Principal Tags (OAuth Claims)

Access OAuth token claims through principal tags:

```cedar
// Check if tag exists
principal.hasTag("role")

// Get tag value
principal.getTag("username") == "admin"

// Combine checks
principal.hasTag("department") && principal.getTag("department") == "finance"
```

### Complete Policy Examples

#### User-Specific Access

```cedar
// Only John can process refunds under $500
permit(
    principal is AgentCore::OAuthUser,
    action == AgentCore::Action::"RefundTool__process_refund",
    resource == AgentCore::Gateway::"arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/gw-abc123"
)
when {
    principal.hasTag("username") &&
    principal.getTag("username") == "John" &&
    context.input.amount < 500
};
```

#### Role-Based Access

```cedar
// Managers can process any refund amount
permit(
    principal is AgentCore::OAuthUser,
    action == AgentCore::Action::"RefundTool__process_refund",
    resource
)
when {
    principal.hasTag("role") &&
    principal.getTag("role") == "manager"
};
```

#### Forbid Override

```cedar
// Never allow refunds over $10,000 (even for managers)
forbid(
    principal,
    action == AgentCore::Action::"RefundTool__process_refund",
    resource
)
when {
    context.input.amount >= 10000
};
```

---

## Natural Language Policy Authoring

### Overview

AgentCore Policy supports natural language to Cedar conversion (NL2Cedar), enabling policy creation without learning Cedar syntax:

1. **Describe intent** - Write authorization requirements in plain English
2. **Generate candidates** - AI generates Cedar policy options
3. **Validate** - Policies checked against tool schema
4. **Analyze** - Automated reasoning detects issues
5. **Review and create** - Select and deploy the best option

### Writing Effective Natural Language Policies

#### Structure Requirements

Every policy description should specify:

1. **Who** (Principal) - Which users, roles, or groups
2. **What** (Action) - Which tools or operations
3. **When** (Conditions) - Under what circumstances

#### Good Examples

```text
# User-based policy
"Allow users with the username 'john' to process refunds under $500"

# Role-based policy
"Allow users with the manager role to process refunds of any amount"

# Tool-scoped policy
"Allow all authenticated users to use the check_status tool"

# Constraint-based policy
"Allow any user to process refunds when the amount is less than $1000
and the customer tier is 'standard'"

# Combined conditions
"Allow finance department users to process refunds under $5000
OR allow any manager to process refunds of any amount"
```

#### Common Mistakes to Avoid

| Mistake | Bad Example | Good Example |
|---------|-------------|--------------|
| Vague principal | "Some users can..." | "Users with the admin role can..." |
| Ambiguous action | "Access the system" | "Use the process_refund tool" |
| Subjective condition | "For reasonable amounts" | "When amount is less than $1000" |
| Missing condition | "Managers can do refunds" | "Managers can process refunds of any amount" |
| Unclear logic | "Maybe allow if..." | "Allow when amount < $500 AND status = pending" |

### Automated Reasoning Analysis

The NL2Cedar system uses automated reasoning to detect:

- **Overly permissive policies** - Grants more access than intended
- **Overly restrictive policies** - Blocks legitimate access
- **Unsatisfiable conditions** - Conditions that can never be true
- **Redundant policies** - Overlap with existing policies
- **Conflicts** - Contradictions with other policies

### Code Example

```python
import boto3
import time

client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

# Start policy generation
response = client.start_policy_generation(
    policyEngineId='pe-abc123xyz',
    name='SmallRefundPolicy',
    content={
        'text': 'Allow any authenticated user to process refunds under $1000'
    },
    resource={
        'gateway': {
            'gatewayArn': 'arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/gw-abc123'
        }
    }
)

generation_id = response['policyGenerationId']

# Poll for completion
while True:
    result = client.get_policy_generation(
        policyEngineId='pe-abc123xyz',
        policyGenerationId=generation_id
    )

    if result['status'] in ['GENERATED', 'GENERATE_FAILED']:
        break

    time.sleep(2)

# Review generated policies
if result['status'] == 'GENERATED':
    for option in result['generatedPolicies']:
        print("Generated Cedar Policy:")
        print(option['statement'])
        print(f"Findings: {option.get('findings', 'None')}")

    # Create policy from best option
    client.create_policy(
        policyEngineId='pe-abc123xyz',
        name='small_refund_policy',
        definition={
            'cedar': {
                'statement': result['generatedPolicies'][0]['statement']
            }
        }
    )
```

---

## Policy Patterns

### Pattern 1: User-Based Access Control

Restrict tool access to specific users.

```cedar
// Only allow specific users to use sensitive tools
permit(
    principal is AgentCore::OAuthUser,
    action == AgentCore::Action::"DatabaseTool__delete_records",
    resource
)
when {
    principal.hasTag("username") &&
    principal.getTag("username") in ["admin", "dba"]
};
```

### Pattern 2: Role-Based Access Control (RBAC)

Grant access based on organizational roles.

```cedar
// Finance role can process payments
permit(
    principal is AgentCore::OAuthUser,
    action in [
        AgentCore::Action::"PaymentTool__process_payment",
        AgentCore::Action::"PaymentTool__void_payment",
        AgentCore::Action::"PaymentTool__check_status"
    ],
    resource
)
when {
    principal.hasTag("role") &&
    principal.getTag("role") == "finance"
};

// Support role can only check status
permit(
    principal is AgentCore::OAuthUser,
    action == AgentCore::Action::"PaymentTool__check_status",
    resource
)
when {
    principal.hasTag("role") &&
    principal.getTag("role") == "support"
};
```

### Pattern 3: Tool Restrictions with Limits

Apply numeric limits to tool parameters.

```cedar
// Regular users: refunds under $500
permit(
    principal is AgentCore::OAuthUser,
    action == AgentCore::Action::"RefundTool__process_refund",
    resource
)
when {
    context.input.amount < 500
};

// Supervisors: refunds under $5000
permit(
    principal is AgentCore::OAuthUser,
    action == AgentCore::Action::"RefundTool__process_refund",
    resource
)
when {
    principal.hasTag("role") &&
    principal.getTag("role") == "supervisor" &&
    context.input.amount < 5000
};

// Hard limit: never allow over $10000
forbid(
    principal,
    action == AgentCore::Action::"RefundTool__process_refund",
    resource
)
when {
    context.input.amount >= 10000
};
```

### Pattern 4: Time-Based and Contextual Access

Restrict access based on request context.

```cedar
// Only allow during business hours (checked via context)
permit(
    principal is AgentCore::OAuthUser,
    action == AgentCore::Action::"OrderTool__cancel_order",
    resource
)
when {
    context.input.business_hours == true
};

// Restrict to specific regions
permit(
    principal is AgentCore::OAuthUser,
    action == AgentCore::Action::"DataTool__query",
    resource
)
when {
    context.input.region in ["us-east-1", "us-west-2"]
};
```

### Pattern 5: Data Filtering and Field-Level Access

Control access to specific data categories.

```cedar
// Allow access to non-PII data
permit(
    principal is AgentCore::OAuthUser,
    action == AgentCore::Action::"CustomerTool__get_info",
    resource
)
when {
    context.input.data_category == "non_pii"
};

// Only compliance team can access PII
permit(
    principal is AgentCore::OAuthUser,
    action == AgentCore::Action::"CustomerTool__get_info",
    resource
)
when {
    principal.hasTag("team") &&
    principal.getTag("team") == "compliance" &&
    context.input.data_category == "pii"
};
```

---

## Code Examples

### Example 1: Basic Policy Engine Setup

Complete setup of a policy engine with a simple policy.

```python
"""
Basic policy engine setup with refund limit policy.
"""
from bedrock_agentcore_starter_toolkit.operations.policy.client import PolicyClient
from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
import time

def setup_policy_engine():
    region = "us-east-1"

    # Initialize clients
    policy_client = PolicyClient(region_name=region)
    gateway_client = GatewayClient(region_name=region)

    # Step 1: Create policy engine
    print("Creating policy engine...")
    engine = policy_client.create_or_get_policy_engine(
        name="RefundPolicyEngine",
        description="Controls refund processing permissions"
    )
    print(f"Engine ID: {engine['policyEngineId']}")

    # Step 2: Wait for engine to be active
    while engine['status'] != 'ACTIVE':
        time.sleep(2)
        engine = policy_client.get_policy_engine(engine['policyEngineId'])

    # Step 3: Create policy
    cedar_statement = '''
    permit(
        principal is AgentCore::OAuthUser,
        action == AgentCore::Action::"RefundTool__process_refund",
        resource
    )
    when {
        context.input.amount < 1000
    };
    '''

    print("Creating Cedar policy...")
    policy = policy_client.create_or_get_policy(
        policy_engine_id=engine['policyEngineId'],
        name="refund_limit_1000",
        description="Allow refunds under $1000",
        definition={"cedar": {"statement": cedar_statement}}
    )
    print(f"Policy ID: {policy['policyId']}")

    # Step 4: Attach to gateway
    gateway_id = "gw-abc123xyz"  # Your gateway ID
    print(f"Attaching to gateway {gateway_id}...")

    gateway_client.update_gateway_policy_engine(
        gateway_identifier=gateway_id,
        policy_engine_arn=engine['policyEngineArn'],
        mode="ENFORCE"
    )

    print("Setup complete!")
    return engine, policy

if __name__ == "__main__":
    setup_policy_engine()
```

### Example 2: Cedar Policy Creation with Validation

Create policies with proper validation handling.

```python
"""
Create Cedar policies with validation and error handling.
"""
import boto3

def create_validated_policy(
    policy_engine_id: str,
    name: str,
    statement: str,
    description: str = None,
    strict: bool = True
):
    """Create a policy with validation."""
    client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

    validation_mode = 'FAIL_ON_ANY_FINDINGS' if strict else 'IGNORE_ALL_FINDINGS'

    try:
        response = client.create_policy(
            policyEngineId=policy_engine_id,
            name=name,
            description=description or f"Policy: {name}",
            validationMode=validation_mode,
            definition={
                'cedar': {
                    'statement': statement
                }
            }
        )

        print(f"Policy created: {response['policyId']}")
        print(f"Status: {response['status']}")

        if response.get('statusReasons'):
            print(f"Notes: {response['statusReasons']}")

        return response

    except client.exceptions.ValidationException as e:
        print(f"Validation failed: {e}")
        print("Check Cedar syntax and schema compatibility")
        raise
    except client.exceptions.ConflictException as e:
        print(f"Policy already exists: {e}")
        raise

# Example usage
if __name__ == "__main__":
    # Create tiered refund policies
    policies = [
        {
            "name": "standard_refund",
            "statement": '''
            permit(principal, action == AgentCore::Action::"RefundTool__process_refund", resource)
            when { context.input.amount < 500 };
            ''',
            "description": "Standard users: refunds under $500"
        },
        {
            "name": "supervisor_refund",
            "statement": '''
            permit(principal is AgentCore::OAuthUser, action == AgentCore::Action::"RefundTool__process_refund", resource)
            when {
                principal.hasTag("role") &&
                principal.getTag("role") == "supervisor" &&
                context.input.amount < 5000
            };
            ''',
            "description": "Supervisors: refunds under $5000"
        },
        {
            "name": "hard_limit",
            "statement": '''
            forbid(principal, action == AgentCore::Action::"RefundTool__process_refund", resource)
            when { context.input.amount >= 10000 };
            ''',
            "description": "Never allow refunds $10000+"
        }
    ]

    engine_id = "pe-abc123xyz"

    for policy in policies:
        create_validated_policy(
            policy_engine_id=engine_id,
            name=policy["name"],
            statement=policy["statement"],
            description=policy["description"]
        )
```

### Example 3: Gateway Integration

Complete integration of policy engine with gateway.

```python
"""
Integrate policy engine with AgentCore Gateway.
"""
from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
from bedrock_agentcore_starter_toolkit.operations.policy.client import PolicyClient
import boto3
import time

def setup_gateway_with_policy():
    region = "us-east-1"

    gateway_client = GatewayClient(region_name=region)
    policy_client = PolicyClient(region_name=region)

    # Step 1: Create OAuth authorizer
    print("Creating OAuth authorizer...")
    cognito_response = gateway_client.create_oauth_authorizer_with_cognito("SecureGateway")

    # Step 2: Create gateway
    print("Creating gateway...")
    gateway = gateway_client.create_mcp_gateway(
        name=None,  # Auto-generated
        role_arn=None,  # Auto-created
        authorizer_config=cognito_response["authorizer_config"],
        enable_semantic_search=False
    )
    print(f"Gateway URL: {gateway['gatewayUrl']}")

    # Fix IAM permissions
    gateway_client.fix_iam_permissions(gateway)
    print("Waiting for IAM propagation...")
    time.sleep(30)

    # Step 3: Add Lambda target
    print("Adding tool target...")
    target = gateway_client.create_mcp_gateway_target(
        gateway=gateway,
        name="RefundTarget",
        target_type="lambda",
        target_payload={
            "lambdaArn": "arn:aws:lambda:us-east-1:123456789012:function:RefundTool",
            "toolSchema": {
                "inlinePayload": [{
                    "name": "process_refund",
                    "description": "Process a customer refund",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "amount": {
                                "type": "integer",
                                "description": "Refund amount in dollars"
                            }
                        },
                        "required": ["amount"]
                    }
                }]
            }
        },
        credentials=None
    )

    # Step 4: Create policy engine
    print("Creating policy engine...")
    engine = policy_client.create_or_get_policy_engine(
        name="GatewayPolicyEngine",
        description=f"Policy engine for {gateway['gatewayId']}"
    )

    # Step 5: Create policy
    cedar_statement = f'''
    permit(
        principal is AgentCore::OAuthUser,
        action == AgentCore::Action::"RefundTarget___process_refund",
        resource == AgentCore::Gateway::"{gateway['gatewayArn']}"
    )
    when {{
        context.input.amount < 1000
    }};
    '''

    print("Creating policy...")
    policy = policy_client.create_or_get_policy(
        policy_engine_id=engine["policyEngineId"],
        name="refund_limit_policy",
        description="Allow refunds under $1000",
        definition={"cedar": {"statement": cedar_statement}}
    )

    # Step 6: Attach policy engine to gateway
    print("Attaching policy engine to gateway...")
    gateway_client.update_gateway_policy_engine(
        gateway_identifier=gateway["gatewayId"],
        policy_engine_arn=engine["policyEngineArn"],
        mode="ENFORCE"
    )

    print("\nSetup complete!")
    print(f"Gateway URL: {gateway['gatewayUrl']}")
    print(f"Policy Engine: {engine['policyEngineId']}")
    print(f"Mode: ENFORCE")

    return gateway, engine, policy

if __name__ == "__main__":
    setup_gateway_with_policy()
```

### Example 4: Natural Language Policy Authoring

Generate policies from natural language descriptions.

```python
"""
Generate Cedar policies from natural language using NL2Cedar.
"""
import boto3
import time

def generate_policy_from_nl(
    policy_engine_id: str,
    gateway_arn: str,
    name: str,
    description: str
):
    """Generate Cedar policy from natural language."""
    client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

    # Start generation
    print(f"Generating policy: {description}")
    response = client.start_policy_generation(
        policyEngineId=policy_engine_id,
        name=name,
        content={
            'text': description
        },
        resource={
            'gateway': {
                'gatewayArn': gateway_arn
            }
        }
    )

    generation_id = response['policyGenerationId']
    print(f"Generation ID: {generation_id}")

    # Poll for completion
    while True:
        result = client.get_policy_generation(
            policyEngineId=policy_engine_id,
            policyGenerationId=generation_id
        )

        status = result['status']
        print(f"Status: {status}")

        if status == 'GENERATED':
            break
        elif status == 'GENERATE_FAILED':
            print(f"Generation failed: {result.get('statusReasons')}")
            return None

        time.sleep(3)

    # Review generated policies
    print("\n=== Generated Policies ===")
    generated = result.get('generatedPolicies', [])

    for i, option in enumerate(generated):
        print(f"\nOption {i + 1}:")
        print(option['statement'])
        if option.get('findings'):
            print(f"Findings: {option['findings']}")

    return generated

def create_from_generated(
    policy_engine_id: str,
    name: str,
    generated_statement: str,
    description: str
):
    """Create policy from generated Cedar statement."""
    client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

    response = client.create_policy(
        policyEngineId=policy_engine_id,
        name=name,
        description=description,
        validationMode='FAIL_ON_ANY_FINDINGS',
        definition={
            'cedar': {
                'statement': generated_statement
            }
        }
    )

    print(f"Policy created: {response['policyId']}")
    return response

# Example usage
if __name__ == "__main__":
    engine_id = "pe-abc123xyz"
    gateway_arn = "arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/gw-abc123"

    # Generate policies from natural language
    policies_nl = [
        {
            "name": "SmallRefunds",
            "description": "Allow any authenticated user to process refunds under $500"
        },
        {
            "name": "ManagerRefunds",
            "description": "Allow users with the manager role to process refunds of any amount"
        },
        {
            "name": "BlockLarge",
            "description": "Never allow any user to process refunds over $10000"
        }
    ]

    for policy in policies_nl:
        generated = generate_policy_from_nl(
            policy_engine_id=engine_id,
            gateway_arn=gateway_arn,
            name=policy["name"],
            description=policy["description"]
        )

        if generated:
            # Create from first generated option
            create_from_generated(
                policy_engine_id=engine_id,
                name=policy["name"].lower() + "_policy",
                generated_statement=generated[0]['statement'],
                description=policy["description"]
            )
```

### Example 5: Policy Testing and Debugging

Test policies before enforcement.

```python
"""
Test policies in LOG_ONLY mode before enforcement.
"""
import boto3
import requests
import json
import time

def test_policy_decisions(
    gateway_url: str,
    access_token: str,
    test_cases: list
):
    """Test policy decisions with various inputs."""
    results = []

    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print(f"Tool: {test['tool']}")
        print(f"Args: {test['arguments']}")
        print(f"Expected: {test['expected']}")

        # Call the tool through the gateway
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "name": test['tool'],
            "arguments": test['arguments']
        }

        try:
            response = requests.post(
                f"{gateway_url}/mcp/tools/call",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                actual = "ALLOW"
                result_data = response.json()
            elif response.status_code == 403:
                actual = "DENY"
                result_data = {"error": "Access denied by policy"}
            else:
                actual = "ERROR"
                result_data = {"error": response.text}

            passed = actual == test['expected']
            print(f"Actual: {actual} - {'PASS' if passed else 'FAIL'}")

            results.append({
                "name": test['name'],
                "expected": test['expected'],
                "actual": actual,
                "passed": passed,
                "response": result_data
            })

        except Exception as e:
            print(f"Error: {e}")
            results.append({
                "name": test['name'],
                "expected": test['expected'],
                "actual": "ERROR",
                "passed": False,
                "error": str(e)
            })

    # Summary
    print("\n=== Test Summary ===")
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    print(f"Passed: {passed}/{total}")

    return results

def switch_enforcement_mode(gateway_id: str, engine_arn: str, mode: str):
    """Switch between ENFORCE and LOG_ONLY modes."""
    client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

    response = client.update_gateway(
        gatewayId=gateway_id,
        policyEngineConfiguration={
            'policyEngineArn': engine_arn,
            'enforcementMode': mode
        }
    )

    print(f"Gateway updated to {mode} mode")
    return response

# Example test suite
if __name__ == "__main__":
    gateway_url = "https://gateway-abc123.bedrock-agentcore.us-east-1.amazonaws.com"
    gateway_id = "gw-abc123"
    engine_arn = "arn:aws:bedrock-agentcore:us-east-1:123456789012:policy-engine/pe-xyz789"
    access_token = "your-oauth-token"

    # Test cases
    test_cases = [
        {
            "name": "Small refund (should allow)",
            "tool": "process_refund",
            "arguments": {"amount": 100},
            "expected": "ALLOW"
        },
        {
            "name": "Medium refund (should allow)",
            "tool": "process_refund",
            "arguments": {"amount": 999},
            "expected": "ALLOW"
        },
        {
            "name": "Large refund (should deny)",
            "tool": "process_refund",
            "arguments": {"amount": 5000},
            "expected": "DENY"
        },
        {
            "name": "Huge refund (should deny)",
            "tool": "process_refund",
            "arguments": {"amount": 15000},
            "expected": "DENY"
        }
    ]

    # Run in LOG_ONLY mode first
    print("=== Testing in LOG_ONLY mode ===")
    switch_enforcement_mode(gateway_id, engine_arn, "LOG_ONLY")
    time.sleep(5)  # Wait for propagation

    results = test_policy_decisions(gateway_url, access_token, test_cases)

    # If all tests pass, switch to ENFORCE
    if all(r['passed'] for r in results):
        print("\nAll tests passed! Switching to ENFORCE mode...")
        switch_enforcement_mode(gateway_id, engine_arn, "ENFORCE")
    else:
        print("\nSome tests failed. Review policies before enforcing.")
```

---

## Integration Patterns

### With AgentCore Gateway

Policy engines integrate directly with gateways to control tool access.

```python
from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
from bedrock_agentcore_starter_toolkit.operations.policy.client import PolicyClient

gateway_client = GatewayClient(region_name='us-east-1')
policy_client = PolicyClient(region_name='us-east-1')

# Create policy engine for gateway
engine = policy_client.create_or_get_policy_engine(
    name=f"PolicyEngine_{gateway['gatewayId']}",
    description=f"Policy engine for gateway {gateway['gatewayId']}"
)

# Create policies specific to gateway tools
for target in gateway_client.list_targets(gateway['gatewayId']):
    tool_name = target['name']

    # Create tool-specific policy
    policy_client.create_or_get_policy(
        policy_engine_id=engine['policyEngineId'],
        name=f"{tool_name}_default_policy",
        definition={
            "cedar": {
                "statement": f'''
                permit(
                    principal is AgentCore::OAuthUser,
                    action == AgentCore::Action::"{tool_name}___*",
                    resource == AgentCore::Gateway::"{gateway['gatewayArn']}"
                );
                '''
            }
        }
    )

# Attach to gateway
gateway_client.update_gateway_policy_engine(
    gateway_identifier=gateway['gatewayId'],
    policy_engine_arn=engine['policyEngineArn'],
    mode="ENFORCE"
)
```

### With AgentCore Observability

Monitor policy decisions through CloudWatch.

```python
import boto3

# Policy decisions are logged to CloudWatch
logs_client = boto3.client('logs', region_name='us-east-1')

# Query policy decision logs
response = logs_client.filter_log_events(
    logGroupName='/aws/bedrock-agentcore/policy-decisions',
    filterPattern='{ $.decision = "DENY" }',
    startTime=int((time.time() - 3600) * 1000),  # Last hour
    limit=100
)

for event in response['events']:
    log = json.loads(event['message'])
    print(f"Time: {log['timestamp']}")
    print(f"Gateway: {log['gatewayId']}")
    print(f"Tool: {log['action']}")
    print(f"Decision: {log['decision']}")
    print(f"Principal: {log['principal']}")
    print(f"Reason: {log.get('reason', 'N/A')}")
    print("---")

# Create CloudWatch alarm for policy denials
cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

cloudwatch.put_metric_alarm(
    AlarmName='PolicyDenialSpike',
    MetricName='PolicyDenials',
    Namespace='AWS/BedrockAgentCore',
    Statistic='Sum',
    Period=300,
    EvaluationPeriods=1,
    Threshold=100,
    ComparisonOperator='GreaterThanThreshold',
    Dimensions=[
        {'Name': 'GatewayId', 'Value': 'gw-abc123'}
    ],
    AlarmActions=['arn:aws:sns:us-east-1:123456789012:alerts']
)
```

---

## Best Practices

1. **Start with LOG_ONLY mode** - Test policies without blocking legitimate traffic before switching to ENFORCE.

2. **Use forbid for hard limits** - Critical restrictions should use forbid policies since they override all permits.

3. **Be specific with principals** - Avoid wildcards when possible; specify exact users, roles, or groups.

4. **Document policy intent** - Use descriptions to explain the business rule each policy implements.

5. **Test with real scenarios** - Create test cases that match actual usage patterns before deployment.

6. **Review generated policies** - NL2Cedar output should be reviewed and potentially refined before use.

7. **Use validation mode appropriately** - FAIL_ON_ANY_FINDINGS for production, IGNORE_ALL_FINDINGS only for testing.

8. **Layer policies by role** - Create separate policies for different user roles with appropriate limits.

9. **Monitor policy decisions** - Use CloudWatch to track ALLOW/DENY patterns and identify issues.

10. **Version control Cedar statements** - Store policy definitions in version control for audit trails.

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ValidationException` | Invalid Cedar syntax | Check Cedar statement syntax, validate against schema |
| `ResourceNotFoundException` | Policy engine or gateway not found | Verify IDs exist and are in ACTIVE status |
| `ConflictException` | Policy name already exists | Use unique names or use create_or_get pattern |
| `AccessDeniedException` | Insufficient IAM permissions | Add bedrock-agentcore:* permissions to role |
| `PolicyNotApplicable` | Policy doesn't match request | Verify action name matches tool format |
| `SchemaValidation` | Policy references unknown fields | Check context.input fields match tool schema |

### Debugging Tips

```bash
# Check policy engine status
aws bedrock-agentcore-control get-policy-engine \
    --policy-engine-id pe-abc123xyz

# List policies in engine
aws bedrock-agentcore-control list-policies \
    --policy-engine-id pe-abc123xyz

# Get specific policy details
aws bedrock-agentcore-control get-policy \
    --policy-engine-id pe-abc123xyz \
    --policy-id pol-def456

# Check gateway policy engine attachment
aws bedrock-agentcore-control get-gateway \
    --gateway-id gw-abc123

# View policy decision logs
aws logs filter-log-events \
    --log-group-name /aws/bedrock-agentcore/policy-decisions \
    --filter-pattern '{ $.gatewayId = "gw-abc123" }'
```

### Policy Not Enforcing

1. Verify policy engine is attached to gateway
2. Check enforcement mode is ENFORCE (not LOG_ONLY)
3. Confirm policy status is ACTIVE
4. Verify action name matches target format: `TargetName___tool_method`
5. Check principal type matches authentication method

### Natural Language Generation Fails

1. Simplify the description - focus on one rule at a time
2. Be explicit about principals, actions, and conditions
3. Avoid vague terms like "appropriate" or "reasonable"
4. Check gateway ARN is correct and accessible
5. Review findings in the generation response

---

## Limits & Quotas

| Resource | Default Limit | Adjustable |
|----------|--------------|------------|
| Policy engines per account | 50 | Yes |
| Policies per policy engine | 100 | Yes |
| Cedar statement size | 153,600 chars | No |
| Policy name length | 48 chars | No |
| Description length | 4,096 chars | No |
| Natural language prompt | 4,096 chars | No |
| Generated policy expiration | 7 days | No |
| Policy generations per day | 100 | Yes |
| Concurrent policy generations | 10 | Yes |

---

## Pricing

**Preview** - AgentCore Policy is currently in preview and available at no charge.

**Post-Preview pricing** (anticipated):
- Policy engine hosting: Per engine/month
- Policy evaluations: Per 1,000 evaluations
- Natural language generation: Per 1,000 input tokens

---

## Related Services

- [AgentCore Gateway](./03-gateway.md) - Tool integration and MCP protocol
- [AgentCore Identity](./04-identity.md) - User authentication and OAuth
- [AgentCore Observability](./08-observability.md) - Monitoring and logging
- [AgentCore Runtime](./01-runtime.md) - Agent deployment and execution
