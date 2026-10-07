# DeployPilot — Decision Log

This file records important project decisions so later Codex threads do not need to reconstruct them from chat history.

## D-001 — Build DeployPilot as a focused portfolio MVP

**Status:** Accepted  
**Date:** 2026-10-07

DeployPilot will demonstrate one complete software-delivery workflow rather than attempt to become a production SaaS platform.

Reason:

- clearer portfolio story;
- manageable scope;
- easier to finish;
- easier to explain in interviews.

---

## D-002 — Use React + TypeScript + Vite for the frontend

**Status:** Accepted  
**Date:** 2026-10-07

Reason:

- demonstrates TypeScript explicitly;
- appropriate for a small developer dashboard;
- Vite keeps setup lightweight.

---

## D-003 — Use Python + FastAPI for the DeployPilot backend

**Status:** Accepted  
**Date:** 2026-10-07

Reason:

- simple API development;
- strong fit for AI integration;
- keeps backend implementation readable;
- aligns with existing Python familiarity.

---

## D-004 — Use a small FastAPI demo application as the deployable workload

**Status:** Accepted  
**Date:** 2026-10-07

The demo workload is separate from the DeployPilot backend.

Reason:

- gives CI/CD a real application to test and deploy;
- easy to create controlled failure scenarios;
- avoids unnecessary application complexity.

---

## D-005 — Use Docker for application packaging

**Status:** Accepted  
**Date:** 2026-10-07

Reason:

- directly demonstrates containerization;
- integrates cleanly with GitHub Actions, ACR, and Azure Container Apps.

---

## D-006 — Use GitHub Actions for CI/CD

**Status:** Accepted  
**Date:** 2026-10-07

Reason:

- repository-native;
- relevant to target roles;
- supports test, build, push, and deployment automation.

---

## D-007 — Use Azure Container Registry for image storage

**Status:** Accepted  
**Date:** 2026-10-07

Reason:

- native fit for the Azure deployment path;
- straightforward integration with Azure Container Apps.

---

## D-008 — Use Azure Container Apps instead of AKS for v1

**Status:** Accepted  
**Date:** 2026-10-07

Reason:

- proves cloud-native container deployment;
- avoids unnecessary Kubernetes operational complexity;
- preserves time for CI/CD and AI troubleshooting.

AKS / Kubernetes is explicitly postponed.

---

## D-009 — Use Bicep for Infrastructure as Code

**Status:** Accepted  
**Date:** 2026-10-07

Reason:

- Azure-native IaC;
- demonstrates reproducible infrastructure;
- keeps cloud configuration versioned with the project.

---

## D-010 — Prefer OIDC from GitHub Actions to Azure

**Status:** Accepted  
**Date:** 2026-10-07

Reason:

- avoids relying on long-lived Azure credentials where practical;
- demonstrates a modern CI/CD authentication pattern.

---

## D-011 — Use the OpenAI API for failure interpretation

**Status:** Accepted  
**Date:** 2026-10-07

AI will be used to explain failure evidence, not to determine whether a deployment succeeded.

Reason:

- deterministic tooling already knows pass / fail state;
- AI adds value by translating technical evidence into actionable guidance.

---

## D-012 — Do not send the entire repository to the LLM by default

**Status:** Accepted  
**Date:** 2026-10-07

Preferred AI input:

- pipeline stage;
- status;
- relevant error;
- selected log excerpts;
- exit code;
- health result;
- relevant configuration names;
- small source snippets only when useful.

Reason:

- minimum necessary context;
- lower token usage;
- clearer troubleshooting prompts;
- better security and privacy posture.

---

## D-013 — Keep DeployPilot v1 primarily read-only

**Status:** Accepted  
**Date:** 2026-10-07

DeployPilot may observe and explain failures, but it will not automatically:

- change source code;
- modify infrastructure;
- change secrets;
- redeploy applications.

Reason:

- keeps AI advisory rather than autonomous;
- reduces risk and implementation complexity;
- produces a cleaner v1 architecture.

---

## D-014 — No database unless a concrete requirement appears

**Status:** Accepted  
**Date:** 2026-10-07

Do not introduce PostgreSQL or another database just to make the project look more complete.

A database may be added later only if deployment history or another feature genuinely requires persistence.

---

## D-015 — Demonstrate three classes of outcome

**Status:** Accepted  
**Date:** 2026-10-07

The final MVP demo should include:

1. successful deployment;
2. CI / unit-test failure;
3. deployment or runtime failure.

This gives the project a clear end-to-end demonstration.
