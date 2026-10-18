import { useEffect, useState } from 'react'
import './App.css'

import type {
  DeploymentStatus,
  FailureAnalysis,
  FailureEvidence,
  FailureReport,
  RuntimeFailureReport,
  StageStatus,
} from './types'

function getStatusSymbol(status: StageStatus) {
  switch (status) {
    case 'passed':
      return '✓'
    case 'failed':
      return '✕'
    case 'running':
      return '…'
    case 'pending':
      return '○'
  }
}


function getStatusLabel(status: StageStatus) {
  switch (status) {
    case 'passed':
      return 'Passed'
    case 'failed':
      return 'Failed'
    case 'running':
      return 'Running'
    case 'pending':
      return 'Pending'
  }
}


function StatusRow({
  label,
  status,
}: {
  label: string
  status: StageStatus
}) {
  return (
    <div className={`status-row status-${status}`}>
      <span className="status-name">{label}</span>

      <span className="status-value">
        <span className="status-symbol">
          {getStatusSymbol(status)}
        </span>

        {getStatusLabel(status)}
      </span>
    </div>
  )
}


function App() {
  const [deployment, setDeployment] =
    useState<DeploymentStatus | null>(null)

  const [analysis, setAnalysis] =
    useState<FailureAnalysis | null>(null)

  const [failureEvidence, setFailureEvidence] =
    useState<FailureEvidence | null>(null)

  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const [analysisLoading, setAnalysisLoading] =
    useState(false)

  const [error, setError] = useState<string | null>(null)

  async function loadDashboard(
    isRefresh = false
  ) {
    if (isRefresh) {
      setRefreshing(true)
    } else {
      setLoading(true)
    }

    setError(null)

    try {
      const deploymentResponse = await fetch(
        'http://127.0.0.1:8000/api/deployment',
        {
          cache: 'no-store',
        }
      )

      if (!deploymentResponse.ok) {
        throw new Error(
          `Deployment request returned ${deploymentResponse.status}`
        )
      }

      const deploymentData: DeploymentStatus =
        await deploymentResponse.json()

      setDeployment(deploymentData)
      setAnalysis(null)
      setFailureEvidence(null)

      const hasPipelineFailure = [
        deploymentData.tests,
        deploymentData.build,
        deploymentData.container,
        deploymentData.deployment,
      ].includes('failed')

      const hasRuntimeFailure =
        deploymentData.runtime === 'failed'

      if (hasPipelineFailure) {
        setAnalysisLoading(true)

        try {
          const reportResponse = await fetch(
            `http://127.0.0.1:8000/api/failure-report/${deploymentData.run_id}`,
            {
              method: 'POST',
              cache: 'no-store',
            }
          )

          if (!reportResponse.ok) {
            throw new Error(
              `Failure report request returned ${reportResponse.status}`
            )
          }

          const reportData: FailureReport =
            await reportResponse.json()

          if (reportData.run_id !== deploymentData.run_id) {
            throw new Error(
              'Failure analysis does not match the current workflow run'
            )
          }

          setFailureEvidence(
            reportData.evidence
          )

          setAnalysis(
            reportData.analysis
          )
        } finally {
          setAnalysisLoading(false)
        }

      } else if (hasRuntimeFailure) {
        setAnalysisLoading(true)

        try {
          const reportResponse = await fetch(
            'http://127.0.0.1:8000/api/runtime-failure-report',
            {
              method: 'POST',
              cache: 'no-store',
            }
          )

          if (!reportResponse.ok) {
            throw new Error(
              `Runtime failure report returned ${reportResponse.status}`
            )
          }

          const reportData: RuntimeFailureReport =
            await reportResponse.json()

          setFailureEvidence(
            reportData.evidence
          )

          setAnalysis(
            reportData.analysis
          )
        } finally {
          setAnalysisLoading(false)
        }

      } else {
        setAnalysis(null)
        setFailureEvidence(null)
      }

    } catch (err) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError(
          'Unable to load DeployPilot data'
        )
      }

    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    loadDashboard()
  }, [])

  if (loading) {
    return (
      <main className="page">
        <section className="dashboard">
          <p>Loading deployment...</p>
        </section>
      </main>
    )
  }

  if (error) {
    return (
      <main className="page">
        <section className="dashboard">
          <h1>DeployPilot</h1>
          <p>Unable to load deployment.</p>
          <p>{error}</p>
        </section>
      </main>
    )
  }

  if (!deployment) {
    return null
  }

  return (
    <main className="page">
      <section className="dashboard">
        <header className="dashboard-header">
          <div>
            <h1>DeployPilot</h1>
            <p>Deployment dashboard</p>
          </div>

          <button
            className="refresh-button"
            onClick={() => loadDashboard(true)}
            disabled={refreshing || analysisLoading}
          >
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </header>

        <section className="deployment-card">
          <div className="deployment-meta">
            <div>
              <span className="meta-label">Application</span>
              <strong>{deployment.application}</strong>
            </div>

            <div>
              <span className="meta-label">Environment</span>
              <strong>{deployment.environment}</strong>
            </div>
          </div>

          <div className="deployment-meta">
            <div>
              <span className="meta-label">
                Branch
              </span>

              <strong>
                {deployment.branch}
              </strong>
            </div>

            <div>
              <span className="meta-label">
                Commit
              </span>

              <strong title={deployment.commit_sha}>
                {deployment.commit_sha.slice(0, 7)}
              </strong>
            </div>

            <div>
              <span className="meta-label">
                Workflow run
              </span>

              <a
                href={deployment.workflow_url}
                target="_blank"
                rel="noreferrer"
              >
                #{deployment.run_number}
              </a>
            </div>

            <div>
              <span className="meta-label">
                Updated
              </span>

              <strong>
                {new Date(
                  deployment.updated_at
                ).toLocaleString()}
              </strong>
            </div>
          </div>

          <div className="status-list">
            <StatusRow
              label="Build"
              status={deployment.build}
            />

            <StatusRow
              label="Tests"
              status={deployment.tests}
            />

            <StatusRow
              label="Container"
              status={deployment.container}
            />

            <StatusRow
              label="Deployment"
              status={deployment.deployment}
            />

            <StatusRow
              label="Runtime"
              status={deployment.runtime}
            />
          </div>
        </section>

        {analysisLoading && (
          <section className="analysis-card">
            <span className="analysis-eyebrow">
              AI Deployment Assistant
            </span>

            <p>
              Analyzing failure evidence...
            </p>
          </section>
        )}

        {analysis && !analysisLoading && (
          <section className="analysis-card">
            <div className="analysis-header">
              <div>
                <span className="analysis-eyebrow">
                  AI Deployment Assistant
                </span>

                <h2>Failure analysis</h2>
              </div>

              <span className="analysis-stage">
                {analysis.stage}
              </span>
            </div>

            <div className="analysis-section">
              <span className="analysis-label">
                Problem
              </span>

              <p>{analysis.problem}</p>
            </div>

            <div className="analysis-section">
              <span className="analysis-label">
                Likely cause
              </span>

              <p>{analysis.likely_cause}</p>
            </div>

            <div className="analysis-section">
              <span className="analysis-label">
                Suggested fix
              </span>

              <p>{analysis.suggested_fix}</p>
            </div>
          </section>
        )}

        {failureEvidence && !analysisLoading && (
          <section className="evidence-card">
            <details>
              <summary>
                View failure evidence
              </summary>

              <div className="evidence-content">
                <div className="evidence-meta">
                  <span>Stage</span>
                  <strong>{failureEvidence.stage}</strong>
                </div>

                <div className="evidence-meta">
                  <span>Detected error</span>
                  <strong>{failureEvidence.error_message}</strong>
                </div>

                {failureEvidence.exit_code !== null &&
                  failureEvidence.exit_code !== undefined && (
                    <div className="evidence-meta">
                      <span>Exit code</span>
                      <strong>{failureEvidence.exit_code}</strong>
                    </div>
                  )}

                {failureEvidence.health_status && (
                  <div className="evidence-meta">
                    <span>Health</span>
                    <strong>{failureEvidence.health_status}</strong>
                  </div>
                )}

                {failureEvidence.http_status !== null &&
                  failureEvidence.http_status !== undefined && (
                    <div className="evidence-meta">
                      <span>HTTP status</span>
                      <strong>{failureEvidence.http_status}</strong>
                    </div>
                  )}

                <pre className="evidence-log">
                  {failureEvidence.logs.join('\n')}
                </pre>
              </div>
            </details>
          </section>
        )}
      </section>
    </main>
  )
}

export default App
