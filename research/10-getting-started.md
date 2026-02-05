# Getting Started with AgentCore

This guide walks you through everything you need to deploy your first AI agent on Amazon Bedrock AgentCore, from initial setup to production deployment.

---

## Quick Reference

### CLI Commands at a Glance

| Command | Description |
|---------|-------------|
| `agentcore create` | Create a new agent project (interactive) |
| `agentcore dev` | Start local development server |
| `agentcore invoke --dev "prompt"` | Test agent locally |
| `agentcore launch` | Deploy agent to AgentCore Runtime |
| `agentcore invoke '{"prompt": "..."}'` | Invoke deployed agent |
| `agentcore destroy` | Delete deployed resources |
| `agentcore configure` | Configure existing agent for deployment |
| `agentcore memory create` | Create memory resource |
| `agentcore memory list` | List memory resources |
| `agentcore gateway create-mcp-gateway` | Create a gateway |

### Environment Setup Checklist

- [ ] Python 3.10+ installed
- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] AWS credentials with appropriate permissions
- [ ] Model access enabled in Amazon Bedrock console
- [ ] Virtual environment created and activated
- [ ] AgentCore packages installed

---

## Prerequisites

### Python Requirements

AgentCore requires Python 3.10 or newer. Verify your version:

```bash
python3 --version
# Expected output: Python 3.10.x or higher
```

If you need to upgrade Python, use your package manager:

```bash
# macOS with Homebrew
brew install python@3.12

# Ubuntu/Debian
sudo apt update && sudo apt install python3.12

# Windows - Download from python.org
```

### AWS Account and Credentials

You need an AWS account with credentials configured. Install the AWS CLI if you haven't already:

```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Windows
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```

Configure your credentials:

```bash
aws configure
# Enter your Access Key ID, Secret Access Key, region (us-east-1), and output format (json)
```

Verify your credentials:

```bash
aws sts get-caller-identity
```

### IAM Permissions

#### Using AWS Managed Policy (Quickest)

Attach the `BedrockAgentCoreFullAccess` managed policy to your IAM user or role:

```bash
aws iam attach-user-policy \
  --user-name YOUR_USERNAME \
  --policy-arn arn:aws:iam::aws:policy/BedrockAgentCoreFullAccess
```

#### Starter Toolkit Permissions

The starter toolkit requires additional permissions for CodeBuild, ECR, and IAM role management. Create a custom policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "IAMRoleManagement",
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:GetRole",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:TagRole",
        "iam:ListRolePolicies",
        "iam:ListAttachedRolePolicies"
      ],
      "Resource": [
        "arn:aws:iam::*:role/*BedrockAgentCore*",
        "arn:aws:iam::*:role/service-role/*BedrockAgentCore*"
      ]
    },
    {
      "Sid": "CodeBuildProjectAccess",
      "Effect": "Allow",
      "Action": [
        "codebuild:StartBuild",
        "codebuild:BatchGetBuilds",
        "codebuild:ListBuildsForProject",
        "codebuild:CreateProject",
        "codebuild:UpdateProject",
        "codebuild:BatchGetProjects"
      ],
      "Resource": [
        "arn:aws:codebuild:*:*:project/bedrock-agentcore-*",
        "arn:aws:codebuild:*:*:build/bedrock-agentcore-*"
      ]
    },
    {
      "Sid": "CodeBuildListAccess",
      "Effect": "Allow",
      "Action": ["codebuild:ListProjects"],
      "Resource": "*"
    },
    {
      "Sid": "IAMPassRoleAccess",
      "Effect": "Allow",
      "Action": ["iam:PassRole"],
      "Resource": [
        "arn:aws:iam::*:role/AmazonBedrockAgentCore*",
        "arn:aws:iam::*:role/service-role/AmazonBedrockAgentCore*"
      ]
    },
    {
      "Sid": "CloudWatchLogsAccess",
      "Effect": "Allow",
      "Action": [
        "logs:GetLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ],
      "Resource": [
        "arn:aws:logs:*:*:log-group:/aws/bedrock-agentcore/*",
        "arn:aws:logs:*:*:log-group:/aws/codebuild/*"
      ]
    },
    {
      "Sid": "S3Access",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:CreateBucket",
        "s3:PutLifecycleConfiguration"
      ],
      "Resource": [
        "arn:aws:s3:::bedrock-agentcore-*",
        "arn:aws:s3:::bedrock-agentcore-*/*"
      ]
    },
    {
      "Sid": "ECRRepositoryAccess",
      "Effect": "Allow",
      "Action": [
        "ecr:CreateRepository",
        "ecr:DescribeRepositories",
        "ecr:GetRepositoryPolicy",
        "ecr:InitiateLayerUpload",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage",
        "ecr:UploadLayerPart",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:ListImages",
        "ecr:TagResource"
      ],
      "Resource": ["arn:aws:ecr:*:*:repository/bedrock-agentcore-*"]
    },
    {
      "Sid": "ECRAuthorizationAccess",
      "Effect": "Allow",
      "Action": ["ecr:GetAuthorizationToken"],
      "Resource": "*"
    }
  ]
}
```

Save this as `agentcore-toolkit-policy.json` and create the policy:

```bash
aws iam create-policy \
  --policy-name AgentCoreStarterToolkitPolicy \
  --policy-document file://agentcore-toolkit-policy.json
```

#### Execution Role for Runtime

When your agent runs in AgentCore Runtime, it assumes an execution role. The starter toolkit creates this automatically, but for custom deployments, create a role with this trust policy:

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

### Model Access

Enable foundation model access in the Amazon Bedrock console:

1. Navigate to Amazon Bedrock in the AWS Console
2. Go to Model Access in the left navigation
3. Click Manage Model Access
4. Enable the models you want to use (e.g., Anthropic Claude Sonnet 4.0)
5. Submit and wait for access to be granted

---

## Installation

### Step 1: Create Project Directory

```bash
mkdir my-agent-project
cd my-agent-project
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# On Windows: .venv\Scripts\activate
```

### Step 3: Upgrade pip

```bash
pip install --upgrade pip
```

### Step 4: Install AgentCore Packages

Install the core packages:

```bash
pip install bedrock-agentcore bedrock-agentcore-starter-toolkit
```

For specific frameworks, install additional packages:

```bash
# For Strands Agents (recommended for beginners)
pip install strands-agents

# For LangGraph
pip install langgraph langchain langchain-aws

# For OpenAI Agents SDK
pip install openai-agents

# For Google ADK
pip install google-adk

# For CrewAI
pip install crewai crewai-tools
```

### Step 5: Verify Installation

```bash
agentcore --help
```

You should see the CLI help output with available commands:

```
Usage: agentcore [OPTIONS] COMMAND [ARGS]...

  Amazon Bedrock AgentCore Starter Toolkit CLI

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  configure  Configure an existing agent for deployment
  create     Create a new agent project
  deploy     Deploy agent (alias for launch)
  destroy    Delete deployed resources
  dev        Start local development server
  gateway    Gateway management commands
  invoke     Invoke your agent
  launch     Deploy agent to AgentCore Runtime
  memory     Memory management commands
```

---

## Your First Agent

### Step 1: Create Your Agent

Run the interactive creation wizard:

```bash
agentcore create
```

The wizard prompts you to:

1. **Choose a framework**: Select from Strands Agents, LangGraph, OpenAI Agents SDK, or Google ADK
2. **Provide a project name**: Enter a name for your agent
3. **Select a model provider**: Choose Amazon Bedrock, OpenAI, Anthropic, or Gemini
4. **Configure additional options**: Memory, Gateway, Observability

This generates:

- Agent code with your selected framework
- `.bedrock_agentcore.yaml` configuration file
- `requirements.txt` with dependencies
- Basic project structure

### Step 2: Explore the Generated Files

After creation, your project structure looks like this:

```
my-agent/
├── agent.py              # Main agent code
├── requirements.txt      # Python dependencies
├── .bedrock_agentcore.yaml   # AgentCore configuration
└── README.md             # Project documentation
```

Examine the generated `agent.py`:

```python
from strands import Agent
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Create agent with optional tools
agent = Agent()

# Initialize AgentCore app
app = BedrockAgentCoreApp()

@app.entrypoint
def agent_invocation(payload, context):
    """Handler for agent invocation"""
    user_message = payload.get("prompt", "Hello!")
    result = agent(user_message)
    return {"result": result.message}

app.run()
```

### Step 3: Test Locally

Start the local development server:

```bash
agentcore dev
```

This starts a server on `http://localhost:8080` that mimics the AgentCore Runtime.

In a separate terminal, test your agent:

```bash
agentcore invoke --dev "Hello! What can you help me with?"
```

You should see a response from your agent.

### Step 4: Deploy to AgentCore Runtime

When you're satisfied with local testing, deploy:

```bash
agentcore launch
```

This command:

- Builds your container using AWS CodeBuild (no Docker required locally)
- Creates necessary AWS resources (IAM roles, ECR repository)
- Deploys to AgentCore Runtime
- Configures CloudWatch logging

Note the ARN in the output - you'll need it for programmatic invocation.

### Step 5: Test Your Deployed Agent

```bash
agentcore invoke '{"prompt": "Tell me a joke"}'
```

If you see a joke in the response, congratulations - your agent is running in the cloud!

### Step 6: Invoke Programmatically

Create `invoke_agent.py`:

```python
import json
import uuid
import boto3

# Replace with your agent ARN from agentcore launch output
AGENT_ARN = "arn:aws:bedrock-agentcore:us-east-1:123456789012:agent-runtime/my-agent"

def invoke_agent(prompt: str) -> dict:
    client = boto3.client('bedrock-agentcore')

    response = client.invoke_agent_runtime(
        agentRuntimeArn=AGENT_ARN,
        runtimeSessionId=str(uuid.uuid4()),
        payload=json.dumps({"prompt": prompt}).encode(),
        qualifier="DEFAULT"
    )

    content = []
    for chunk in response.get("response", []):
        content.append(chunk.decode('utf-8'))

    return json.loads(''.join(content))

if __name__ == "__main__":
    result = invoke_agent("What's the weather like today?")
    print(result)
```

Run it:

```bash
python invoke_agent.py
```

---

## Framework-Specific Quickstarts

### Strands Agents

Strands Agents is the recommended framework for beginners. It's simple, Pythonic, and integrates well with AWS services.

```python
from strands import Agent
from strands_tools import file_read, file_write, editor
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Create agent with tools
agent = Agent(tools=[file_read, file_write, editor])

app = BedrockAgentCoreApp()

@app.entrypoint
def agent_invocation(payload, context):
    user_message = payload.get("prompt", "No prompt provided")
    result = agent(user_message)
    print(f"Context: {context}")
    print(f"Result: {result}")
    return {"result": result.message}

app.run()
```

Install dependencies:

```bash
pip install strands-agents strands-tools
```

Full example: [GitHub - Strands Agents](https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/03-integrations/agentic-frameworks/strands-agents)

### LangGraph

LangGraph provides a graph-based approach to building agents with fine-grained control over execution flow.

```python
from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

# Initialize LLM
llm = init_chat_model(
    "us.anthropic.claude-3-5-haiku-20241022-v1:0",
    model_provider="bedrock_converse",
)

# Define state
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Create graph
graph_builder = StateGraph(State)

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()

@app.entrypoint
def agent_invocation(payload, context):
    prompt = payload.get("prompt", "Hello!")
    messages = {"messages": [{"role": "user", "content": prompt}]}
    output = graph.invoke(messages)
    return {"result": output['messages'][-1].content}

app.run()
```

Install dependencies:

```bash
pip install langgraph langchain langchain-aws
```

Full example: [GitHub - LangGraph](https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/03-integrations/agentic-frameworks/langgraph)

### OpenAI Agents SDK

Use the OpenAI Agents SDK with AgentCore for agents that leverage OpenAI's tooling.

```python
from agents import Agent, Runner, WebSearchTool
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import asyncio

app = BedrockAgentCoreApp()

# Create agent with web search capability
agent = Agent(
    name="Assistant",
    tools=[WebSearchTool()],
)

async def run_agent(query: str):
    result = await Runner.run(agent, query)
    return result

@app.entrypoint
async def agent_invocation(payload, context):
    query = payload.get("prompt", "How can I help you today?")
    result = await run_agent(query)
    return {"result": result.final_output}

app.run()
```

Install dependencies:

```bash
pip install openai-agents
```

Full example: [GitHub - OpenAI Agents](https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/03-integrations/agentic-frameworks/openai-agents)

### Google ADK

The Google Agent Development Kit integrates with Gemini and provides built-in tools.

```python
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types
import asyncio
from bedrock_agentcore.runtime import BedrockAgentCoreApp

APP_NAME = "google_search_agent"
USER_ID = "user1234"

# Create agent with Google Search
root_agent = Agent(
    model="gemini-2.0-flash",
    name="search_agent",
    description="Agent to answer questions using Google Search.",
    instruction="I can answer your questions by searching the internet.",
    tools=[google_search]
)

async def call_agent(query: str, user_id: str, session_id: str):
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run_async(user_id=user_id, session_id=session_id, new_message=content)

    async for event in events:
        if event.is_final_response():
            return event.content.parts[0].text
    return "No response"

app = BedrockAgentCoreApp()

@app.entrypoint
def agent_invocation(payload, context):
    query = payload.get("prompt", "What is Bedrock AgentCore Runtime?")
    user_id = payload.get("user_id", USER_ID)
    return asyncio.run(call_agent(query, user_id, context.session_id))

app.run()
```

Install dependencies:

```bash
pip install google-adk
```

Full example: [GitHub - Google ADK](https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/03-integrations/agentic-frameworks/adk)

### CrewAI

CrewAI enables multi-agent collaboration with specialized roles.

```python
from crewai import Agent, Crew, Process, Task
from crewai_tools import MathTool, WeatherTool
from langchain_aws import ChatBedrock
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

def create_crew():
    llm = ChatBedrock(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        model_kwargs={"temperature": 0.1}
    )

    researcher = Agent(
        role="Senior Research Specialist",
        goal="Find comprehensive and accurate information",
        backstory="Experienced research specialist with talent for finding relevant information.",
        verbose=True,
        llm=llm,
        tools=[MathTool(), WeatherTool()]
    )

    analyst = Agent(
        role="Data Analyst",
        goal="Analyze and synthesize research findings",
        backstory="Expert analyst who transforms raw data into insights.",
        verbose=True,
        llm=llm
    )

    research_task = Task(
        description="Research the topic: {topic}",
        agent=researcher,
        expected_output="Comprehensive research findings"
    )

    analysis_task = Task(
        description="Analyze research findings and provide recommendations",
        agent=analyst,
        expected_output="Analysis report with recommendations",
        context=[research_task]
    )

    return Crew(
        agents=[researcher, analyst],
        tasks=[research_task, analysis_task],
        process=Process.sequential,
        verbose=True
    )

crew = create_crew()

@app.entrypoint
def crewai_agent(payload):
    topic = payload.get("prompt", "AI agents")
    result = crew.kickoff(inputs={"topic": topic})
    return result.raw

app.run()
```

Install dependencies:

```bash
pip install crewai crewai-tools langchain-aws
```

Full example: [GitHub - CrewAI](https://github.com/awslabs/amazon-bedrock-agentcore-samples/blob/main/01-tutorials/01-AgentCore-runtime/01-hosting-agent/04-crewai-with-bedrock-model/)

---

## Local Development

### Development Server

The `agentcore dev` command starts a local server that mimics AgentCore Runtime:

```bash
agentcore dev
```

Options:

- `--port PORT`: Change the default port (8080)
- `--host HOST`: Change the default host (localhost)
- `--reload`: Enable auto-reload on code changes

### Testing Locally

Use the `--dev` flag with `agentcore invoke`:

```bash
# Simple text prompt
agentcore invoke --dev "What is 2 + 2?"

# JSON payload
agentcore invoke --dev '{"prompt": "Summarize this document", "document": "..."}'
```

### Debugging

Enable verbose logging in your agent:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.entrypoint
def agent_invocation(payload, context):
    logger.debug(f"Received payload: {payload}")
    logger.debug(f"Context: {context}")
    # ... rest of your code
```

### Environment Variables

Set environment variables for local development:

```bash
# AWS region
export AWS_DEFAULT_REGION=us-east-1

# For non-Bedrock model providers
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GOOGLE_API_KEY=...
```

---

## Deployment Options

### CLI Deploy (Recommended)

The simplest option using AWS CodeBuild (no Docker required locally):

```bash
agentcore launch
```

This is the recommended approach for most use cases.

### Local Build + Cloud Deploy

If you have Docker installed and want to build locally:

```bash
agentcore launch --local-build
```

This builds the container on your machine and pushes to ECR.

### Fully Local Development

For development and testing only:

```bash
agentcore launch --local
```

This builds and runs entirely locally (requires Docker).

### Comparison

| Method | Docker Required | Build Location | Best For |
|--------|-----------------|----------------|----------|
| `agentcore launch` | No | AWS CodeBuild | Most users |
| `agentcore launch --local-build` | Yes | Local machine | Build customization |
| `agentcore launch --local` | Yes | Local machine | Development only |

### Custom Execution Role

Use an existing IAM role:

```bash
agentcore configure -e agent.py --execution-role arn:aws:iam::123456789012:role/MyRole
agentcore launch
```

### ARM64 Requirement

AgentCore Runtime requires ARM64 containers (AWS Graviton). The toolkit handles this automatically:

- **Default (CodeBuild)**: Builds ARM64 containers in the cloud
- **Local build**: Only works correctly on ARM64 machines (Apple Silicon, Graviton)

---

## Configuration Deep Dive

### The .bedrock_agentcore.yaml File

After running `agentcore create` or `agentcore configure`, a `.bedrock_agentcore.yaml` file is generated:

```yaml
agentcore:
  version: "1.0"

project:
  name: my-agent
  description: A helpful AI agent

runtime:
  entrypoint: agent.py
  runtime_type: python
  python_version: "3.11"

  # Resource configuration
  memory_size: 512  # MB
  timeout: 300      # seconds

  # Environment variables
  environment:
    LOG_LEVEL: INFO

# Optional: Memory configuration
memory:
  enabled: true
  memory_id: null  # Auto-created if null

# Optional: Gateway configuration
gateway:
  enabled: false
  gateway_id: null

# Optional: Observability
observability:
  enabled: true

# Deployment configuration
deployment:
  region: us-east-1
  execution_role_arn: null  # Auto-created if null
```

### Environment Variables

Configure environment variables in your agent:

**Option 1: In .bedrock_agentcore.yaml**

```yaml
runtime:
  environment:
    MY_API_KEY: secret-value
    DEBUG_MODE: "true"
```

**Option 2: At runtime via AWS Console**

Set environment variables in the AgentCore Runtime configuration.

**Option 3: AWS Secrets Manager**

For sensitive values, use Secrets Manager:

```python
import boto3

def get_secret(secret_name: str) -> str:
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

# In your agent
api_key = get_secret("my-api-key")
```

### Secrets Management Best Practices

1. Never hardcode secrets in your agent code
2. Use environment variables for non-sensitive configuration
3. Use AWS Secrets Manager for API keys, passwords, credentials
4. Grant your execution role permission to access secrets

---

## Adding Services

### Adding Memory

Memory provides context persistence for your agents with short-term (session) and long-term (cross-session) storage.

**Step 1: Create Memory Resource**

```bash
agentcore memory create CustomerSupport \
  --region us-east-1 \
  --description "Customer support memory" \
  --strategies '[{"semanticMemoryStrategy": {"name": "semanticLTM", "namespaces": ["/strategies/{memoryStrategyId}/actors/{actorId}/"]}}]' \
  --wait
```

**Step 2: Integrate with Your Agent**

```python
from bedrock_agentcore.memory.session import MemorySessionManager
from bedrock_agentcore.memory.constants import ConversationalMessage, MessageRole

# Initialize memory session
session_manager = MemorySessionManager(
    memory_id="YOUR_MEMORY_ID",
    region_name="us-east-1"
)

@app.entrypoint
def agent_invocation(payload, context):
    # Create or get session
    session = session_manager.create_memory_session(
        actor_id=payload.get("user_id", "default"),
        session_id=context.session_id
    )

    # Get conversation history
    turns = session.get_last_k_turns(k=10)

    # Process with agent
    result = agent(payload.get("prompt"))

    # Store the interaction
    session.add_turns(messages=[
        ConversationalMessage(payload.get("prompt"), MessageRole.USER),
        ConversationalMessage(result.message, MessageRole.ASSISTANT)
    ])

    return {"result": result.message}
```

### Adding Gateway

Gateway provides secure tool and API connections for your agents.

**Step 1: Create Gateway**

```bash
agentcore gateway create-mcp-gateway \
  --name MyGateway \
  --region us-east-1 \
  --enable_semantic_search
```

**Step 2: Add Targets**

```bash
# Add a Lambda target
agentcore gateway create-mcp-gateway-target \
  --gateway-arn arn:aws:bedrock-agentcore:us-east-1:123456789012:gateway/my-gateway \
  --gateway-url https://gateway.bedrock-agentcore.us-east-1.amazonaws.com/my-gateway \
  --name MyLambdaTarget \
  --target-type lambda
```

**Step 3: Connect to Your Agent**

```python
from strands import Agent
from strands.tools.mcp import MCPClient

# Connect to gateway
mcp_client = MCPClient(gateway_url="YOUR_GATEWAY_URL")

# Create agent with gateway tools
agent = Agent(tools=mcp_client.list_tools())
```

### Adding Code Interpreter

Code Interpreter enables secure Python/JavaScript execution.

```python
from bedrock_agentcore.tools import CodeInterpreter

# Create interpreter
interpreter = CodeInterpreter(
    region_name="us-east-1",
    # Optional: VPC configuration for network access
)

# Execute code
result = interpreter.execute("""
import pandas as pd
import matplotlib.pyplot as plt

# Your data analysis code here
data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
print(data.describe())
""")

print(result.output)
```

### Adding Browser

Browser enables web interaction capabilities.

```python
from bedrock_agentcore.tools import Browser

# Create browser instance
browser = Browser(
    region_name="us-east-1",
    # Optional: session recording
    record_session=True
)

# Navigate and interact
browser.navigate("https://example.com")
content = browser.get_page_content()
browser.click("#submit-button")
```

---

## Code Examples

### Example 1: Customer Support Agent

A complete customer support agent with memory and tools:

```python
from strands import Agent
from strands_tools import file_read
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory.session import MemorySessionManager
from bedrock_agentcore.memory.constants import ConversationalMessage, MessageRole

app = BedrockAgentCoreApp()

# Initialize memory
memory_manager = MemorySessionManager(
    memory_id="customer-support-memory",
    region_name="us-east-1"
)

# Create agent with system prompt
agent = Agent(
    system_prompt="""You are a helpful customer support agent.
    Be polite, professional, and helpful.
    If you don't know the answer, say so and offer to escalate.""",
    tools=[file_read]
)

@app.entrypoint
def support_agent(payload, context):
    user_id = payload.get("user_id", "anonymous")
    prompt = payload.get("prompt", "")

    # Get or create session
    session = memory_manager.create_memory_session(
        actor_id=user_id,
        session_id=context.session_id
    )

    # Get conversation history for context
    history = session.get_last_k_turns(k=5)

    # Build context from history
    context_prompt = ""
    for turn in history:
        context_prompt += f"{turn.role}: {turn.content}\n"

    # Invoke agent with context
    full_prompt = f"Previous conversation:\n{context_prompt}\n\nUser: {prompt}"
    result = agent(full_prompt)

    # Store interaction
    session.add_turns(messages=[
        ConversationalMessage(prompt, MessageRole.USER),
        ConversationalMessage(result.message, MessageRole.ASSISTANT)
    ])

    return {"result": result.message, "session_id": context.session_id}

app.run()
```

### Example 2: Research Agent with Web Search

An agent that can search the web and synthesize information:

```python
from strands import Agent
from strands.tools.mcp import MCPClient
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

# Connect to gateway with web search tool
mcp_client = MCPClient(gateway_url="YOUR_GATEWAY_URL")

agent = Agent(
    system_prompt="""You are a research assistant.
    Use the web search tool to find accurate, up-to-date information.
    Always cite your sources.
    Synthesize information from multiple sources when possible.""",
    tools=mcp_client.list_tools()
)

@app.entrypoint
def research_agent(payload, context):
    query = payload.get("prompt", "")
    depth = payload.get("depth", "brief")  # brief, standard, comprehensive

    if depth == "comprehensive":
        prompt = f"""Conduct comprehensive research on: {query}

        1. Search for multiple perspectives
        2. Find recent developments
        3. Include historical context
        4. Cite all sources"""
    else:
        prompt = f"Research and summarize: {query}"

    result = agent(prompt)
    return {"result": result.message}

app.run()
```

### Example 3: Data Analysis Agent

An agent that uses Code Interpreter for data analysis:

```python
from strands import Agent
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.tools import CodeInterpreter

app = BedrockAgentCoreApp()

interpreter = CodeInterpreter(region_name="us-east-1")

agent = Agent(
    system_prompt="""You are a data analysis assistant.
    When given data, write Python code to analyze it.
    Use pandas, matplotlib, and numpy as needed.
    Explain your findings clearly."""
)

@app.entrypoint
def analysis_agent(payload, context):
    data = payload.get("data")
    question = payload.get("prompt", "Analyze this data")

    # Have the agent generate analysis code
    code_prompt = f"""Given this data:
    {data}

    Question: {question}

    Write Python code to analyze this data and answer the question.
    Use pandas for data manipulation and matplotlib for visualization."""

    result = agent(code_prompt)

    # Extract and execute the code
    code = extract_code_block(result.message)
    if code:
        execution_result = interpreter.execute(code)
        return {
            "analysis": result.message,
            "execution_output": execution_result.output,
            "charts": execution_result.artifacts
        }

    return {"result": result.message}

def extract_code_block(text: str) -> str:
    """Extract Python code from markdown code blocks"""
    import re
    pattern = r'```python\n(.*?)\n```'
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[0] if matches else None

app.run()
```

### Example 4: Multi-Agent Orchestrator

Coordinate multiple specialized agents:

```python
from strands import Agent
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

# Specialized agents
researcher = Agent(
    system_prompt="You are a research specialist. Find and summarize information."
)

writer = Agent(
    system_prompt="You are a technical writer. Create clear, well-structured documents."
)

reviewer = Agent(
    system_prompt="You are an editor. Review content for accuracy and clarity."
)

orchestrator = Agent(
    system_prompt="""You are an orchestrator managing a team of specialists:
    - Researcher: For finding information
    - Writer: For creating content
    - Reviewer: For quality checks

    Coordinate their work to complete tasks efficiently."""
)

@app.entrypoint
def orchestrated_agent(payload, context):
    task = payload.get("prompt", "")
    task_type = payload.get("type", "research")

    if task_type == "research":
        # Single agent task
        return {"result": researcher(task).message}

    elif task_type == "document":
        # Multi-agent pipeline
        research = researcher(f"Research: {task}")
        draft = writer(f"Based on this research, create a document:\n{research.message}")
        final = reviewer(f"Review and improve this document:\n{draft.message}")

        return {
            "research": research.message,
            "draft": draft.message,
            "final": final.message
        }

    else:
        # Let orchestrator decide
        return {"result": orchestrator(task).message}

app.run()
```

---

## Common Patterns

### Multi-Agent Coordination

**Pattern 1: Sequential Pipeline**

```python
result1 = agent1(task)
result2 = agent2(result1.message)
result3 = agent3(result2.message)
```

**Pattern 2: Parallel Execution**

```python
import asyncio

async def parallel_agents(task):
    results = await asyncio.gather(
        agent1.arun(task),
        agent2.arun(task),
        agent3.arun(task)
    )
    return results
```

**Pattern 3: Router Pattern**

```python
def route_to_agent(task):
    classification = classifier_agent(f"Classify this task: {task}")

    if "research" in classification.message.lower():
        return research_agent(task)
    elif "code" in classification.message.lower():
        return coding_agent(task)
    else:
        return general_agent(task)
```

### Tool Integration Patterns

**Pattern 1: Conditional Tool Use**

```python
agent = Agent(tools=[tool1, tool2])

@app.entrypoint
def handler(payload, context):
    task = payload.get("prompt")
    use_tools = payload.get("use_tools", True)

    if use_tools:
        return {"result": agent(task).message}
    else:
        # Direct model call without tools
        return {"result": agent.model.invoke(task)}
```

**Pattern 2: Tool Chaining**

```python
@app.entrypoint
def handler(payload, context):
    # Step 1: Search
    search_results = search_tool.run(payload.get("query"))

    # Step 2: Analyze with agent
    analysis = agent(f"Analyze these results: {search_results}")

    # Step 3: Store results
    storage_tool.save(analysis.message)

    return {"result": analysis.message}
```

### Memory Patterns

**Pattern 1: Conversation Memory**

```python
session = memory_manager.create_memory_session(actor_id, session_id)
history = session.get_last_k_turns(k=10)
```

**Pattern 2: Semantic Memory Search**

```python
# Find relevant past interactions
relevant_memories = session.search_long_term_memories(
    query="customer complaint about shipping",
    namespace_prefix="/",
    top_k=5
)
```

**Pattern 3: Memory with TTL**

```python
# Short-term memory expires after session
session.add_turns(messages, ttl=3600)  # 1 hour

# Long-term memory persists
session.add_long_term_memory(fact="User prefers email communication")
```

---

## Troubleshooting First Deployment

### Common Errors and Solutions

#### Permission Denied Errors

**Symptom**: `AccessDenied` or `UnauthorizedAccess` errors

**Solutions**:

1. Verify AWS credentials:
   ```bash
   aws sts get-caller-identity
   ```

2. Check IAM policies are attached:
   ```bash
   aws iam list-attached-user-policies --user-name YOUR_USER
   ```

3. Ensure `BedrockAgentCoreFullAccess` policy is attached

#### Model Access Denied

**Symptom**: `ResourceNotFoundException` or model access errors

**Solutions**:

1. Enable model access in Bedrock console
2. Verify you're in the correct region:
   ```bash
   aws configure get region
   ```
3. Check model is available in your region

#### CodeBuild Failures

**Symptom**: Deployment fails during build phase

**Solutions**:

1. Check CodeBuild logs in AWS Console:
   - Navigate to CodeBuild > Build history
   - Find your build and view logs

2. Common causes:
   - Invalid `requirements.txt`
   - Missing dependencies
   - Python version mismatch

3. Fix and retry:
   ```bash
   agentcore destroy
   agentcore launch
   ```

#### Port 8080 In Use (Local Development)

**Symptom**: `Address already in use` error

**Solutions**:

```bash
# Find process using port 8080
lsof -ti:8080

# Kill the process
kill -9 $(lsof -ti:8080)

# Or use a different port
agentcore dev --port 8081
```

#### Region Mismatch

**Symptom**: Resources not found or inconsistent behavior

**Solutions**:

1. Check your configured region:
   ```bash
   aws configure get region
   ```

2. Set region explicitly:
   ```bash
   export AWS_DEFAULT_REGION=us-east-1
   ```

3. Ensure all resources are in the same region

#### Container Build Issues

**Symptom**: Local build fails with architecture errors

**Solutions**:

1. Use CodeBuild (recommended):
   ```bash
   agentcore launch  # No --local-build flag
   ```

2. If building locally, ensure ARM64 architecture:
   ```bash
   # Check your architecture
   uname -m  # Should show arm64 on Apple Silicon
   ```

### Viewing Logs

**CloudWatch Logs**:

1. Navigate to CloudWatch > Log groups
2. Find `/aws/bedrock-agentcore/runtimes/{agent-id}-DEFAULT`
3. View log streams for recent invocations

**CLI Log Access**:

```bash
aws logs describe-log-streams \
  --log-group-name /aws/bedrock-agentcore/runtimes/YOUR_AGENT_ID-DEFAULT

aws logs get-log-events \
  --log-group-name /aws/bedrock-agentcore/runtimes/YOUR_AGENT_ID-DEFAULT \
  --log-stream-name STREAM_NAME
```

### Resource Cleanup

If deployment fails, clean up resources:

```bash
agentcore destroy
```

Manual cleanup if needed:

```bash
# Delete ECR repository
aws ecr delete-repository --repository-name bedrock-agentcore-YOUR_AGENT --force

# Delete IAM role
aws iam delete-role --role-name AmazonBedrockAgentCoreRole-YOUR_AGENT
```

---

## Next Steps

### Advanced Topics

- [Runtime Deep Dive](01-runtime.md) - Understanding AgentCore Runtime internals
- [Memory Patterns](02-memory.md) - Advanced memory strategies
- [Gateway Configuration](03-gateway.md) - Tool and API integration
- [Identity & Auth](04-identity.md) - OAuth, SSO, and user federation
- [Code Interpreter](05-code-interpreter.md) - Secure code execution
- [Browser Automation](06-browser.md) - Web interaction capabilities
- [Observability](08-observability.md) - Tracing and monitoring
- [Evaluations](09-evaluations.md) - Quality assessment

### Documentation & Resources

- [AWS Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [GitHub Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples/)
- [Strands Agents Documentation](https://strandsagents.com/latest/documentation/docs/)
- [Starter Toolkit CLI Reference](https://aws.github.io/bedrock-agentcore-starter-toolkit/api-reference/cli.html)

### Available Interfaces

| Interface | Use Case |
|-----------|----------|
| **AgentCore Starter Toolkit (CLI)** | Project creation, deployment, management |
| **AgentCore Python SDK** | Agent development with built-in features |
| **AWS SDK (Boto3)** | Advanced operations, integration |
| **AgentCore MCP Server** | IDE integration (Kiro, Cursor, Claude Code) |
| **AWS Console** | Visual management and testing |

### Supported Regions

AgentCore is available in:

- `us-east-1` (N. Virginia)
- `us-west-2` (Oregon)
- `eu-central-1` (Frankfurt)
- `ap-southeast-2` (Sydney)

### Getting Help

- File issues on [GitHub](https://github.com/awslabs/amazon-bedrock-agentcore-samples/issues)
- Ask questions on [AWS re:Post](https://repost.aws/tags/TA4cPjihK9RBuJxO4qjA9L3g/amazon-bedrock)
- Review [troubleshooting documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-troubleshooting.html)
