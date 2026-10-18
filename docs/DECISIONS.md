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

---

## D-016 — Use a user-assigned identity for ACR image pulls

**Status:** Accepted  
**Date:** 2026-10-16

The foundation template creates a user-assigned managed identity and assigns the built-in `AcrPull` role at the ACR resource scope. The Container App will use this identity to pull its image. This assumes the registry uses the non-ABAC permission model.

Reason:

- avoids registry admin credentials;
- limits pull permission to this registry;
- lets the identity and permission exist before the Container App is deployed.

---

## D-017 — Start the Container Apps environment without Log Analytics

**Status:** Accepted  
**Date:** 2026-10-16

The development Container Apps environment uses the Consumption workload profile and disables zone redundancy. The current template does not configure Log Analytics or an app log destination.

Reason:

- keeps the first environment small and avoids a Log Analytics workspace at this stage;
- allows the demo app to use Consumption scaling;
- leaves log collection as a later explicit decision when runtime failure evidence is implemented.

This choice limits log-based troubleshooting until a collection path is added.

---

## D-018 — Separate CI image publishing from runtime image pulls

**Status:** Accepted  
**Date:** 2026-10-17

The foundation template creates a second user-assigned identity for GitHub deployment and grants it `AcrPush` at the ACR resource scope. The runtime identity keeps its separate `AcrPull` assignment.

Reason:

- GitHub can push and pull images without registry admin credentials;
- the role assignment is limited to this registry;
- CI publishing and Container App runtime use separate identities.

The foundation template defines the GitHub OIDC federated credential and a resource-group-scoped Container Apps Contributor assignment for the GitHub identity. The new role assignment still needs to be deployed before the workflow can manage Container Apps.

The federated credential uses a branch-scoped GitHub OIDC subject containing the immutable owner and repository IDs. The subject format must match the repository's actual GitHub OIDC token before deployment.

---

## D-019 — Use stable API error responses

**Status:** Accepted
**Date:** 2026-10-18

Backend errors use an `error` object with a stable `code` and a short `message`. Request validation returns a generic message, and AI or GitHub provider exceptions are not echoed to API clients.

Reason:

- gives the frontend predictable errors to display or handle;
- avoids exposing provider details or validation internals;
- keeps the MVP response format small.
