Your research agent needs hours, not seconds. Here's how to give it an 8-hour runway with a real browser:

![AgentCore Runtime](images/runtime-article.webp)

Deep research -- competitive analysis, market surveys, literature reviews -- means browsing dozens of pages and synthesizing findings over minutes or hours. Standard request-response patterns timeout long before the work is done.

AgentCore Runtime lets you deploy a LangGraph research agent that runs for up to **8 hours** in an isolated microVM, uses **AgentCore Browser** for real web interaction, and streams results back asynchronously. Deploy once, invoke with a topic, get a report -- no infrastructure to manage.

## Prerequisites

- AWS account with Bedrock AgentCore access
- Python 3.10+, AWS credentials configured
- Playwright installed (`playwright install chromium`)

## Environment Setup

```bash
# Install dependencies
pip install boto3 langgraph langchain-aws playwright
playwright install chromium

# Set environment variables
export AWS_REGION=us-east-1
```

## Implementation

### Define the Research Agent with LangGraph

```python
import json
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_aws import ChatBedrock
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.tools.browser_client import BrowserClient
from playwright.async_api import async_playwright

class ResearchState(TypedDict):
    topic: str
    urls_to_visit: list[str]
    pages_visited: list[dict]
    synthesis: str

llm = ChatBedrock(model_id="us.anthropic.claude-sonnet-4-20250514-v1:0", region_name="us-east-1")
browser_client = BrowserClient(region_name="us-east-1")

async def plan_research(state: ResearchState) -> dict:
    """Ask the LLM to generate target URLs for the research topic."""
    response = llm.invoke(
        f"Given the topic '{state['topic']}', return a JSON array of 5-10 "
        "URLs to visit for thorough research. Return ONLY the JSON array."
    )
    return {"urls_to_visit": json.loads(response.content)}

async def browse_pages(state: ResearchState) -> dict:
    """Visit each URL with AgentCore Browser and extract page content."""
    pages = []
    async with browser_client.start_session(
        browser_id="aws.browser.v1", timeout_seconds=3600
    ) as session:
        async with async_playwright() as pw:
            browser = await pw.chromium.connect_over_cdp(session.automation_stream_url)
            page = browser.contexts[0].pages[0]
            for url in state["urls_to_visit"]:
                try:
                    await page.goto(url, timeout=30000)
                    await page.wait_for_load_state("networkidle")
                    title = await page.title()
                    text = await page.inner_text("body")
                    pages.append({"url": url, "title": title, "content": text[:8000]})
                except Exception as e:
                    pages.append({"url": url, "error": str(e)})
    return {"pages_visited": pages}

async def synthesize(state: ResearchState) -> dict:
    """Synthesize browsed content into a structured research report."""
    sources = "\n\n".join(
        f"### {p['title']} ({p['url']})\n{p['content'][:3000]}"
        for p in state["pages_visited"] if "content" in p
    )
    response = llm.invoke(
        f"Based on these sources about '{state['topic']}', write a research "
        f"report with Executive Summary, Key Findings, and Recommendations."
        f"\n\nSources:\n{sources}"
    )
    return {"synthesis": response.content}

# Build the LangGraph: plan -> browse -> synthesize
graph = StateGraph(ResearchState)
graph.add_node("plan", plan_research)
graph.add_node("browse", browse_pages)
graph.add_node("synthesize", synthesize)
graph.set_entry_point("plan")
graph.add_edge("plan", "browse")
graph.add_edge("browse", "synthesize")
graph.add_edge("synthesize", END)
research_agent = graph.compile()

# Wrap in AgentCore Runtime
app = BedrockAgentCoreApp()

@app.entrypoint()
async def main(request):
    result = await research_agent.ainvoke({"topic": request.get("topic", "")})
    return {"report": result["synthesis"]}

if __name__ == "__main__":
    app.run()
```

### Deploy with 8-Hour Timeout

```bash
# Deploy the deep research agent to AgentCore Runtime
agentcore deploy \
    --name deep-research-agent \
    --memory 2048 \
    --timeout 28800 \
    --region us-east-1
```

### Invoke Asynchronously and Poll for Results

```python
import boto3, json

client = boto3.client("bedrock-agentcore", region_name="us-east-1")

response = client.invoke_agent_runtime(
    agentRuntimeArn="arn:aws:bedrock-agentcore:us-east-1:123456789012:agent/deep-research-agent",
    runtimeSessionId="research-session-001",
    payload=json.dumps({
        "topic": "Enterprise adoption patterns for AI agent frameworks in 2025"
    }).encode()
)

# Stream results -- the connection stays open while the agent works
for line in response["response"].iter_lines(chunk_size=10):
    if line:
        decoded = line.decode("utf-8")
        if decoded.startswith("data: "):
            print(decoded[6:])
```

## Key Benefits

- **8-hour execution**: Deep research runs as long as it needs -- no timeout gymnastics or chained Lambda calls
- **Real browser access**: AgentCore Browser navigates JavaScript-heavy pages, handles logins, and renders dynamic content that HTTP requests miss
- **I/O wait is free**: While the agent waits for pages to load or the LLM to respond, you are not billed for CPU -- critical for long-running research
- **Framework flexibility**: LangGraph manages the research graph; swap in CrewAI or Strands without changing the deployment

## Common Patterns

Research agents follow a plan-browse-synthesize loop. For deeper investigations, add a review node after synthesis that identifies knowledge gaps and feeds new URLs back to the browse step, repeating until coverage is sufficient or the time budget is spent.

## Next Steps

Start with a simple three-node graph (plan, browse, synthesize) targeting 5 URLs. Once validated, add iterative refinement loops and parallel browsing for faster coverage. Enable session recording on the Browser to audit what your agent actually saw during research.

📚 Documentation: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html
🌐 Browser service: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser.html
🔧 GitHub samples: https://github.com/awslabs/amazon-bedrock-agentcore-samples/

#AWS #AI #AgentCore #DeepResearch #LangGraph #Developers
