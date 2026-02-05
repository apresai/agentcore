# AgentCore Skills Ecosystem

This repository includes two Claude Code skills for working with AWS Bedrock AgentCore.

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │         External Sources                │
                    │  AWS Docs · GitHub Samples · Web        │
                    └───────────────┬─────────────────────────┘
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────────┐
│                    Knowledge Base (this repo)                      │
│  /Users/chad/dev/agentcore/                                       │
│  ├── research/        ← Curated documentation (source of truth)   │
│  ├── articles/        ← Published content                         │
│  ├── examples/        ← Runnable code                             │
│  └── .claude/skills/  ← Skills (portable with repo)               │
└───────────────────┬───────────────────────────┬───────────────────┘
                    │                           │
                    ▼                           ▼
         ┌──────────────────┐        ┌──────────────────┐
         │ agentcore-article │        │    agentcore     │
         │    (Producer)     │        │   (Consumer)     │
         │                   │        │                  │
         │ • Reads research  │        │ • Reads research │
         │ • Searches AWS    │        │ • Reads articles │
         │ • Updates research│        │ • Reads examples │
         │ • Writes articles │        │ • Fetches GitHub │
         │ • Creates examples│        │ • Helps build    │
         └──────────────────┘        └──────────────────┘
```

## Available Skills

### `/agentcore` (Consumer)

**Use for:** Building agents, API usage, CLI commands, troubleshooting, code patterns.

Triggers:
- "How do I deploy an AgentCore agent?"
- "What is AgentCore Memory?"
- "Show me a Strands agent example"
- "AgentCore deployment is failing"

### `/agentcore-article` (Producer)

**Use for:** Creating articles, updating research, generating example code.

Triggers:
- "Write an article about AgentCore Runtime"
- "Create a tutorial for AgentCore Memory"

## Installation

Skills are stored in the repo at `.claude/skills/` and linked to your global skills directory.

### Verify Setup

```bash
# Check symlinks exist
ls -la ~/.claude/skills/agentcore*
```

Expected output:
```
agentcore -> /Users/chad/dev/agentcore/.claude/skills/agentcore
agentcore-article -> /Users/chad/dev/agentcore/.claude/skills/agentcore-article
```

### Manual Installation

If symlinks are missing, create them:

```bash
# Create symlinks
ln -s /Users/chad/dev/agentcore/.claude/skills/agentcore ~/.claude/skills/agentcore
ln -s /Users/chad/dev/agentcore/.claude/skills/agentcore-article ~/.claude/skills/agentcore-article
```

### Cloning to Another Machine

After cloning the repo, run:

```bash
# Create skills directory if needed
mkdir -p ~/.claude/skills

# Create symlinks (adjust path to where you cloned)
ln -s /path/to/agentcore/.claude/skills/agentcore ~/.claude/skills/agentcore
ln -s /path/to/agentcore/.claude/skills/agentcore-article ~/.claude/skills/agentcore-article
```

## How the Skills Work

### agentcore (Consumer)

1. **Quick reference** - Embedded CLI commands, SDK imports, service overview
2. **Dynamic loading** - Reads research files based on user's question topic
3. **Code patterns** - Embedded examples for common tasks
4. **GitHub fetch** - Pulls latest examples when user asks for "latest"
5. **AWS search** - Searches docs for "what's new" queries

### agentcore-article (Producer)

1. **Gather requirements** - Asks about feature, format, audience, language
2. **Research** - Reads local files, searches AWS docs, web search
3. **Update knowledge base** - Adds new info to research files
4. **Generate code** - Creates runnable examples in `articles/examples/`
5. **Generate art** - Creates Lego builder-themed images
6. **Write article** - Follows format templates

## Updating When AgentCore Changes

### Research Files Need Update

When AWS releases new AgentCore features:

1. Run `/agentcore-article` for affected services
2. Select the feature to research
3. The skill will search AWS docs and update research files

### Manual Research Update

1. Read AWS documentation
2. Edit `research/XX-service.md` following existing format
3. Commit changes

### Adding New Service Coverage

1. Create `research/XX-new-service.md` following existing format
2. Add entry to file mapping in both skills:
   - `.claude/skills/agentcore/SKILL.md` - Research File Mapping table
   - `.claude/skills/agentcore-article/SKILL.md` - Research File Mapping table
3. Add art prompt in agentcore-article skill

## Troubleshooting

### Skills Not Showing

```bash
# Verify symlinks
ls -la ~/.claude/skills/

# Recreate if broken
rm ~/.claude/skills/agentcore ~/.claude/skills/agentcore-article
ln -s /Users/chad/dev/agentcore/.claude/skills/agentcore ~/.claude/skills/agentcore
ln -s /Users/chad/dev/agentcore/.claude/skills/agentcore-article ~/.claude/skills/agentcore-article
```

### Skill Returns Wrong Info

The skill may be using outdated research files. Check:

1. When was `research/XX-service.md` last updated?
2. Run `/agentcore-article` to refresh from AWS docs
3. Manually update if needed

### Wrong Skill Triggered

- For building/coding/troubleshooting → `/agentcore`
- For writing articles/content → `/agentcore-article`

If the wrong skill is triggered, explicitly invoke the correct one.

## Repository Structure

```
/Users/chad/dev/agentcore/
├── .claude/
│   └── skills/
│       ├── agentcore/           # Consumer skill
│       │   └── SKILL.md
│       └── agentcore-article/   # Producer skill
│           └── SKILL.md
├── research/                    # Source of truth
│   ├── 00-overview.md
│   ├── 01-runtime.md
│   ├── 02-memory.md
│   ├── 03-gateway.md
│   ├── 04-identity.md
│   ├── 05-code-interpreter.md
│   ├── 06-browser.md
│   ├── 07-policy.md
│   ├── 08-observability.md
│   ├── 09-evaluations.md
│   ├── 10-getting-started.md
│   └── 11-pricing.md
├── articles/                    # Published content
│   ├── examples/                # Runnable code
│   │   └── runtime/
│   └── images/                  # Generated art
├── CLAUDE.md                    # Project instructions
└── SKILLS.md                    # This file
```
