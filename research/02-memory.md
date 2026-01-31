# AgentCore Memory

## Overview

AgentCore Memory is a fully managed service that gives AI agents the ability to remember past interactions, enabling intelligent, context-aware, and personalized conversations.

## The Problem It Solves

Without memory, AI agents are **stateless** - each interaction is treated as new with no knowledge of previous conversations. AgentCore Memory allows agents to build a coherent understanding of users over time.

## Memory Types

### Short-Term Memory
- Captures **turn-by-turn interactions** within a single session
- Maintains immediate context
- No need for users to repeat information

**Example**: User asks "What's the weather in Seattle?" then follows with "What about tomorrow?" - the agent understands "tomorrow" refers to Seattle weather.

### Long-Term Memory
- **Automatically extracts and stores key insights** across sessions
- Stores user preferences, important facts, session summaries
- Persistent knowledge retention across multiple sessions

**Example**: Customer mentions preference for window seats during flight booking. In future interactions, agent proactively offers window seats.

## Key Benefits

1. **Natural Conversations**: Context awareness, ambiguous statement resolution, human-like interaction
2. **Personalized Experiences**: Retain user preferences, historical data, key facts across sessions
3. **Reduced Development Complexity**: Offload conversational state management to focus on core business logic

## Use Cases

### Conversational Agents
Customer support chatbots remembering previous issues and preferences for more relevant assistance.

### Task-Oriented/Workflow Agents
AI orchestrating multi-step processes (invoice approval) tracks status of each step and maintains workflow progress.

### Multi-Agent Systems
Team of AI agents managing supply chain shares memory to:
- Synchronize inventory levels
- Anticipate demand
- Optimize logistics

### Autonomous/Planning Agents
Autonomous vehicles planning routes, adjusting to traffic, learning from past experiences.

## Framework Support

- LangGraph
- LangChain
- Strands
- LlamaIndex

## Pricing

- **Short-term memory**: Charged per event creation
- **Long-term memory**:
  - Per stored memory record (monthly)
  - Per retrieval request
