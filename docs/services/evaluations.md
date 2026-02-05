# Evaluations

> Automated quality assessment using LLM-as-a-Judge

**Status: Preview** (No charges during preview)

## Overview

AgentCore Evaluations provides purpose-built evaluation tools to measure how well agents perform tasks, handle edge cases, and maintain consistency. The service uses LLM-as-a-Judge techniques to provide measurable quality signals.

## Evaluation Types

```
┌─────────────────────────────────────────────────────────────────┐
│                    Evaluation Types                             │
├─────────────────────────────┬───────────────────────────────────┤
│         Online              │           On-Demand               │
│                             │                                   │
│  Real-time scoring of       │  Batch evaluation of              │
│  production responses       │  historical data                  │
│                             │                                   │
│  • Continuous monitoring    │  • Regression testing             │
│  • Immediate feedback       │  • Model comparison               │
│  • Quality gates            │  • Optimization cycles            │
└─────────────────────────────┴───────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Evaluator Types                              │
├─────────────────────────────┬───────────────────────────────────┤
│        Built-in             │           Custom                  │
│                             │                                   │
│  • Helpfulness              │  • Domain-specific                │
│  • Accuracy                 │  • Brand voice                    │
│  • Coherence                │  • Compliance                     │
│  • Safety                   │  • Business rules                 │
└─────────────────────────────┴───────────────────────────────────┘
```

## Quick Start

### Create Evaluator

```python
from bedrock_agentcore.evaluations import EvaluationsClient

evals = EvaluationsClient()

# Create custom evaluator
evaluator = evals.create_evaluator(
    name="helpfulness",
    description="Evaluate if the response is helpful",
    criteria="""
    Score the response on helpfulness (1-5):
    5: Completely addresses the user's need with actionable information
    4: Mostly helpful with minor gaps
    3: Partially helpful
    2: Minimally helpful
    1: Not helpful at all
    """,
    model_id="anthropic.claude-3-sonnet-20240229-v1:0"
)
```

### Run Online Evaluation

```python
# Enable online evaluation for agent
evals.enable_online_evaluation(
    agent_id="my-agent",
    evaluators=["helpfulness", "accuracy", "safety"],
    sample_rate=0.1  # Evaluate 10% of responses
)

# Scores are automatically collected
# View in Observability dashboard
```

### Run On-Demand Evaluation

```python
# Evaluate historical traces
results = evals.evaluate(
    agent_id="my-agent",
    evaluators=["helpfulness"],
    trace_ids=["trace-1", "trace-2", "trace-3"]
)

for result in results:
    print(f"Trace: {result.trace_id}")
    print(f"  Score: {result.score}/5")
    print(f"  Reasoning: {result.reasoning}")
```

### Compare Models

```python
# A/B test different models
results = evals.compare(
    agent_id="my-agent",
    test_cases=[
        {"input": "What is AgentCore?"},
        {"input": "How do I deploy an agent?"},
    ],
    models=[
        "anthropic.claude-3-sonnet-20240229-v1:0",
        "anthropic.claude-3-haiku-20240307-v1:0"
    ],
    evaluators=["helpfulness", "accuracy"]
)

# Results show which model performs better
```

## Built-in Evaluators

| Evaluator | Description |
|-----------|-------------|
| **Helpfulness** | Does the response address the user's need? |
| **Accuracy** | Is the information factually correct? |
| **Coherence** | Is the response well-organized and clear? |
| **Safety** | Is the response free from harmful content? |
| **Relevance** | Does the response stay on topic? |

## Custom Evaluator Example

```python
# Create compliance evaluator
compliance_evaluator = evals.create_evaluator(
    name="financial-compliance",
    description="Check financial advice compliance",
    criteria="""
    Evaluate if the response follows financial compliance rules:

    PASS if:
    - Includes required disclaimers
    - Does not guarantee returns
    - Recommends consulting a financial advisor

    FAIL if:
    - Makes specific investment recommendations
    - Promises specific returns
    - Missing disclaimers
    """,
    scoring="pass_fail"  # Binary scoring
)
```

## Framework Integration

### Strands

```python
from strands import Agent
from strands.evaluations import AgentCoreEvaluator

agent = Agent(
    model=model,
    evaluators=[
        AgentCoreEvaluator(
            evaluators=["helpfulness"],
            sample_rate=0.1
        )
    ]
)
```

### LangGraph

```python
from langchain_agentcore import AgentCoreEvaluationCallback

# Add as callback
app = workflow.compile()
response = app.invoke(
    {"messages": [...]},
    config={
        "callbacks": [
            AgentCoreEvaluationCallback(
                evaluators=["helpfulness"]
            )
        ]
    }
)
```

## Use Cases

| Use Case | Approach |
|----------|----------|
| Continuous quality monitoring | Online evaluation |
| Pre-deployment testing | On-demand batch |
| Model selection | Compare evaluations |
| Compliance checking | Custom evaluators |
| Regression detection | Scheduled on-demand |

## Pricing

**No charges during Preview.**

## Related

- [Detailed Research](../../research/09-evaluations.md)
- [Evaluations Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html)
