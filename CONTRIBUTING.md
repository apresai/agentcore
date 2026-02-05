# Contributing to AgentCore Knowledge Base

Thank you for your interest in contributing to the AgentCore knowledge base! This document provides guidelines for contributing.

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Getting Started](#getting-started)
- [Content Guidelines](#content-guidelines)
- [Pull Request Process](#pull-request-process)
- [Using Claude Code Skills](#using-claude-code-skills)

---

## Ways to Contribute

### 1. Update Research Documentation

The `research/` directory contains detailed documentation for each AgentCore service. You can:

- Fix errors or outdated information
- Add new details from AWS documentation
- Improve explanations and examples

### 2. Write Articles

The `articles/` directory contains published content. You can:

- Write new articles (see [article ideas](articles/00-article-ideas.md))
- Improve existing articles
- Add code examples

### 3. Add Code Examples

The `articles/examples/` directory contains runnable code. You can:

- Add new examples for different services
- Improve existing examples
- Add examples for different frameworks

### 4. Improve Documentation

The `docs/` directory contains GitHub documentation. You can:

- Fix typos and errors
- Improve clarity and organization
- Add missing information

---

## Getting Started

### Fork and Clone

```bash
# Fork the repository on GitHub, then clone
git clone https://github.com/YOUR_USERNAME/agentcore.git
cd agentcore
```

### Set Up Claude Code Skills (Optional)

If you use Claude Code, set up the skills for easier contribution:

```bash
# Create symlinks
ln -s $(pwd)/.claude/skills/agentcore ~/.claude/skills/agentcore
ln -s $(pwd)/.claude/skills/agentcore-article ~/.claude/skills/agentcore-article
```

### Create a Branch

```bash
git checkout -b feature/your-feature-name
```

---

## Content Guidelines

### Research Files (`research/`)

Research files are the **source of truth** for AgentCore information. Follow these guidelines:

1. **Be accurate**: Cross-reference with [official AWS documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
2. **Be comprehensive**: Include all relevant details
3. **Use consistent formatting**: Follow the structure of existing files
4. **Include sources**: Link to official documentation

**File naming**: `XX-service-name.md` (e.g., `01-runtime.md`)

**Structure**:
```markdown
# Service Name

## Overview
Brief description

## Key Features
- Feature 1
- Feature 2

## Technical Details
Detailed information

## Code Examples
Working code snippets

## Related Resources
Links to official docs
```

### Articles (`articles/`)

Articles are polished content for publication. Follow these guidelines:

1. **Original content**: Write original analysis, not copied documentation
2. **Practical focus**: Include real use cases and examples
3. **Runnable code**: All code examples must work when copy-pasted
4. **Proper attribution**: Link to sources

**Formats**:
- **Short**: ~1,500 characters (LinkedIn post length)
- **Standard**: 3,000-5,000 characters (5-10 min read)
- **Long**: 8,000-15,000 characters (tutorial/guide)

### Code Examples (`articles/examples/`)

All code examples must be:

1. **Completely runnable**: Copy-paste ready
2. **Self-contained**: Include all imports and dependencies
3. **Documented**: Include README with setup instructions
4. **Tested**: Verified against real AWS infrastructure

**Structure**:
```
examples/service-name/
├── main.py           # Main example code
├── requirements.txt  # Dependencies
└── README.md         # Setup and usage instructions
```

### Documentation (`docs/`)

Documentation follows GitHub Flavored Markdown conventions:

1. **Use headings**: Organize content hierarchically
2. **Use tables**: For structured information
3. **Use code blocks**: With language identifiers
4. **Use relative links**: Link between docs using relative paths
5. **Use collapsible sections**: For optional details

**GitHub Markdown features to use**:
- Mermaid diagrams for architecture
- `> [!NOTE]`, `> [!TIP]`, `> [!WARNING]` for callouts
- `<details>` for collapsible sections
- Tables for structured data

---

## Pull Request Process

### 1. Prepare Your Changes

- Ensure your changes follow the content guidelines
- Test any code examples
- Run spell check

### 2. Commit with Descriptive Messages

```bash
git add .
git commit -m "Add Memory service deep dive article

- Add runnable Python example
- Include SDK and boto3 alternatives
- Add architecture diagram"
```

### 3. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear title describing the change
- Description of what and why
- Link to any related issues

### 4. PR Review

- Respond to feedback promptly
- Make requested changes
- Keep the PR focused on a single change

---

## Using Claude Code Skills

This repo includes two Claude Code skills to help with contributions:

### `/agentcore` — Research and Build

Use this skill to:
- Get information about AgentCore services
- Generate code examples
- Troubleshoot issues

```
"What are the key features of AgentCore Memory?"
"Show me a Gateway example with Lambda"
"How do I add Policy rules?"
```

### `/agentcore-article` — Write Articles

Use this skill to:
- Generate complete articles
- Create runnable code examples
- Update research documentation

```
"Write an article about AgentCore Browser"
"Create a tutorial for Code Interpreter"
```

The skill follows a 7-step workflow:
1. Gather requirements (feature, format, audience)
2. Research (local files + AWS docs + web)
3. Update knowledge base (if new info found)
4. Plan code examples
5. Generate artwork (Lego builder theme)
6. Write article
7. Test and save

---

## Questions?

- **GitHub Issues**: Open an issue for questions or discussions
- **AWS re:Post**: [AgentCore Community](https://repost.aws/tags/TAG-agentcore)

---

## Code of Conduct

- Be respectful and constructive
- Focus on the content, not the contributor
- Help others learn and improve

Thank you for contributing!
