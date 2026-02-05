# AgentCore Code Interpreter Example

Demonstrates secure Python code execution using AWS Bedrock AgentCore Code Interpreter.

## What This Shows

- Starting a real Code Interpreter session on AWS
- Executing Python code in an isolated sandbox
- Getting results from the secure execution environment
- Proper session cleanup

## Prerequisites

- AWS account with Bedrock AgentCore access
- AWS credentials configured (`aws configure`)
- Python 3.10+

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Expected Output

```
============================================================
AgentCore Code Interpreter Demo
============================================================

[Step 1] Starting Code Interpreter session...
✓ Session started: ci-session-xxxxx

[Step 2] Executing Python code...
Code: Calculate statistics for sample data

[Step 3] Results from sandboxed execution:
----------------------------------------
Data Analysis Results:
  Sample size: 15
  Mean: 52.3
  Std Dev: 28.7
  Median: 55.0
  Min: 10, Max: 95
  Range: 85
----------------------------------------
Exit code: 0

[Bonus] Running a more complex calculation...
Investment Growth Calculator:
  Principal: $10,000.00
  Rate: 7.0% annually
  Time: 10 years
  Compounding: Monthly
  Final Amount: $20,096.61
  Interest Earned: $10,096.61

[Step 4] Cleaning up session...
✓ Session stopped

============================================================
Code Interpreter Benefits:
  • Secure sandbox: Code runs isolated from your systems
  • No setup: Use aws.codeinterpreter.v1 immediately
  • Multi-language: Python, JavaScript, TypeScript
  • Large files: Up to 5GB via S3 integration
  • Long running: Sessions up to 8 hours
============================================================
```

## Key Concepts

### AWS Managed Resource

This example uses `aws.codeinterpreter.v1` - the AWS managed Code Interpreter that requires no setup. Just start a session and execute code.

### Session Isolation

Each session runs in an isolated container:
- Separate filesystem
- Separate memory
- Automatic cleanup on session end

### Supported Languages

| Language | Use Case |
|----------|----------|
| Python | Data analysis, ML, calculations |
| JavaScript | JSON processing, web tasks |
| TypeScript | Type-safe scripting |

## Learn More

- [Code Interpreter Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter.html)
- [AgentCore Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples/)
