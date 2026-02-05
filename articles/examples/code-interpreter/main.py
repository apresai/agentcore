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
    print("AgentCore Code Interpreter - Deep Thought's Calculator")
    print("=" * 60)
    print()
    print('  "I checked it very thoroughly," said the computer,')
    print('  "and that quite definitely is the answer."')
    print()
    print("  Deep Thought computed for 7.5 million years.")
    print("  Code Interpreter does it in seconds.")

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
# ==============================================
# Deep Thought's Verification Calculations
# "The Answer is 42. Let me prove it."
# ==============================================

calculations = [
    ("6 * 7", 6 * 7),
    ("84 / 2", int(84 / 2)),
    ("2 * 3 * 7", 2 * 3 * 7),
    ("6 ** 2 + 6", 6 ** 2 + 6),
    ("126 / 3", int(126 / 3)),
]

print("Deep Thought Verification Results:")
print("=" * 42)  # 42 characters wide, naturally

all_42 = True
for expr, result in calculations:
    status = "CONFIRMED" if result == 42 else "ERROR"
    if result != 42:
        all_42 = False
    print(f"  {expr:>12} = {result:>4}  [{status}]")

print("=" * 42)
if all_42:
    print(f"  All {len(calculations)} calculations confirmed: The Answer is 42.")
else:
    print("  WARNING: The Universe may be broken.")

print()
print("  Fun fact: 42 is 101010 in binary.")
print(f"  Verified: bin(42) = {bin(42)}")
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
        print("\n[Bonus] The Question about six and nine...")

        complex_code = '''
# ==============================================
# The Question: What do you get if you multiply
# six by nine? (in base 13, that IS 42)
# ==============================================
import math

def base_convert(num, base):
    """Convert number to given base."""
    if num == 0:
        return "0"
    digits = []
    while num:
        digits.append(str(num % base))
        num //= base
    return "".join(reversed(digits))

# The famous "six by nine" calculation
result_base10 = 6 * 9  # = 54 in base 10
result_base13 = base_convert(42, 13)  # 42 in base 13

print("The Question & The Answer:")
print("-" * 42)
print(f"  6 x 9 = {result_base10} (base 10)")
print(f"  42 in base 13 = {result_base13}")
print(f"  {result_base13} in base 13 = 4*13 + 2 = {4*13 + 2} (base 10)")
print()
print("  As Douglas Adams said:")
print("  'I may be a sorry case, but I don\\'t write jokes in base 13.'")
print()
print(f"  Bonus: 42! has {len(str(math.factorial(42)))} digits")
print(f"  Bonus: 42 in binary = {bin(42)}")
print(f"  Bonus: 42 in hex = {hex(42)}")
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
    print("  • Secure sandbox - code runs in its own little universe")
    print("  • No setup - like the Guide, it just works")
    print("  • Multi-language - Python, JavaScript, TypeScript")
    print("  • Large files - up to 5GB (enough for the Guide's database)")
    print("  • 8-hour sessions - still faster than Deep Thought")
    print("=" * 60)


if __name__ == "__main__":
    main()
