# Customer Support Agent Example

Runnable example demonstrating Memory + Gateway + Runtime integration for customer support bots.

**Article**: [Building a Customer Support Agent with AgentCore](../../customer-support-standard.md)

## What This Demonstrates

1. **Tool Integration** - Mock CRM lookup and ticket creation tools
2. **Memory Management** - Session context and learned preferences
3. **Conversation Flow** - Multi-turn support conversations
4. **Agent Architecture** - How to structure a support agent

## Prerequisites

- Python 3.10+ installed
- (Optional) AWS account with Bedrock AgentCore access for production deployment

## Quick Start (Local Mock)

Run locally without AWS credentials using mock services:

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the demo
python main.py
```

## Expected Output

```
============================================================
Customer Support Agent with AgentCore
============================================================

Initializing agent components...
  Agent initialized with 3 tools
  Memory: Mock (local)

Starting session: session_1234567890
Customer: alice@example.com

------------------------------------------------------------
Conversation:
------------------------------------------------------------

Customer: Hi, I'm alice@example.com and I have a question about my recent order

Agent: Hello Alice Johnson! I can see you're a premium customer with us since
2023-01-15. I can see your recent orders: ORD-1234, ORD-1235, ORD-1240.
How can I help you today?

Customer: My order ORD-1234 was supposed to arrive but I haven't received it

Agent: I've checked the order and it shows as 'delivered' on 2024-12-01.
If you haven't received it, I can create a ticket to investigate.

Customer: Can you create a ticket for this issue? It's quite urgent.

Agent: I've created ticket TKT-5234 for you with high priority. Our team will
review it within 4 hours. Is there anything else I can help with?

Customer: Thank you so much for your help!

Agent: You're welcome! Is there anything else I can help you with today?

------------------------------------------------------------

Memory contents:
  Events stored: 4
  Preferences learned: ['Customer tier: premium']

============================================================
Demo complete!
```

## File Structure

```
customer-support/
    main.py          # Main agent demo with conversation simulation
    tools.py         # Mock CRM and ticketing system implementations
    requirements.txt # Python dependencies
    README.md        # This file
```

## Running with AgentCore (Production)

To use actual AgentCore services instead of mocks:

### 1. Deploy Lambda Tools

Deploy the tool handlers from `tools.py` as Lambda functions:

```bash
# Package and deploy lookup_customer_handler
# Package and deploy create_ticket_handler
# Package and deploy get_order_status_handler
```

### 2. Create Gateway

```bash
agentcore gateway create-mcp-gateway \
    --name CustomerSupportGateway \
    --region us-east-1
```

### 3. Register Tools with Gateway

```bash
agentcore gateway create-mcp-gateway-target \
    --gateway-id <your-gateway-id> \
    --name CRMTools \
    --type lambda \
    --lambda-arn arn:aws:lambda:us-east-1:123456789012:function:lookup-customer
```

### 4. Create Memory

```bash
agentcore memory create \
    --name CustomerSupportMemory \
    --strategies SessionSummarizer,PreferenceLearner
```

### 5. Set Environment Variables

```bash
export AWS_REGION=us-east-1
export AGENTCORE_GATEWAY_ID=<your-gateway-id>
export AGENTCORE_MEMORY_ID=<your-memory-id>
```

### 6. Run with AgentCore

Modify `main.py` to use `main_with_agentcore()` instead of `main()`.

## Testing Tools Directly

Test the mock tools without running the full agent:

```bash
python tools.py
```

Output:
```
Testing Mock CRM...
Alice lookup: {"found": true, "customer": {...}}
Unknown lookup: {"found": false, "message": "No customer found..."}
Order status: {"status": "delivered", ...}

Testing Mock Ticket System...
Created ticket: {"success": true, "ticket": {...}}

All tests passed!
```

## Architecture

```
                    main.py
                       |
                       v
            +-------------------+
            |  CustomerSupport  |
            |      Agent        |
            +--------+----------+
                     |
         +-----------+-----------+
         |                       |
         v                       v
   +-----------+           +-----------+
   | MockMemory|           |   tools   |
   +-----------+           +-----------+
   | events    |           | MockCRM   |
   | prefs     |           | MockTicket|
   +-----------+           +-----------+
```

In production, replace MockMemory with AgentCore Memory client and tools with Gateway calls.

## Customization Ideas

1. **Add more tools**: Order refund, shipping updates, account changes
2. **Improve context**: Use full conversation history for better responses
3. **Add Strands**: Replace rule-based logic with actual LLM agent
4. **Add Policy**: Restrict tool access based on customer tier
5. **Add Observability**: Trace all tool calls and memory operations

## Learn More

- [AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [AgentCore Memory Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)
- [AgentCore Gateway Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)
- [GitHub Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples/)
