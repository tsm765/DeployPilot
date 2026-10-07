# DeployPilot — Project Context

## 1. Project Summary

DeployPilot is an AI-assisted developer tool that automates the deployment of a small application from GitHub to Azure and helps developers understand failures when the software delivery process breaks.

The core project statement is:

> DeployPilot helps developers deploy small applications from GitHub to Azure and understand what went wrong when the deployment fails.

The project is intentionally designed as a portfolio-quality MVP rather than a production SaaS platform.

## 2. Problem

Developers repeatedly have to:

- run tests,
- build applications,
- containerize them,
- provision cloud infrastructure,
- deploy them,
- inspect CI/CD failures,
- inspect runtime failures,
- and translate technical logs into a concrete next action.

The deployment steps can be automated, but troubleshooting is still often manual and time-consuming.

DeployPilot addresses both parts:

1. automate the delivery path;
2. explain failures in a developer-friendly way.

## 3. Core Principle

Every v1 feature should support at least one of these questions:

- Does this help automate deployment?
- Does this help understand a failed deployment?

If not, it probably belongs in a later version.

## 4. MVP Goal

The MVP must prove one complete story:

> A developer pushes a small application to GitHub. The application is tested, containerized, deployed to Azure, and if something fails, DeployPilot presents the failed stage, a likely cause, and a suggested fix.

## 5. MVP Capabilities

### 5.1 Demo application

A small application exists only so DeployPilot has something real to build and deploy.

Minimum useful behavior:

- `/` returns a simple response.
- `/health` reports application health.
- a small test suite exists.
- the app can be configured to demonstrate deliberate failures.

### 5.2 Continuous Integration

A GitHub Actions workflow should:

1. trigger on push / pull request as appropriate;
2. install dependencies;
3. run tests;
4. run lightweight checks;
5. build a Docker image.

### 5.3 Azure container delivery

The delivery flow should continue:

1. build Docker image;
2. push image to Azure Container Registry;
3. deploy image to Azure Container Apps;
4. verify the deployed application.

### 5.4 Infrastructure as Code

Azure resources should be created reproducibly with Bicep instead of relying only on portal clicks.

Core resources include:

- Azure Container Registry;
- Azure Container Apps Environment;
- Azure Container App;
- required identities / configuration.

The Azure resource group may be created separately if doing so keeps the first version simpler.

### 5.5 DeployPilot dashboard

The frontend should remain deliberately small.

It should show information such as:

- application name;
- environment;
- latest deployment;
- build status;
- test status;
- container status;
- deployment status;
- AI analysis;
- access to raw failure information where useful.

### 5.6 AI-assisted failure analysis

The AI component receives selected failure evidence and returns a structured explanation.

Target response fields:

- `stage`
- `problem`
- `likely_cause`
- `suggested_fix`

The AI is not responsible for deciding whether a deployment succeeded. GitHub, Azure, health checks, and application status do that deterministically.

## 6. Demonstration Scenarios

The MVP should deliberately demonstrate at least these three cases.

### Scenario A — Successful deployment

- tests pass;
- image builds;
- deployment succeeds;
- health check succeeds;
- DeployPilot reports a healthy deployment.

### Scenario B — CI failure

Example:

- a unit test is intentionally broken;
- GitHub Actions stops at the test stage;
- DeployPilot presents the failed stage and an AI explanation.

### Scenario C — Deployment or runtime failure

Examples:

- required environment variable missing;
- application starts incorrectly;
- application returns HTTP 500;
- health check fails.

DeployPilot should show the relevant evidence and produce an actionable explanation.

## 7. User Flow

The primary user is a developer.

Normal flow:

1. developer changes code;
2. developer pushes to GitHub;
3. GitHub Actions starts;
4. tests run;
5. Docker image builds;
6. image is pushed to ACR;
7. application is deployed to Azure Container Apps;
8. deployment / health status is collected;
9. DeployPilot dashboard shows the result.

If a failure occurs:

1. failed stage is identified;
2. relevant logs / metadata are collected;
3. FastAPI normalizes the evidence;
4. selected evidence is sent to the OpenAI API;
5. the model returns structured analysis;
6. the dashboard displays the diagnosis.

The v1 dashboard is primarily read-only. It observes and explains. It does not automatically modify code, change Azure resources, or redeploy the application.

## 8. AI Data-Handling Model

The OpenAI API does not automatically inspect the GitHub repository or running application.

DeployPilot explicitly chooses what is sent.

Preferred v1 AI context:

- pipeline stage;
- status;
- error message;
- relevant log excerpts;
- exit code;
- health status;
- configuration names;
- a small relevant source snippet only if needed.

Do not send the full repository by default.

The design principle is:

> Minimum useful context, not unrestricted code access.

## 9. Technology Stack

### Frontend

- React
- TypeScript
- Vite

### Backend

- Python
- FastAPI

### Demo application

- Python
- FastAPI

### DevOps and cloud

- Git
- GitHub
- GitHub Actions
- Docker
- Azure Container Registry
- Azure Container Apps
- Bicep

### AI

- OpenAI API

### Authentication target

- GitHub Actions -> Azure through OIDC where practical.

## 10. Explicitly Out of Scope for v1

Do not add these unless the roadmap changes:

- Kubernetes / AKS;
- AWS or GCP deployment;
- arbitrary third-party repository onboarding;
- GitHub OAuth onboarding;
- user accounts;
- multi-user permissions;
- automatic AI code modification;
- autonomous redeployment;
- full observability platform;
- advanced enterprise security platform;
- complex database architecture;
- multi-service / microservice architecture;
- mobile application;
- generic chat assistant;
- support for every possible failure mode;
- large-scale or global architecture.

## 11. Portfolio Objective

DeployPilot should demonstrate the intersection of:

- cloud engineering;
- software development;
- DevOps;
- platform engineering;
- automation;
- Infrastructure as Code;
- Git / GitHub;
- CI/CD;
- containers;
- TypeScript;
- Python;
- AI-assisted developer tooling.

The final project should be understandable enough to explain clearly in an interview from code push to failure diagnosis.
