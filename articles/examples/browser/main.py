#!/usr/bin/env python3
"""
AgentCore Browser Example
=========================
Demonstrates: Secure, isolated browser sessions for AI agents

This example shows how to:
1. Start a browser session using AWS managed browser
2. Get WebSocket automation and live view URLs
3. Optionally connect with Playwright for automation
4. Clean up the session

Prerequisites:
    pip install -r requirements.txt
    aws configure  # Set up AWS credentials with AgentCore access

Usage:
    python main.py

Expected output:
    ============================================================
    AgentCore Browser Demo
    ============================================================

    [Step 1] Starting browser session...
    ✓ Session started: session-xxxxx
    ✓ Session is READY

    [Step 2] Session URLs:
    - Automation WebSocket: wss://...
    - Live View WebSocket: wss://...

    [Step 3] Navigating to example.com...
    ✓ Page title: Example Domain

    [Step 4] Cleaning up session...
    ✓ Session stopped

    ============================================================
"""

import os
import time
import asyncio
import boto3
from botocore.exceptions import ClientError

# Optional: load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def start_browser_session(client, browser_id: str, session_name: str) -> dict:
    """Start a browser session and wait for it to be ready."""

    response = client.start_browser_session(
        browserIdentifier=browser_id,
        name=session_name,
        sessionTimeoutSeconds=900  # 15 minutes
    )

    return response


def get_session_info(client, browser_id: str, session_id: str) -> dict:
    """Get session information including WebSocket URLs."""

    response = client.get_browser_session(
        browserIdentifier=browser_id,
        sessionId=session_id
    )

    return response


async def automate_with_playwright(automation_url: str) -> str:
    """Connect to browser session with Playwright and navigate to a page."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return "(Playwright not installed - skipping automation demo)"

    async with async_playwright() as p:
        # Connect to the remote browser via CDP
        browser = await p.chromium.connect_over_cdp(automation_url)

        # Get the default context and page
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()

        # Navigate to example.com
        await page.goto('https://example.com')

        # Get page title
        title = await page.title()

        # Take a screenshot (optional)
        screenshot = await page.screenshot()
        print(f"  Screenshot captured ({len(screenshot)} bytes)")

        await browser.close()

        return title


def main():
    """Main function demonstrating AgentCore Browser."""

    print("=" * 60)
    print("AgentCore Browser Demo")
    print("=" * 60)

    region = os.getenv("AWS_REGION", "us-east-1")

    # Initialize data plane client
    client = boto3.client('bedrock-agentcore', region_name=region)

    browser_id = "aws.browser.v1"  # AWS managed browser (no setup required)
    session_id = None

    try:
        # Step 1: Start browser session
        print("\n[Step 1] Starting browser session...")

        session_name = f"demo-session-{int(time.time())}"

        start_response = start_browser_session(client, browser_id, session_name)
        session_id = start_response['sessionId']
        print(f"✓ Session started: {session_id}")

        # Wait for session to be ready
        print("  Waiting for session to be ready...")
        automation_url = None
        live_view_url = None

        for i in range(60):  # Up to 2 minutes
            session_info = get_session_info(client, browser_id, session_id)
            status = session_info['status']

            if status in ('ACTIVE', 'READY'):
                print(f"✓ Session is {status}")
                # Get URLs from streams field
                streams = session_info.get('streams', {})
                automation_url = streams.get('automationStream', {}).get('streamEndpoint')
                live_view_url = streams.get('liveViewStream', {}).get('streamEndpoint')
                break
            elif status in ('FAILED', 'STOPPED'):
                raise Exception(f"Session failed: {session_info}")
            if i % 10 == 0 and i > 0:
                print(f"  Status: {status}...")
            time.sleep(2)
        else:
            raise Exception("Session did not become ready within timeout")

        # Step 2: Display session URLs
        print("\n[Step 2] Session URLs:")
        if automation_url:
            print(f"  - Automation WebSocket: {automation_url[:60]}...")
        else:
            print("  - Automation WebSocket: (not available)")
        if live_view_url:
            print(f"  - Live View WebSocket: {live_view_url[:60]}...")
        else:
            print("  - Live View WebSocket: (not available)")

        # Step 3: Optionally automate with Playwright
        print("\n[Step 3] Browser automation demo...")
        if automation_url:
            try:
                result = asyncio.run(automate_with_playwright(automation_url))
                print(f"✓ Page title: {result}")
            except Exception as e:
                print(f"  Automation note: {e}")
        else:
            print("  (No automation URL available)")

        print("\n✓ Browser session working successfully!")

        # Show what you can do with the session
        print("\n[Info] What you can do with browser sessions:")
        print("  • Connect with Playwright for programmatic control")
        print("  • Use Live View URL for real-time monitoring")
        print("  • Navigate, click, fill forms, take screenshots")
        print("  • Execute JavaScript in the browser context")
        print("  • Record sessions for audit and replay")

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
                client.stop_browser_session(
                    browserIdentifier=browser_id,
                    sessionId=session_id
                )
                print("✓ Session stopped")
            except Exception as cleanup_error:
                print(f"  Cleanup note: {cleanup_error}")

    # Summary
    print("\n" + "=" * 60)
    print("Browser Benefits:")
    print("  • Secure isolation: Each session runs in dedicated microVM")
    print("  • No setup: Use aws.browser.v1 immediately")
    print("  • Live view: Watch agents browse in real-time")
    print("  • Session recording: Full audit trail to S3")
    print("  • Playwright compatible: Use familiar automation tools")
    print("=" * 60)


if __name__ == "__main__":
    main()
