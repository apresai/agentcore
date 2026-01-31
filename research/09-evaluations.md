# AgentCore Evaluations

## Overview

Amazon Bedrock AgentCore Evaluations provides automated assessment tools to measure how well agents or tools perform specific tasks, handle edge cases, and maintain consistency across different inputs and contexts.

## Purpose

- Data-driven optimization
- Ensure agents meet quality standards before and after deployment
- Measurable quality signals
- Structured insights for performance optimization

## How It Works

### Framework Integration
Integrates with:
- **Strands**
- **LangGraph**

With instrumentation libraries:
- **OpenTelemetry**
- **OpenInference**

### Scoring Mechanism
Traces are:
1. Converted to unified format
2. Scored using **LLM-as-a-Judge** techniques
3. Evaluated by built-in or custom evaluators

## Evaluator Types

### Built-in Evaluators
- Public and accessible to all users
- ARN format: `arn:aws:bedrock-agentcore:::evaluator/Builtin.Helpfulness`

### Custom Evaluators
- Private to your account
- Explicit access grants required
- ARN format: `arn:aws:bedrock-agentcore:region:account:evaluator/my-evaluator-id`

## Access Control

- IAM resource-based policies for evaluators and configurations
- IAM identity-based policies for users and roles

## Evaluation Modes

### Online Evaluation
Continuous assessment during agent operation.

### On-Demand Evaluation
Triggered assessments for specific test scenarios.

## Limits

- Up to **1,000 evaluation configurations** per region per account
- Up to **100 active** at any point in time
- Up to **1 million input/output tokens per minute** per account (large regions)

## Integration

All results integrated into AgentCore Observability powered by Amazon CloudWatch for unified monitoring.

## Status

**Preview** - Offered at no charge during preview phase.
