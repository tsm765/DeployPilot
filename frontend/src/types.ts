export type StageStatus =
  | 'pending'
  | 'running'
  | 'passed'
  | 'failed'

export type FailureStage =
  | 'tests'
  | 'build'
  | 'container'
  | 'deployment'
  | 'runtime'

export interface DeploymentStatus {
  application: string
  environment: string

  build: StageStatus
  tests: StageStatus
  container: StageStatus
  deployment: StageStatus
  runtime: StageStatus

  run_id: number
  run_number: number
  branch: string
  commit_sha: string
  workflow_url: string
  created_at: string
  updated_at: string
}

export interface FailureEvidence {
  application: string
  environment: string
  stage: FailureStage
  error_message: string
  logs: string[]
  exit_code?: number | null
  health_status?: string | null
  http_status?: number | null
}

export interface FailureAnalysis {
  stage: FailureStage
  problem: string
  likely_cause: string
  suggested_fix: string
}

export interface FailureReport {
  run_id: number
  evidence: FailureEvidence
  analysis: FailureAnalysis
}

export interface RuntimeFailureReport {
  evidence: FailureEvidence
  analysis: FailureAnalysis
}
