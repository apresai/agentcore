# AgentCore Evaluations

> Automated assessment tools using LLM-as-a-Judge to measure agent quality, performance, and consistency across tasks and edge cases.

## Quick Reference

| Evaluator Type | ARN Format | Modifiable |
|----------------|------------|------------|
| Built-in | `arn:aws:bedrock-agentcore:::evaluator/Builtin.Helpfulness` | No |
| Custom | `arn:aws:bedrock-agentcore:region:account:evaluator/evaluator-id` | Yes |

| Evaluation Level | Scope | Use Case |
|------------------|-------|----------|
| `SESSION` | Entire conversation | Goal completion, overall quality |
| `TRACE` | Single agent turn | Response quality, helpfulness |
| `TOOL_CALL` | Individual tool invocation | Tool selection accuracy, parameter fidelity |

| Evaluation Mode | Description |
|-----------------|-------------|
| Online | Continuous monitoring of live production traffic |
| On-Demand | Targeted assessment of specific traces or sessions |

| CLI Command | Description |
|-------------|-------------|
| `agentcore eval evaluator create` | Create custom evaluator |
| `agentcore eval evaluator list` | List all evaluators |
| `agentcore eval online create` | Create online evaluation config |
| `agentcore eval run` | Run on-demand evaluation |

| SDK Client | Purpose |
|------------|---------|
| `bedrock-agentcore` (data plane) | Run evaluations, get results |
| `bedrock-agentcore-control` (control plane) | Create/manage evaluators and configs |

| Key API | Description |
|---------|-------------|
| `CreateEvaluator` | Create custom evaluator |
| `CreateOnlineEvaluationConfig` | Create online evaluation configuration |
| `Evaluate` | Run on-demand evaluation |
| `ListEvaluators` | List all evaluators |
| `GetEvaluator` | Get evaluator details |

---

## Overview

Amazon Bedrock AgentCore Evaluations provides automated assessment tools to measure how well your agent or tools perform specific tasks, handle edge cases, and maintain consistency across different inputs and contexts. The service enables data-driven optimization and ensures your agents meet quality standards before and after deployment.

AgentCore Evaluations integrates with popular agent frameworks including Strands and LangGraph with OpenTelemetry and OpenInference instrumentation libraries. Under the hood, traces from these agents are converted to a unified format and scored using LLM-as-a-Judge techniques for both built-in and custom evaluators.

---

## Core Concepts

### LLM-as-a-Judge

AgentCore Evaluations uses large language models (LLMs) to automatically assess the quality, correctness, or effectiveness of an agent's output. Instead of relying on manual review or rule-based checks, the LLM produces a score, label, or explanation based on the input and output being evaluated.

This approach enables:
- **Scalable assessments** across large numbers of agent interactions
- **Consistent scoring** using predefined criteria
- **Customizable evaluation** with domain-specific instructions
- **Reference-free evaluation** without requiring ground truth labels

### Evaluators

Evaluators are components that analyze agent traces and provide quantitative scores based on specific criteria. Each evaluator has:
- **Unique ARN** for identification and access control
- **Evaluation instructions** defining assessment criteria
- **Rating scale** (numerical or categorical)
- **Model configuration** specifying the judge model

### Evaluation Configurations

An evaluation configuration defines how your agent is evaluated, including:
- **Data source** (CloudWatch log groups or agent endpoint)
- **Evaluators to apply** (up to 10 per configuration)
- **Sampling rules** (percentage of sessions to evaluate)
- **Filters** (conditions for selecting sessions)

### Scoring

Evaluators produce structured results containing:
- **Value**: Numerical score (0.0 to 1.0)
- **Label**: Human-readable category (e.g., "Very Helpful", "Incorrect")
- **Explanation**: Reasoning for the assigned score
- **Token usage**: Input/output tokens consumed

---

## Evaluator Types

### Built-in Evaluators

Built-in evaluators are pre-configured options that use optimized evaluator models and prompt templates for common evaluation scenarios. They cannot be modified.

**Session-Level Evaluators:**

| Evaluator | ID | Description |
|-----------|-----|-------------|
| Goal Success Rate | `Builtin.GoalSuccessRate` | Assesses whether all user goals were achieved in the session |

**Trace-Level Evaluators:**

| Evaluator | ID | Description |
|-----------|-----|-------------|
| Coherence | `Builtin.Coherence` | Evaluates logical consistency and cohesion |
| Conciseness | `Builtin.Conciseness` | Measures efficiency of communication |
| Context Relevance | `Builtin.ContextRelevance` | Assesses relevance of context to the query |
| Correctness | `Builtin.Correctness` | Evaluates factual accuracy |
| Faithfulness | `Builtin.Faithfulness` | Checks consistency with conversation history |
| Harmfulness | `Builtin.Harmfulness` | Detects potentially harmful content |
| Helpfulness | `Builtin.Helpfulness` | Measures how helpful the response is |
| Instruction Following | `Builtin.InstructionFollowing` | Evaluates adherence to instructions |
| Refusal | `Builtin.Refusal` | Assesses appropriate refusal behavior |
| Response Relevance | `Builtin.ResponseRelevance` | Measures relevance to user query |
| Stereotyping | `Builtin.Stereotyping` | Detects stereotypical content |

**Tool-Level Evaluators:**

| Evaluator | ID | Description |
|-----------|-----|-------------|
| Tool Parameter Accuracy | `Builtin.ToolParameterAccuracy` | Evaluates correctness of tool parameters |
| Tool Selection Accuracy | `Builtin.ToolSelectionAccuracy` | Assesses whether correct tool was selected |

### Custom Evaluators

Custom evaluators allow you to define your own:
- **Evaluator model** (Bedrock foundation models)
- **Evaluation instructions** with domain-specific criteria
- **Rating scale** (numerical or categorical)
- **Inference parameters** (temperature, max tokens)

Custom evaluators are private to your account and can only be accessed by users who are explicitly granted access using IAM policies.

### Evaluator Configuration

Each custom evaluator requires:

```json
{
    "llmAsAJudge": {
        "modelConfig": {
            "bedrockEvaluatorModelConfig": {
                "modelId": "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
                "inferenceConfig": {
                   "maxTokens": 500,
                   "temperature": 1.0
                }
             }
        },
        "instructions": "Your evaluation instructions with {placeholders}",
        "ratingScale": {
            "numerical": [
                {"value": 1.0, "label": "Excellent", "definition": "..."},
                {"value": 0.5, "label": "Average", "definition": "..."},
                {"value": 0.0, "label": "Poor", "definition": "..."}
            ]
        }
    }
}
```

---

## Evaluation Modes

### Online Evaluation

Online evaluation continuously monitors your agent's quality using live production traffic. It provides:

**Continuous Performance Assessment:**
- Real-time monitoring across multiple evaluation criteria
- Aggregated scores displayed in dashboards
- Trend tracking over time
- Low-scoring session investigation

**Session Sampling and Filtering:**
- Percentage-based sampling (0.01% to 100%)
- Conditional filters to evaluate specific interactions
- Up to 5 filters per configuration

**Evaluator Protection:**
When an online evaluation configuration is enabled, custom evaluators are automatically locked:
- No modifications allowed to locked evaluators
- No deletion while any evaluation job is using the evaluator
- Clone a new evaluator if changes are needed

### On-Demand Evaluation

On-demand evaluation provides targeted assessments of specific agent interactions by directly analyzing chosen spans or traces. Use cases include:

- **Custom evaluator testing** before production deployment
- **Customer interaction investigation** for specific issues
- **Issue validation** after implementing fixes
- **Historical data analysis** for quality improvements
- **Early development lifecycle** evaluation

With on-demand evaluation, you specify exact spans or traces to evaluate by providing their IDs, then apply built-in or custom evaluators.

---

## SDK Reference

### AgentCore Starter Toolkit (High-Level SDK)

The starter toolkit provides a simplified interface for evaluations.

#### Installation

```bash
pip install bedrock-agentcore-starter-toolkit
```

#### Evaluation Client

```python
from bedrock_agentcore_starter_toolkit import Evaluation

eval_client = Evaluation()
```

#### Create Custom Evaluator

```python
import json

with open('custom_evaluator_config.json') as f:
    evaluator_config = json.load(f)

custom_evaluator = eval_client.create_evaluator(
    name="response_quality_evaluator",
    level="TRACE",
    description="Evaluates response quality",
    config=evaluator_config
)

print(f"Evaluator ID: {custom_evaluator['evaluatorId']}")
```

#### Create Online Evaluation

```python
config = eval_client.create_online_config(
    config_name="my_online_eval",
    agent_id="agent_myagent-ABC123xyz",
    sampling_rate=1.0,  # 1% of sessions
    evaluator_list=["Builtin.GoalSuccessRate", "Builtin.Helpfulness"],
    config_description="Production evaluation",
    auto_create_execution_role=True,
    enable_on_create=True
)

print(f"Config ID: {config['onlineEvaluationConfigId']}")
```

#### Run On-Demand Evaluation

```python
results = eval_client.run(
    agent_id="YOUR_AGENT_ID",
    session_id="YOUR_SESSION_ID",
    evaluators=["Builtin.Helpfulness", "Builtin.GoalSuccessRate"]
)

successful = results.get_successful_results()
failed = results.get_failed_results()

for result in successful:
    print(f"Evaluator: {result.evaluator_name}")
    print(f"Score: {result.value:.2f}")
    print(f"Label: {result.label}")
```

### boto3 Direct (Control Plane APIs)

For fine-grained control, use boto3 directly.

```python
import boto3

control_client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
data_client = boto3.client('bedrock-agentcore', region_name='us-east-1')
```

#### CreateEvaluator

```python
response = control_client.create_evaluator(
    evaluatorName="my_custom_evaluator",
    level="TRACE",
    description="Custom response quality evaluator",
    evaluatorConfig={
        "llmAsAJudge": {
            "modelConfig": {
                "bedrockEvaluatorModelConfig": {
                    "modelId": "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
                    "inferenceConfig": {
                        "maxTokens": 500,
                        "temperature": 1.0
                    }
                }
            },
            "instructions": "Evaluate the quality of the response. Context: {context} Response: {assistant_turn}",
            "ratingScale": {
                "numerical": [
                    {"value": 1.0, "label": "Excellent", "definition": "Outstanding quality"},
                    {"value": 0.5, "label": "Average", "definition": "Acceptable quality"},
                    {"value": 0.0, "label": "Poor", "definition": "Unacceptable quality"}
                ]
            }
        }
    }
)

evaluator_id = response['evaluatorId']
evaluator_arn = response['evaluatorArn']
```

#### CreateOnlineEvaluationConfig

```python
response = control_client.create_online_evaluation_config(
    onlineEvaluationConfigName="production_eval_config",
    description="Continuous evaluation of production agent",
    rule={
        "samplingConfig": {"samplingPercentage": 10.0}
    },
    dataSourceConfig={
        "cloudWatchLogs": {
            "logGroupNames": ["/aws/agentcore/my-agent"],
            "serviceNames": ["my_agent.DEFAULT"]
        }
    },
    evaluators=[
        {"evaluatorId": "Builtin.Helpfulness"},
        {"evaluatorId": "Builtin.GoalSuccessRate"}
    ],
    evaluationExecutionRoleArn="arn:aws:iam::123456789012:role/AgentCoreEvaluationRole",
    enableOnCreate=True
)

config_id = response['onlineEvaluationConfigId']
```

#### Evaluate (On-Demand)

```python
# With session spans
response = data_client.evaluate(
    evaluatorId="Builtin.Helpfulness",
    evaluationInput={"sessionSpans": session_span_logs}
)

# With specific trace targets
response = data_client.evaluate(
    evaluatorId="Builtin.Helpfulness",
    evaluationInput={"sessionSpans": session_span_logs},
    evaluationTarget={"traceIds": ["trace-id-1", "trace-id-2"]}
)

# With specific span targets (for tool-level evaluators)
response = data_client.evaluate(
    evaluatorId="Builtin.ToolSelectionAccuracy",
    evaluationInput={"sessionSpans": session_span_logs},
    evaluationTarget={"spanIds": ["span-id-1", "span-id-2"]}
)

for result in response['evaluationResults']:
    print(f"Score: {result['value']}, Label: {result['label']}")
```

#### ListEvaluators

```python
response = control_client.list_evaluators(maxResults=50)

for evaluator in response['evaluatorSummaries']:
    print(f"{evaluator['evaluatorName']}: {evaluator['evaluatorId']}")
```

#### GetEvaluator

```python
response = control_client.get_evaluator(evaluatorId="my-evaluator-id")

print(f"Name: {response['evaluatorName']}")
print(f"Level: {response['level']}")
print(f"Status: {response['status']}")
```

#### DeleteEvaluator

```python
control_client.delete_evaluator(evaluatorId="my-evaluator-id")
```

---

## Creating Custom Evaluators

### Evaluation Instructions

Instructions define how the LLM judge should evaluate agent performance. Include at least one placeholder that will be replaced with actual trace data.

**Session-Level Placeholders:**
- `{context}` - User prompts, assistant responses, and tool calls across all turns
- `{available_tools}` - Set of available tool calls with descriptions

**Trace-Level Placeholders:**
- `{context}` - All information from previous turns plus current turn's user prompt
- `{assistant_turn}` - The assistant response for the current turn

**Tool-Level Placeholders:**
- `{available_tools}` - Set of available tool calls with descriptions
- `{context}` - Previous turns plus current turn's user prompt and prior tool calls
- `{tool_turn}` - The tool call under evaluation

### Model Selection

Supported models for evaluation include Claude and other Bedrock foundation models. Use the global inference profile for cross-region support:

```
global.anthropic.claude-sonnet-4-5-20250929-v1:0
```

### Rating Scales

**Numerical Scale:**
```json
{
    "numerical": [
        {"value": 1.0, "label": "Excellent", "definition": "Outstanding quality"},
        {"value": 0.75, "label": "Good", "definition": "Above average quality"},
        {"value": 0.5, "label": "Average", "definition": "Acceptable quality"},
        {"value": 0.25, "label": "Poor", "definition": "Below average quality"},
        {"value": 0.0, "label": "Very Poor", "definition": "Unacceptable quality"}
    ]
}
```

**Categorical Scale:**
```json
{
    "categorical": [
        {"label": "Yes", "definition": "Criteria fully met"},
        {"label": "No", "definition": "Criteria not met"}
    ]
}
```

### Best Practices for Instructions

1. **Define role clearly** - Begin by establishing the judge model's role
2. **Use MECE approach** - Mutually Exclusive, Collectively Exhaustive criteria
3. **Include examples** - 1-3 relevant examples of expected evaluations
4. **Manage context** - Choose placeholders strategically based on requirements
5. **Keep scoring simple** - Start with binary scoring if uncertain
6. **Avoid output formatting** - The service adds standardization automatically

---

## Code Examples

### Example 1: Basic Evaluation Setup

```python
"""
Basic setup for evaluating an agent with built-in evaluators.
"""
from bedrock_agentcore_starter_toolkit import Evaluation

# Initialize evaluation client
eval_client = Evaluation()

# Run evaluation on a session
results = eval_client.run(
    agent_id="agent_customer-support-ABC123",
    session_id="session-uuid-12345",
    evaluators=[
        "Builtin.Helpfulness",
        "Builtin.Correctness",
        "Builtin.Conciseness"
    ]
)

# Process results
print(f"Evaluated {len(results.get_successful_results())} traces")

for result in results.get_successful_results():
    print(f"\n{result.evaluator_name}:")
    print(f"  Score: {result.value:.2f}")
    print(f"  Label: {result.label}")
    if result.explanation:
        print(f"  Reasoning: {result.explanation[:200]}...")
```

### Example 2: Custom Evaluator for Domain-Specific Criteria

```python
"""
Create a custom evaluator for evaluating a customer support agent
that should stay within its defined scope.
"""
import boto3
import json

client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

# Define custom evaluator configuration
evaluator_config = {
    "llmAsAJudge": {
        "modelConfig": {
            "bedrockEvaluatorModelConfig": {
                "modelId": "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
                "inferenceConfig": {
                    "maxTokens": 500,
                    "temperature": 1.0
                }
            }
        },
        "instructions": """You are evaluating whether a customer support agent stays within its defined scope.

The agent should ONLY answer questions about:
1. Order status and tracking
2. Return and refund policies
3. Product availability
4. Account management

Evaluate the assistant's response based on:
- Did the agent attempt to answer questions outside its scope?
- Did the agent appropriately redirect off-topic questions?
- Did the agent provide accurate information within its scope?

Context: {context}
Assistant Response: {assistant_turn}

Rate the response based on scope adherence and quality.""",
        "ratingScale": {
            "numerical": [
                {
                    "value": 1.0,
                    "label": "Excellent",
                    "definition": "Agent stayed within scope and provided accurate, helpful response"
                },
                {
                    "value": 0.75,
                    "label": "Good",
                    "definition": "Agent mostly stayed within scope with minor deviations"
                },
                {
                    "value": 0.5,
                    "label": "Acceptable",
                    "definition": "Agent partially addressed the query with some scope issues"
                },
                {
                    "value": 0.25,
                    "label": "Poor",
                    "definition": "Agent significantly deviated from its defined scope"
                },
                {
                    "value": 0.0,
                    "label": "Unacceptable",
                    "definition": "Agent completely ignored scope boundaries"
                }
            ]
        }
    }
}

# Create the evaluator
response = client.create_evaluator(
    evaluatorName="customer_support_scope_evaluator",
    level="TRACE",
    description="Evaluates whether customer support agent stays within defined scope",
    evaluatorConfig=evaluator_config
)

print(f"Created evaluator: {response['evaluatorId']}")
print(f"ARN: {response['evaluatorArn']}")
```

### Example 3: Online Evaluation Configuration

```python
"""
Set up continuous evaluation of a production agent with sampling and filtering.
"""
import boto3

client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

# Create online evaluation configuration
response = client.create_online_evaluation_config(
    onlineEvaluationConfigName="production_customer_support_eval",
    description="Continuous quality monitoring for customer support agent",
    rule={
        "samplingConfig": {
            "samplingPercentage": 10.0  # Evaluate 10% of sessions
        }
    },
    dataSourceConfig={
        "agentEndpoint": {
            "agentRuntimeId": "agent_customer-support-ABC123",
            "agentRuntimeEndpointName": "DEFAULT"
        }
    },
    evaluators=[
        {"evaluatorId": "Builtin.Helpfulness"},
        {"evaluatorId": "Builtin.Correctness"},
        {"evaluatorId": "Builtin.GoalSuccessRate"},
        {"evaluatorId": "customer_support_scope_evaluator"}  # Custom evaluator
    ],
    evaluationExecutionRoleArn="arn:aws:iam::123456789012:role/AgentCoreEvaluationRole",
    enableOnCreate=True
)

print(f"Created online evaluation config: {response['onlineEvaluationConfigId']}")
print(f"Status: {response['status']}")
print(f"Execution Status: {response['executionStatus']}")
```

### Example 4: On-Demand Evaluation with CloudWatch Logs

```python
"""
Download session spans from CloudWatch and run on-demand evaluation.
"""
import boto3
import json
import time
from datetime import datetime, timedelta

region = "us-east-1"
agent_id = "agent_myagent-ABC123xyz"
session_id = "test-session-12345"

def query_session_logs(log_group_name: str, session_id: str) -> list:
    """Query CloudWatch logs for session spans."""
    client = boto3.client('logs', region_name=region)

    start_time = datetime.now() - timedelta(hours=1)
    end_time = datetime.now()

    query = f"""
    fields @timestamp, @message
    | filter ispresent(scope.name) and ispresent(attributes.session.id)
    | filter attributes.session.id = "{session_id}"
    | sort @timestamp asc
    """

    query_id = client.start_query(
        logGroupName=log_group_name,
        startTime=int(start_time.timestamp()),
        endTime=int(end_time.timestamp()),
        queryString=query
    )['queryId']

    # Wait for query to complete
    while True:
        result = client.get_query_results(queryId=query_id)
        if result['status'] in ['Complete', 'Failed']:
            break
        time.sleep(1)

    if result['status'] == 'Failed':
        raise Exception("Query failed")

    # Extract messages as JSON
    spans = []
    for row in result['results']:
        for field in row:
            if field['field'] == '@message' and field['value'].strip().startswith('{'):
                spans.append(json.loads(field['value']))

    return spans

# Download spans from CloudWatch
log_group = f"/aws/bedrock-agentcore/runtimes/{agent_id}-DEFAULT"
session_spans = query_session_logs(log_group, session_id)
print(f"Downloaded {len(session_spans)} spans")

# Run evaluation
data_client = boto3.client('bedrock-agentcore', region_name=region)

response = data_client.evaluate(
    evaluatorId="Builtin.Helpfulness",
    evaluationInput={"sessionSpans": session_spans}
)

# Process results
for result in response['evaluationResults']:
    print(f"\nEvaluator: {result['evaluatorName']}")
    print(f"Score: {result['value']:.2f}")
    print(f"Label: {result['label']}")
    print(f"Trace ID: {result['context']['spanContext'].get('traceId', 'N/A')}")
```

### Example 5: CI/CD Integration for Agent Quality Gates

```python
"""
Integrate evaluations into CI/CD pipeline for quality gates.
"""
import boto3
import sys
from bedrock_agentcore_starter_toolkit import Evaluation

# Configuration
AGENT_ID = "agent_myagent-ABC123xyz"
TEST_SESSION_ID = "ci-test-session-12345"
QUALITY_THRESHOLD = 0.7  # Minimum acceptable score
REQUIRED_EVALUATORS = [
    "Builtin.Helpfulness",
    "Builtin.Correctness",
    "Builtin.GoalSuccessRate"
]

def run_quality_gate():
    """Run evaluation quality gate for CI/CD."""
    eval_client = Evaluation()

    print("Running agent quality evaluation...")
    print(f"Agent: {AGENT_ID}")
    print(f"Session: {TEST_SESSION_ID}")
    print(f"Threshold: {QUALITY_THRESHOLD}")

    # Run evaluation
    results = eval_client.run(
        agent_id=AGENT_ID,
        session_id=TEST_SESSION_ID,
        evaluators=REQUIRED_EVALUATORS
    )

    successful = results.get_successful_results()
    failed = results.get_failed_results()

    print(f"\nResults: {len(successful)} successful, {len(failed)} failed")

    # Check for evaluation failures
    if failed:
        print("\nEvaluation failures:")
        for f in failed:
            print(f"  - {f.evaluator_name}: {f.error_message}")
        return False

    # Check quality threshold
    all_passed = True
    for result in successful:
        status = "PASS" if result.value >= QUALITY_THRESHOLD else "FAIL"
        print(f"\n{result.evaluator_name}: {status}")
        print(f"  Score: {result.value:.2f} (threshold: {QUALITY_THRESHOLD})")
        print(f"  Label: {result.label}")

        if result.value < QUALITY_THRESHOLD:
            all_passed = False
            print(f"  Reason: {result.explanation[:150]}...")

    return all_passed

def main():
    """Main entry point for CI/CD."""
    try:
        passed = run_quality_gate()

        if passed:
            print("\n[SUCCESS] All quality gates passed!")
            sys.exit(0)
        else:
            print("\n[FAILURE] Quality gates failed!")
            sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] Evaluation failed: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
```

---

## Integration Patterns

### With AgentCore Observability

Evaluations integrate seamlessly with CloudWatch-based observability:

```python
"""
Set up agent with observability and evaluations.
"""
from strands import Agent
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure OpenTelemetry
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Create agent with instrumentation
model = BedrockModel(model_id="anthropic.claude-sonnet-4-20250514")
agent = Agent(model=model, system_prompt="You are a helpful assistant.")

app = BedrockAgentCoreApp()

@app.entrypoint()
async def main(request):
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("agent_invocation") as span:
        prompt = request.get("prompt", "")
        span.set_attribute("user.prompt", prompt)

        response = agent(prompt)
        span.set_attribute("agent.response_length", len(str(response)))

        return {"response": str(response)}

if __name__ == "__main__":
    app.run()
```

### With Agent Frameworks

**Strands Agent with Evaluations:**

```python
from strands import Agent
from strands.models import BedrockModel
from aws_opentelemetry_distro import AwsOpenTelemetryDistro

# Enable auto-instrumentation
AwsOpenTelemetryDistro().configure(
    service_name="my_strands_agent",
    exporter_endpoint="https://xray.us-east-1.amazonaws.com"
)

model = BedrockModel(model_id="anthropic.claude-sonnet-4-20250514")
agent = Agent(model=model, system_prompt="You are a helpful assistant.")

# Agent traces are automatically captured for evaluation
response = agent("What is the weather today?")
```

**LangGraph with OpenTelemetry:**

```python
from langgraph.graph import StateGraph
from langchain_aws import ChatBedrock
from opentelemetry.instrumentation.langchain import LangchainInstrumentor

# Enable LangChain instrumentation
LangchainInstrumentor().instrument()

# Build LangGraph agent
graph = StateGraph(AgentState)
# ... configure graph nodes and edges

agent = graph.compile()

# All traces are captured for evaluation
result = agent.invoke({"messages": [{"role": "user", "content": "Hello"}]})
```

---

## Best Practices

1. **Start with built-in evaluators** - Use built-in evaluators for common use cases before creating custom ones. They are optimized and well-tested.

2. **Choose appropriate evaluation levels** - Select TRACE for individual response quality, TOOL_CALL for tool usage accuracy, and SESSION for overall goal completion.

3. **Use sampling wisely** - Start with 10% sampling for production monitoring. Increase for critical agents or during development.

4. **Define clear evaluation criteria** - Use the MECE (Mutually Exclusive, Collectively Exhaustive) approach to ensure comprehensive coverage without overlap.

5. **Include examples in instructions** - Add 1-3 relevant examples showing expected evaluations to improve judge model accuracy.

6. **Monitor evaluator costs** - LLM-as-a-Judge consumes tokens. Balance evaluation coverage with cost by adjusting sampling rates.

7. **Implement quality gates** - Integrate evaluations into CI/CD pipelines to catch quality regressions before production.

8. **Review low-scoring sessions** - Use on-demand evaluation to investigate sessions that score below threshold.

9. **Version your evaluators** - Create new evaluators rather than modifying existing ones used in production. Lock prevents accidental changes.

10. **Combine online and on-demand** - Use online for continuous monitoring and on-demand for targeted investigation and testing.

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ValidationException` | Invalid evaluator config | Check ARN format, level, and instruction placeholders |
| `ResourceNotFoundException` | Evaluator not found | Verify evaluator ID and region |
| `AccessDeniedException` | Missing permissions | Add required IAM permissions for evaluations |
| `ConflictException` | Evaluator name exists | Use unique evaluator name in region |
| `ThrottlingException` | Token limit exceeded | Reduce sampling rate or evaluation frequency |
| `ServiceQuotaExceededException` | Too many active configs | Disable unused evaluation configs |
| `ModelAccessDenied` | Evaluator model not enabled | Enable model in Bedrock console |
| `InvalidPlaceholder` | Unknown placeholder in instructions | Use only supported placeholders for the level |

### Debugging Tips

```bash
# Check evaluator status
aws bedrock-agentcore-control get-evaluator --evaluator-id my-evaluator-id

# List online evaluation configs
aws bedrock-agentcore-control list-online-evaluation-configs

# Get evaluation config details
aws bedrock-agentcore-control get-online-evaluation-config \
    --online-evaluation-config-id config-id

# View evaluation results in CloudWatch
aws logs filter-log-events \
    --log-group-name /aws/agentcore/evaluations \
    --filter-pattern "evaluatorId"
```

### IAM Permissions

Required IAM policy for evaluation operations:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock-agentcore:Evaluate",
                "bedrock-agentcore-control:CreateEvaluator",
                "bedrock-agentcore-control:GetEvaluator",
                "bedrock-agentcore-control:ListEvaluators",
                "bedrock-agentcore-control:UpdateEvaluator",
                "bedrock-agentcore-control:DeleteEvaluator",
                "bedrock-agentcore-control:CreateOnlineEvaluationConfig",
                "bedrock-agentcore-control:GetOnlineEvaluationConfig",
                "bedrock-agentcore-control:ListOnlineEvaluationConfigs",
                "bedrock-agentcore-control:UpdateOnlineEvaluationConfig",
                "bedrock-agentcore-control:DeleteOnlineEvaluationConfig"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:StartQuery",
                "logs:GetQueryResults",
                "logs:FilterLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:log-group:/aws/agentcore/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": "arn:aws:bedrock:*::foundation-model/*"
        }
    ]
}
```

---

## Limits & Quotas

| Resource | Default Limit | Adjustable |
|----------|--------------|------------|
| Evaluation configurations per region | 1,000 | Yes |
| Active evaluation configurations | 100 | Yes |
| Evaluators per configuration | 10 | No |
| Input/output tokens per minute (large regions) | 1,000,000 | Yes |
| Filters per configuration | 5 | No |
| Sampling percentage | 0.01% - 100% | N/A |
| Session idle timeout | 1 - 60 minutes | N/A |
| Evaluation results per API call | 10 | No |
| Rating scale definitions | 20 | No |
| Evaluator instruction length | 10,000 characters | No |

---

## Pricing

**Status:** Preview - Offered at no charge during preview phase.

**General Availability Pricing:**

| Component | Pricing Model |
|-----------|---------------|
| Built-in evaluators | Per input/output tokens processed |
| Custom evaluators | Per evaluation + inference costs for model used |

Cost optimization tips:
- Use sampling to reduce evaluation volume
- Choose appropriate evaluation levels (SESSION is most efficient)
- Batch evaluations when possible
- Monitor token usage in CloudWatch

---

## Related Services

- [AgentCore Runtime](./01-runtime.md) - Deploy and run agents
- [AgentCore Memory](./02-memory.md) - Add conversation memory
- [AgentCore Gateway](./03-gateway.md) - Connect tools via MCP
- [AgentCore Observability](./08-observability.md) - Monitoring and tracing
- [AgentCore Policy](./07-policy.md) - Deterministic access control
- [Amazon CloudWatch](https://docs.aws.amazon.com/cloudwatch/) - Metrics, logs, and dashboards
