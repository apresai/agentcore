"""
Configuration for this example.

All settings are environment-overridable and default to sensible values, so
this file runs standalone (no shared module, no secrets). boto3 reads AWS
credentials and AWS_BEARER_TOKEN_BEDROCK from the environment itself.
"""

import os

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = os.environ.get("AGENTCORE_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0")

# AWS managed Code Interpreter - no setup required
CODE_INTERPRETER_ID = os.environ.get("AGENTCORE_CODE_INTERPRETER_ID", "aws.codeinterpreter.v1")
SESSION_TIMEOUT_SECONDS = int(os.environ.get("AGENTCORE_SESSION_TIMEOUT_SECONDS", "900"))
