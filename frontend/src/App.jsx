// ============================================================
// App.jsx — Main state machine + polling loop
// Mirrors Streamlit session_state + while True: time.sleep(2)
// ============================================================

import { useState, useRef, useCallback } from 'react'
import { submitIdea, pollStatus } from './api'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import IdeaForm from './components/IdeaForm'
import ProgressBar from './components/ProgressBar'
import ResultCards from './components/ResultCards'
import LandingPagePreview from './components/LandingPagePreview'
import FullReport from './components/FullReport'

// Initial state — mirrors Streamlit session_state defaults
const INITIAL_STATE = {
  jobId: null,
  result: null,
  running: false,
  error: null,
  progress: 0,
  currentStep: '',
}

export default function App() {
  const [state, setState] = useState(INITIAL_STATE)
  const intervalRef = useRef(null)

  // ── Stop polling ──────────────────────────────────────────
  function stopPolling() {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  // ── Poll every 2 seconds — mirrors time.sleep(2) loop ────
  function startPolling(jobId) {
    stopPolling()

    intervalRef.current = setInterval(async () => {
      try {
        const data = await pollStatus(jobId)

        const pct = data.progress ?? 0
        const step = data.current_step ?? 'Running...'
        const status = data.status ?? 'running'

        // Update progress display
        setState(prev => ({
          ...prev,
          progress: pct,
          currentStep: step,
        }))

        if (status === 'completed') {
          stopPolling()
          setState(prev => ({
            ...prev,
            result: data.result,
            running: false,
            currentStep: 'Done',
            progress: 100,
          }))
        }

        if (status === 'failed') {
          stopPolling()
          setState(prev => ({
            ...prev,
            error: data.error || 'Pipeline failed.',
            running: false,
          }))
        }
      } catch (err) {
        stopPolling()
        setState(prev => ({
          ...prev,
          error: 'Connection lost. Is the FastAPI server running?',
          running: false,
        }))
      }
    }, 2000) // 2-second poll, same as Streamlit
  }

  // ── Handle form submit — mirrors analyze_clicked block ───
  const handleSubmit = useCallback(async (idea) => {
    setState({
      ...INITIAL_STATE,
      running: true,
    })

    try {
      const data = await submitIdea(idea)
      const jobId = data.job_id

      setState(prev => ({
        ...prev,
        jobId,
        progress: data.progress ?? 0,
        currentStep: data.current_step ?? 'Queued',
      }))

      startPolling(jobId)
    } catch (err) {
      setState(prev => ({
        ...prev,
        running: false,
        error: `API Error: ${err.message}`,
      }))
    }
  }, [])

  // ── Reset — mirrors sidebar Reset button ─────────────────
  function handleReset() {
    stopPolling()
    setState(INITIAL_STATE)
  }

  const { running, result, error, progress, currentStep } = state

  return (
    <div className="app-layout">
      {/* ── Sidebar ─────────────────────────────────────── */}
      <Sidebar
        currentStep={currentStep}
        isDone={!!result}
        onReset={handleReset}
      />

      {/* ── Main Content ────────────────────────────────── */}
      <main className="main-content">
        <Header />

        {/* Input form */}
        <IdeaForm onSubmit={handleSubmit} disabled={running} />

        {/* Progress bar (while running) */}
        {running && (
          <ProgressBar progress={progress} currentStep={currentStep} />
        )}

        {/* Error box */}
        {error && !running && (
          <div className="error-box" id="error-display">
            <span>⚠</span>
            <span>{error}</span>
          </div>
        )}

        {/* Results section */}
        {result && !running && (
          <section className="results-section" id="results-section">
            <h2 className="results-title">Startup Validation Report</h2>

            {/* 4 analysis cards in 2-col grid */}
            <ResultCards result={result} />

            {/* AI-generated landing page preview */}
            <LandingPagePreview html={result.landing_page} />

            {/* Full report + download */}
            <FullReport result={result} />
          </section>
        )}
      </main>
    </div>
  )
}
