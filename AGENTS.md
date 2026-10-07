# DeployPilot — Codex Instructions

## Purpose

DeployPilot is a portfolio project that demonstrates an end-to-end software delivery workflow:

GitHub -> GitHub Actions -> Docker -> Azure Container Registry -> Azure Container Apps

When CI/CD or runtime failures occur, DeployPilot uses an LLM to turn relevant failure evidence into a structured, actionable explanation for the developer.

## Read First

Before making significant changes, read:

- `docs/PROJECT_CONTEXT.md`
- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`
- `docs/ROADMAP.md`

Treat those files as the source of truth for project scope and architecture.

## Core Technology Choices

- Frontend: React + TypeScript + Vite
- Backend: Python + FastAPI
- Demo application: small Python + FastAPI service
- Containers: Docker
- CI/CD: GitHub Actions
- Container registry: Azure Container Registry (ACR)
- Runtime: Azure Container Apps (ACA)
- Infrastructure as Code: Bicep
- AI: OpenAI API
- GitHub -> Azure authentication target: OIDC where practical

Do not replace these technologies without a clear reason and an explicit update to `docs/DECISIONS.md`.

## Scope Rules

Version 1 must stay intentionally small.

Do not add the following unless the roadmap explicitly moves them into scope:

- Kubernetes / AKS
- multi-cloud deployment
- support for arbitrary external repositories
- user authentication or multi-user accounts
- automatic AI code changes
- autonomous redeployment
- a full observability platform
- microservices
- unnecessary databases
- complex frontend features

Prefer the smallest implementation that proves the end-to-end workflow.

## AI Design Principle

Deterministic systems detect failures. AI interprets them.

The LLM should receive only the minimum useful context, such as:

- pipeline stage
- status
- relevant error messages
- relevant log excerpts
- exit codes
- health-check results
- selected configuration names
- small relevant code snippets only when clearly needed

Do not send the entire repository to the LLM by default.

## Security Rules

- Never commit API keys, Azure credentials, connection strings, or secrets.
- Never expose the OpenAI API key to the frontend.
- Keep secrets server-side.
- Prefer environment variables / managed secret mechanisms.
- Prefer OIDC for GitHub Actions authentication to Azure instead of long-lived credentials where practical.
- Avoid logging secrets or sensitive environment variable values.

## Engineering Rules

- Keep code simple enough to explain in a junior cloud / DevOps / software engineering interview.
- Prefer clear modules and explicit data flow over clever abstractions.
- Add tests for important behavior.
- Run relevant tests before declaring a task complete.
- Keep API responses structured and predictable.
- For AI analysis, prefer structured JSON output over free-form prose.
- Update documentation when architecture or scope changes.

## Documentation Rules

After a meaningful milestone:

1. Update `docs/ROADMAP.md`.
2. Update `docs/DECISIONS.md` if a significant technical decision was made.
3. Update `docs/ARCHITECTURE.md` if system structure or data flow changed.
4. Keep `docs/PROJECT_CONTEXT.md` aligned with the current MVP.

## Completion Standard

A task is complete when:

- the implementation works,
- relevant tests pass,
- secrets are not exposed,
- the code remains understandable,
- and the relevant project documentation reflects the change.
