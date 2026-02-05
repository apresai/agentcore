# AgentCore Code Interpreter

## Quick Reference

### CLI Commands

| Command | Description |
|---------|-------------|
| `aws bedrock-agentcore create-code-interpreter` | Create a custom Code Interpreter resource |
| `aws bedrock-agentcore list-code-interpreters` | List all Code Interpreter resources |
| `aws bedrock-agentcore get-code-interpreter` | Get details of a Code Interpreter |
| `aws bedrock-agentcore delete-code-interpreter` | Delete a Code Interpreter resource |
| `aws bedrock-agentcore start-code-interpreter-session` | Start an execution session |
| `aws bedrock-agentcore stop-code-interpreter-session` | Stop an active session |

### SDK Clients

| Client | Service | Purpose |
|--------|---------|---------|
| `bedrock-agentcore-control` | Control Plane | Create, list, delete Code Interpreter resources |
| `bedrock-agentcore` | Data Plane | Start sessions, execute code, manage files |
| `CodeInterpreter` (high-level) | AgentCore SDK | Simplified session management |

### Key APIs (Data Plane)

| API | Description |
|-----|-------------|
| `StartCodeInterpreterSession` | Initialize an execution environment |
| `StopCodeInterpreterSession` | Terminate and release resources |
| `InvokeCodeInterpreter` | Execute operations (see invocation commands below) |

### Invocation Commands

| Command | Description |
|---------|-------------|
| `executeCode` | Run Python, JavaScript, or TypeScript code |
| `executeCommand` | Run terminal/shell commands |
| `startCommandExecution` | Start long-running command asynchronously |
| `getTask` | Check status of async command |
| `stopTask` | Cancel an async command |
| `writeFiles` | Write files to the session filesystem |
| `readFiles` | Read file contents |
| `listFiles` | List files in a directory |
| `removeFiles` | Delete files from session |

---

## Overview

The Amazon Bedrock AgentCore Code Interpreter enables AI agents to write and execute code securely in sandbox environments, enhancing accuracy and expanding ability to solve complex end-to-end tasks. In Agentic AI applications, agents may execute arbitrary code that can lead to data compromise or security risks. Code Interpreter provides secure, isolated execution within containerized environments.

### Why Use Code Interpreter

| Use Case | Description |
|----------|-------------|
| **Secure Execution** | Run code in isolated sandboxes without exposing sensitive data |
| **Mathematical Precision** | Solve computational problems requiring exact calculations |
| **Data Analysis** | Process CSV, Excel, JSON at scale (up to 5GB via S3) |
| **Complex Workflows** | Multi-step problem solving combining reasoning with computation |
| **Validation** | Verify agent outputs through actual code execution |

---

## Core Concepts

### Supported Languages

| Language | Runtime | Use Cases |
|----------|---------|-----------|
| Python | Pre-built with common libraries | Data analysis, ML, general computation |
| JavaScript | Node.js runtime | Web-related processing, JSON manipulation |
| TypeScript | Transpiled to JavaScript | Type-safe scripting |

Pre-installed libraries include NumPy, Pandas, Matplotlib, and other common data science packages. Additional packages can be installed via pip/npm during a session.

### File Handling

| Method | Size Limit | Description |
|--------|------------|-------------|
| Inline Upload | Up to 100 MB | Direct file content in API calls |
| S3 via Terminal | Up to 5 GB | Reference files from S3 using AWS CLI |

Files persist within a session and are automatically cleaned up when the session ends.

### Session Management

Sessions provide isolated execution environments with:

- **Session ID**: Unique identifier for the execution context
- **Session Timeout**: Configurable duration (default 15 minutes, max 8 hours)
- **State Persistence**: Variables and files persist across invocations within a session
- **Resource Isolation**: Each session runs in its own containerized environment

### Network Modes

| Mode | Description |
|------|-------------|
| `PUBLIC` | Full internet access for package installation and external APIs |
| `SANDBOX` | Restricted network access for enhanced security |

### Managed vs Custom Resources

| Resource Type | Identifier | Description |
|--------------|------------|-------------|
| AWS Managed | `aws.codeinterpreter.v1` | Default resource, no setup required |
| Custom | User-defined ID | Custom configuration with specific IAM role and network settings |

---

## CLI Reference

### Installation

The AWS CLI v2 includes AgentCore commands. Ensure you have the latest version:

```bash
aws --version
# aws-cli/2.x.x ...

# Update if needed
brew upgrade awscli  # macOS
```

### Create Code Interpreter

Create a custom Code Interpreter resource with specific configuration:

```bash
aws bedrock-agentcore create-code-interpreter \
  --region us-east-1 \
  --name "data-analysis-interpreter" \
  --description "Code Interpreter for data analysis tasks" \
  --network-configuration '{"networkMode": "PUBLIC"}' \
  --execution-role-arn "arn:aws:iam::123456789012:role/CodeInterpreterRole"
```

**Options:**

| Option | Required | Description |
|--------|----------|-------------|
| `--name` | Yes | Unique name for the resource |
| `--description` | No | Human-readable description |
| `--network-configuration` | Yes | Network mode: `PUBLIC` or `SANDBOX` |
| `--execution-role-arn` | Yes | IAM role for AWS resource access |

### List Code Interpreters

```bash
# List all Code Interpreters
aws bedrock-agentcore list-code-interpreters \
  --region us-east-1 \
  --max-results 10

# With pagination
aws bedrock-agentcore list-code-interpreters \
  --region us-east-1 \
  --max-results 10 \
  --next-token "eyJuZXh0VG9rZW4iOi..."
```

### Start Session

```bash
aws bedrock-agentcore start-code-interpreter-session \
  --region us-east-1 \
  --code-interpreter-id "aws.codeinterpreter.v1" \
  --name "analysis-session-001" \
  --description "Data analysis session" \
  --session-timeout-seconds 3600
```

**Options:**

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--code-interpreter-id` | Yes | - | Resource ID or `aws.codeinterpreter.v1` |
| `--name` | Yes | - | Session name |
| `--description` | No | - | Session description |
| `--session-timeout-seconds` | No | 900 | Session duration (max 28800) |

### Stop Session

```bash
aws bedrock-agentcore stop-code-interpreter-session \
  --region us-east-1 \
  --code-interpreter-id "aws.codeinterpreter.v1" \
  --session-id "session-abc123"
```

---

## SDK Reference

### AgentCore SDK (High-Level)

The `bedrock-agentcore` package provides a simplified interface for Code Interpreter operations.

#### Installation

```bash
pip install bedrock-agentcore boto3
```

#### Basic Usage

```python
from bedrock_agentcore.tools.code_interpreter_client import CodeInterpreter
import json

# Initialize client
code_client = CodeInterpreter('us-east-1')

# Start session
code_client.start()

try:
    # Execute code
    response = code_client.invoke("executeCode", {
        "language": "python",
        "code": 'print("Hello from Code Interpreter!")'
    })

    # Process streaming response
    for event in response["stream"]:
        print(json.dumps(event["result"], indent=2))
finally:
    # Always clean up
    code_client.stop()
```

#### Context Manager (Recommended)

```python
from bedrock_agentcore.tools.code_interpreter_client import code_session
import json

with code_session("us-east-1") as code_client:
    response = code_client.invoke("executeCode", {
        "language": "python",
        "code": """
import pandas as pd
data = {'name': ['Alice', 'Bob'], 'age': [30, 25]}
df = pd.DataFrame(data)
print(df.to_string())
"""
    })

    for event in response["stream"]:
        result = event.get("result", {})
        for content in result.get("content", []):
            if content["type"] == "text":
                print(content["text"])
```

### Boto3 Direct Access

For fine-grained control, use boto3 clients directly.

#### Control Plane Client

Manages Code Interpreter resources (create, list, delete):

```python
import boto3

# Control plane client for resource management
cp_client = boto3.client(
    'bedrock-agentcore-control',
    region_name='us-east-1'
)

# Create a custom Code Interpreter
response = cp_client.create_code_interpreter(
    name="my-interpreter",
    description="Custom interpreter for ML tasks",
    executionRoleArn="arn:aws:iam::123456789012:role/CodeInterpreterRole",
    networkConfiguration={
        "networkMode": "PUBLIC"
    }
)
print(f"Created: {response['codeInterpreterId']}")

# List all Code Interpreters
response = cp_client.list_code_interpreters()
for ci in response.get('codeInterpreterSummaries', []):
    print(f"  {ci['name']}: {ci['codeInterpreterId']}")
```

#### Data Plane Client

Manages sessions and executes code:

```python
import boto3
import json

# Data plane client for execution
dp_client = boto3.client(
    'bedrock-agentcore',
    region_name='us-east-1'
)

# Start session
session_response = dp_client.start_code_interpreter_session(
    codeInterpreterIdentifier="aws.codeinterpreter.v1",
    name="my-session",
    sessionTimeoutSeconds=1800
)
session_id = session_response["sessionId"]
print(f"Session started: {session_id}")

try:
    # Execute code
    exec_response = dp_client.invoke_code_interpreter(
        codeInterpreterIdentifier="aws.codeinterpreter.v1",
        sessionId=session_id,
        name="executeCode",
        arguments={
            "language": "python",
            "code": "print(sum(range(100)))"
        }
    )

    # Process streaming response
    for event in exec_response['stream']:
        if 'result' in event:
            result = event['result']
            for content in result.get('content', []):
                if content['type'] == 'text':
                    print(content['text'])

finally:
    # Stop session
    dp_client.stop_code_interpreter_session(
        codeInterpreterIdentifier="aws.codeinterpreter.v1",
        sessionId=session_id
    )
    print(f"Session stopped: {session_id}")
```

#### File Operations

```python
import boto3

dp_client = boto3.client('bedrock-agentcore', region_name='us-east-1')

# Assuming session_id is already obtained

# Write files
dp_client.invoke_code_interpreter(
    codeInterpreterIdentifier="aws.codeinterpreter.v1",
    sessionId=session_id,
    name="writeFiles",
    arguments={
        "content": [
            {"path": "data/input.csv", "text": "name,value\nA,100\nB,200"},
            {"path": "config.json", "text": '{"threshold": 150}'}
        ]
    }
)

# List files
response = dp_client.invoke_code_interpreter(
    codeInterpreterIdentifier="aws.codeinterpreter.v1",
    sessionId=session_id,
    name="listFiles",
    arguments={"directoryPath": "data"}
)

# Read files
response = dp_client.invoke_code_interpreter(
    codeInterpreterIdentifier="aws.codeinterpreter.v1",
    sessionId=session_id,
    name="readFiles",
    arguments={"paths": ["data/input.csv"]}
)

# Remove files
dp_client.invoke_code_interpreter(
    codeInterpreterIdentifier="aws.codeinterpreter.v1",
    sessionId=session_id,
    name="removeFiles",
    arguments={"paths": ["config.json"]}
)
```

#### Terminal Commands

```python
# Execute shell command (blocking)
response = dp_client.invoke_code_interpreter(
    codeInterpreterIdentifier="aws.codeinterpreter.v1",
    sessionId=session_id,
    name="executeCommand",
    arguments={"command": "pip install requests && pip list"}
)

# Execute long-running command (async)
response = dp_client.invoke_code_interpreter(
    codeInterpreterIdentifier="aws.codeinterpreter.v1",
    sessionId=session_id,
    name="startCommandExecution",
    arguments={"command": "python train_model.py"}
)
task_id = response["taskId"]

# Check task status
response = dp_client.invoke_code_interpreter(
    codeInterpreterIdentifier="aws.codeinterpreter.v1",
    sessionId=session_id,
    name="getTask",
    arguments={"taskId": task_id}
)

# Stop task if needed
dp_client.invoke_code_interpreter(
    codeInterpreterIdentifier="aws.codeinterpreter.v1",
    sessionId=session_id,
    name="stopTask",
    arguments={"taskId": task_id}
)
```

---

## Code Examples

### Example 1: Basic Python Execution

Simple code execution with result handling:

```python
from bedrock_agentcore.tools.code_interpreter_client import code_session
import json

def execute_python_code(code: str, region: str = "us-east-1") -> str:
    """Execute Python code and return the output."""
    with code_session(region) as client:
        response = client.invoke("executeCode", {
            "language": "python",
            "code": code
        })

        output_parts = []
        for event in response["stream"]:
            result = event.get("result", {})
            for content in result.get("content", []):
                if content["type"] == "text":
                    output_parts.append(content["text"])

        return "\n".join(output_parts)

# Usage
result = execute_python_code("""
import math

def calculate_compound_interest(principal, rate, time, n=12):
    '''Calculate compound interest with monthly compounding.'''
    amount = principal * (1 + rate/n) ** (n * time)
    return round(amount, 2)

# Calculate investment growth
principal = 10000
annual_rate = 0.07
years = 10

final_amount = calculate_compound_interest(principal, annual_rate, years)
print(f"Initial investment: ${principal:,}")
print(f"After {years} years at {annual_rate*100}% APR: ${final_amount:,}")
print(f"Total earnings: ${final_amount - principal:,}")
""")
print(result)
```

### Example 2: File Operations and Data Processing

Upload, process, and download data files:

```python
from bedrock_agentcore.tools.code_interpreter_client import code_session
import json
import base64

def analyze_csv_data(csv_content: str, region: str = "us-east-1") -> dict:
    """Upload CSV, analyze it, and return insights."""
    with code_session(region) as client:
        # Write the CSV file
        client.invoke("writeFiles", {
            "content": [{"path": "data.csv", "text": csv_content}]
        })

        # Analyze the data
        response = client.invoke("executeCode", {
            "language": "python",
            "code": """
import pandas as pd
import json

df = pd.read_csv('data.csv')

analysis = {
    'rows': len(df),
    'columns': list(df.columns),
    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
    'summary': df.describe().to_dict(),
    'missing_values': df.isnull().sum().to_dict(),
    'sample': df.head(3).to_dict(orient='records')
}

print(json.dumps(analysis, indent=2, default=str))
"""
        })

        # Extract the JSON result
        for event in response["stream"]:
            result = event.get("result", {})
            for content in result.get("content", []):
                if content["type"] == "text":
                    return json.loads(content["text"])

        return {}

# Usage
csv_data = """date,product,sales,region
2024-01-01,Widget A,150,North
2024-01-01,Widget B,200,South
2024-01-02,Widget A,175,North
2024-01-02,Widget B,180,South
2024-01-03,Widget A,160,East"""

insights = analyze_csv_data(csv_data)
print(f"Analyzed {insights['rows']} rows with columns: {insights['columns']}")
```

### Example 3: Data Visualization

Generate charts and retrieve as base64 images:

```python
from bedrock_agentcore.tools.code_interpreter_client import code_session
import json
import base64

def create_chart(data: dict, chart_type: str = "bar") -> bytes:
    """Generate a chart and return as PNG bytes."""
    with code_session("us-east-1") as client:
        # Write data file
        client.invoke("writeFiles", {
            "content": [{"path": "chart_data.json", "text": json.dumps(data)}]
        })

        # Generate chart
        response = client.invoke("executeCode", {
            "language": "python",
            "code": f"""
import matplotlib.pyplot as plt
import json
import base64
from io import BytesIO

with open('chart_data.json') as f:
    data = json.load(f)

fig, ax = plt.subplots(figsize=(10, 6))

if '{chart_type}' == 'bar':
    ax.bar(data['labels'], data['values'], color='steelblue')
elif '{chart_type}' == 'line':
    ax.plot(data['labels'], data['values'], marker='o', color='steelblue')
elif '{chart_type}' == 'pie':
    ax.pie(data['values'], labels=data['labels'], autopct='%1.1f%%')

ax.set_title(data.get('title', 'Chart'))
if '{chart_type}' != 'pie':
    ax.set_xlabel(data.get('xlabel', ''))
    ax.set_ylabel(data.get('ylabel', ''))
    plt.xticks(rotation=45, ha='right')

plt.tight_layout()

# Save to bytes
buffer = BytesIO()
plt.savefig(buffer, format='png', dpi=150)
buffer.seek(0)
img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
print(img_base64)
"""
        })

        # Extract base64 image
        for event in response["stream"]:
            result = event.get("result", {})
            for content in result.get("content", []):
                if content["type"] == "text":
                    return base64.b64decode(content["text"])

        return b""

# Usage
chart_data = {
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "values": [150, 220, 180, 290],
    "title": "Quarterly Sales",
    "xlabel": "Quarter",
    "ylabel": "Revenue ($K)"
}

png_bytes = create_chart(chart_data, "bar")
with open("quarterly_sales.png", "wb") as f:
    f.write(png_bytes)
```

### Example 4: Strands Agent Integration

Build an agent that uses Code Interpreter for validation:

```python
from strands import Agent
from strands_tools.code_interpreter import AgentCoreCodeInterpreter

# Initialize Code Interpreter tool
code_interpreter = AgentCoreCodeInterpreter(region="us-east-1")

# System prompt for validation-focused agent
SYSTEM_PROMPT = """You are an AI assistant that validates answers through code execution.

When asked about code, algorithms, calculations, or data:
1. Write Python code to verify your answers
2. Use the code interpreter to execute and validate
3. Show your reasoning and the execution results
4. If results differ from expectations, debug and explain

Always prefer computation over estimation for numerical questions."""

# Create agent with Code Interpreter
agent = Agent(
    tools=[code_interpreter.code_interpreter],
    system_prompt=SYSTEM_PROMPT
)

# Test prompts
prompts = [
    "What is the 50th Fibonacci number?",
    "Is 104729 a prime number?",
    "What's the standard deviation of [23, 45, 67, 89, 12, 34, 56]?"
]

for prompt in prompts:
    print(f"\n{'='*50}")
    print(f"Question: {prompt}")
    print(f"{'='*50}")
    response = agent(prompt)
    print(response.message["content"][0]["text"])
```

### Example 5: LangGraph Integration

Multi-step data analysis workflow with LangGraph:

```python
from langgraph.graph import StateGraph, END
from langchain_aws import ChatBedrockConverse
from bedrock_agentcore.tools.code_interpreter_client import code_session
from typing import TypedDict, Annotated
import operator
import json

class AnalysisState(TypedDict):
    """State for data analysis workflow."""
    data_path: str
    raw_data: str
    cleaned_data: str
    analysis_results: Annotated[list, operator.add]
    final_report: str
    errors: Annotated[list, operator.add]

def load_data(state: AnalysisState) -> dict:
    """Load and validate data from S3 or local path."""
    with code_session("us-east-1") as client:
        response = client.invoke("executeCode", {
            "language": "python",
            "code": f"""
import pandas as pd

# Load data (simulated for example)
data = '''date,metric,value
2024-01-01,revenue,1000
2024-01-02,revenue,1200
2024-01-03,revenue,950
2024-01-01,users,500
2024-01-02,users,550
2024-01-03,users,480'''

df = pd.read_csv(pd.io.common.StringIO(data))
print(df.to_csv(index=False))
"""
        })

        for event in response["stream"]:
            result = event.get("result", {})
            for content in result.get("content", []):
                if content["type"] == "text":
                    return {"raw_data": content["text"]}

    return {"errors": ["Failed to load data"]}

def clean_data(state: AnalysisState) -> dict:
    """Clean and preprocess data."""
    with code_session("us-east-1") as client:
        client.invoke("writeFiles", {
            "content": [{"path": "raw.csv", "text": state["raw_data"]}]
        })

        response = client.invoke("executeCode", {
            "language": "python",
            "code": """
import pandas as pd

df = pd.read_csv('raw.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.dropna()
df = df.sort_values(['date', 'metric'])
print(df.to_csv(index=False))
"""
        })

        for event in response["stream"]:
            result = event.get("result", {})
            for content in result.get("content", []):
                if content["type"] == "text":
                    return {"cleaned_data": content["text"]}

    return {"errors": ["Failed to clean data"]}

def analyze_trends(state: AnalysisState) -> dict:
    """Analyze trends in the data."""
    with code_session("us-east-1") as client:
        client.invoke("writeFiles", {
            "content": [{"path": "clean.csv", "text": state["cleaned_data"]}]
        })

        response = client.invoke("executeCode", {
            "language": "python",
            "code": """
import pandas as pd
import json

df = pd.read_csv('clean.csv')
df['date'] = pd.to_datetime(df['date'])

results = {}
for metric in df['metric'].unique():
    metric_df = df[df['metric'] == metric]
    results[metric] = {
        'mean': metric_df['value'].mean(),
        'std': metric_df['value'].std(),
        'trend': 'up' if metric_df['value'].iloc[-1] > metric_df['value'].iloc[0] else 'down',
        'change_pct': ((metric_df['value'].iloc[-1] - metric_df['value'].iloc[0]) / metric_df['value'].iloc[0] * 100)
    }

print(json.dumps(results, indent=2))
"""
        })

        for event in response["stream"]:
            result = event.get("result", {})
            for content in result.get("content", []):
                if content["type"] == "text":
                    return {"analysis_results": [json.loads(content["text"])]}

    return {"errors": ["Failed to analyze trends"]}

def generate_report(state: AnalysisState) -> dict:
    """Generate final analysis report."""
    results = state["analysis_results"][0] if state["analysis_results"] else {}

    report_lines = ["# Data Analysis Report\n"]
    for metric, stats in results.items():
        report_lines.append(f"## {metric.title()}")
        report_lines.append(f"- Average: {stats['mean']:.2f}")
        report_lines.append(f"- Std Dev: {stats['std']:.2f}")
        report_lines.append(f"- Trend: {stats['trend']} ({stats['change_pct']:.1f}%)")
        report_lines.append("")

    return {"final_report": "\n".join(report_lines)}

# Build the workflow graph
workflow = StateGraph(AnalysisState)

workflow.add_node("load", load_data)
workflow.add_node("clean", clean_data)
workflow.add_node("analyze", analyze_trends)
workflow.add_node("report", generate_report)

workflow.set_entry_point("load")
workflow.add_edge("load", "clean")
workflow.add_edge("clean", "analyze")
workflow.add_edge("analyze", "report")
workflow.add_edge("report", END)

# Compile and run
app = workflow.compile()

result = app.invoke({
    "data_path": "s3://my-bucket/data.csv",
    "raw_data": "",
    "cleaned_data": "",
    "analysis_results": [],
    "final_report": "",
    "errors": []
})

print(result["final_report"])
```

---

## Integration Patterns

### With AgentCore Runtime

Deploy agents with Code Interpreter as a serverless function:

```python
# agent_handler.py
from bedrock_agentcore.tools.code_interpreter_client import code_session
from strands import Agent
from strands_tools.code_interpreter import AgentCoreCodeInterpreter
import json

def handler(event, context):
    """Lambda handler for Code Interpreter agent."""

    # Initialize tools
    code_interpreter = AgentCoreCodeInterpreter(region="us-east-1")

    agent = Agent(
        tools=[code_interpreter.code_interpreter],
        system_prompt="You are a data analyst. Use code to analyze data accurately."
    )

    # Process request
    user_input = event.get("input", "")
    response = agent(user_input)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "response": response.message["content"][0]["text"]
        })
    }
```

Deploy to AgentCore Runtime:

```bash
agentcore create --name data-analyst-agent \
  --handler agent_handler.handler \
  --runtime python3.11 \
  --memory 512 \
  --timeout 300

agentcore deploy --name data-analyst-agent
```

### With AgentCore Gateway

Expose Code Interpreter as an MCP tool through Gateway:

```python
# Define MCP tool schema
tool_schema = {
    "name": "execute_analysis",
    "description": "Execute Python code for data analysis",
    "input_schema": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute"
            },
            "data": {
                "type": "string",
                "description": "Optional CSV data to analyze"
            }
        },
        "required": ["code"]
    }
}

# Gateway integration
from bedrock_agentcore.gateway import Gateway
from bedrock_agentcore.tools.code_interpreter_client import code_session

gateway = Gateway(region="us-east-1")

@gateway.tool("execute_analysis")
def execute_analysis(code: str, data: str = None) -> dict:
    """MCP tool for code execution."""
    with code_session("us-east-1") as client:
        if data:
            client.invoke("writeFiles", {
                "content": [{"path": "input.csv", "text": data}]
            })

        response = client.invoke("executeCode", {
            "language": "python",
            "code": code
        })

        output = []
        for event in response["stream"]:
            result = event.get("result", {})
            for content in result.get("content", []):
                if content["type"] == "text":
                    output.append(content["text"])

        return {"output": "\n".join(output)}
```

---

## Best Practices

### 1. Use Context Managers for Session Management

Always use `code_session` to ensure proper cleanup:

```python
# Good
with code_session("us-east-1") as client:
    client.invoke("executeCode", {"language": "python", "code": "..."})

# Bad - manual management risks resource leaks
client = CodeInterpreter("us-east-1")
client.start()
# If an exception occurs here, session is never stopped
client.stop()
```

### 2. Handle Streaming Responses Properly

Code execution results are streamed; always iterate through events:

```python
response = client.invoke("executeCode", {...})
for event in response["stream"]:
    result = event.get("result", {})
    if "content" in result:
        for item in result["content"]:
            if item["type"] == "text":
                print(item["text"])
            elif item["type"] == "error":
                handle_error(item)
```

### 3. Include Error Handling in Executed Code

Wrap code in try/except for graceful failure:

```python
code = """
try:
    import pandas as pd
    df = pd.read_csv('data.csv')
    result = df.describe().to_json()
    print(result)
except FileNotFoundError:
    print('{"error": "File not found"}')
except Exception as e:
    print(f'{{"error": "{str(e)}"}}')
"""
```

### 4. Optimize for Large Datasets

Use S3 for files over 100MB and process in chunks:

```python
code = """
import pandas as pd

# Process large CSV in chunks
chunks = pd.read_csv('s3://bucket/large-file.csv', chunksize=100000)
results = []
for chunk in chunks:
    results.append(chunk.groupby('category').sum())

final = pd.concat(results).groupby(level=0).sum()
print(final.to_csv())
"""
```

### 5. Set Appropriate Session Timeouts

Match timeout to expected workload:

```python
# Quick calculations: 5 minutes
dp_client.start_code_interpreter_session(
    sessionTimeoutSeconds=300,
    ...
)

# Data processing: 30 minutes
dp_client.start_code_interpreter_session(
    sessionTimeoutSeconds=1800,
    ...
)

# ML training: up to 8 hours
dp_client.start_code_interpreter_session(
    sessionTimeoutSeconds=28800,
    ...
)
```

### 6. Preserve State Across Invocations

Variables persist within a session; use this for multi-step workflows:

```python
# First invocation - load data
client.invoke("executeCode", {
    "language": "python",
    "code": "import pandas as pd; df = pd.read_csv('data.csv')"
})

# Second invocation - df is still available
client.invoke("executeCode", {
    "language": "python",
    "code": "print(df.describe())"
})
```

### 7. Clean Up Temporary Files

Remove files when no longer needed to free memory:

```python
# After processing
client.invoke("removeFiles", {
    "paths": ["temp.csv", "intermediate.json", "output/"]
})
```

### 8. Use Appropriate Network Mode

Choose based on security requirements:

- `PUBLIC`: When you need pip install, external API calls
- `SANDBOX`: For sensitive data processing, compliance requirements

### 9. Implement Idempotent Operations

Design code to handle retries safely:

```python
code = """
import os
output_file = 'result.json'

# Check if already processed
if os.path.exists(output_file):
    with open(output_file) as f:
        print(f.read())
else:
    # Process and save
    result = expensive_computation()
    with open(output_file, 'w') as f:
        json.dump(result, f)
    print(json.dumps(result))
"""
```

### 10. Monitor and Log Execution

Track execution for debugging and optimization:

```python
import time

start = time.time()
response = client.invoke("executeCode", {
    "language": "python",
    "code": code
})

execution_time = time.time() - start
print(f"Execution completed in {execution_time:.2f}s")

# Log to CloudWatch for observability
```

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `SessionNotFoundException` | Session expired or invalid ID | Start a new session; check timeout settings |
| `CodeExecutionTimeoutException` | Code exceeded execution limit | Optimize code or increase session timeout |
| `ResourceNotFoundException` | Invalid Code Interpreter ID | Use `aws.codeinterpreter.v1` or verify custom ID |
| `ValidationException` | Invalid parameters | Check language, code format, and required fields |
| `AccessDeniedException` | Missing IAM permissions | Add required permissions to execution role |
| `ServiceQuotaExceededException` | Too many concurrent sessions | Wait and retry; request quota increase |
| `ThrottlingException` | Rate limit exceeded | Implement exponential backoff |
| `InternalServerError` | AWS service issue | Retry with backoff; check AWS status |

### Debugging Tips

#### Enable Verbose Logging

```python
import logging
import boto3

# Enable boto3 debug logging
logging.basicConfig(level=logging.DEBUG)
boto3.set_stream_logger('botocore', logging.DEBUG)
```

#### Capture Full Response

```python
response = client.invoke("executeCode", {...})
full_response = []
for event in response["stream"]:
    full_response.append(event)
    print(json.dumps(event, indent=2, default=str))
```

#### Test Code Locally First

```python
# Test your code locally before sending to Code Interpreter
code = """
print("Hello World")
"""

# Local test
exec(code)

# Then send to Code Interpreter
client.invoke("executeCode", {"language": "python", "code": code})
```

#### Check Session State

```python
# List files to verify session state
response = client.invoke("listFiles", {"directoryPath": ""})
for event in response["stream"]:
    print(json.dumps(event, indent=2))
```

---

## Limits and Quotas

| Resource | Default Limit | Maximum | Notes |
|----------|--------------|---------|-------|
| Session timeout | 900 seconds (15 min) | 28,800 seconds (8 hours) | Configurable per session |
| Inline file size | 100 MB | 100 MB | Use S3 for larger files |
| S3 file size | 5 GB | 5 GB | Via terminal commands |
| Concurrent sessions | 10 per account | Adjustable | Request quota increase |
| Code execution timeout | 300 seconds | Session timeout | Per invocation |
| Memory per session | 512 MB | 4 GB | Depends on resource config |
| Max file path length | 255 characters | 255 characters | Standard filesystem limit |
| Max code size | 100 KB | 100 KB | Per invocation |

To request a quota increase, use the AWS Service Quotas console or contact AWS Support.

---

## Pricing

Code Interpreter uses consumption-based pricing with no upfront commitments.

### Billing Components

| Component | Billing Unit | Notes |
|-----------|--------------|-------|
| CPU | Per second of actual usage | Only charged during active execution |
| Memory | Per GB-second | Peak memory consumed per second |
| Minimum billing | 1 second, 128 MB | Per invocation |
| I/O wait | Free | No charge during idle/wait periods |

### Cost Optimization

- **I/O wait is free**: Agentic workloads typically spend 30-70% of time in I/O wait, which is not billed
- **No pre-allocation**: Pay only for actual compute consumed
- **Automatic scaling**: Resources scale with workload, no over-provisioning
- **Session management**: Stop sessions when not in use to avoid timeout charges

### Additional Costs

- **Data transfer**: Standard EC2 data transfer rates apply
- **S3 usage**: Standard S3 pricing for file storage
- **Model inference**: Separate charges for any Bedrock model calls

See [AgentCore Pricing](https://aws.amazon.com/bedrock/agentcore/pricing/) for current rates.

---

## Related Services

| Service | Relationship |
|---------|-------------|
| [AgentCore Runtime](./01-runtime.md) | Deploy agents with Code Interpreter as serverless functions |
| [AgentCore Gateway](./03-gateway.md) | Expose Code Interpreter as MCP tools |
| [AgentCore Memory](./02-memory.md) | Persist analysis results across sessions |
| [AgentCore Observability](./07-observability.md) | Monitor Code Interpreter execution |
| [AgentCore Browser](./06-browser.md) | Combine with Browser for web data extraction |

### External Links

- [Code Interpreter Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-tool.html)
- [API Reference](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-api-reference-examples.html)
- [GitHub Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples/)
- [AgentCore Pricing](https://aws.amazon.com/bedrock/agentcore/pricing/)
