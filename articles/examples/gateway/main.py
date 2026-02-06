#!/usr/bin/env python3
"""
AgentCore Gateway Example
=========================
Demonstrates: Creating a Gateway and understanding MCP tool integration

This example shows how to:
1. Create a Gateway resource
2. Wait for it to become active
3. Demonstrate the Gateway API structure
4. Clean up resources

Note: Adding Lambda targets requires additional setup (API key credential
providers, S3 buckets for schemas). See the full Gateway documentation
for production deployment patterns.

Prerequisites:
    pip install -r requirements.txt
    aws configure  # Set up AWS credentials with AgentCore access

Usage:
    python main.py

Expected output:
    ============================================================
    AgentCore Gateway Demo
    ============================================================

    [Step 1] Creating Gateway...
    ✓ Gateway created: demo-gateway-xxxxx
    ✓ Gateway is READY

    [Step 2] Gateway configuration:
    - Endpoint: https://xxxxx.gateway.bedrock-agentcore.us-east-1.amazonaws.com
    - Protocol: MCP
    - Auth: IAM

    [Step 3] Cleaning up...
    ✓ Gateway deleted

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
    """Main function demonstrating AgentCore Gateway."""

    print("=" * 60)
    print("AgentCore Gateway - The Babel Fish")
    print("=" * 60)
    print()
    print("  ~~ The Babel Fish of APIs ~~")
    print("  Translating any protocol to MCP so your")
    print("  agents can understand the Universe.")
    print()
    print('  "The Babel fish is small, yellow, leech-like, and')
    print('   probably the oddest thing in the Universe."')
    print()
    print("  Gateway does for APIs what the Babel Fish does for")
    print("  language: instant, universal translation.")

    region = os.getenv("AWS_REGION", "us-east-1")

    # Initialize clients
    control_client = boto3.client('bedrock-agentcore-control', region_name=region)
    iam_client = boto3.client('iam', region_name=region)
    sts_client = boto3.client('sts', region_name=region)

    account_id = sts_client.get_caller_identity()['Account']

    gateway_id = None
    role_name = f"agentcore-gateway-demo-{int(time.time())}"

    try:
        # Step 1: Create IAM role for Gateway
        print("\n[Step 1] Creating Gateway...")

        # Create trust policy for Gateway
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "bedrock-agentcore.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }

        try:
            role_response = iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Role for AgentCore Gateway demo'
            )
            role_arn = role_response['Role']['Arn']

            # Wait for role to propagate
            print("  Waiting for IAM role to propagate...")
            time.sleep(10)
        except iam_client.exceptions.EntityAlreadyExistsException:
            role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"

        print(f"✓ IAM role ready: {role_name}")

        # Create Gateway
        gateway_name = f"demo-gateway-{int(time.time())}"

        gateway_response = control_client.create_gateway(
            name=gateway_name,
            description="Babel Fish Gateway - universal protocol translator",
            roleArn=role_arn,
            authorizerType='NONE',  # No auth for demo (use IAM or JWT in production)
            protocolType='MCP'
        )

        gateway_id = gateway_response['gatewayId']
        print(f"✓ Gateway created: {gateway_id}")

        # Wait for Gateway to become active
        print("  Waiting for Gateway to become ready...")
        gateway_endpoint = None
        for i in range(60):  # Up to 2 minutes
            status_response = control_client.get_gateway(gatewayIdentifier=gateway_id)
            status = status_response['status']
            if status in ('ACTIVE', 'READY'):
                print(f"✓ Gateway is {status}")
                gateway_endpoint = status_response.get('gatewayUrl', 'N/A')
                break
            elif status == 'FAILED':
                raise Exception(f"Gateway creation failed: {status_response}")
            if i % 10 == 0 and i > 0:
                print(f"  Status: {status}...")
            time.sleep(2)
        else:
            raise Exception("Gateway did not become active within timeout")

        # Step 2: Display Gateway configuration
        print("\n[Step 2] Gateway configuration:")
        print(f"  - Gateway ID: {gateway_id}")
        print(f"  - Endpoint: {gateway_endpoint}")
        print(f"  - Protocol: MCP (Model Context Protocol)")
        print(f"  - Auth: None (demo) - use IAM or JWT in production")

        # Show what you would do next
        print("\n[Info] Next steps to add tools:")
        print("  1. Create a Lambda function or API endpoint")
        print("  2. Create an API Key credential provider (for external APIs)")
        print("  3. Add a Gateway Target with tool schema")
        print("  4. Invoke tools via MCP protocol")
        print("")
        print("  Example CLI commands:")
        print(f"    agentcore gateway create-mcp-gateway-target \\")
        print(f"        --gateway-id {gateway_id} \\")
        print(f"        --name MyTool \\")
        print(f"        --type lambda \\")
        print(f"        --lambda-arn <your-function-arn>")

        print("\n✓ Gateway working successfully!")

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
        # Step 3: Clean up resources
        print("\n[Step 3] Cleaning up...")

        # Delete Gateway and wait for deletion to complete
        if gateway_id:
            try:
                control_client.delete_gateway(gatewayIdentifier=gateway_id)
                # Wait for deletion to actually complete (API is async)
                for i in range(60):  # Up to 2 minutes
                    try:
                        status_response = control_client.get_gateway(gatewayIdentifier=gateway_id)
                        status = status_response['status']
                        if status in ('DELETED', 'FAILED'):
                            break
                        if i % 10 == 0:
                            print(f"  Waiting for gateway deletion (status: {status})...")
                        time.sleep(2)
                    except control_client.exceptions.ResourceNotFoundException:
                        break  # Gateway is gone
                    except Exception:
                        break
                print("✓ Gateway deleted")
            except Exception as e:
                print(f"  ⚠ Gateway cleanup failed: {e}")
                print(f"  Manual cleanup: aws bedrock-agentcore-control delete-gateway --gateway-identifier {gateway_id} --region {region}")

        # Delete IAM role
        try:
            iam_client.delete_role(RoleName=role_name)
            print("✓ IAM role deleted")
        except Exception as e:
            print(f"  IAM cleanup: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("Gateway Benefits (The Babel Fish Advantage):")
    print("  • Universal translation: Any API speaks MCP")
    print("  • Any backend: Lambda, REST, MCP servers, Smithy")
    print("  • Semantic search: Find tools by asking, not browsing")
    print("  • Built-in auth: OAuth, JWT, API keys - all handled")
    print("  • 1-click integrations: Salesforce, Slack, Jira, GitHub")
    print()
    print('  "It is of course well known that careless talk costs')
    print('   lives, but the full scale of the problem is not always')
    print('   appreciated." Use Gateway. Talk to any API.')
    print("=" * 60)


if __name__ == "__main__":
    main()
