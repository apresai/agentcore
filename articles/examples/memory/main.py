#!/usr/bin/env python3
"""
AgentCore Memory Example
========================
Demonstrates: Short-term and long-term memory for context-aware agents
Article: /articles/memory-standard.md

Prerequisites:
- pip install -r requirements.txt
- AWS credentials configured
- Bedrock AgentCore access enabled

Usage:
    python main.py

Expected output:
    ✓ Memory created: mem-xxxxx
    ✓ Event stored successfully
    ✓ Short-term events retrieved: 1 event(s)
    ✓ Memory working successfully!
"""

import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Using boto3 for broader compatibility
import boto3

def main():
    """Main function demonstrating AgentCore Memory."""

    region = os.getenv("AWS_REGION", "us-east-1")

    # Initialize clients
    control_client = boto3.client('bedrock-agentcore-control', region_name=region)
    data_client = boto3.client('bedrock-agentcore', region_name=region)
    print("✓ AgentCore clients initialized")

    # Create a unique memory name (alphanumeric + underscore only, must start with letter)
    memory_name = f"MemoryExample_{int(time.time())}"

    memory_id = None  # Initialize for cleanup

    try:
        # Step 1: Create memory resource
        print(f"\nCreating memory: {memory_name}...")
        create_response = control_client.create_memory(
            name=memory_name,
            description="Demo memory for article example",
            eventExpiryDuration=3,  # 3 days TTL for short-term (min 3, max 365 days)
            memoryStrategies=[
                {
                    'userPreferenceMemoryStrategy': {
                        'name': 'PreferenceLearner',
                        'namespaces': ['preferences']
                    }
                }
            ]
        )

        memory_id = create_response['memory']['id']
        print(f"✓ Memory created: {memory_id}")

        # Wait for memory to become active (can take 2-3 minutes)
        print("Waiting for memory to become active (this may take 2-3 minutes)...")
        for i in range(150):  # Up to 5 minutes
            status_response = control_client.get_memory(memoryId=memory_id)
            status = status_response['memory']['status']
            if status == 'ACTIVE':
                print("✓ Memory is active")
                break
            elif status == 'FAILED':
                raise Exception(f"Memory creation failed: {status_response}")
            if i % 10 == 0:
                print(f"  Status: {status}...")
            time.sleep(2)
        else:
            raise Exception("Memory did not become active within timeout")

        # Step 2: Store a conversation event (short-term memory)
        print("\nStoring conversation event...")
        actor_id = "demo_user_123"
        session_id = f"session_{int(time.time())}"

        from datetime import datetime, timezone
        event_timestamp = datetime.now(timezone.utc)

        data_client.create_event(
            memoryId=memory_id,
            actorId=actor_id,
            sessionId=session_id,
            eventTimestamp=event_timestamp,
            payload=[
                {
                    'conversational': {
                        'role': 'USER',
                        'content': {'text': 'I prefer window seats and vegetarian meals on flights'}
                    }
                },
                {
                    'conversational': {
                        'role': 'ASSISTANT',
                        'content': {'text': 'I\'ve noted your preferences: window seats and vegetarian meals. I\'ll remember this for future bookings!'}
                    }
                }
            ]
        )
        print("✓ Event stored successfully")

        # Step 3: Retrieve short-term memory (events)
        print("\nRetrieving short-term memory...")
        events_response = data_client.list_events(
            memoryId=memory_id,
            actorId=actor_id,
            sessionId=session_id
        )

        events = events_response.get('events', [])
        print(f"✓ Short-term events retrieved: {len(events)} event(s)")

        if events:
            for event in events:
                payload = event.get('payload', [])
                for item in payload:
                    if 'conversational' in item:
                        conv = item['conversational']
                        role = conv.get('role', 'unknown')
                        content = conv.get('content', {}).get('text', '')[:50]
                        print(f"  - {role}: {content}...")

        # Step 4: Try to retrieve long-term memory
        # Note: Long-term extraction is async, may not be available immediately
        print("\nChecking for long-term memories (async extraction)...")
        try:
            records_response = data_client.retrieve_memory_records(
                memoryId=memory_id,
                namespace="preferences",
                searchCriteria={
                    'searchQuery': "travel preferences",
                    'topK': 5
                }
            )

            records = records_response.get('memoryRecords', [])
            if records:
                print(f"✓ Long-term memories found: {len(records)}")
                for record in records:
                    content = record.get('content', {}).get('text', 'N/A')[:60]
                    print(f"  - {content}...")
            else:
                print("  (Long-term extraction is async - memories will appear after processing)")
        except Exception as e:
            print(f"  (Long-term retrieval: {str(e)[:80]}...)")

        print("\n✓ Memory working successfully!")
        print(f"\nMemory ID: {memory_id}")
        print("Use this ID to retrieve memories in future sessions.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise

    finally:
        # Cleanup: Delete the memory resource
        print(f"\nCleaning up: Deleting memory {memory_name}...")
        try:
            control_client.delete_memory(memoryId=memory_id)
            print("✓ Memory deleted successfully")
        except Exception as cleanup_error:
            print(f"  Cleanup note: {cleanup_error}")


if __name__ == "__main__":
    main()
