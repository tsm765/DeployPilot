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
}

export interface FailureEvidence {
  application: string
  environment: string
  stage: FailureStage
  error_message: string
  logs: string[]
  exit_code?: number | null
  health_status?: string | null
}

export interface FailureAnalysis {
  stage: FailureStage
  problem: string
  likely_cause: string
  suggested_fix: string
}
