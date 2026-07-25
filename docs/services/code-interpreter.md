# Code Interpreter

> Secure sandbox environment for agents to execute code

## Overview

AgentCore Code Interpreter enables AI agents to write and execute code securely, enhancing their accuracy and expanding their ability to solve complex end-to-end tasks.

## Capabilities

```
┌─────────────────────────────────────────────────────────────────┐
│                    Code Interpreter                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Languages:  Python │ JavaScript │ TypeScript                   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Secure Sandbox                          │   │
│  │                                                          │   │
│  │  • Containerized execution                              │   │
│  │  • Isolated from your systems                           │   │
│  │  • Pre-installed libraries                              │   │
│  │  • Configurable network access                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  File Support:                                                  │
│  • Inline upload: up to 100MB                                   │
│  • S3 upload: up to 5GB                                         │
│  • Formats: CSV, Excel, JSON, and more                          │
│                                                                 │
│  Execution Time:                                                │
│  • Default: 15 minutes                                          │
│  • Maximum: 8 hours                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Specifications

| Feature | Value |
|---------|-------|
| **Languages** | Python, JavaScript, TypeScript |
| **Inline upload** | Up to 100MB |
| **S3 upload** | Up to 5GB |
| **Default timeout** | 15 minutes |
| **Maximum timeout** | 8 hours |
| **Network** | Configurable |

## Quick Start

There is no `bedrock_agentcore.code_interpreter` module or `CodeInterpreterClient`/`.execute()`/`.create_session()` - the real high-level class is `CodeInterpreter` in `bedrock_agentcore.tools`, with `start()`, `execute_code()`, `execute_command()`, `upload_file()`, and `install_packages()`. The constructor takes `region` as a positional argument.

### Execute Code

```python
from bedrock_agentcore.tools import CodeInterpreter

interpreter = CodeInterpreter("us-east-1")
interpreter.start()

try:
    result = interpreter.execute_code("""
import pandas as pd
import numpy as np

# Generate sample data
data = {'value': np.random.randn(100)}
df = pd.DataFrame(data)

# Calculate statistics
print(f"Mean: {df['value'].mean():.2f}")
print(f"Std:  {df['value'].std():.2f}")
""")

    for event in result["stream"]:
        for content in event.get("result", {}).get("content", []):
            if content["type"] == "text":
                print(content["text"])
finally:
    interpreter.stop()
```

### Process Files

```python
from bedrock_agentcore.tools import CodeInterpreter

interpreter = CodeInterpreter("us-east-1")
interpreter.start()

try:
    with open("data.csv", "rb") as f:
        interpreter.upload_file(path="data.csv", content=f.read())

    result = interpreter.execute_code("""
import pandas as pd

df = pd.read_csv('data.csv')
print(f"Rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(df.describe())
""")
finally:
    interpreter.stop()
```

### Large File Processing (S3)

`execute_code()` has no `input_s3_uri`/`output_s3_uri` parameter - files over the 100MB inline-upload limit are staged through S3 with shell commands inside the session (the session's execution role needs S3 read/write access):

```python
from bedrock_agentcore.tools import CodeInterpreter

interpreter = CodeInterpreter("us-east-1")
interpreter.start()

try:
    interpreter.execute_command(
        "aws s3 cp s3://my-bucket/large_dataset.parquet /tmp/large_dataset.parquet"
    )

    result = interpreter.execute_code("""
import pandas as pd

df = pd.read_parquet('/tmp/large_dataset.parquet')
summary = df.groupby('category').agg({'value': ['mean', 'sum']})
summary.to_csv('/tmp/summary.csv')
""")

    interpreter.execute_command("aws s3 cp /tmp/summary.csv s3://my-bucket/output/summary.csv")
finally:
    interpreter.stop()
```

## Use Cases

| Use Case | Example |
|----------|---------|
| **Data Analysis** | Analyze CSV, calculate statistics |
| **Calculations** | Complex math, financial models |
| **Visualization** | Generate charts and graphs |
| **File Processing** | Transform data formats |
| **Code Generation** | Generate and test code |

## Pre-installed Libraries

### Python
- pandas, numpy, scipy
- matplotlib, seaborn
- scikit-learn
- requests

### JavaScript/TypeScript
- lodash
- axios
- moment
- csv-parse

## Security Features

- Containerized isolation
- Ephemeral execution environment
- CloudTrail logging for audit
- No persistent state between executions

## Pricing

- CPU consumption + peak memory, per second

## Related

- [Detailed Research](../../research/05-code-interpreter.md)
- [Code Interpreter Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter.html)
