// ============================================================
// PROGRESS BAR — mirrors Streamlit progress + status_text
// ============================================================

const ALL_STEPS = [
  'Market Research',
  'Competitor Analysis',
  'Merging Results',
  'Revenue Model',
  'MVP Planning',
  'Landing Page',
  'Finalizing',
  'Done',
]

function normalize(s) {
  return s?.toLowerCase().replace(/[^a-z]/g, '') || ''
}

export default function ProgressBar({ progress, currentStep }) {
  const normCurrent = normalize(currentStep)

  const currentIdx = ALL_STEPS.findIndex(
    s => normalize(s) === normCurrent || normCurrent.includes(normalize(s))
  )

  return (
    <div className="progress-section">
      <div className="progress-header">
        <div className="progress-step-label">
          <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
          {currentStep || 'Running...'}
        </div>
        <span className="progress-pct">{progress}%</span>
      </div>

      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="progress-steps-dots">
        {ALL_STEPS.map((step, i) => {
          const done = i < currentIdx
          const active = i === currentIdx
          return (
            <span
              key={step}
              className={`progress-step-chip ${active ? 'active' : ''} ${done ? 'done' : ''}`}
            >
              {done ? '✓ ' : ''}{step}
            </span>
          )
        })}
      </div>
    </div>
  )
}
