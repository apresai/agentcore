Your AI agent just processed a $50,000 refund. Nobody approved it. Not even the Vogons would let that slide, and they once demolished an entire planet over a planning permission issue. Here's how to prevent that:

![AgentCore Policy](images/policy-article.webp)

AI agents are non-deterministic. They adapt, improvise, and sometimes act outside their intended authority. Traditional guardrails — prompt engineering, output filtering — are probabilistic. They reduce risk but don't eliminate it. For regulated industries, "usually follows the rules" isn't good enough. You need the implacable, form-filing, triplicate-stamping bureaucratic certainty of a Vogon — but without the poetry.

AgentCore Policy provides **deterministic access control** using Cedar, AWS's open-source policy language. Every tool call passes through a policy engine at the Gateway boundary *before* execution. No exceptions. If the policy says deny, the call is blocked — regardless of what the agent decided to do.

## Prerequisites

- AWS account with Bedrock AgentCore access
- Python 3.10+ installed
- boto3 SDK (`pip install boto3`)
- An existing AgentCore Gateway (see Gateway article)

## Environment Setup

```bash
pip install boto3 python-dotenv
export AWS_REGION=us-east-1
```

## Implementation

### Create a Policy Engine and Cedar Policies

```python
import boto3
import time

control = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

# Step 1: Create a policy engine
engine = control.create_policy_engine(
    name='RefundGovernance',
    description='Controls who can process refunds and for how much'
)
engine_id = engine['policyEngineId']
print(f"✓ Policy engine created: {engine_id}")

# Wait for ACTIVE status
while True:
    status = control.get_policy_engine(policyEngineId=engine_id)['status']
    if status == 'ACTIVE':
        break
    time.sleep(2)
print("✓ Policy engine is ACTIVE")

# Step 2: Create Cedar policies — tiered refund limits
# Regular users: refunds under $500
control.create_policy(
    policyEngineId=engine_id,
    name='standard_refund_limit',
    description='Any user can process refunds under $500',
    definition={'cedar': {'statement': '''
        permit(
            principal is AgentCore::OAuthUser,
            action == AgentCore::Action::"RefundTool__process_refund",
            resource
        ) when { context.input.amount < 500 };
    '''}}
)
print("✓ Policy created: standard refund limit (<$500)")

# Managers: refunds under $5,000
control.create_policy(
    policyEngineId=engine_id,
    name='manager_refund_limit',
    description='Managers can process refunds under $5000',
    definition={'cedar': {'statement': '''
        permit(
            principal is AgentCore::OAuthUser,
            action == AgentCore::Action::"RefundTool__process_refund",
            resource
        ) when {
            principal.hasTag("role") &&
            principal.getTag("role") == "manager" &&
            context.input.amount < 5000
        };
    '''}}
)
print("✓ Policy created: manager refund limit (<$5000)")

# Hard ceiling: nobody can process $10,000+ (forbid overrides all permits)
control.create_policy(
    policyEngineId=engine_id,
    name='absolute_refund_ceiling',
    description='Block all refunds $10,000 or above',
    definition={'cedar': {'statement': '''
        forbid(
            principal,
            action == AgentCore::Action::"RefundTool__process_refund",
            resource
        ) when { context.input.amount >= 10000 };
    '''}}
)
print("✓ Policy created: absolute ceiling ($10,000)")
```

### Attach Policy Engine to Gateway

```python
# Attach to your existing gateway — start with LOG_ONLY to test
control.update_gateway(
    gatewayIdentifier='gw-abc123',
    policyEngineConfiguration={
        'policyEngineArn': engine['policyEngineArn'],
        'enforcementMode': 'LOG_ONLY'  # Test first, then switch to ENFORCE
    }
)
print("✓ Policy engine attached to gateway (LOG_ONLY mode)")

# After validating decisions in CloudWatch, switch to enforcement:
# control.update_gateway(
#     gatewayIdentifier='gw-abc123',
#     policyEngineConfiguration={
#         'policyEngineArn': engine['policyEngineArn'],
#         'enforcementMode': 'ENFORCE'
#     }
# )
```

### Generate Policies from Natural Language

```python
# Don't know Cedar syntax? Describe what you want in plain English
response = control.start_policy_generation(
    policyEngineId=engine_id,
    name='NLGeneratedPolicy',
    content={'text': 'Only finance department users can void payments'},
    resource={'gateway': {
        'gatewayArn': 'arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/gw-abc123'
    }}
)

# Poll for generated Cedar
generation_id = response['policyGenerationId']
while True:
    result = control.get_policy_generation(
        policyEngineId=engine_id, policyGenerationId=generation_id
    )
    if result['status'] == 'GENERATED':
        print("Generated Cedar policy:")
        print(result['generatedPolicies'][0]['statement'])
        break
    time.sleep(3)
```

## How Cedar Works with AgentCore

```
Agent → Gateway → Policy Engine → Tool
                      |
              Cedar evaluation:
              - Who is asking? (principal)
              - What tool? (action)
              - What inputs? (context.input)
              → ALLOW or DENY (deterministic)
```

Cedar follows a **default-deny** model with **forbid-wins** semantics. If no policy matches, access is denied. If any `forbid` policy matches, the result is DENY regardless of `permit` policies. It's the Vogon approach to authorization: resistance is useless, and so is trying to talk your way past a `forbid` rule. The good news is that Cedar syntax is considerably less painful than Vogon poetry — which, as you may recall, is the third worst in the universe.

## Key Benefits

- **Deterministic enforcement**: Every tool call is evaluated at the boundary, outside agent code — no prompt injection can bypass it
- **Natural language authoring**: Describe policies in plain English and get validated Cedar output with automated reasoning analysis
- **Graduated rollout**: Start with LOG_ONLY mode to observe decisions, then switch to ENFORCE when confident

## Common Patterns

Teams typically layer policies by role: broad `permit` rules for read-only tools, scoped `permit` rules with dollar limits for financial operations, and `forbid` rules as absolute ceilings that override everything. The LOG_ONLY mode is critical for testing — it evaluates policies and logs decisions without blocking traffic, letting you validate before enforcing.

## Next Steps

Create a policy engine, attach it to your gateway in LOG_ONLY mode, and review decisions in CloudWatch before switching to ENFORCE. Start with simple permit/forbid rules and add role-based conditions as you identify access patterns. As Prostetnic Vogon Jeltz would say: "Resistance is useless!" — and with Cedar policy enforcement at the gateway boundary, he'd finally be right about something.

📚 Documentation: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy.html
💻 Full runnable example: `articles/examples/gateway/` (policy integrates with Gateway)
🔧 GitHub samples: https://github.com/awslabs/amazon-bedrock-agentcore-samples/

#AWS #AI #AgentCore #Security #Cedar #Architects
