# DeployPilot — Roadmap

## Status Legend

- [ ] Not started
- [~] In progress
- [x] Complete

## Phase 1 — Project Definition

- [x] Define the core problem.
- [x] Define the MVP.
- [x] Define v1 exclusions.
- [x] Define the user flow.
- [x] Lock the technology stack.
- [x] Create persistent Codex project-context files.

**Phase 1 outcome:** project scope and architecture are stable enough to begin implementation.

---

## Phase 2 — Repository Bootstrap

- [x] Create the Git repository.
- [x] Create the initial directory structure.
- [x] Add `.gitignore`.
- [ ] Add initial `README.md`.
- [ ] Add frontend scaffold.
- [ ] Add backend scaffold.
- [ ] Add demo application scaffold.
- [ ] Confirm local development commands.

**Exit condition:** the repository opens cleanly in Codex and each main component has a minimal runnable scaffold.

---

## Phase 3 — Demo Application

- [ ] Implement `/`.
- [ ] Implement `/health`.
- [ ] Add a small automated test suite.
- [ ] Add a controlled HTTP 500 failure path.
- [ ] Add a configurable missing-environment-variable failure.
- [ ] Confirm tests pass locally.

**Exit condition:** the demo application is simple, testable, and capable of controlled failures.

---

## Phase 4 — DeployPilot Backend

- [ ] Create FastAPI backend.
- [ ] Define deployment-status models.
- [ ] Define failure-evidence model.
- [ ] Create API endpoint(s) for deployment status.
- [ ] Create API endpoint for failure analysis.
- [ ] Add validation and basic tests.

**Exit condition:** backend can accept / expose structured deployment information without AI.

---

## Phase 5 — DeployPilot Frontend

- [ ] Create React + TypeScript + Vite app.
- [ ] Create deployment summary view.
- [ ] Create stage status display.
- [ ] Create AI analysis panel.
- [ ] Create raw-log view or expandable section.
- [ ] Connect frontend to FastAPI backend.

**Exit condition:** dashboard can render realistic deployment data from the backend.

---

## Phase 6 — Docker

- [ ] Create Dockerfile for demo application.
- [ ] Build image locally.
- [ ] Run image locally.
- [ ] Verify `/health`.
- [ ] Add appropriate `.dockerignore`.

**Exit condition:** demo application runs reliably from a Docker image.

---

## Phase 7 — Continuous Integration

- [ ] Add GitHub Actions workflow.
- [ ] Install dependencies in CI.
- [ ] Run tests in CI.
- [ ] Run lightweight checks.
- [ ] Build Docker image in CI.
- [ ] Confirm a deliberately broken test fails the workflow.

**Exit condition:** every relevant push can deterministically pass or fail through CI.

---

## Phase 8 — Azure Infrastructure with Bicep

- [ ] Define ACR.
- [ ] Define Container Apps Environment.
- [ ] Define Container App.
- [ ] Define required identity / permissions.
- [ ] Define required configuration parameters.
- [ ] Validate Bicep.
- [ ] Deploy infrastructure.

**Exit condition:** Azure runtime infrastructure can be recreated from code.

---

## Phase 9 — Continuous Deployment

- [ ] Configure GitHub -> Azure authentication.
- [ ] Prefer OIDC where practical.
- [ ] Push Docker image to ACR.
- [ ] Deploy image to Azure Container Apps.
- [ ] Verify deployed health endpoint.
- [ ] Expose deployment status to DeployPilot.

**Exit condition:** a Git push can result in an automated Azure deployment.

---

## Phase 10 — Failure Evidence Collection

- [ ] Define normalized failure schema.
- [ ] Capture CI-stage failures.
- [ ] Capture deployment-stage failures.
- [ ] Capture runtime / health failures.
- [ ] Limit log excerpts to relevant information.
- [ ] Add secret-redaction rules where needed.

**Exit condition:** DeployPilot can produce a compact structured failure record without AI.

---

## Phase 11 — AI Deployment Assistant

- [ ] Add server-side OpenAI API integration.
- [ ] Keep API key out of frontend and Git.
- [ ] Define structured AI response schema.
- [ ] Create prompt for failure interpretation.
- [ ] Send only minimum useful context.
- [ ] Validate / parse model output.
- [ ] Display analysis in dashboard.

**Exit condition:** selected failure evidence produces a reliable structured diagnosis.

---

## Phase 12 — Demonstration Scenarios

### Scenario 1 — Success

- [ ] Tests pass.
- [ ] Image builds.
- [ ] Deployment succeeds.
- [ ] Health check passes.
- [ ] Dashboard shows healthy state.

### Scenario 2 — CI failure

- [ ] Deliberately fail a unit test.
- [ ] Capture failed test evidence.
- [ ] AI explains the failure.
- [ ] Dashboard displays suggested next action.

### Scenario 3 — Deployment / runtime failure

- [ ] Deliberately remove required configuration or trigger HTTP 500.
- [ ] Capture runtime / deployment evidence.
- [ ] AI explains the failure.
- [ ] Dashboard displays suggested next action.

**Exit condition:** all three flows can be demonstrated predictably.

---

## Phase 13 — Engineering Polish

- [ ] Improve error handling.
- [ ] Add structured logging.
- [ ] Review secret handling.
- [ ] Review API validation.
- [ ] Clean project structure.
- [ ] Add important tests.
- [ ] Remove unused dependencies and dead code.

---

## Phase 14 — Portfolio and Interview Readiness

- [ ] Complete README.
- [ ] Add architecture diagram.
- [ ] Add screenshots.
- [ ] Document CI/CD flow.
- [ ] Document Bicep infrastructure.
- [ ] Document AI design and minimum-context approach.
- [ ] Document security considerations.
- [ ] Document deliberate failure demos.
- [ ] Add lessons learned.
- [ ] Add future improvements.
- [ ] Prepare a concise interview explanation.

**Final MVP exit condition:**

A reviewer can understand and demonstrate:

Code -> Test -> Build -> Containerize -> Provision -> Deploy -> Observe -> Troubleshoot

without needing undocumented manual steps.

---

## Deferred / v2 Ideas

Only consider these after the MVP is complete:

- GitHub OAuth / arbitrary repository onboarding;
- deployment history backed by a database;
- multiple applications;
- staging and production environments;
- rollback;
- Azure Monitor / Application Insights integration;
- automatic pull-request fix suggestions;
- controlled remediation workflows;
- Kubernetes / AKS;
- additional cloud providers.
