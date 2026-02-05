#!/usr/bin/env python3
"""
Customer Support Agent with AgentCore
======================================
Demonstrates: Memory + Gateway + Runtime integration for support bots

Article: /articles/customer-support-standard.md

Prerequisites:
- pip install -r requirements.txt
- AWS credentials configured
- Bedrock AgentCore access enabled

Usage:
    python main.py

Expected output:
    Agent initialized with 3 tools
    Memory created: CustomerSupport_xxx
    Session: session_xxx

    Customer: Hi, I'm alice@example.com and I have a question about my order
    Agent: Hello Alice! I can see you're a premium customer...

    Customer: My order ORD-1234 hasn't arrived yet
    Agent: I've looked up your order ORD-1234...

    Customer: Can you create a ticket for this?
    Agent: I've created ticket TKT-xxxx for you...

    Cleaning up resources...
    Done!
"""

import os
import sys
import time
import json
from datetime import datetime, timezone

# Optional: load .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not required for local testing

# Import mock tools for local testing
from tools import MockCRM, MockTicketSystem


def create_support_agent():
    """Create a support agent with tools (local mock version)."""

    # Initialize mock services
    crm = MockCRM()
    tickets = MockTicketSystem()

    # Tool functions that wrap the mock services
    def lookup_customer(email: str) -> str:
        """Look up customer information by email address."""
        result = crm.lookup_customer(email)
        return json.dumps(result)

    def create_ticket(
        customer_id: str,
        subject: str,
        priority: str = "medium",
        description: str = ""
    ) -> str:
        """Create a support ticket for a customer issue."""
        result = tickets.create_ticket(
            customer_id=customer_id,
            subject=subject,
            priority=priority,
            description=description
        )
        return json.dumps(result)

    def get_order_status(order_id: str) -> str:
        """Check the status of an order."""
        result = crm.get_order_status(order_id)
        return json.dumps(result)

    tools = {
        "lookup_customer": lookup_customer,
        "create_ticket": create_ticket,
        "get_order_status": get_order_status
    }

    return tools


class MockMemory:
    """Mock memory for local testing without AWS."""

    def __init__(self):
        self.events = {}  # {actor_id: {session_id: [events]}}
        self.preferences = {}  # {actor_id: [preferences]}

    def create_event(self, actor_id: str, session_id: str, messages: list):
        """Store conversation event."""
        if actor_id not in self.events:
            self.events[actor_id] = {}
        if session_id not in self.events[actor_id]:
            self.events[actor_id][session_id] = []

        self.events[actor_id][session_id].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "messages": messages
        })

    def get_events(self, actor_id: str, session_id: str) -> list:
        """Retrieve conversation history."""
        if actor_id in self.events and session_id in self.events[actor_id]:
            return self.events[actor_id][session_id]
        return []

    def add_preference(self, actor_id: str, preference: str):
        """Store a learned preference."""
        if actor_id not in self.preferences:
            self.preferences[actor_id] = []
        if preference not in self.preferences[actor_id]:
            self.preferences[actor_id].append(preference)

    def get_preferences(self, actor_id: str) -> list:
        """Retrieve stored preferences."""
        return self.preferences.get(actor_id, [])


class CustomerSupportAgent:
    """Customer support agent with memory and tools."""

    def __init__(self, tools: dict, memory: MockMemory):
        self.tools = tools
        self.memory = memory
        self.current_customer = None
        self.current_session = None
        self.session_context = {}  # Track context across turns

        self.system_prompt = """You are a helpful customer support agent. You have access to:
1. lookup_customer(email) - Get customer information
2. get_order_status(order_id) - Check order status
3. create_ticket(customer_id, subject, priority, description) - Create support tickets

Guidelines:
- Always greet customers warmly
- Look up customer info when they identify themselves
- Check order status when they mention an order
- Create tickets for issues that need escalation
- Be concise but helpful"""

    def start_session(self, customer_email: str, session_id: str):
        """Start a new support session."""
        self.current_customer = customer_email
        self.current_session = session_id
        self.session_context = {}  # Reset context for new session

        # Get any stored preferences
        preferences = self.memory.get_preferences(customer_email)
        return preferences

    def _detect_tool_call(self, message: str, context: dict) -> tuple:
        """Simple rule-based tool detection for demo purposes."""
        message_lower = message.lower()

        # Check for email mentions to look up customer
        if "@" in message and "example.com" in message:
            # Extract email
            words = message.split()
            for word in words:
                if "@" in word and "." in word:
                    email = word.strip(".,!?")
                    return ("lookup_customer", {"email": email})

        # Check for order status requests
        if "order" in message_lower and "ORD-" in message:
            # Extract order ID
            for word in message.split():
                if word.startswith("ORD-"):
                    order_id = word.strip(".,!?")
                    return ("get_order_status", {"order_id": order_id})

        # Check for ticket creation requests
        if any(word in message_lower for word in ["ticket", "escalate", "report", "create"]):
            if context.get("customer_id"):
                return ("create_ticket", {
                    "customer_id": context.get("customer_id"),
                    "subject": context.get("issue", "Customer support request"),
                    "priority": "high" if "urgent" in message_lower else "medium",
                    "description": message
                })

        return (None, None)

    def _generate_response(self, message: str, tool_result: str = None, context: dict = None) -> str:
        """Generate agent response (simplified for demo)."""
        context = context or {}
        message_lower = message.lower()

        # If we have a tool result, format the response
        if tool_result:
            try:
                result = json.loads(tool_result)

                # Customer lookup response
                if "customer" in result and result.get("found"):
                    customer = result["customer"]
                    self.memory.add_preference(
                        self.current_customer,
                        f"Customer tier: {customer['tier']}"
                    )
                    return (
                        f"Hello {customer['name']}! I can see you're a {customer['tier']} customer "
                        f"with us since {customer['account_created']}. I can see your recent orders: "
                        f"{', '.join(customer['recent_orders'])}. How can I help you today?"
                    )

                # Order status response
                if "status" in result and "delivered" in str(result.get("status", "")):
                    return (
                        f"I've checked the order and it shows as '{result['status']}' "
                        f"on {result.get('delivered_date', 'recently')}. "
                        f"If you haven't received it, I can create a ticket to investigate."
                    )

                if "status" in result and result.get("status") == "shipped":
                    return (
                        f"Your order is currently shipped. "
                        f"Tracking number: {result.get('tracking', 'N/A')}. "
                        f"Is there anything else I can help with?"
                    )

                # Ticket creation response
                if "ticket" in result and result.get("success"):
                    ticket = result["ticket"]
                    return (
                        f"I've created ticket {ticket['ticket_id']} for you with "
                        f"{ticket['priority']} priority. Our team will review it within "
                        f"{'4 hours' if ticket['priority'] == 'high' else '24 hours'}. "
                        f"Is there anything else I can help with?"
                    )

                # Not found responses
                if result.get("found") == False:
                    return (
                        f"I couldn't find that customer in our system. "
                        f"Could you verify the email address?"
                    )

            except json.JSONDecodeError:
                pass

        # Default responses based on message content
        if any(word in message_lower for word in ["hi", "hello", "hey"]):
            return (
                "Hello! Welcome to customer support. I'm here to help. "
                "Could you please provide your email address so I can look up your account?"
            )

        if "thank" in message_lower:
            return (
                "You're welcome! Is there anything else I can help you with today?"
            )

        if "no" in message_lower and any(word in message_lower for word in ["that's all", "nothing", "bye"]):
            return (
                "Great! Thank you for contacting support. Have a wonderful day!"
            )

        # Default
        return (
            "I understand. Let me help you with that. "
            "Could you provide more details about your issue?"
        )

    def chat(self, message: str) -> str:
        """Process a customer message and return response."""

        # Use persistent session context
        context = self.session_context

        # Track issue topic from message
        if "order" in message.lower():
            context["issue"] = "Order delivery issue"

        # Detect if we need to call a tool
        tool_name, tool_args = self._detect_tool_call(message, context)

        tool_result = None
        if tool_name and tool_name in self.tools:
            tool_result = self.tools[tool_name](**tool_args)

            # Update session context from tool result
            try:
                result_data = json.loads(tool_result)
                if "customer" in result_data and result_data.get("found"):
                    context["customer_id"] = result_data["customer"]["customer_id"]
                    context["customer_name"] = result_data["customer"]["name"]
                    context["customer_tier"] = result_data["customer"]["tier"]
            except:
                pass

        # Generate response
        response = self._generate_response(message, tool_result, context)

        # Store interaction in memory
        self.memory.create_event(
            actor_id=self.current_customer,
            session_id=self.current_session,
            messages=[
                {"role": "user", "content": message},
                {"role": "assistant", "content": response}
            ]
        )

        return response


def main():
    """Main function demonstrating the customer support agent."""

    print("=" * 60)
    print("Customer Support Agent with AgentCore")
    print("=" * 60)
    print()

    # Initialize components
    print("Initializing agent components...")
    tools = create_support_agent()
    memory = MockMemory()
    agent = CustomerSupportAgent(tools, memory)

    print(f"  Agent initialized with {len(tools)} tools")
    print(f"  Memory: Mock (local)")
    print()

    # Start a support session
    customer_email = "alice@example.com"
    session_id = f"session_{int(time.time())}"

    print(f"Starting session: {session_id}")
    print(f"Customer: {customer_email}")
    print()

    agent.start_session(customer_email, session_id)

    # Simulate conversation
    conversations = [
        "Hi, I'm alice@example.com and I have a question about my recent order",
        "My order ORD-1234 was supposed to arrive but I haven't received it",
        "Can you create a ticket for this issue? It's quite urgent.",
        "Thank you so much for your help!",
    ]

    print("-" * 60)
    print("Conversation:")
    print("-" * 60)

    for message in conversations:
        print(f"\nCustomer: {message}")
        response = agent.chat(message)
        print(f"\nAgent: {response}")
        print()
        time.sleep(0.5)  # Small delay for readability

    print("-" * 60)
    print()

    # Show what was stored in memory
    print("Memory contents:")
    print(f"  Events stored: {len(memory.get_events(customer_email, session_id))}")
    print(f"  Preferences learned: {memory.get_preferences(customer_email)}")
    print()

    print("=" * 60)
    print("Demo complete!")
    print()
    print("To run with actual AgentCore services:")
    print("  1. Deploy tools as Lambda functions")
    print("  2. Create Gateway and register tools")
    print("  3. Create Memory resource")
    print("  4. Update main.py to use boto3 clients")
    print("=" * 60)


def main_with_agentcore():
    """
    Production version using actual AgentCore services.

    Uncomment and modify this function when you have AgentCore access.
    """
    import boto3

    region = os.getenv("AWS_REGION", "us-east-1")
    memory_id = os.getenv("AGENTCORE_MEMORY_ID")
    gateway_id = os.getenv("AGENTCORE_GATEWAY_ID")

    if not memory_id or not gateway_id:
        print("Error: Set AGENTCORE_MEMORY_ID and AGENTCORE_GATEWAY_ID environment variables")
        sys.exit(1)

    # Initialize AgentCore clients
    control_client = boto3.client('bedrock-agentcore-control', region_name=region)
    data_client = boto3.client('bedrock-agentcore', region_name=region)

    print(f"Connected to AgentCore in {region}")
    print(f"Memory ID: {memory_id}")
    print(f"Gateway ID: {gateway_id}")

    # Example: Call a tool through Gateway
    response = data_client.invoke_gateway(
        gatewayId=gateway_id,
        method='tools/call',
        payload=json.dumps({
            'name': 'lookup_customer',
            'arguments': {'email': 'alice@example.com'}
        }).encode()
    )

    result = json.loads(response['payload'].read())
    print(f"Gateway tool result: {result}")

    # Example: Store event in Memory
    from datetime import datetime, timezone

    data_client.create_event(
        memoryId=memory_id,
        actorId="alice@example.com",
        sessionId=f"session_{int(time.time())}",
        eventTimestamp=datetime.now(timezone.utc),
        payload=[
            {'conversational': {'role': 'USER', 'content': {'text': 'Test message'}}},
            {'conversational': {'role': 'ASSISTANT', 'content': {'text': 'Test response'}}}
        ]
    )

    print("Event stored in Memory")


if __name__ == "__main__":
    # Run the mock version for local testing
    main()

    # Uncomment below to run with actual AgentCore:
    # main_with_agentcore()
