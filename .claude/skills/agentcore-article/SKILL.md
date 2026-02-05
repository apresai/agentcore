---
name: agentcore-article
description: Generate AgentCore articles with research, runnable code examples, and builder-themed art
---

# AgentCore Article Generator

Generate LinkedIn articles showcasing AWS Bedrock AgentCore features with researched content, **fully runnable code examples**, and Lego builder-themed artwork in AWS brand colors.

> **Related Skills:**
> - Use `/agentcore` skill for help building agents (API usage, troubleshooting, code patterns)
> - Use this skill (`/agentcore-article`) for creating articles and content

## Knowledge Base Location

This skill operates on the AgentCore knowledge base at `/Users/chad/dev/agentcore/`:

```
/Users/chad/dev/agentcore/
├── research/           # Documentation summaries (source of truth)
├── articles/           # Published articles
│   ├── examples/       # Runnable code examples
│   └── images/         # Generated artwork
└── .claude/skills/     # This skill and /agentcore skill
```

## Workflow

### Step 1: Gather Requirements

Use `AskUserQuestion` with these questions:

```json
{
  "questions": [
    {
      "question": "Which AgentCore feature should the article focus on?",
      "header": "Feature",
      "options": [
        {"label": "Memory", "description": "Short-term and long-term agent memory"},
        {"label": "Runtime", "description": "Serverless microVM agent hosting"},
        {"label": "Gateway", "description": "Convert APIs/Lambda to MCP tools"},
        {"label": "Identity", "description": "Agent authentication and credentials"}
      ],
      "multiSelect": false
    },
    {
      "question": "What article format do you want?",
      "header": "Format",
      "options": [
        {"label": "Short (~5 min read)", "description": "1,500-2,000 chars - Hook + setup + working example + CTA"},
        {"label": "Standard (5-10 min read)", "description": "3,000-5,000 chars - Full tutorial with prerequisites and examples"},
        {"label": "Long (~30 min read)", "description": "8,000-15,000 chars - Comprehensive guide with multiple examples"}
      ],
      "multiSelect": false
    },
    {
      "question": "Who is the target audience?",
      "header": "Audience",
      "options": [
        {"label": "Developers", "description": "Hands-on builders who want code"},
        {"label": "Architects", "description": "Technical decision makers evaluating solutions"},
        {"label": "Decision makers", "description": "Business/tech leaders evaluating AI investments"}
      ],
      "multiSelect": false
    },
    {
      "question": "What programming language for code examples?",
      "header": "Language",
      "options": [
        {"label": "Python", "description": "Most common for AI/ML workloads"},
        {"label": "TypeScript", "description": "Full-stack and Node.js developers"},
        {"label": "Go", "description": "Systems and infrastructure developers"}
      ],
      "multiSelect": false
    }
  ]
}
```

If user selects "Other" for feature, ask which specific service:
- Code Interpreter (secure Python/JS/TS execution)
- Browser (isolated web interaction)
- Policy (Cedar-based access control)
- Observability (OTEL tracing)
- Evaluations (LLM-as-a-Judge quality assessment)

### Step 2: Research Phase

1. **Read existing research** from `research/` directory:
   - `research/00-overview.md` - Always read for context
   - `research/XX-feature.md` - Read file matching selected feature

2. **Search AWS documentation** using `mcp__aws-mcp__aws___search_documentation`:
   ```
   search_phrase: "Bedrock AgentCore [feature]"
   topics: ["reference_documentation", "current_awareness"]
   ```

3. **Web search for recent updates** using `WebSearch`:
   - Query: "AWS Bedrock AgentCore [feature] 2026"
   - Look for announcements, blog posts, case studies

4. **Identify new data** - Note any information not in research files

### Step 3: Update Knowledge Base

If new provable data was found:

1. Read the appropriate `research/XX-feature.md` file
2. Add new information following existing format:
   - Use markdown headers matching existing style
   - Include source attribution for new data
   - Keep factual, avoid marketing language
3. Use `Edit` tool to add new sections

**Only add information that is:**
- Documented in official AWS sources
- Verifiable and specific (not vague claims)
- Not already present in research files

### Step 4: Plan Code Examples

**CRITICAL: All code must be REAL and RUNNABLE, not pseudo-code snippets.**

Based on format, plan the code:

| Format | Code Requirements |
|--------|-------------------|
| **Short** | 15-30 line complete example with imports, verification output |
| **Standard** | 40-60 line working example with setup, implementation, verification |
| **Long** | Multiple files: main implementation, helper functions, tests |

**Code requirements:**
- Must be copy-paste runnable from terminal
- Include ALL necessary imports at the top
- Include verification step that prints success output
- Show expected terminal output in comments or docstring
- **Show both SDK options**: AgentCore SDK as primary, boto3 as alternative
- Reference official AWS SDK patterns

**SDK options to demonstrate:**
```python
# Option 1: AgentCore SDK (recommended)
from agentcore import AgentCoreClient

# Option 2: boto3 (lower-level)
import boto3
client = boto3.client('bedrock-agentcore')
```

**AgentCore CLI commands reference:**
```bash
agentcore create    # Create new agent
agentcore deploy    # Deploy agent to Runtime
agentcore invoke    # Invoke deployed agent
agentcore tools     # Manage Gateway tools
```

**Every code example must include:**
1. A comment header with what the code does
2. All imports
3. Configuration/setup section
4. Main implementation
5. Verification that prints success (e.g., "✓ Agent deployed: agent-123")

### Step 5: Generate Builder Art

Use `gimage generate` with Lego builder theme in **AWS brand colors**.

**AWS Brand Colors (REQUIRED in all prompts):**
- Primary: AWS Orange (#FF9900) - use for accents, highlights, key elements
- Secondary: AWS Dark Blue (#232F3E) - use for backgrounds, structures
- Accent: White and light grays - use for contrast and highlights

**Base prompt template:**
```
[Feature concept] depicted as a scene with Lego minifigures building/assembling [visual metaphor], AWS orange (#FF9900) accents on key elements, dark blue (#232F3E) background structures, AWS logo visible on a banner or screen, clean professional lighting, product photography style, shallow depth of field, miniature scale
```

**Feature-specific prompts:**

| Feature | Prompt |
|---------|--------|
| **Memory** | "Lego minifigures organizing glowing AWS orange (#FF9900) memory blocks into dark blue (#232F3E) wooden shelves, AWS logo on a small digital display, warm studio lighting, tilt-shift photography style" |
| **Runtime** | "Lego construction workers building a futuristic serverless structure from AWS orange (#FF9900) blocks on dark blue (#232F3E) platform, AWS logo on a blueprint nearby, architectural model lighting" |
| **Gateway** | "Lego engineers connecting AWS orange (#FF9900) API bridge pieces between two dark blue (#232F3E) platforms, AWS logo illuminated sign overhead, technical workshop setting" |
| **Identity** | "Lego security guards with tiny orange (#FF9900) ID badges standing at a glowing gateway with dark blue (#232F3E) frame, AWS logo on badge scanner, dramatic spotlight lighting" |
| **Code Interpreter** | "Lego scientist minifigures working at tiny computer terminals with orange (#FF9900) code on dark blue (#232F3E) screens, AWS logo on lab coat, laboratory setting" |
| **Browser** | "Lego explorers navigating through a miniature web of orange (#FF9900) connected screens on dark blue (#232F3E) background, AWS logo on compass, adventure diorama style" |
| **Policy** | "Lego judges holding tiny orange (#FF9900) rule books at a small dark blue (#232F3E) courtroom bench, AWS logo gavel, formal miniature setting" |
| **Observability** | "Lego detectives examining orange (#FF9900) traces and metrics on tiny dark blue (#232F3E) monitors with magnifying glasses, AWS logo badge, noir detective lighting" |
| **Evaluations** | "Lego teachers grading papers with orange (#FF9900) checkmarks at a miniature dark blue (#232F3E) desk, AWS logo on chalkboard, classroom diorama" |

**gimage + WebP conversion commands:**
```bash
# 1. Generate the image (gimage outputs PNG)
gimage generate "[prompt]" -o /Users/chad/dev/agentcore/articles/images/[feature]-article.png

# 2. Resize to 800x800 for web
gimage resize -i /Users/chad/dev/agentcore/articles/images/[feature]-article.png --width 800 --height 800 -o /Users/chad/dev/agentcore/articles/images/[feature]-article-resized.png

# 3. Convert to WebP (high quality, ~50-120KB vs ~2MB PNG)
cwebp -q 85 -mt -sharp_yuv -preset photo /Users/chad/dev/agentcore/articles/images/[feature]-article-resized.png -o /Users/chad/dev/agentcore/articles/images/[feature]-article.webp

# 4. Clean up intermediate files
rm /Users/chad/dev/agentcore/articles/images/[feature]-article.png /Users/chad/dev/agentcore/articles/images/[feature]-article-resized.png
```

### Step 6: Generate Article

Assemble the article using these templates:

---

#### SHORT FORMAT (1,500-2,000 chars, ~5 min read)

```markdown
[Hook - problem statement in ~140 chars that creates urgency]

![AgentCore [Feature]](images/[feature]-article.webp)

[2-3 sentences explaining the pain point and why it matters]

[2-3 sentences introducing AgentCore [feature] as the solution]

## Prerequisites

- AWS account with Bedrock AgentCore access
- [Language] [version] installed
- Required packages: [list key packages]

## Quick Start

```[language]
# [Feature] Example - [what this demonstrates]
# Expected output: [what success looks like]

[15-30 line complete, runnable example with:]
[- All imports at top]
[- Configuration/setup]
[- Main implementation]
[- Verification that prints success message]
```

## How to Run

```bash
[Exact commands to install dependencies and run]
```

Expected output:
```
[What the user should see when it works]
```

[Key benefit statement with specific metric if available]

[2-3 sentences on what to explore next]

📚 Documentation: [docs link]
💻 Full example: articles/examples/[feature]/

#AWS #AI #AgentCore #[FeatureTag]
```

**Hook formulas for short:**
- "Your AI agent forgets everything after each session. Here's the fix:"
- "Building agents without [feature]? You're making this harder than it needs to be."
- "[Pain point]? AgentCore [feature] solves this in [X] lines of code."

---

#### STANDARD FORMAT (3,000-5,000 chars, 5-10 min read)

```markdown
[Hook - attention-grabbing problem in ~140 chars]

![AgentCore [Feature]](images/[feature]-article.webp)

[Context paragraph - why this matters for the audience, specific pain points]

[Feature explanation - what AgentCore [feature] does and how it solves the problem]

## Prerequisites

- AWS account with Bedrock AgentCore access
- [Language] [version] installed
- AgentCore CLI (`pip install agentcore-cli`)
- Required packages listed in `requirements.txt`

## Environment Setup

```bash
# Install dependencies
pip install agentcore-sdk boto3

# Set environment variables
export AWS_REGION=us-east-1
export AWS_PROFILE=your-profile
```

## Implementation

### Option 1: AgentCore SDK (Recommended)

```[language]
# [Feature] with AgentCore SDK
# This example demonstrates [what it does]

[20-30 line working example with imports, setup, implementation, verification]
```

### Option 2: boto3 (Lower-level)

```[language]
# [Feature] with boto3
# Same functionality, more control

[15-20 line alternative example]
```

## Running the Example

```bash
[Commands to run]
```

Expected output:
```
[Success output showing the feature working]
```

## Key Benefits

- **[Benefit 1]**: [Specific detail with metric]
- **[Benefit 2]**: [Specific detail with metric]
- **[Benefit 3]**: [Specific detail with metric]

## Common Patterns

[2-3 sentences on how teams typically use this feature]

## Next Steps

[CTA paragraph with links]

📚 Documentation: [link]
💻 Full runnable example: `articles/examples/[feature]/`
🔧 GitHub samples: [link]

#AWS #AI #AgentCore #[FeatureTag] #[AudienceTag]
```

---

#### LONG FORMAT (8,000-15,000 chars, ~30 min read)

```markdown
# [Title - Clear, Benefit-Focused]

![AgentCore [Feature]](images/[feature]-article.webp)

## The Problem

[3-4 paragraphs explaining the pain point in detail]
[Include specific scenarios: "You're building an AI assistant that needs to..."]
[Quantify the problem: "Teams spend X hours..." or "Without this, agents fail Y% of the time"]

## The Solution

[AgentCore [feature] overview - what it is and how it helps]
[Include architecture description: "Under the hood, [feature] uses..."]
[Compare to alternatives: "Unlike rolling your own, AgentCore provides..."]

## Prerequisites

### AWS Account Setup

- AWS account with Bedrock AgentCore access enabled
- IAM permissions: `bedrock-agentcore:*` (or specific permissions listed)
- Region: us-east-1, us-west-2, ap-southeast-2, or eu-central-1

### Local Environment

- [Language] [version] or later
- pip/npm/go modules for package management

### Required Packages

```bash
# requirements.txt
agentcore-sdk>=1.0.0
boto3>=1.34.0
python-dotenv>=1.0.0
```

## Getting Started

### Step 1: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Configure Credentials

```[language]
# config.py - Configuration setup
[10-15 lines showing credential and config setup]
```

### Step 3: Core Implementation

[Detailed explanation of the main implementation]

```[language]
# main.py - [Feature] implementation
# This demonstrates: [specific capability]
# Expected output: [what success looks like]

[40-60 line complete working example with:]
[- Comprehensive imports]
[- Configuration loading]
[- Error handling]
[- Main logic]
[- Verification/test output]
```

### Step 4: Verification

[How to verify it works]

```[language]
# test_[feature].py - Verify the implementation works
[15-25 line verification script]
```

### Step 5: Run It

```bash
# Run the example
python main.py

# Expected output:
# ✓ [Feature] initialized
# ✓ [Action] completed
# ✓ Result: [specific output]
```

## Advanced Usage

### [Advanced Pattern 1]

[Explanation with code example]

```[language]
[15-20 line advanced example]
```

### [Advanced Pattern 2]

[Explanation with code example]

```[language]
[15-20 line advanced example]
```

## Key Benefits

### [Benefit 1 Header]
[Expanded explanation with metrics/specifics - 2-3 sentences]

### [Benefit 2 Header]
[Expanded explanation with metrics/specifics - 2-3 sentences]

### [Benefit 3 Header]
[Expanded explanation with metrics/specifics - 2-3 sentences]

## Pricing

[Pricing breakdown from research]
- [Pricing tier 1]
- [Pricing tier 2]
- Free tier: $200 for new customers

## Troubleshooting

### Common Issues

**Issue: [Common error]**
Solution: [How to fix]

**Issue: [Another common error]**
Solution: [How to fix]

## Next Steps

[CTA with multiple resource links]

📚 **Documentation**: [link]
💻 **Full runnable code**: `articles/examples/[feature]/`
🔧 **GitHub samples**: [link]
🎥 **Video tutorial**: [if available]

#AWS #AI #AgentCore #[FeatureTag] #[AudienceTag] #Tutorial
```

---

## LinkedIn Character Limits Reference

| Format | Target Length | Read Time |
|--------|---------------|-----------|
| Short | 1,500-2,000 chars | ~5 min |
| Standard | 3,000-5,000 chars | 5-10 min |
| Long | 8,000-15,000 chars | ~30 min |

| Platform Limit | Value | Note |
|----------------|-------|------|
| Posts max | 3,000 chars | Short articles fit here |
| "See more" cutoff | ~140-210 chars | Hook must fit before this |
| Articles max | 125,000 chars | Long format fits easily |

---

### Step 6.5: Create Runnable Code Files

**CRITICAL: Every article must have accompanying runnable code files.**

Create actual code files in `articles/examples/[feature]/`:

```
articles/examples/[feature]/
├── main.py (or main.ts, main.go)
├── requirements.txt (or package.json)
└── README.md
```

#### File Templates

**requirements.txt (Python):**
```
# AgentCore [Feature] Example
# https://docs.aws.amazon.com/bedrock-agentcore/

agentcore-sdk>=1.0.0
boto3>=1.34.0
python-dotenv>=1.0.0
```

**package.json (TypeScript):**
```json
{
  "name": "agentcore-[feature]-example",
  "version": "1.0.0",
  "description": "AgentCore [Feature] runnable example",
  "main": "main.ts",
  "scripts": {
    "start": "npx ts-node main.ts"
  },
  "dependencies": {
    "@aws-sdk/client-bedrock-agentcore": "^3.0.0",
    "dotenv": "^16.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "ts-node": "^10.9.0"
  }
}
```

**README.md:**
```markdown
# AgentCore [Feature] Example

Runnable example demonstrating [Feature] from the article:
[Link to article]

## Prerequisites

- AWS account with Bedrock AgentCore access
- [Language] [version] installed
- AWS credentials configured (`aws configure`)

## Setup

[Language-specific setup commands]

## Run

[Exact command to run]

## Expected Output

```
[What success looks like]
```

## Learn More

- [Documentation link]
- [GitHub samples link]
```

**main.py template:**
```python
#!/usr/bin/env python3
"""
AgentCore [Feature] Example
===========================
Demonstrates: [what this code does]
Article: /articles/[feature]-[format].md

Prerequisites:
- pip install -r requirements.txt
- AWS credentials configured
- Bedrock AgentCore access enabled

Usage:
    python main.py

Expected output:
    ✓ [Feature] initialized successfully
    ✓ [Action] completed
    Result: [specific output]
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Option 1: AgentCore SDK (Recommended)
from agentcore import AgentCoreClient

def main():
    """Main function demonstrating [Feature]."""

    # Initialize client
    client = AgentCoreClient(
        region=os.getenv("AWS_REGION", "us-east-1")
    )
    print("✓ AgentCore client initialized")

    # [Main implementation]
    # ...

    # Verification
    print("✓ [Feature] working successfully!")
    print(f"Result: [output]")

if __name__ == "__main__":
    main()
```

#### Code File Requirements

1. **Must be copy-paste runnable** - User can clone and run immediately
2. **Include all imports** - No missing dependencies
3. **Print verification output** - User sees success/failure clearly
4. **Show both SDK options** where applicable:
   - AgentCore SDK as primary (simpler)
   - boto3 as alternative (more control)
5. **Include docstring** with:
   - What the code demonstrates
   - Prerequisites
   - How to run
   - Expected output

### Step 6.6: Test Code Examples

**CRITICAL: Run the code against real AWS infrastructure to verify it works before delivering the article.**

This step prevents publishing broken code examples that frustrate readers. Real tests > mock tests.

#### Test Execution Flow

```
1. SETUP     → Install dependencies, configure environment
2. EXECUTE   → Run the code, capture output
3. VERIFY    → Check for success markers, expected output
4. CLEANUP   → Delete any AWS resources created
5. REPORT    → Pass/fail with details
```

#### Step-by-Step Instructions

**1. Install dependencies:**
```bash
cd /Users/chad/dev/agentcore/articles/examples/[feature]
pip install -r requirements.txt  # or: npm install
```

**2. Set environment:**
```bash
export AWS_REGION=us-east-1
export AWS_PROFILE=default  # or appropriate profile
```

**3. Run the example:**
```bash
python main.py  # or: npx ts-node main.ts, go run main.go
```

**4. Verify output:**
- Look for success markers (✓ symbols)
- Check for expected output mentioned in the code's docstring
- Note any resource IDs created (agent IDs, memory IDs, etc.)

**5. Cleanup AWS resources:**

| Feature | Cleanup Command |
|---------|-----------------|
| **Runtime** | `agentcore destroy --name [agent-name] --force` |
| **Memory** | `aws bedrock-agentcore delete-memory --memory-id [id]` |
| **Gateway** | `aws bedrock-agentcore delete-gateway --gateway-id [id]` |
| **Identity** | `aws bedrock-agentcore delete-credential --credential-id [id]` |
| **Code Interpreter** | (auto-cleanup - sessions are ephemeral) |
| **Browser** | (auto-cleanup - sessions are ephemeral) |
| **Observability** | (no cleanup needed - logs remain in CloudWatch) |
| **Evaluations** | (no cleanup needed - results stored automatically) |
| **Policy** | `aws bedrock-agentcore delete-policy --policy-id [id]` |

#### If Test Fails

Stop and report the error to the user:

```
❌ Code test failed!

Error:
[paste the error message/stack trace]

File: articles/examples/[feature]/main.py
Line: [if identifiable]

Options:
1. Fix the code and re-run Step 6.6
2. Skip testing and proceed (not recommended)
```

Use `AskUserQuestion` to let user choose:
```json
{
  "questions": [{
    "question": "The code test failed. How would you like to proceed?",
    "header": "Test Failed",
    "options": [
      {"label": "Fix and retry", "description": "I'll fix the error and run the test again"},
      {"label": "Skip testing", "description": "Proceed without verification (not recommended)"}
    ],
    "multiSelect": false
  }]
}
```

If user chooses "Fix and retry":
1. Analyze the error
2. Edit the code files to fix the issue
3. Re-run the test from the beginning

#### If Test Passes

Report success and continue to Step 7:

```
✓ Code test passed!

Output:
[captured stdout - truncate if very long]

Resources created and cleaned up:
- [list any resources that were created and deleted]

Proceeding to Step 7: Save and Deliver
```

#### Testing Tips

- **Timeout**: If code hangs for >60 seconds, kill it and report as failure
- **Partial success**: If some operations succeed and others fail, report the specific failure
- **Network errors**: Retry once for transient errors (throttling, timeouts)
- **Missing permissions**: Report the specific IAM permission needed
- **Region issues**: Ensure us-east-1 is used (AgentCore availability)

## Research File Mapping

| Feature | Research File |
|---------|---------------|
| Overview | `research/00-overview.md` |
| Runtime | `research/01-runtime.md` |
| Memory | `research/02-memory.md` |
| Gateway | `research/03-gateway.md` |
| Identity | `research/04-identity.md` |
| Code Interpreter | `research/05-code-interpreter.md` |
| Browser | `research/06-browser.md` |
| Policy | `research/07-policy.md` |
| Observability | `research/08-observability.md` |
| Evaluations | `research/09-evaluations.md` |

## Documentation Links

- Main docs: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/
- Product page: https://aws.amazon.com/bedrock/agentcore/
- GitHub samples: https://github.com/awslabs/amazon-bedrock-agentcore-samples/

### Step 7: Save and Deliver

Save all files and provide links to the user.

**File structure:**
```
/Users/chad/dev/agentcore/articles/
├── [feature]-[format].md           # Article
├── images/
│   └── [feature]-article.webp       # Generated art
└── examples/
    └── [feature]/                  # Runnable code
        ├── main.py (or .ts/.go)
        ├── requirements.txt (or package.json)
        └── README.md
```

**File naming convention:**
```
Article:  /Users/chad/dev/agentcore/articles/[feature]-[format].md
Code:     /Users/chad/dev/agentcore/articles/examples/[feature]/
Image:    /Users/chad/dev/agentcore/articles/images/[feature]-article.webp
```

Examples:
- `articles/runtime-short.md` + `articles/examples/runtime/`
- `articles/memory-standard.md` + `articles/examples/memory/`
- `articles/gateway-long.md` + `articles/examples/gateway/`

**Use `Write` tool** to save:
1. Article markdown file
2. Code files (main.py, requirements.txt, README.md)

**Final output to user:**
```
Article generated successfully!

📄 Article:  /Users/chad/dev/agentcore/articles/[feature]-[format].md
🎨 Image:    /Users/chad/dev/agentcore/articles/images/[feature]-article.webp
💻 Code:     /Users/chad/dev/agentcore/articles/examples/[feature]/

[Character count] characters ([format] format, ~X min read)

To run the example:
  cd articles/examples/[feature]
  pip install -r requirements.txt
  python main.py
```

## Checklist

Before delivering the article:

**Research & Content:**
- [ ] Research file read for selected feature
- [ ] AWS docs searched for latest information
- [ ] New data added to research files (if found)

**Article Quality:**
- [ ] Character count matches target format (Short: 1,500-2,000, Standard: 3,000-5,000, Long: 8,000-15,000)
- [ ] Hook fits before "See more" (~140 chars)
- [ ] Prerequisites/requirements section included
- [ ] All hashtags included
- [ ] CTA with documentation link included

**Code Files (CRITICAL):**
- [ ] Code files created in `articles/examples/[feature]/`
- [ ] `main.py` (or .ts/.go) is complete and runnable
- [ ] `requirements.txt` (or package.json) lists all dependencies
- [ ] `README.md` has setup and run instructions
- [ ] Code includes verification output (prints success message)
- [ ] Both SDK options shown (AgentCore SDK + boto3)

**Code Testing (CRITICAL - Step 6.6):**
- [ ] Dependencies installed successfully
- [ ] Code executed without errors
- [ ] Expected output verified (✓ markers present)
- [ ] AWS resources cleaned up after test
- [ ] Test passed before delivery

**Art:**
- [ ] Art generated with `gimage generate`
- [ ] Prompt includes AWS brand colors (#FF9900 orange, #232F3E dark blue)
- [ ] Image link included in article: `![AgentCore [Feature]](images/[feature]-article.webp)`

**Files Saved:**
- [ ] Article saved to `articles/[feature]-[format].md`
- [ ] Code saved to `articles/examples/[feature]/`
- [ ] All file paths provided to user
