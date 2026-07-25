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

`BrowserClient` (`bedrock_agentcore.tools.browser_client`) manages session lifecycle only - it does not expose `navigate()`/`click()`/`fill()`/`screenshot()` methods itself. Automation happens by connecting a real browser-automation library (Playwright below) over CDP to the signed WebSocket URL the client hands you. The constructor takes `region` as a **positional** argument, not `region_name`.

### Start a Session

```python
from bedrock_agentcore.tools.browser_client import browser_session

# Context manager handles session lifecycle (start on enter, stop on exit)
with browser_session("us-east-1", identifier="aws.browser.v1", name="my-session") as client:
    # Automation and live-view WebSocket connections require SigV4-signed
    # headers - generate_ws_headers() returns the URL and headers together.
    ws_url, headers = client.generate_ws_headers()
    print(f"Session ID: {client.session_id}")
```

### Navigate and Interact (via Playwright)

```python
from bedrock_agentcore.tools.browser_client import browser_session
from playwright.sync_api import sync_playwright

with browser_session("us-east-1", identifier="aws.browser.v1") as client:
    ws_url, headers = client.generate_ws_headers()

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url, headers=headers)
        page = browser.contexts[0].pages[0]

        page.goto("https://example.com")
        page.click("button.submit")
        page.fill("input[name='email']", "user@example.com")
        page.fill("input[name='password']", "password123")

        screenshot = page.screenshot()
```

### Extract Data

```python
# Get page content
content = page.content()

# Execute JavaScript
result = page.evaluate("""
    Array.from(document.querySelectorAll('.product-price'))
        .map(el => el.textContent)
""")

# Get all links
links = page.eval_on_selector_all("a[href]", "els => els.map(el => el.href)")
```

### Enable Recording

Recording is configured on a **custom browser tool**, not per-session - the AWS managed `aws.browser.v1` tool never records:

```python
import uuid
from bedrock_agentcore.tools.browser_client import BrowserClient, browser_session

client = BrowserClient("us-east-1")

browser_tool = client.create_browser(
    name="my-recording-browser",
    description="Browser with session recording enabled",
    network_configuration={"networkMode": "PUBLIC"},
    recording={
        "enabled": True,
        "s3Location": {"bucket": "my-recordings-bucket", "prefix": "sessions"},
    },
    execution_role_arn="arn:aws:iam::123456789012:role/BrowserRole",
    client_token=str(uuid.uuid4()),
)

with browser_session("us-east-1", identifier=browser_tool["browserId"]) as recorded:
    ws_url, headers = recorded.generate_ws_headers()
    # ... do browser operations ...
# Recording uploads to S3 when the session stops.
```

## Playwright Integration

```python
from bedrock_agentcore.tools.browser_client import browser_session
from playwright.sync_api import sync_playwright

with browser_session("us-east-1", identifier="aws.browser.v1") as client:
    ws_url, headers = client.generate_ws_headers()

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url, headers=headers)
        page = browser.contexts[0].pages[0]
        page.goto("https://example.com")
        page.click("button")
```

## Other CDP-Compatible Frameworks

Any framework that can attach to a remote Chromium instance over CDP (BrowserUse, Selenium, etc.), not just Playwright, can connect using the same signed WebSocket URL and headers returned by `generate_ws_headers()` - there is no separate per-framework AgentCore API. Consult the framework's own docs for how it accepts a CDP endpoint and headers:

```python
from bedrock_agentcore.tools.browser_client import browser_session

with browser_session("us-east-1", identifier="aws.browser.v1") as client:
    ws_url, headers = client.generate_ws_headers()
    # Pass ws_url (+ headers, if the framework supports them) to whichever
    # CDP-compatible automation library you're using.
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
