import { useEffect, useState } from 'react'
import './App.css'

import type {
  DeploymentStatus,
  FailureAnalysis,
  FailureEvidence,
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

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadDashboard() {
      try {
        const deploymentResponse = await fetch(
          'http://127.0.0.1:8000/api/deployment'
        )

        if (!deploymentResponse.ok) {
          throw new Error(
            `Deployment request returned ${deploymentResponse.status}`
          )
        }

        const deploymentData: DeploymentStatus =
          await deploymentResponse.json()

        setDeployment(deploymentData)

        if (deploymentData.deployment === 'failed') {
          const failure: FailureEvidence = {
            application: deploymentData.application,
            environment: deploymentData.environment,
            stage: 'deployment',
            error_message:
              'Required environment variable DEMO_CONFIG is missing',
            logs: [
              'Health check returned HTTP 500',
            ],
            health_status: 'unhealthy',
          }

          const analysisResponse = await fetch(
            'http://127.0.0.1:8000/api/analyze',
            {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(failure),
            }
          )

          if (!analysisResponse.ok) {
            throw new Error(
              `Analysis request returned ${analysisResponse.status}`
            )
          }

          const analysisData: FailureAnalysis =
            await analysisResponse.json()

          setAnalysis(analysisData)
        }
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message)
        } else {
          setError('Unable to load DeployPilot data')
        }
      } finally {
        setLoading(false)
      }
    }

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
          </div>
        </section>

        {analysis && (
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
      </section>
    </main>
  )
}

export default App
