# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

A collection of **system prompts** for 7 specialized QA agents, each defined as a Markdown file in `agents/`. There is no runnable code — the repo is a knowledge base and prompt library. The agents are designed to be loaded into Claude Code (or any LLM) to give it a specialized QA persona.

## Agent Roster

| File | Agent | Specialty |
|------|-------|-----------|
| `agents/ARIA.md` | ARIA | Web test automation (Playwright, Cypress, Robot Framework) |
| `agents/KAUE.md` | KAUÊ | Mobile automation (Maestro, Appium, Robot Framework AppiumLibrary) |
| `agents/NEXUS.md` | NEXUS | API testing (RestAssured, Postman, k6) |
| `agents/FLUX.md` | FLUX | Performance & observability (k6, JMeter, Grafana) |
| `agents/ATLAS.md` | ATLAS | QA architecture & strategy |
| `agents/HELIX.md` | HELIX | Exploratory testing & emerging trends |
| `agents/SIGMA.md` | SIGMA | Business quality & executive reporting |

## How to Activate an Agent

```bash
# Pass a system prompt directly
claude --system-prompt agents/ARIA.md "Create an E2E test for the login flow"

# Or copy to clipboard (macOS) and paste into Claude
cat agents/NEXUS.md | pbcopy
```

See `USAGE.md` for the full decision matrix (which agent for which task), validation checklists per agent, and MCP configuration.

## Knowledge Base Sources

Agent prompts are grounded in content from four Brazilian QA references:
- **Júlio de Lima** — API strategy, BDD, JMeter, AI in testing
- **Fernando Papito** — Playwright, Robot Framework, CI/CD, Page Objects
- **QAzando** — Mobile (iFood/IBM/Neon), web, diverse stacks
- **Vinícius Pessoni** — Java+RestAssured, CTFL, technical leadership

## Planned Extensions (not yet implemented)

- `knowledge_base/` — RAG source material organized by author
- `tools/collect.py` — YouTube content collector
- `tools/mcp.json` — MCP server configuration
