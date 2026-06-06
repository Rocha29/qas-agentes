# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

A collection of **system prompts** for 8 specialized QA agents, each defined as a Markdown file in `agents/`. There is no runnable code — the repo is a knowledge base and prompt library. The agents are designed to be loaded into Claude Code (or any LLM) to give it a specialized QA persona.

## Agent Roster

| File | Agent | Specialty |
|------|-------|-----------|
| `agents/SIGMA-LEAD.md` | SIGMA-LEAD | Orchestrator — reads user stories from `historias/`, builds the Sprint QA Plan, routes to the right agents |
| `agents/ARIA-WEB.md` | ARIA-WEB | Web & WebView automation (Playwright, Cypress, Robot Framework) |
| `agents/KAUE-MOBILE.md` | KAUE-MOBILE | Mobile automation Android/iOS/WebView (Maestro, Appium, Robot AppiumLibrary) |
| `agents/NEXUS-API.md` | NEXUS-API | API & BFF testing (RestAssured, Postman, k6) |
| `agents/FLUX-PERF.md` | FLUX-PERF | Performance & observability (k6, JMeter, Grafana) |
| `agents/ATLAS-ARCH.md` | ATLAS-ARCH | QA architecture & strategy |
| `agents/HELIX-EXPLORE.md` | HELIX-EXPLORE | Exploratory testing & emerging trends |
| `agents/SIGMA-BIZ.md` | SIGMA-BIZ | Business quality & executive reporting |

## How to Activate an Agent

```bash
# Orchestrated mode — SIGMA-LEAD reads the story and builds the plan
claude --system-prompt agents/SIGMA-LEAD.md
# then type: HIST-042

# Direct mode — activate a specific agent
claude --system-prompt agents/ARIA-WEB.md
claude --system-prompt agents/NEXUS-API.md

# Or copy to clipboard (macOS) and paste into Claude
cat agents/NEXUS-API.md | pbcopy
```

See `WORKFLOW.md` for the full decision guide (orchestrated vs direct mode, WebView partnerships, execution order).

## User Stories

Story files live in `historias/`. Naming convention: `HIST-NNN.md`.

- `historias/_template-negocio.md` — template for business stories (with BDD from internal AI tool)
- `historias/_template-tecnico.md` — template for technical stories (BFF, API, infra from Tech Lead)

## Knowledge Base Sources

Agent prompts are grounded in content from five Brazilian QA references:
- **Júlio de Lima** — API strategy, BDD, JMeter, AI in testing
- **Fernando Papito** — Playwright, Robot Framework, CI/CD, Page Objects
- **QAzando** — Mobile (iFood/IBM/Neon), web, diverse stacks
- **Vinícius Pessoni** — Java+RestAssured, CTFL, technical leadership
- **Walmyr (Talking About Testing)** — Cypress, Playwright, quality culture

## Planned Extensions (not yet implemented)

- `knowledge_base/` — RAG source material organized by author
- `tools/collect.py` — YouTube content collector
- `tools/mcp.json` — MCP server configuration
