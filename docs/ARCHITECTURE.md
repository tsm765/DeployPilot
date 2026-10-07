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

### 2.5 Azure Container Apps

Responsibilities:

- run the demo application;
- expose the deployed workload;
- provide deployment / revision status;
- support environment variables and secrets;
- provide runtime evidence needed for troubleshooting.

### 2.6 DeployPilot FastAPI Backend

Responsibilities:

- receive or retrieve deployment information;
- normalize data from CI/CD and Azure;
- expose API endpoints for the frontend;
- prepare failure-analysis requests;
- call the OpenAI API;
- validate / normalize structured AI output.

The backend is the only component that should hold the OpenAI API key.

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

### 2.8 React + TypeScript Frontend

Responsibilities:

- display latest deployment state;
- show stage-by-stage status;
- display AI analysis;
- optionally display raw relevant logs.

The v1 UI should remain small and focused.

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
