# AgentCore Code Interpreter

## Overview

The Amazon Bedrock AgentCore Code Interpreter enables AI agents to write and execute code securely in sandbox environments, enhancing accuracy and expanding ability to solve complex end-to-end tasks.

## The Problem It Solves

In Agentic AI applications, agents may execute arbitrary code that can lead to data compromise or security risks. Code Interpreter provides secure, isolated execution.

## Key Features

### Secure Code Execution
- Containerized environment within Amazon Bedrock AgentCore
- Isolated sandbox execution
- Security maintained without compromising performance

### Supported Languages
- Python
- JavaScript
- TypeScript

### File Handling
- **Inline upload**: Up to 100 MB
- **S3 upload via terminal**: Up to 5 GB

### Execution Duration
- Default: 15 minutes
- Extended: Up to 8 hours

### Customization
- Session properties configuration
- Network modes for enterprise/security requirements

## Why Use Code Interpreter?

### Execute Code Securely
Perform complex workflows and data analysis while accessing internal data sources without exposing sensitive data.

### Extends Problem-Solving
- Solve computational problems difficult to address through reasoning alone
- Precise mathematical calculations
- Data processing at scale

### Handles Structured Data
- CSV, Excel, JSON processing
- Data cleaning and analysis

### Complex Workflows
- Multi-step problem solving combining reasoning with computation
- Iterative development and debugging

## Pre-built Runtimes

Code Interpreter comes with pre-built runtimes including:
- Advanced features
- Large file support
- Internet access
- CloudTrail logging

## Best Practices

1. Keep code snippets concise and focused
2. Use comments to document code
3. Optimize for performance with large datasets
4. Save intermediate results for complex operations
5. Use `code_session` context manager for proper cleanup
6. Include try/except blocks for error handling
7. Process results as streams
8. Clean up temporary files
9. Close sessions when done to release resources

## Pricing

Charged for:
- Actual CPU consumption
- Peak memory consumed (per second, 1-second minimum)
- 128MB minimum memory billing
- I/O wait and idle time is free
