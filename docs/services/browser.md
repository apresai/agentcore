# Browser

> Secure, isolated browser environment for web automation

## Overview

AgentCore Browser provides a managed browser runtime that enables AI agents to interact with web applications at scale. It runs in containerized environments, keeping web activity separate from your systems.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Your Agent                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │ WebSocket
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AgentCore Browser                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Isolated Browser Session                    │   │
│  │                                                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │ Navigate │  │   Fill   │  │  Click   │              │   │
│  │  │          │  │  Forms   │  │ Elements │              │   │
│  │  └──────────┘  └──────────┘  └──────────┘              │   │
│  │                                                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │Screenshot│  │ Extract  │  │  Execute │              │   │
│  │  │          │  │   Data   │  │    JS    │              │   │
│  │  └──────────┘  └──────────┘  └──────────┘              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │   Live View    │   Recording    │   CloudTrail Logs     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Specifications

| Feature | Value |
|---------|-------|
| **Session duration** | Up to 8 hours |
| **Default timeout** | 15 minutes |
| **Streaming** | WebSocket |
| **Frameworks** | Playwright, BrowserUse |
| **Recording** | DOM, actions, network |

## Key Features

| Feature | Description |
|---------|-------------|
| **Session Isolation** | Ephemeral container per session |
| **Live View** | Real-time monitoring of sessions |
| **Recording** | Capture DOM changes, actions, logs |
| **AWS Managed** | Reduced CAPTCHA interruptions |
| **Configurable** | Timeout, viewport, user agent |

## Quick Start

### Create Browser Session

```python
from bedrock_agentcore.browser import BrowserClient

browser = BrowserClient()

# Start session
session = browser.create_session(
    timeout_minutes=30,
    viewport={"width": 1920, "height": 1080}
)

print(f"Session ID: {session.session_id}")
print(f"Live View URL: {session.live_view_url}")
```

### Navigate and Interact

```python
# Navigate to URL
await session.navigate("https://example.com")

# Find and click element
await session.click("button.submit")

# Fill form
await session.fill("input[name='email']", "user@example.com")
await session.fill("input[name='password']", "password123")

# Take screenshot
screenshot = await session.screenshot()
```

### Extract Data

```python
# Get page content
content = await session.get_content()

# Execute JavaScript
result = await session.evaluate("""
    document.querySelectorAll('.product-price')
        .map(el => el.textContent)
""")

# Get all links
links = await session.query_selector_all("a[href]")
```

### Enable Recording

```python
# Create session with recording
session = browser.create_session(
    recording={
        "enabled": True,
        "s3_bucket": "my-recordings-bucket",
        "capture": ["dom", "actions", "network", "console"]
    }
)

# ... do browser operations ...

# Stop and save recording
recording_url = await session.stop_recording()
```

## Playwright Integration

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    # Connect to AgentCore Browser
    browser = await p.chromium.connect_over_cdp(
        session.cdp_url
    )

    page = browser.pages[0]
    await page.goto("https://example.com")
    await page.click("button")
```

## BrowserUse Integration

```python
from browser_use import Browser

# Configure to use AgentCore Browser
browser = Browser(
    endpoint=session.cdp_url
)

# Use with your agent
result = await browser.run(
    "Find the cheapest flight to New York"
)
```

## Use Cases

| Use Case | Description |
|----------|-------------|
| **Web Scraping** | Extract data from websites |
| **Form Automation** | Fill and submit forms |
| **Testing** | Automate web testing |
| **Research** | Gather information from web |
| **Monitoring** | Track website changes |

## Security Features

- Containerized isolation from your systems
- Ephemeral sessions (reset after each use)
- Automatic termination when TTL expires
- CloudTrail logging for audit
- No persistent cookies or data

## Pricing

- CPU consumption + peak memory, per second

## Related

- [Detailed Research](../../research/06-browser.md)
- [Browser Developer Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser.html)
