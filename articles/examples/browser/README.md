# AgentCore Browser Example

Demonstrates secure, isolated browser sessions for AI agents using AWS Bedrock AgentCore.

## What This Shows

- Starting a browser session with AWS managed browser
- Getting WebSocket URLs for automation and live view
- Optional Playwright integration for browser control
- Proper session cleanup

## Prerequisites

- AWS account with Bedrock AgentCore access
- AWS credentials configured (`aws configure`)
- Python 3.10+
- (Optional) Playwright for browser automation

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Optional: Install Playwright browsers
playwright install chromium
```

## Run

```bash
python main.py
```

## Expected Output

```
============================================================
AgentCore Browser Demo
============================================================

[Step 1] Starting browser session...
✓ Session started: session-xxxxx
  Waiting for session to be ready...
✓ Session is READY

[Step 2] Session URLs:
  - Automation WebSocket: wss://xxxxx.browser.bedrock-agentcore...
  - Live View WebSocket: wss://xxxxx.browser.bedrock-agentcore...

[Step 3] Browser automation demo...
  Screenshot captured (12345 bytes)
✓ Page title: Example Domain

✓ Browser session working successfully!

[Step 4] Cleaning up session...
✓ Session stopped

============================================================
Browser Benefits:
  • Secure isolation: Each session runs in dedicated microVM
  • No setup: Use aws.browser.v1 immediately
  • Live view: Watch agents browse in real-time
  • Session recording: Full audit trail to S3
  • Playwright compatible: Use familiar automation tools
============================================================
```

## Key Concepts

### AWS Managed Browser

Use `aws.browser.v1` for instant access - no setup required:
- Public network access
- Default viewport (1920x1080)
- 15-minute default timeout

### WebSocket URLs

Each session provides two WebSocket endpoints:
- **Automation URL**: For Playwright/CDP control
- **Live View URL**: For real-time monitoring

### Playwright Integration

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp(automation_url)
    page = browser.contexts[0].pages[0]
    await page.goto('https://example.com')
```

### Session Recording

Create a custom browser for recording:
```bash
aws bedrock-agentcore-control create-browser \
    --name "recording-browser" \
    --network-configuration '{"networkMode": "PUBLIC"}' \
    --recording '{"enabled": true, "s3Location": {"bucket": "my-bucket"}}'
```

## Learn More

- [Browser Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser.html)
- [Playwright Docs](https://playwright.dev/python/)
- [AgentCore Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples/)
