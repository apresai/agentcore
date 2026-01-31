# AgentCore Browser

## Overview

The Amazon Bedrock AgentCore Browser provides a secure, isolated browser environment for agents to interact with web applications. It runs in a containerized environment, keeping web activity separate from your system.

## Key Features

### Session-Based Web Browsing
- Isolated browser sessions
- Configurable timeouts (default: 15 minutes, max: 8 hours)
- Multiple simultaneous sessions

### Security Features
- **Isolation**: Containerized environment separate from your system
- **Ephemeral sessions**: Temporary sessions that reset after each use
- **Automatic termination**: Sessions end when time-to-live expires
- Session isolation for security

### Observability
- Live viewing
- CloudTrail logging
- Session replay capabilities
- CloudWatch metrics for real-time performance insights

## Workflow

### Step 1: Create a Browser Tool
Choose between:
- **AWS Managed Browser** (`aws.browser.v1`) - Quick setup
- **Custom Browser** - Advanced features:
  - Session recording
  - Custom network settings
  - Specific IAM execution roles

### Step 2: Start a Browser Session
Launch isolated sessions with configurable timeouts.

### Step 3: Interact with the Browser
WebSocket-based streaming APIs for:

**Automation Endpoint**:
- Navigate websites
- Click elements
- Fill out forms
- Take screenshots

**Compatible Libraries**:
- Strands
- Nova Act
- Playwright

**Live View Endpoint**:
- Real-time session monitoring
- Direct user interaction through live stream

### Step 4: Monitor and Record Sessions
- Live View for real-time monitoring
- Session recording (custom browsers)
- CloudWatch metrics

**Session Recording Captures**:
- DOM changes
- User actions
- Console logs
- Network events

Recorded sessions stored in S3 with:
- Video playback
- Timeline navigation
- User action tracking
- Comprehensive logs

## Why Use Remote Browsers?

A remote browser runs in a separate environment, allowing AI agents to interact with the web as humans do:

- Navigate websites, fill forms, click buttons
- Parse dynamic content
- Serverless, auto-scaling infrastructure
- Visual understanding through screenshots
- Human intervention with live interactive view
- Session isolation for security
- Complex web application navigation
- Comprehensive audit capabilities

## Pricing

Charged for:
- Actual CPU consumption
- Peak memory consumed (per second)
- 1-second minimum, 128MB minimum
- I/O wait and idle time is free
