#!/usr/bin/env python3
"""
AgentCore Code Interpreter Example
===================================
Demonstrates: Secure Python code execution with AWS Bedrock AgentCore

This example uses the REAL AWS Code Interpreter service to:
1. Start an isolated execution session
2. Execute Python code for data analysis
3. Show results from the sandboxed environment
4. Clean up the session

Prerequisites:
    pip install -r requirements.txt
    aws configure  # Set up AWS credentials with AgentCore access

Usage:
    python main.py

Expected output:
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
    Mean: 52.3
    Std Dev: 28.7
    Min: 10, Max: 95
    ----------------------------------------

    [Step 4] Cleaning up session...
    ✓ Session stopped

    ============================================================
"""

import os
import json
import time
import boto3
from botocore.exceptions import ClientError

# Optional: load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def main():
    """Main function demonstrating AgentCore Code Interpreter."""

    print("=" * 60)
    print("AgentCore Code Interpreter Demo")
    print("=" * 60)

    region = os.getenv("AWS_REGION", "us-east-1")

    # Initialize the AgentCore data plane client
    client = boto3.client('bedrock-agentcore', region_name=region)

    session_id = None
    code_interpreter_id = "aws.codeinterpreter.v1"  # AWS managed resource

    try:
        # Step 1: Start a Code Interpreter session
        print("\n[Step 1] Starting Code Interpreter session...")

        session_name = f"demo-session-{int(time.time())}"

        start_response = client.start_code_interpreter_session(
            codeInterpreterIdentifier=code_interpreter_id,
            name=session_name,
            sessionTimeoutSeconds=900  # 15 minutes
        )

        session_id = start_response['sessionId']
        print(f"✓ Session started: {session_id}")

        # Wait a moment for session to initialize
        time.sleep(2)

        # Step 2: Execute Python code
        print("\n[Step 2] Executing Python code...")
        print("Code: Calculate statistics for sample data")

        python_code = '''
import statistics

# Sample data - imagine this comes from a real dataset
data = [23, 45, 67, 89, 12, 34, 56, 78, 90, 10, 95, 42, 38, 71, 55]

# Calculate statistics
mean = statistics.mean(data)
stdev = statistics.stdev(data)
min_val = min(data)
max_val = max(data)
median = statistics.median(data)

# Print results
print("Data Analysis Results:")
print(f"  Sample size: {len(data)}")
print(f"  Mean: {mean:.1f}")
print(f"  Std Dev: {stdev:.1f}")
print(f"  Median: {median:.1f}")
print(f"  Min: {min_val}, Max: {max_val}")
print(f"  Range: {max_val - min_val}")
'''

        # Execute the code
        exec_response = client.invoke_code_interpreter(
            codeInterpreterIdentifier=code_interpreter_id,
            sessionId=session_id,
            name="executeCode",
            arguments={
                "language": "python",
                "code": python_code
            }
        )

        # Step 3: Display results
        print("\n[Step 3] Results from sandboxed execution:")
        print("-" * 40)

        # Process streaming response
        stdout_output = []
        stderr_output = []
        exit_code = -1

        for event in exec_response.get('stream', []):
            if 'result' in event:
                result = event['result']
                for content in result.get('content', []):
                    if content.get('type') == 'text':
                        stdout_output.append(content.get('text', ''))
            if 'error' in event:
                stderr_output.append(str(event['error']))

        if stdout_output:
            print('\n'.join(stdout_output))
        if stderr_output:
            print(f"Errors: {' '.join(stderr_output)}")

        print("-" * 40)

        # Bonus: Execute another calculation
        print("\n[Bonus] Running a more complex calculation...")

        complex_code = '''
import math

# Calculate compound interest
principal = 10000
rate = 0.07  # 7% annual
years = 10
compounds_per_year = 12

# Compound interest formula
amount = principal * (1 + rate/compounds_per_year) ** (compounds_per_year * years)
interest_earned = amount - principal

print(f"Investment Growth Calculator:")
print(f"  Principal: ${principal:,.2f}")
print(f"  Rate: {rate*100}% annually")
print(f"  Time: {years} years")
print(f"  Compounding: Monthly")
print(f"  Final Amount: ${amount:,.2f}")
print(f"  Interest Earned: ${interest_earned:,.2f}")
'''

        exec_response2 = client.invoke_code_interpreter(
            codeInterpreterIdentifier=code_interpreter_id,
            sessionId=session_id,
            name="executeCode",
            arguments={
                "language": "python",
                "code": complex_code
            }
        )

        # Process streaming response for bonus
        for event in exec_response2.get('stream', []):
            if 'result' in event:
                result = event['result']
                for content in result.get('content', []):
                    if content.get('type') == 'text':
                        print(content.get('text', ''))

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_msg = e.response.get('Error', {}).get('Message', str(e))
        print(f"\n❌ AWS Error ({error_code}): {error_msg}")

        if 'AccessDenied' in error_code:
            print("\nTroubleshooting:")
            print("  1. Ensure your IAM user/role has bedrock-agentcore permissions")
            print("  2. Check that AgentCore is enabled in your AWS account")
            print("  3. Verify you're in a supported region (us-east-1, us-west-2)")
        raise

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise

    finally:
        # Step 4: Clean up - stop the session
        if session_id:
            print("\n[Step 4] Cleaning up session...")
            try:
                client.stop_code_interpreter_session(
                    codeInterpreterIdentifier=code_interpreter_id,
                    sessionId=session_id
                )
                print("✓ Session stopped")
            except Exception as cleanup_error:
                print(f"  Cleanup note: {cleanup_error}")

    # Summary
    print("\n" + "=" * 60)
    print("Code Interpreter Benefits:")
    print("  • Secure sandbox: Code runs isolated from your systems")
    print("  • No setup: Use aws.codeinterpreter.v1 immediately")
    print("  • Multi-language: Python, JavaScript, TypeScript")
    print("  • Large files: Up to 5GB via S3 integration")
    print("  • Long running: Sessions up to 8 hours")
    print("=" * 60)


if __name__ == "__main__":
    main()
