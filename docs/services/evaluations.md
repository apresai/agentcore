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

The real submodule is `bedrock_agentcore.evaluation` (singular), exposing `EvaluationClient` - there is no `bedrock_agentcore.evaluations` module or `EvaluationsClient` class.

### Create Evaluator

```python
from bedrock_agentcore.evaluation import EvaluationClient

evals = EvaluationClient(region_name="us-east-1")

# Create a custom LLM-as-a-judge evaluator and wait for it to become ACTIVE
evaluator = evals.create_evaluator_and_wait(
    evaluatorName="helpfulness",
    level="TRACE",
    description="Evaluate if the response is helpful",
    evaluatorConfig={
        "llmAsAJudge": {
            "modelConfig": {
                "bedrockEvaluatorModelConfig": {
                    "modelId": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    "inferenceConfig": {"maxTokens": 500, "temperature": 1.0},
                }
            },
            "instructions": (
                "Score the response on helpfulness (1-5). "
                "Context: {context} Response: {assistant_turn}"
            ),
            "ratingScale": {
                "numerical": [
                    {"value": 1.0, "label": "Excellent", "definition": "Completely addresses the user's need"},
                    {"value": 0.5, "label": "Average", "definition": "Partially helpful"},
                    {"value": 0.0, "label": "Poor", "definition": "Not helpful at all"},
                ]
            },
        }
    },
)

evaluator_id = evaluator["evaluatorId"]
```

### Run Online Evaluation

```python
# Continuously sample and score production sessions
config = evals.create_online_evaluation_config_and_wait(
    onlineEvaluationConfigName="production_eval_config",
    description="Continuous evaluation of production agent",
    rule={"samplingConfig": {"samplingPercentage": 10.0}},
    dataSourceConfig={
        "cloudWatchLogs": {
            "logGroupNames": ["/aws/bedrock-agentcore/runtimes/my-agent-DEFAULT"],
            "serviceNames": ["my_agent.DEFAULT"],
        }
    },
    evaluators=[{"evaluatorId": "Builtin.Helpfulness"}, {"evaluatorId": evaluator_id}],
    evaluationExecutionRoleArn="arn:aws:iam::123456789012:role/AgentCoreEvaluationRole",
    enableOnCreate=True,
)

# Scores are automatically collected
# View in the CloudWatch GenAI Observability dashboard
```

### Run On-Demand Evaluation

`run()` collects spans for a session from CloudWatch and evaluates them - there is no `evaluate(trace_ids=...)` shortcut on the client itself:

```python
# Evaluate a specific agent session
results = evals.run(
    evaluator_ids=["Builtin.Helpfulness", evaluator_id],
    session_id="session-abc",
    agent_id="my-agent",
)

for result in results:
    print(f"Evaluator: {result['evaluatorId']}")
    print(f"  Score: {result.get('value')}")
    print(f"  Reasoning: {result.get('explanation')}")
```

### Compare Models

There is no `compare()` method - run the same evaluators against sessions produced by each model and compare the results yourself:

```python
results_a = evals.run(evaluator_ids=["Builtin.Helpfulness"], session_id="session-model-a", agent_id="my-agent")
results_b = evals.run(evaluator_ids=["Builtin.Helpfulness"], session_id="session-model-b", agent_id="my-agent")

avg_a = sum(r["value"] for r in results_a) / len(results_a)
avg_b = sum(r["value"] for r in results_b) / len(results_b)
print(f"Model A: {avg_a:.2f}, Model B: {avg_b:.2f}")
```

## Built-in Evaluators

Built-in evaluator IDs use a `Builtin.` prefix (e.g. `Builtin.Helpfulness`), not the bare names below:

| Evaluator ID | Description |
|--------------|-------------|
| `Builtin.Helpfulness` | Does the response address the user's need? |
| `Builtin.Correctness` | Is the information factually correct? |
| `Builtin.Coherence` | Is the response well-organized and clear? |
| `Builtin.Harmfulness` | Detects potentially harmful content |
| `Builtin.ResponseRelevance` | Does the response stay on topic? |

See the [detailed research](../../research/09-evaluations.md#built-in-evaluators) for the full list.

## Custom Evaluator Example

There is no `criteria=`/`scoring=` shorthand - a pass/fail evaluator is an `llmAsAJudge` config with a `categorical` rating scale instead of `numerical`:

```python
compliance_evaluator = evals.create_evaluator_and_wait(
    evaluatorName="financial-compliance",
    level="TRACE",
    description="Check financial advice compliance",
    evaluatorConfig={
        "llmAsAJudge": {
            "modelConfig": {
                "bedrockEvaluatorModelConfig": {
                    "modelId": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    "inferenceConfig": {"maxTokens": 500, "temperature": 1.0},
                }
            },
            "instructions": (
                "Evaluate whether the response follows financial compliance rules. "
                "PASS if it includes required disclaimers, does not guarantee returns, "
                "and recommends consulting a financial advisor. FAIL if it makes "
                "specific investment recommendations, promises specific returns, or "
                "is missing disclaimers. Context: {context} Response: {assistant_turn}"
            ),
            "ratingScale": {
                "categorical": [
                    {"label": "PASS", "definition": "Follows all financial compliance rules"},
                    {"label": "FAIL", "definition": "Violates one or more compliance rules"},
                ]
            },
        }
    },
)
```

## Framework Integration

There is no `strands.evaluations.AgentCoreEvaluator` or `langchain_agentcore.AgentCoreEvaluationCallback` - Strands and LangGraph agents don't need a framework-specific evaluation integration. Their OpenTelemetry/OpenInference traces are already converted to a unified span format under the hood, so any session from either framework can be evaluated the same way, once tracing is enabled (see [AgentCore Observability](observability.md)):

```python
from bedrock_agentcore.evaluation import EvaluationClient

evals = EvaluationClient(region_name="us-east-1")

# Works the same whether session-abc came from a Strands or LangGraph agent
results = evals.run(
    evaluator_ids=["Builtin.Helpfulness"],
    session_id="session-abc",
    agent_id="my-agent",
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
