# DeployPilot — Architecture

## 1. System Overview

Version 1 uses a deliberately small architecture.

```text
Developer
   |
   | git push
   v
GitHub Repository
   |
   v
GitHub Actions
   |
   +--> install dependencies
   +--> run tests
   +--> run checks
   +--> build Docker image
   |
   v
Azure Container Registry
   |
   v
Azure Container Apps
   |
   +--> deployment status
   +--> health status
   +--> runtime / failure evidence
   |
   v
DeployPilot FastAPI Backend
   |
   +--> normalize deployment information
   +--> select relevant failure context
   |
   v
OpenAI API
   |
   v
Structured diagnosis
   |
   v
DeployPilot FastAPI Backend
   |
   v
React + TypeScript Dashboard
```

Infrastructure is defined through Bicep.

## 2. Main Components

### 2.1 GitHub Repository

Responsibilities:

- source control;
- pull requests;
- GitHub Actions workflow definitions;
- project documentation;
- Bicep templates;
- application source code.

### 2.2 GitHub Actions

Responsibilities:

- react to repository events;
- install dependencies;
- run automated tests;
- run lightweight checks;
- build Docker images;
- authenticate to Azure;
- push images to ACR;
- trigger / perform deployment;
- expose workflow failure information.

GitHub Actions is the automation layer.

### 2.3 Demo Application

A deliberately small FastAPI application used as the deployable workload.

Responsibilities:

- provide a real application for CI/CD;
- expose `/` and `/health`;
- support controlled failure scenarios.

The demo application is not the DeployPilot backend.

### 2.4 Azure Container Registry

Responsibilities:

- store versioned Docker images;
- provide the image consumed by Azure Container Apps.

The foundation Bicep template creates separate user-assigned identities for Container App runtime and GitHub deployment. It grants the runtime identity `AcrPull` and the GitHub identity `AcrPush`, each at the registry scope. It also assigns Container Apps Contributor to the GitHub identity at the resource-group scope for app deployment. The Container App will use its identity to pull images without registry admin credentials. The template defines a federated credential for GitHub Actions on the configured branch, using an OIDC subject containing the GitHub owner and repository IDs. The new role assignment still needs to be deployed.

### 2.5 Azure Container Apps

Responsibilities:

- run the demo application;
- expose the deployed workload;
- provide deployment / revision status;
- support environment variables and secrets;
- provide runtime evidence needed for troubleshooting.

The development environment uses only the Consumption workload profile, with zone redundancy disabled. The template does not configure Log Analytics or an app log destination. Log-based runtime evidence remains limited until a collection path is added.

The app Bicep template defines the demo Container App in that environment. It uses the runtime user-assigned identity to pull an image from ACR, exposes port 8000 over HTTPS, and scales from zero to one Consumption replica. The app template has not yet been deployed.

### 2.6 DeployPilot FastAPI Backend

Responsibilities:

- receive or retrieve deployment information;
- normalize data from CI/CD and Azure;
- expose API endpoints for the frontend;
- prepare failure-analysis requests;
- call the OpenAI API;
- validate / normalize structured AI output.

The backend is the only component that should hold the OpenAI API key.

API failures use an `error` object with stable `code` and `message` fields. Missing configuration, missing failure evidence, GitHub request failures, and AI request failures use explicit codes. Validation responses omit Pydantic internals, and AI provider exception details are not returned to clients.

The backend writes JSON logs to stdout for deployment status collection, failure evidence, runtime health failures, and AI analysis. Event records include only stage, run ID, status, and HTTP status when relevant; prompts, tokens, and evidence logs are not included. Provider exceptions are logged server-side with tracebacks while API clients receive stable error messages.

The backend also requests the latest `main` push run of the configured GitHub Actions workflow and exposes a small set of run metadata at `/api/github/latest-run`. Its `/api/deployment` endpoint combines the run ID, number, branch, commit, URL, and timestamps with stage statuses mapped from the run's latest-attempt jobs. It also maps the deployed app's health probe to a `runtime` stage (`healthy` to `passed`, otherwise `failed`). The GitHub owner, repository, and workflow file are selected through server-side environment variables.

`GET /api/runtime-health` probes the deployed demo app's `/health` URL using the server-side `DEMO_APP_BASE_URL` and a 15-second timeout. HTTP 200 is healthy; other HTTP responses, timeouts, and connection failures are unhealthy. This check is deterministic and does not call AI.

Unhealthy HTTP response text is capped at 2,000 characters plus a truncation marker before it enters runtime evidence. GitHub workflow, job, and redirected log requests each have a 15-second timeout and reject non-successful HTTP responses.

The `/api/failure-evidence/{run_id}` endpoint finds a recognized failed pipeline step in the specified run and returns the last 60 nonblank lines of its job log with the stage and step name. Selected lines are redacted before they become evidence. GitHub requests use a server-side `GITHUB_TOKEN` when one is configured. The evidence endpoint does not call AI.

`GET /api/runtime-failure-evidence` turns a failed live health probe into structured runtime evidence, including the HTTP status when available. It redacts the health URL and response or error text before adding them to evidence. It reports a connection or timeout failure with a null HTTP status. A healthy runtime has no failure evidence.

`POST /api/runtime-failure-report` performs one live health probe, then analyzes its evidence if the runtime is unhealthy. The response includes both runtime evidence and AI analysis, without a GitHub run ID.

`POST /api/failure-report/{run_id}` collects evidence for that exact run once, sends the same evidence to the AI analyzer, and returns the run ID, evidence, and structured analysis in one response.

### 2.7 OpenAI API

Responsibilities:

- interpret selected failure evidence;
- return structured troubleshooting output.

Target output:

```json
{
  "stage": "deployment",
  "problem": "Container failed to start",
  "likely_cause": "A required environment variable is missing",
  "suggested_fix": "Configure the variable in Azure Container Apps"
}
```

The model should not be treated as the source of truth for deployment state.

The backend sends only the failure stage, error message, selected log lines, exit code, health status, and HTTP status to the OpenAI Responses API. It redacts error text and log lines again before constructing that request, including evidence supplied through `/api/analyze`. It requests strict JSON with `problem`, `likely_cause`, and `suggested_fix`; the backend supplies the stage from deterministic evidence. The request uses `store=False`, and the API key remains server-side.

The OpenAI client is created only when analysis runs, so importing the backend for mocked tests does not require an API key.

`POST /api/analyze` accepts caller-supplied failure evidence. The run-specific failure report endpoint collects evidence automatically before analysis.

### 2.8 React + TypeScript Frontend

Responsibilities:

- display latest deployment state;
- show stage-by-stage status;
- display AI analysis;
- optionally display raw relevant logs.

The v1 UI should remain small and focused.

The dashboard loads `/api/deployment` without HTTP caching and displays the workflow branch, short commit, run link, local update time, and runtime status. It requests `/api/failure-report/{run_id}` for a pipeline failure and checks the returned run ID. If only runtime has failed, it requests `/api/runtime-failure-report` instead. A Refresh button repeats the request and shows when AI analysis is running. The dashboard displays backend-collected evidence in an expandable section; React does not construct it.

When fresh deployment data arrives, the dashboard clears the previous evidence and diagnosis before requesting a new failure report.

### 2.9 Bicep

Responsibilities:

- define Azure infrastructure reproducibly;
- make infrastructure changes reviewable in Git.

## 3. Deterministic vs AI Responsibilities

### Deterministic tooling decides:

- whether tests passed;
- whether the Docker build succeeded;
- whether deployment succeeded;
- container exit code;
- health-check result;
- deployment status.

### AI interprets:

- what the failure likely means;
- what likely caused it;
- what the developer should inspect or change next.

Design rule:

> Detection is deterministic. Interpretation is AI-assisted.

## 4. Failure-Analysis Data Flow

```text
Failure occurs
    |
    v
GitHub / Azure / application produces evidence
    |
    v
DeployPilot backend selects relevant context
    |
    +--> stage
    +--> status
    +--> error
    +--> selected logs
    +--> exit code
    +--> health result
    +--> selected config names
    |
    v
OpenAI API
    |
    v
Structured diagnosis
    |
    v
FastAPI validates response
    |
    v
Frontend displays diagnosis
```

The entire repository is not sent by default.

## 5. Success Data Flow

```text
Developer pushes code
    |
    v
GitHub Actions
    |
    +--> tests pass
    +--> Docker build succeeds
    |
    v
ACR
    |
    v
Azure Container Apps
    |
    v
Health check succeeds
    |
    v
DeployPilot
    |
    v
Dashboard shows healthy deployment
```

AI does not need to be called when there is nothing useful to explain.

## 6. Security Boundaries

### Frontend

Must not contain:

- OpenAI API key;
- Azure credentials;
- GitHub credentials;
- secret environment variable values.

### Backend

May access required secrets through server-side environment configuration.

### GitHub Actions

Should prefer OIDC authentication to Azure where practical.

### AI requests

Before sending evidence:

- avoid including secret values;
- avoid sending whole environment dumps;
- avoid sending the full repository;
- redact sensitive content where necessary.

## 7. Initial Repository Shape

```text
deploypilot/
├── AGENTS.md
├── README.md
├── docs/
│   ├── PROJECT_CONTEXT.md
│   ├── ARCHITECTURE.md
│   ├── DECISIONS.md
│   └── ROADMAP.md
├── frontend/
├── backend/
├── demo-app/
├── tests/
├── infra/
├── .github/
│   └── workflows/
└── .gitignore
```

This structure may evolve, but major changes should be reflected in this file and in `DECISIONS.md`.
