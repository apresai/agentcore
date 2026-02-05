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

### Execute Code

```python
from bedrock_agentcore.code_interpreter import CodeInterpreterClient

interpreter = CodeInterpreterClient()

# Execute Python code
result = interpreter.execute(
    code="""
import pandas as pd
import numpy as np

# Generate sample data
data = {'value': np.random.randn(100)}
df = pd.DataFrame(data)

# Calculate statistics
print(f"Mean: {df['value'].mean():.2f}")
print(f"Std:  {df['value'].std():.2f}")
""",
    language="python"
)

print(result.output)
```

### Process Files

```python
# Upload file for processing
session = interpreter.create_session()

# Upload CSV
session.upload_file(
    file_path="data.csv",
    file_name="data.csv"
)

# Process the file
result = session.execute(
    code="""
import pandas as pd

df = pd.read_csv('data.csv')
print(f"Rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(df.describe())
"""
)
```

### Large File Processing (S3)

```python
# For files > 100MB, use S3
result = interpreter.execute(
    code="""
import pandas as pd

# File is mounted from S3
df = pd.read_parquet('/data/large_dataset.parquet')
summary = df.groupby('category').agg({'value': ['mean', 'sum']})
summary.to_csv('/output/summary.csv')
""",
    input_s3_uri="s3://my-bucket/large_dataset.parquet",
    output_s3_uri="s3://my-bucket/output/"
)
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
