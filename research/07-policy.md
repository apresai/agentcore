# AgentCore Policy

## Overview

Amazon Bedrock AgentCore Policy enables developers to define and enforce security controls for AI agent interactions with tools by creating a protective boundary around agent operations.

## The Problem It Solves

AI agents dynamically adapt to solve complex problems, but this flexibility introduces security challenges:
- Agents may misinterpret business rules
- Agents may act outside intended authority
- Need deterministic control without slowing agents down

## How It Works

1. Create **policy engines**
2. Create and store **deterministic policies**
3. Associate policy engines with **gateways**
4. AgentCore Policy intercepts all agent traffic through Gateways
5. Evaluates each request against defined policies **before** allowing tool access

## Policy Language

Policies are constructed using **Cedar language** - AWS's open-source language for writing and enforcing authorization policies.

### Natural Language Authoring
Developers can describe rules in plain English instead of formal Cedar code:
- Interprets user intent
- Generates candidate policies
- Validates against tool schema
- Uses automated reasoning to check safety conditions:
  - Overly permissive policies
  - Overly restrictive policies
  - Unsatisfiable conditions

## Key Benefits

### Fine-Grained Control
Define exactly:
- Which tools an agent can call
- Precise conditions under which actions are permitted

### Deterministic Enforcement
- Every action through Gateway is intercepted
- Evaluated at the boundary **outside agent code**
- Consistent, reliable enforcement regardless of agent implementation

### Accessible Authoring
- Natural language prompts
- Cedar for fine-grained permissions
- Organization-wide consistency
- CloudWatch integration for logging and auditing

## Key Features

| Feature | Description |
|---------|-------------|
| **Policy Enforcement** | Intercepts and evaluates requests before tool access |
| **Access Controls** | Fine-grained based on user identity and tool input parameters |
| **Policy Authoring** | Cedar language + natural language support |
| **Policy Monitoring** | CloudWatch integration for evaluation monitoring |
| **Infrastructure Integration** | VPC security groups, AWS security infrastructure |
| **Audit Logging** | Detailed logs for compliance and troubleshooting |

## Integration

Integrates with AgentCore Gateway to intercept every tool call before execution. Define:
- Which tools agents can access
- What actions they can perform
- Under what conditions

## Status

**Preview** - Currently at no charge during preview.

## Pricing (Post-Preview)

Charged per 1,000 user input tokens for natural language policy conversion.
