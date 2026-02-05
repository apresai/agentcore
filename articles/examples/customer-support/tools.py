"""
Mock CRM and Ticketing Tools
=============================
Simulates external services for the customer support agent example.

In production, these would be Lambda functions calling your actual CRM/ticketing APIs.
For local testing, they provide realistic mock responses.

Usage:
    # These are called by the agent through Gateway, or directly for testing
    from tools import MockCRM, MockTicketSystem

    crm = MockCRM()
    customer = crm.lookup_customer("alice@example.com")

    tickets = MockTicketSystem()
    ticket = tickets.create_ticket("CUST-001", "Order issue", "high")
"""

import json
import hashlib
from datetime import datetime, timezone
from typing import Optional


class MockCRM:
    """Simulated CRM system with customer data."""

    # Mock customer database
    CUSTOMERS = {
        "alice@example.com": {
            "customer_id": "CUST-001",
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "tier": "premium",
            "account_created": "2023-01-15",
            "recent_orders": ["ORD-1234", "ORD-1235", "ORD-1240"],
            "preferences": {
                "contact_method": "email",
                "language": "en",
                "timezone": "America/New_York"
            },
            "lifetime_value": 2450.00
        },
        "bob@example.com": {
            "customer_id": "CUST-002",
            "name": "Bob Smith",
            "email": "bob@example.com",
            "tier": "standard",
            "account_created": "2024-03-20",
            "recent_orders": ["ORD-5678"],
            "preferences": {
                "contact_method": "phone",
                "language": "en",
                "timezone": "America/Los_Angeles"
            },
            "lifetime_value": 125.00
        },
        "carol@example.com": {
            "customer_id": "CUST-003",
            "name": "Carol White",
            "email": "carol@example.com",
            "tier": "premium",
            "account_created": "2022-06-10",
            "recent_orders": ["ORD-9001", "ORD-9002", "ORD-9010", "ORD-9015"],
            "preferences": {
                "contact_method": "email",
                "language": "en",
                "timezone": "America/Chicago"
            },
            "lifetime_value": 5200.00
        }
    }

    def lookup_customer(self, email: str) -> dict:
        """Look up customer by email address."""
        customer = self.CUSTOMERS.get(email.lower())
        if customer:
            return {
                "found": True,
                "customer": customer
            }
        return {
            "found": False,
            "message": f"No customer found with email: {email}"
        }

    def get_order_status(self, order_id: str) -> dict:
        """Get status of an order."""
        # Mock order statuses
        statuses = {
            "ORD-1234": {"status": "delivered", "delivered_date": "2024-12-01"},
            "ORD-1235": {"status": "shipped", "tracking": "1Z999AA10123456784"},
            "ORD-1240": {"status": "processing", "estimated_ship": "2024-12-20"},
            "ORD-5678": {"status": "delivered", "delivered_date": "2024-11-28"},
            "ORD-9001": {"status": "delivered", "delivered_date": "2024-10-15"},
        }
        return statuses.get(order_id, {"status": "not_found", "order_id": order_id})


class MockTicketSystem:
    """Simulated ticketing system."""

    # In-memory ticket storage
    _tickets = {}

    def create_ticket(
        self,
        customer_id: str,
        subject: str,
        priority: str = "medium",
        description: str = "",
        category: str = "general"
    ) -> dict:
        """Create a new support ticket."""

        # Generate deterministic ticket ID from subject
        hash_input = f"{customer_id}{subject}{datetime.now(timezone.utc).isoformat()}"
        ticket_num = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16) % 10000
        ticket_id = f"TKT-{ticket_num:04d}"

        ticket = {
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "subject": subject,
            "description": description,
            "priority": priority,
            "category": category,
            "status": "open",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "assigned_to": None,
            "resolution": None
        }

        self._tickets[ticket_id] = ticket

        return {
            "success": True,
            "ticket": ticket,
            "message": f"Ticket {ticket_id} created successfully"
        }

    def get_ticket(self, ticket_id: str) -> Optional[dict]:
        """Retrieve a ticket by ID."""
        return self._tickets.get(ticket_id)

    def update_ticket(self, ticket_id: str, updates: dict) -> dict:
        """Update an existing ticket."""
        if ticket_id not in self._tickets:
            return {"success": False, "message": f"Ticket {ticket_id} not found"}

        ticket = self._tickets[ticket_id]
        for key, value in updates.items():
            if key in ticket:
                ticket[key] = value
        ticket["updated_at"] = datetime.now(timezone.utc).isoformat()

        return {"success": True, "ticket": ticket}


# Lambda handler format for AgentCore Gateway
def lookup_customer_handler(event, context):
    """Lambda handler for CRM lookup tool."""
    args = event.get('arguments', {})
    email = args.get('email', '')

    crm = MockCRM()
    result = crm.lookup_customer(email)

    return {
        "content": [{"type": "text", "text": json.dumps(result)}]
    }


def create_ticket_handler(event, context):
    """Lambda handler for ticket creation tool."""
    args = event.get('arguments', {})

    tickets = MockTicketSystem()
    result = tickets.create_ticket(
        customer_id=args.get('customer_id', 'unknown'),
        subject=args.get('subject', 'No subject'),
        priority=args.get('priority', 'medium'),
        description=args.get('description', ''),
        category=args.get('category', 'general')
    )

    return {
        "content": [{"type": "text", "text": json.dumps(result)}]
    }


def get_order_status_handler(event, context):
    """Lambda handler for order status lookup."""
    args = event.get('arguments', {})
    order_id = args.get('order_id', '')

    crm = MockCRM()
    result = crm.get_order_status(order_id)

    return {
        "content": [{"type": "text", "text": json.dumps(result)}]
    }


# For local testing
if __name__ == "__main__":
    print("Testing Mock CRM...")
    crm = MockCRM()

    # Test customer lookup
    result = crm.lookup_customer("alice@example.com")
    print(f"Alice lookup: {json.dumps(result, indent=2)}")

    result = crm.lookup_customer("unknown@example.com")
    print(f"Unknown lookup: {json.dumps(result, indent=2)}")

    # Test order status
    result = crm.get_order_status("ORD-1234")
    print(f"Order status: {json.dumps(result, indent=2)}")

    print("\nTesting Mock Ticket System...")
    tickets = MockTicketSystem()

    # Create ticket
    result = tickets.create_ticket(
        customer_id="CUST-001",
        subject="Order not received",
        priority="high",
        description="Customer reports order ORD-1234 marked delivered but not received"
    )
    print(f"Created ticket: {json.dumps(result, indent=2)}")

    print("\n All tests passed!")
