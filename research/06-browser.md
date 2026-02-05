# AgentCore Browser

> Secure, isolated browser environments for AI agents to interact with web applications, featuring session recording, live view, and WebSocket-based automation.

## Quick Reference

| CLI Command | Description |
|-------------|-------------|
| `aws bedrock-agentcore-control create-browser` | Create custom browser tool |
| `aws bedrock-agentcore-control get-browser` | Get browser tool details |
| `aws bedrock-agentcore-control list-browsers` | List all browser tools |
| `aws bedrock-agentcore-control delete-browser` | Delete browser tool |
| `aws bedrock-agentcore start-browser-session` | Start browser session |
| `aws bedrock-agentcore get-browser-session` | Get session details |
| `aws bedrock-agentcore stop-browser-session` | Stop browser session |
| `aws bedrock-agentcore list-browser-sessions` | List active sessions |

| SDK Client | Purpose |
|------------|---------|
| `BrowserClient` (AgentCore SDK) | High-level browser operations |
| `bedrock-agentcore` (data plane) | Session management, WebSocket streams |
| `bedrock-agentcore-control` (control plane) | Browser tool resource management |

| Key API | Description |
|---------|-------------|
| `CreateBrowser` | Create custom browser tool |
| `StartBrowserSession` | Launch browser session |
| `GetBrowserSession` | Get session info and WebSocket URLs |
| `StopBrowserSession` | Terminate browser session |
| `ListBrowserSessions` | List active sessions |

---

## Overview

Amazon Bedrock AgentCore Browser provides a secure, isolated browser environment for agents to interact with web applications. It runs in a containerized environment, keeping web activity separate from your system.

### Why Use Remote Browsers?

A remote browser runs in a separate environment, allowing AI agents to interact with the web as humans do:

- Navigate websites, fill forms, click buttons
- Parse dynamic content and JavaScript-rendered pages
- Serverless, auto-scaling infrastructure
- Visual understanding through screenshots
- Human intervention with live interactive view
- Session isolation for security
- Complex web application navigation
- Comprehensive audit capabilities through session recording

---

## Core Concepts

### Browser Tools

Browser Tools are the resource definitions that configure how browser sessions operate. There are two types:

#### AWS Managed Browser (`aws.browser.v1`)

The default system browser tool for quick setup:
- No configuration required
- Public network access
- Basic functionality
- No session recording

#### Custom Browser Tools

User-created browser tools with advanced features:
- Session recording to S3
- Custom network settings (VPC, security groups)
- Specific IAM execution roles
- Custom timeout configurations

### Sessions

Sessions are isolated browser instances created from Browser Tools:

- **Isolation**: Each session runs in a dedicated microVM with isolated CPU, memory, and filesystem
- **Ephemeral**: Sessions are temporary and reset after each use
- **Configurable timeout**: Default 15 minutes, maximum 8 hours
- **Concurrent sessions**: Up to 500 simultaneous sessions per account
- **Session data retention**: 30 days for session metadata

### WebSocket Streaming

Browser interaction uses WebSocket-based streaming APIs with two endpoints:

#### Automation Endpoint

For programmatic browser control:
- Navigate websites
- Click elements
- Fill out forms
- Take screenshots
- Execute JavaScript

Compatible with:
- **Strands** - Native AgentCore framework
- **Nova Act** - AWS visual automation
- **Playwright** - Popular browser automation library

#### Live View Endpoint

For real-time session monitoring:
- Watch agent actions as they happen
- Direct user interaction through the stream
- Human-in-the-loop capabilities
- Session debugging

### Session Recording

Recording captures all browser interactions for later analysis:

- **DOM changes** - All page modifications
- **User actions** - Clicks, typing, navigation
- **Console logs** - JavaScript console output
- **CDP events** - Chrome DevTools Protocol events
- **Network events** - HTTP requests and responses

Recordings stored in S3 include:
- Video playback with timeline navigation
- Page-by-page analysis
- User action tracking with click location details
- Comprehensive event logs

---

## CLI Reference

### Installation

The AgentCore Browser CLI commands are available through the AWS CLI with the bedrock-agentcore service.

```bash
# Ensure AWS CLI is installed and configured
aws --version

# Verify AgentCore service is available
aws bedrock-agentcore-control help
```

### create-browser

Create a custom browser tool with advanced features.

```bash
aws bedrock-agentcore-control create-browser [OPTIONS]
```

**Options:**

| Option | Description | Required |
|--------|-------------|----------|
| `--name` | Browser tool name (unique within account) | Yes |
| `--description` | Human-readable description | No |
| `--network-configuration` | Network mode and settings (JSON) | Yes |
| `--recording` | Session recording configuration (JSON) | No |
| `--execution-role-arn` | IAM role for S3/CloudWatch access | Conditional |
| `--region` | AWS region | No |

**Examples:**

```bash
# Basic browser with public network
aws bedrock-agentcore-control create-browser \
    --region us-east-1 \
    --name "my-browser" \
    --description "Browser for web automation" \
    --network-configuration '{"networkMode": "PUBLIC"}'

# Browser with session recording
aws bedrock-agentcore-control create-browser \
    --region us-east-1 \
    --name "recording-browser" \
    --description "Browser with session recording" \
    --network-configuration '{"networkMode": "PUBLIC"}' \
    --recording '{
        "enabled": true,
        "s3Location": {
            "bucket": "my-session-recordings",
            "prefix": "browser-sessions"
        }
    }' \
    --execution-role-arn "arn:aws:iam::123456789012:role/BrowserRecordingRole"

# Browser with VPC configuration
aws bedrock-agentcore-control create-browser \
    --region us-east-1 \
    --name "vpc-browser" \
    --network-configuration '{
        "networkMode": "VPC",
        "securityGroupIds": ["sg-12345678"],
        "subnetIds": ["subnet-12345678", "subnet-87654321"]
    }'
```

### get-browser

Get details about a browser tool.

```bash
aws bedrock-agentcore-control get-browser \
    --region us-east-1 \
    --browser-id <browser-id>
```

**Response includes:**
- Browser ARN and ID
- Status (CREATING, ACTIVE, FAILED)
- Network configuration
- Recording settings
- Creation timestamp

### list-browsers

List all browser tools in the account.

```bash
aws bedrock-agentcore-control list-browsers \
    --region us-east-1 \
    --max-results 50
```

### delete-browser

Delete a browser tool.

```bash
aws bedrock-agentcore-control delete-browser \
    --region us-east-1 \
    --browser-id <browser-id>
```

### start-browser-session

Start a new browser session.

```bash
aws bedrock-agentcore start-browser-session [OPTIONS]
```

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--browser-id` | Browser tool ID (use `aws.browser.v1` for managed) | Required |
| `--session-name` | Human-readable session name | Auto-generated |
| `--session-timeout-seconds` | Session timeout (60-28800) | 900 (15 min) |
| `--viewport-width` | Browser viewport width | 1920 |
| `--viewport-height` | Browser viewport height | 1080 |

**Examples:**

```bash
# Start session with managed browser
aws bedrock-agentcore start-browser-session \
    --region us-east-1 \
    --browser-id aws.browser.v1 \
    --session-name "web-research-session" \
    --session-timeout-seconds 1800

# Start session with custom viewport
aws bedrock-agentcore start-browser-session \
    --region us-east-1 \
    --browser-id br-abc123xyz \
    --session-name "mobile-testing" \
    --viewport-width 375 \
    --viewport-height 812

# Start extended session (8 hours)
aws bedrock-agentcore start-browser-session \
    --region us-east-1 \
    --browser-id br-abc123xyz \
    --session-timeout-seconds 28800
```

### get-browser-session

Get session details including WebSocket URLs.

```bash
aws bedrock-agentcore get-browser-session \
    --region us-east-1 \
    --browser-id <browser-id> \
    --session-id <session-id>
```

**Response includes:**
- Session status (STARTING, ACTIVE, STOPPING, STOPPED)
- Automation stream URL (WebSocket)
- Live view stream URL (WebSocket)
- Viewport dimensions
- Creation and update timestamps

### stop-browser-session

Stop an active browser session.

```bash
aws bedrock-agentcore stop-browser-session \
    --region us-east-1 \
    --browser-id <browser-id> \
    --session-id <session-id>
```

### list-browser-sessions

List sessions for a browser tool.

```bash
aws bedrock-agentcore list-browser-sessions \
    --region us-east-1 \
    --browser-id <browser-id> \
    --max-results 50
```

---

## SDK Reference

### Using AgentCore SDK (Recommended)

The high-level `BrowserClient` provides a simplified interface for browser operations.

```python
from bedrock_agentcore.tools.browser_client import BrowserClient

# Initialize client
client = BrowserClient(region_name='us-east-1')
```

#### Start Session with Context Manager

```python
from bedrock_agentcore.tools.browser_client import BrowserClient

async def browse_website():
    client = BrowserClient(region_name='us-east-1')

    # Context manager handles session lifecycle
    async with client.start_session(
        browser_id='aws.browser.v1',
        session_name='my-session',
        timeout_seconds=1800,
        viewport={'width': 1920, 'height': 1080}
    ) as session:
        # Get automation WebSocket URL
        automation_url = session.automation_stream_url

        # Connect with Playwright
        browser = await playwright.chromium.connect_over_cdp(automation_url)
        page = browser.contexts[0].pages[0]

        await page.goto('https://example.com')
        screenshot = await page.screenshot()

        return screenshot
    # Session automatically stopped on exit
```

#### Manual Session Management

```python
from bedrock_agentcore.tools.browser_client import BrowserClient

client = BrowserClient(region_name='us-east-1')

# Start session
session = client.start_browser_session(
    browser_id='br-abc123xyz',
    session_name='manual-session',
    timeout_seconds=900
)

session_id = session['sessionId']
automation_url = session['automationStreamUrl']
live_view_url = session['liveViewStreamUrl']

# ... perform browser operations ...

# Stop session when done
client.stop_browser_session(
    browser_id='br-abc123xyz',
    session_id=session_id
)
```

#### Create Custom Browser

```python
import uuid
from bedrock_agentcore.tools.browser_client import BrowserClient

client = BrowserClient(region_name='us-east-1')

# Create browser with recording
browser = client.create_browser(
    name='my-recording-browser',
    description='Browser with session recording enabled',
    network_configuration={'networkMode': 'PUBLIC'},
    recording={
        'enabled': True,
        's3Location': {
            'bucket': 'my-recordings-bucket',
            'prefix': 'sessions'
        }
    },
    execution_role_arn='arn:aws:iam::123456789012:role/BrowserRole',
    client_token=str(uuid.uuid4())
)

browser_id = browser['browserId']
```

#### Live View Server

```python
from bedrock_agentcore.tools.browser_client import BrowserClient

async def start_live_view(browser_id: str, session_id: str, port: int = 8080):
    """Start local server for live view."""
    client = BrowserClient(region_name='us-east-1')

    session = client.get_browser_session(
        browser_id=browser_id,
        session_id=session_id
    )

    live_view_url = session['liveViewStreamUrl']

    # Start viewer server
    await client.start_viewer_server(
        live_view_url=live_view_url,
        port=port
    )

    print(f"Live view available at http://localhost:{port}")
```

### Using boto3 Directly

For lower-level control, use boto3 clients directly.

```python
import boto3

# Control plane - manage browser resources
control_client = boto3.client(
    'bedrock-agentcore-control',
    region_name='us-east-1'
)

# Data plane - manage sessions
data_client = boto3.client(
    'bedrock-agentcore',
    region_name='us-east-1'
)
```

#### Control Plane APIs

##### CreateBrowser

```python
import uuid

response = control_client.create_browser(
    name='production-browser',
    description='Production browser for web automation',
    networkConfiguration={
        'networkMode': 'PUBLIC'
    },
    recording={
        'enabled': True,
        's3Location': {
            'bucket': 'session-recordings-123456789012',
            'prefix': 'production'
        }
    },
    executionRoleArn='arn:aws:iam::123456789012:role/BrowserExecutionRole',
    clientToken=str(uuid.uuid4()),
    tags={
        'Environment': 'production',
        'Team': 'ai-agents'
    }
)

browser_id = response['browserId']
browser_arn = response['browserArn']
status = response['status']  # CREATING, ACTIVE, FAILED
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Unique browser name |
| `networkConfiguration` | object | Yes | Network mode and settings |
| `description` | string | No | Human-readable description |
| `recording` | object | No | Recording configuration |
| `executionRoleArn` | string | Conditional | Required for recording |
| `clientToken` | string | No | Idempotency token |
| `tags` | dict | No | Resource tags |

##### GetBrowser

```python
response = control_client.get_browser(
    browserId='br-abc123xyz'
)

print(f"Status: {response['status']}")
print(f"ARN: {response['browserArn']}")
print(f"Network: {response['networkConfiguration']}")
print(f"Recording: {response.get('recording', 'Not configured')}")
```

##### ListBrowsers

```python
response = control_client.list_browsers(
    maxResults=50
)

for browser in response['browserSummaries']:
    print(f"{browser['name']}: {browser['status']}")
```

##### DeleteBrowser

```python
control_client.delete_browser(
    browserId='br-abc123xyz'
)
```

#### Data Plane APIs

##### StartBrowserSession

```python
response = data_client.start_browser_session(
    browserId='br-abc123xyz',
    sessionName='automation-session',
    sessionTimeoutSeconds=1800,
    viewportWidth=1920,
    viewportHeight=1080
)

session_id = response['sessionId']
automation_url = response['automationStreamUrl']
live_view_url = response['liveViewStreamUrl']
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `browserId` | string | Yes | Browser tool ID |
| `sessionName` | string | No | Session name |
| `sessionTimeoutSeconds` | int | No | Timeout (60-28800), default 900 |
| `viewportWidth` | int | No | Viewport width, default 1920 |
| `viewportHeight` | int | No | Viewport height, default 1080 |

##### GetBrowserSession

```python
response = data_client.get_browser_session(
    browserId='br-abc123xyz',
    sessionId='sess-xyz789'
)

status = response['status']  # STARTING, ACTIVE, STOPPING, STOPPED
automation_url = response['automationStreamUrl']
live_view_url = response['liveViewStreamUrl']
viewport = response['viewport']
```

##### StopBrowserSession

```python
data_client.stop_browser_session(
    browserId='br-abc123xyz',
    sessionId='sess-xyz789'
)
```

##### ListBrowserSessions

```python
response = data_client.list_browser_sessions(
    browserId='br-abc123xyz',
    maxResults=50
)

for session in response['sessionSummaries']:
    print(f"{session['sessionId']}: {session['status']}")
```

---

## Browser Tool Types

### AWS Managed Browser (`aws.browser.v1`)

The default system browser for quick setup without custom configuration.

```python
# Use managed browser directly
response = data_client.start_browser_session(
    browserId='aws.browser.v1',
    sessionName='quick-session'
)
```

**Characteristics:**
- No setup required
- Public network access only
- No session recording
- Standard viewport sizes
- Default timeout settings

**Best for:**
- Quick prototyping
- Simple web automation tasks
- Development and testing

### Custom Browser Tools

User-created browser tools with advanced features.

```python
import uuid

# Create custom browser with full features
response = control_client.create_browser(
    name='enterprise-browser',
    description='Enterprise browser with recording and VPC',
    networkConfiguration={
        'networkMode': 'VPC',
        'securityGroupIds': ['sg-12345678'],
        'subnetIds': ['subnet-11111111', 'subnet-22222222']
    },
    recording={
        'enabled': True,
        's3Location': {
            'bucket': 'enterprise-recordings',
            'prefix': 'browser-sessions'
        }
    },
    executionRoleArn='arn:aws:iam::123456789012:role/EnterpriseBrowserRole',
    clientToken=str(uuid.uuid4())
)
```

**Features:**
- Session recording to S3
- VPC network configuration
- Custom security groups
- Custom IAM execution roles
- Extended timeout support

**Best for:**
- Production workloads
- Compliance requirements
- Enterprise environments
- Session auditing

---

## Session Recording

Session recording captures all browser interactions for debugging, auditing, and training.

### Prerequisites

1. **S3 Bucket** - Storage for recording artifacts
2. **IAM Execution Role** - Permissions for S3 and CloudWatch

### IAM Role Setup

Create an execution role with the required permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-recording-bucket",
                "arn:aws:s3:::your-recording-bucket/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:log-group:/aws/bedrock-agentcore/browser/*"
        }
    ]
}
```

**Trust Policy:**

```json
{
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
```

### Create Recording-Enabled Browser

```python
import uuid

response = control_client.create_browser(
    name='recording-browser',
    networkConfiguration={'networkMode': 'PUBLIC'},
    recording={
        'enabled': True,
        's3Location': {
            'bucket': 'my-recordings-bucket',
            'prefix': 'sessions/2024'
        }
    },
    executionRoleArn='arn:aws:iam::123456789012:role/BrowserRecordingRole',
    clientToken=str(uuid.uuid4())
)
```

### Recording Storage Structure

Recordings are stored in S3 with the following structure:

```
s3://your-bucket/your-prefix/
    session-id/
        recording.json      # Session metadata
        events/
            dom-events.json     # DOM change events
            user-actions.json   # User interactions
            console-logs.json   # Console output
            cdp-events.json     # Chrome DevTools Protocol events
            network-events.json # HTTP requests/responses
        screenshots/
            0001.png
            0002.png
            ...
```

### What Recording Captures

| Data Type | Description |
|-----------|-------------|
| DOM changes | All page modifications, element additions/removals |
| User actions | Clicks, typing, scrolling, navigation |
| Console logs | JavaScript console.log, console.error, etc. |
| CDP events | Chrome DevTools Protocol messages |
| Network events | HTTP requests, responses, headers, timing |
| Screenshots | Periodic snapshots and on-action captures |

### Accessing Recordings

#### Via Console

1. Open AgentCore console
2. Navigate to Browser > Sessions
3. Select completed session
4. Use replay interface with:
   - Video player
   - Timeline navigation
   - Page-by-page analysis
   - Event filtering

#### Programmatically

```python
import boto3
import json

s3 = boto3.client('s3')

def get_session_recording(bucket: str, prefix: str, session_id: str):
    """Retrieve session recording from S3."""

    # Get recording metadata
    metadata_key = f"{prefix}/{session_id}/recording.json"
    metadata_obj = s3.get_object(Bucket=bucket, Key=metadata_key)
    metadata = json.loads(metadata_obj['Body'].read())

    # Get user actions
    actions_key = f"{prefix}/{session_id}/events/user-actions.json"
    actions_obj = s3.get_object(Bucket=bucket, Key=actions_key)
    actions = json.loads(actions_obj['Body'].read())

    return {
        'metadata': metadata,
        'actions': actions
    }

# Usage
recording = get_session_recording(
    bucket='my-recordings-bucket',
    prefix='sessions/2024',
    session_id='sess-abc123'
)

for action in recording['actions']:
    print(f"{action['timestamp']}: {action['type']} - {action.get('target', '')}")
```

#### Standalone Replay Viewer

```python
# View recordings without creating new sessions
python -m bedrock_agentcore.tools.browser_replay \
    --bucket my-recordings-bucket \
    --prefix sessions/2024 \
    --session sess-abc123 \
    --profile my-aws-profile
```

---

## Code Examples

### Example 1: Basic Web Browsing with Playwright

```python
import asyncio
from playwright.async_api import async_playwright
import boto3

async def basic_browsing():
    """Basic web browsing with Playwright."""

    # Start browser session
    client = boto3.client('bedrock-agentcore', region_name='us-east-1')

    session = client.start_browser_session(
        browserId='aws.browser.v1',
        sessionName='basic-browsing',
        sessionTimeoutSeconds=900
    )

    automation_url = session['automationStreamUrl']
    session_id = session['sessionId']

    try:
        async with async_playwright() as playwright:
            # Connect to remote browser
            browser = await playwright.chromium.connect_over_cdp(automation_url)
            page = browser.contexts[0].pages[0]

            # Navigate and interact
            await page.goto('https://example.com')
            await page.wait_for_load_state('networkidle')

            # Get page title
            title = await page.title()
            print(f"Page title: {title}")

            # Take screenshot
            screenshot = await page.screenshot()
            with open('screenshot.png', 'wb') as f:
                f.write(screenshot)

            # Extract content
            content = await page.content()
            print(f"Page length: {len(content)} characters")

    finally:
        # Stop session
        client.stop_browser_session(
            browserId='aws.browser.v1',
            sessionId=session_id
        )

asyncio.run(basic_browsing())
```

### Example 2: Form Filling and Navigation

```python
import asyncio
from playwright.async_api import async_playwright
import boto3

async def fill_form_example():
    """Navigate and fill forms."""

    client = boto3.client('bedrock-agentcore', region_name='us-east-1')

    session = client.start_browser_session(
        browserId='aws.browser.v1',
        sessionName='form-filling',
        sessionTimeoutSeconds=1800
    )

    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.connect_over_cdp(
                session['automationStreamUrl']
            )
            page = browser.contexts[0].pages[0]

            # Navigate to form page
            await page.goto('https://httpbin.org/forms/post')

            # Fill form fields
            await page.fill('input[name="custname"]', 'John Doe')
            await page.fill('input[name="custtel"]', '555-1234')
            await page.fill('input[name="custemail"]', 'john@example.com')

            # Select options
            await page.select_option('select[name="size"]', 'medium')

            # Check checkbox
            await page.check('input[name="topping"][value="bacon"]')

            # Fill textarea
            await page.fill('textarea[name="comments"]', 'Please deliver quickly')

            # Take screenshot before submit
            await page.screenshot(path='form-filled.png')

            # Submit form
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')

            # Get response
            response_text = await page.inner_text('pre')
            print(f"Form response: {response_text[:500]}")

    finally:
        client.stop_browser_session(
            browserId='aws.browser.v1',
            sessionId=session['sessionId']
        )

asyncio.run(fill_form_example())
```

### Example 3: Strands Browser Agent

```python
import asyncio
from strands import Agent
from strands.models import BedrockModel
from strands.tools import tool
from strands_tools import BrowserTool
import nest_asyncio

nest_asyncio.apply()

# Initialize browser tool
browser_tool = BrowserTool(
    browser_id='aws.browser.v1',
    region='us-east-1'
)

# Create agent with browser capabilities
model = BedrockModel(model_id='anthropic.claude-sonnet-4-20250514')

agent = Agent(
    model=model,
    tools=[browser_tool],
    system_prompt="""You are a web research assistant with browser access.

You can:
- Navigate to websites
- Search for information
- Extract content from pages
- Take screenshots

When browsing, be methodical:
1. Navigate to the target page
2. Wait for content to load
3. Extract relevant information
4. Summarize findings"""
)

# Use the agent
response = agent(
    "Search for the latest news about AgentCore on the AWS blog and summarize the top 3 articles"
)

print(response)

# Clean up
browser_tool.close()
```

### Example 4: Nova Act Visual Automation

```python
import asyncio
from nova_act import NovaAct
import boto3

async def nova_act_example():
    """Use Nova Act for visual automation."""

    client = boto3.client('bedrock-agentcore', region_name='us-east-1')

    # Start session with larger viewport for visual tasks
    session = client.start_browser_session(
        browserId='aws.browser.v1',
        sessionName='nova-act-session',
        viewportWidth=1920,
        viewportHeight=1080,
        sessionTimeoutSeconds=1800
    )

    try:
        # Initialize Nova Act with session
        nova = NovaAct(
            websocket_url=session['automationStreamUrl'],
            model_id='amazon.nova-pro-v1:0'
        )

        # Navigate using natural language
        await nova.act("Go to amazon.com")

        # Perform visual actions
        await nova.act("Search for 'wireless headphones'")
        await nova.act("Click on the first product result")
        await nova.act("Scroll down to see product reviews")

        # Extract information
        result = await nova.act(
            "Extract the product name, price, and average rating"
        )

        print(f"Product info: {result}")

        # Take annotated screenshot
        screenshot = await nova.screenshot(annotate=True)
        with open('nova-act-result.png', 'wb') as f:
            f.write(screenshot)

    finally:
        client.stop_browser_session(
            browserId='aws.browser.v1',
            sessionId=session['sessionId']
        )

asyncio.run(nova_act_example())
```

### Example 5: Session Recording and Replay

```python
import asyncio
import uuid
from playwright.async_api import async_playwright
import boto3

async def recorded_session_example():
    """Browser session with recording enabled."""

    control_client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    data_client = boto3.client('bedrock-agentcore', region_name='us-east-1')

    # Create browser with recording
    browser_response = control_client.create_browser(
        name=f'recording-demo-{uuid.uuid4().hex[:8]}',
        networkConfiguration={'networkMode': 'PUBLIC'},
        recording={
            'enabled': True,
            's3Location': {
                'bucket': 'my-recordings-bucket',
                'prefix': 'demo-sessions'
            }
        },
        executionRoleArn='arn:aws:iam::123456789012:role/BrowserRecordingRole',
        clientToken=str(uuid.uuid4())
    )

    browser_id = browser_response['browserId']

    # Wait for browser to be active
    import time
    while True:
        status = control_client.get_browser(browserId=browser_id)
        if status['status'] == 'ACTIVE':
            break
        time.sleep(2)

    # Start recorded session
    session = data_client.start_browser_session(
        browserId=browser_id,
        sessionName='recorded-demo',
        sessionTimeoutSeconds=900
    )

    session_id = session['sessionId']

    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.connect_over_cdp(
                session['automationStreamUrl']
            )
            page = browser.contexts[0].pages[0]

            # Perform actions (all will be recorded)
            await page.goto('https://news.ycombinator.com')
            await page.wait_for_load_state('networkidle')

            # Click on first story
            await page.click('.titleline a >> nth=0')
            await page.wait_for_load_state('networkidle')

            # Go back
            await page.go_back()

            # Scroll and interact
            await page.evaluate('window.scrollTo(0, 500)')
            await asyncio.sleep(1)

            print("Session recorded successfully")
            print(f"Session ID: {session_id}")
            print(f"Recording location: s3://my-recordings-bucket/demo-sessions/{session_id}/")

    finally:
        # Stop session (triggers recording upload)
        data_client.stop_browser_session(
            browserId=browser_id,
            sessionId=session_id
        )

        # Optionally clean up browser
        # control_client.delete_browser(browserId=browser_id)

asyncio.run(recorded_session_example())
```

---

## Integration Patterns

### With AgentCore Runtime

Deploy browser-enabled agents to AgentCore Runtime for scalable execution.

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.tools.browser_client import BrowserClient
from playwright.async_api import async_playwright

app = BedrockAgentCoreApp()

@app.entrypoint()
async def web_research_agent(request):
    """Agent that performs web research."""

    query = request.get('query')

    browser_client = BrowserClient(region_name='us-east-1')

    async with browser_client.start_session(
        browser_id='aws.browser.v1',
        timeout_seconds=1800
    ) as session:

        async with async_playwright() as playwright:
            browser = await playwright.chromium.connect_over_cdp(
                session.automation_stream_url
            )
            page = browser.contexts[0].pages[0]

            # Search Google
            await page.goto(f'https://www.google.com/search?q={query}')
            await page.wait_for_load_state('networkidle')

            # Extract results
            results = await page.evaluate('''
                () => {
                    const items = document.querySelectorAll('.g');
                    return Array.from(items).slice(0, 5).map(item => ({
                        title: item.querySelector('h3')?.textContent || '',
                        link: item.querySelector('a')?.href || '',
                        snippet: item.querySelector('.VwiC3b')?.textContent || ''
                    }));
                }
            ''')

            return {
                'query': query,
                'results': results
            }

if __name__ == '__main__':
    app.run()
```

**Deploy to Runtime:**

```bash
agentcore deploy \
    --name web-research-agent \
    --entrypoint agent.py \
    --memory 2048 \
    --timeout 1800
```

### With AgentCore Gateway

Expose browser actions as MCP tools through Gateway.

```python
import json
from bedrock_agentcore.tools.browser_client import BrowserClient
from playwright.async_api import async_playwright

def lambda_handler(event, context):
    """Lambda handler for browser tools via Gateway."""

    tool_name = event.get('name')
    arguments = event.get('arguments', {})

    if tool_name == 'browse_url':
        return browse_url(arguments['url'])
    elif tool_name == 'take_screenshot':
        return take_screenshot(arguments['url'])
    elif tool_name == 'extract_text':
        return extract_text(arguments['url'], arguments.get('selector'))

    return {
        'isError': True,
        'content': [{'type': 'text', 'text': f'Unknown tool: {tool_name}'}]
    }

def browse_url(url: str) -> dict:
    """Browse URL and return page content."""
    import asyncio

    async def _browse():
        client = BrowserClient(region_name='us-east-1')

        async with client.start_session(
            browser_id='aws.browser.v1',
            timeout_seconds=300
        ) as session:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.connect_over_cdp(
                    session.automation_stream_url
                )
                page = browser.contexts[0].pages[0]

                await page.goto(url)
                await page.wait_for_load_state('networkidle')

                title = await page.title()
                content = await page.inner_text('body')

                return {
                    'content': [{
                        'type': 'text',
                        'text': json.dumps({
                            'title': title,
                            'content': content[:5000]
                        })
                    }]
                }

    return asyncio.run(_browse())
```

**Register as Gateway Target:**

```python
control_client.create_gateway_target(
    gatewayId='gw-abc123',
    name='BrowserTools',
    targetConfiguration={
        'lambdaTargetConfiguration': {
            'lambdaArn': 'arn:aws:lambda:us-east-1:123456789012:function:BrowserTools',
            'toolSchema': {
                'tools': [
                    {
                        'name': 'browse_url',
                        'description': 'Navigate to a URL and return page content',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'url': {'type': 'string', 'description': 'URL to browse'}
                            },
                            'required': ['url']
                        }
                    },
                    {
                        'name': 'take_screenshot',
                        'description': 'Take a screenshot of a webpage',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'url': {'type': 'string', 'description': 'URL to screenshot'}
                            },
                            'required': ['url']
                        }
                    },
                    {
                        'name': 'extract_text',
                        'description': 'Extract text from a webpage element',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'url': {'type': 'string', 'description': 'URL to extract from'},
                                'selector': {'type': 'string', 'description': 'CSS selector'}
                            },
                            'required': ['url']
                        }
                    }
                ]
            }
        }
    }
)
```

---

## Best Practices

1. **Use context managers** - Always use `async with` for sessions to ensure proper cleanup, even on errors.

2. **Set appropriate timeouts** - Configure session timeout based on task complexity. Start with 15 minutes and extend only if needed.

3. **Wait for page loads** - Always use `wait_for_load_state('networkidle')` or similar before interacting with elements.

4. **Handle dynamic content** - Use explicit waits (`wait_for_selector`) for JavaScript-rendered content.

5. **Enable recording for debugging** - Use custom browsers with recording for development and troubleshooting.

6. **Clean up sessions** - Always stop sessions when done to avoid unnecessary charges and resource consumption.

7. **Use live view during development** - Monitor agent behavior in real-time to identify issues quickly.

8. **Implement error handling** - Wrap browser operations in try/except blocks and handle common errors gracefully.

9. **Respect rate limits** - Add delays between rapid page navigations to avoid triggering anti-bot measures.

10. **Secure sensitive data** - Never store passwords or sensitive data in recordings; use session-specific credentials.

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `SessionNotFound` | Invalid session ID or session expired | Verify session exists and is ACTIVE |
| `BrowserNotFound` | Invalid browser ID | Check browser ID and ensure it exists |
| `SessionTimeout` | Session exceeded timeout | Increase `sessionTimeoutSeconds` |
| `WebSocketConnectionFailed` | Network issues | Check connectivity and security groups |
| `RecordingUploadFailed` | S3 permissions issue | Verify execution role has S3 write access |
| `ViewportError` | Invalid viewport dimensions | Use standard dimensions (1920x1080) |
| `BrowserCreationFailed` | IAM or configuration error | Check execution role and network config |
| `ConcurrentSessionLimit` | Too many active sessions | Stop unused sessions (max 500) |

### Debugging Tips

```bash
# Check browser status
aws bedrock-agentcore-control get-browser \
    --browser-id br-abc123 \
    --region us-east-1

# List active sessions
aws bedrock-agentcore list-browser-sessions \
    --browser-id br-abc123 \
    --region us-east-1

# Get session details
aws bedrock-agentcore get-browser-session \
    --browser-id br-abc123 \
    --session-id sess-xyz789 \
    --region us-east-1

# View CloudWatch logs
aws logs tail /aws/bedrock-agentcore/browser/br-abc123 --follow
```

### Session Not Starting

1. Verify browser tool exists and is ACTIVE
2. Check IAM permissions for `bedrock-agentcore:StartBrowserSession`
3. Ensure you haven't exceeded concurrent session limit
4. Verify network configuration allows outbound connections

### Recording Not Appearing

1. Confirm recording is enabled on the browser tool
2. Verify S3 bucket exists and is accessible
3. Check execution role has `s3:PutObject` permission
4. Wait for session to fully stop (recordings upload on session end)
5. Check correct S3 prefix path

### WebSocket Connection Issues

1. Verify automation URL is correct and not expired
2. Check network allows WebSocket connections (wss://)
3. Ensure session is in ACTIVE state
4. Try reconnecting with a fresh session

---

## Limits & Quotas

| Resource | Default Limit | Adjustable |
|----------|--------------|------------|
| Browser tools per account | 100 | Yes |
| Concurrent sessions per account | 500 | Yes |
| Concurrent sessions per browser | 100 | Yes |
| Session timeout minimum | 60 seconds | No |
| Session timeout maximum | 28800 seconds (8 hours) | No |
| Session timeout default | 900 seconds (15 minutes) | N/A |
| Session data retention | 30 days | No |
| Viewport width minimum | 800 | No |
| Viewport width maximum | 3840 | No |
| Viewport height minimum | 600 | No |
| Viewport height maximum | 2160 | No |
| Recording max file size | 10 GB | No |

---

## Pricing

### Session Usage

Charged for:
- Actual CPU consumption
- Peak memory consumed (per second)
- 1-second minimum billing increment
- 128 MB minimum memory billing
- I/O wait and idle time is **free**

### Recording Storage

- S3 storage costs for recording artifacts
- Standard S3 pricing applies
- Consider S3 lifecycle policies for cost optimization

### Cost Optimization Tips

1. **Use appropriate timeouts** - Don't set 8-hour timeout for 5-minute tasks
2. **Stop sessions promptly** - Don't leave sessions running idle
3. **Use managed browser for simple tasks** - No setup overhead
4. **Archive old recordings** - Use S3 lifecycle policies to move to Glacier
5. **Monitor session metrics** - Use CloudWatch to identify optimization opportunities

---

## Related Services

- [AgentCore Runtime](./01-runtime.md) - Deploy browser-enabled agents
- [AgentCore Gateway](./03-gateway.md) - Expose browser tools via MCP
- [AgentCore Memory](./02-memory.md) - Store browsing context
- [AgentCore Identity](./04-identity.md) - Authenticate to web services
- [AgentCore Code Interpreter](./05-code-interpreter.md) - Process extracted data
- [AgentCore Observability](./08-observability.md) - Monitor browser sessions
