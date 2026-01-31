# AgentCore Pricing

## Pricing Model

**Consumption-based** with:
- No upfront commitments
- No minimum fees
- Pay only for what you use
- Each service billed independently

## Free Tier

**$200 in Free Tier credits** for new AWS customers to explore AgentCore services.

## Service-Specific Pricing

### Runtime, Browser, and Code Interpreter

Charged for:
- **Actual CPU consumption** (per second)
- **Peak memory consumed** (per second)

Key details:
- 1-second minimum billing
- 128MB minimum memory billing
- **I/O wait and idle time is FREE** (if no background process running)

This is particularly cost-effective for agents waiting on LLM responses.

### Gateway

Charged for:
- Number of **MCP operations** (ListTools, CallTool, Ping)
- **Search queries**
- **Tools indexed** for semantic search

### Identity

- **No charge** when used through AgentCore Runtime or Gateway
- Otherwise: per request for OAuth token or API key

### Memory

**Short-term Memory**:
- Per event creation

**Long-term Memory**:
- Per stored memory record (monthly)
- Per retrieval request

### Policy (Preview)

- **Currently no charge** during preview
- Post-preview: per 1,000 user input tokens for natural language policy conversion

### Evaluations (Preview)

- **Currently no charge** during preview

### Observability

Follows **Amazon CloudWatch pricing** for:
- Data ingestion
- Storage
- Queries

## Cost Optimization Tips

1. **I/O wait is free**: Design agents that spend time waiting for LLM responses rather than active CPU work
2. **Use Identity through Runtime/Gateway**: Avoid separate Identity charges
3. **Take advantage of previews**: Policy and Evaluations currently free
4. **Monitor with Observability**: Identify bottlenecks and optimize resource usage

## Pricing Page

For detailed pricing: [AgentCore Pricing](https://aws.amazon.com/bedrock/agentcore/pricing/)
