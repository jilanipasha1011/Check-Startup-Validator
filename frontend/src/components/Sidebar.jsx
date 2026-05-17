// ============================================================
// PIPELINE STEPS — mirrors Streamlit STEPS list
// ============================================================
export const STEPS = [
  'Market Research',
  'Competitor Analysis',
  'Merging Results',
  'Revenue Model',
  'MVP Planning',
  'Landing Page',
  'Finalizing',
  'Done',
]

// Normalize step label for comparison
function normalize(s) {
  return s?.toLowerCase().replace(/[^a-z]/g, '') || ''
}

export default function Sidebar({ currentStep, isDone, onReset }) {
  const normCurrent = normalize(currentStep)

  const currentIdx = STEPS.findIndex(
    s => normalize(s) === normCurrent || normCurrent.includes(normalize(s))
  )

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span className="emoji">🚀</span>
        Startup Validator
      </div>

      <div>
        <p className="sidebar-section-title">Pipeline Steps</p>
        <div className="pipeline-steps">
          {STEPS.map((step, i) => {
            const done = isDone || i < currentIdx
            const active = !isDone && i === currentIdx
            return (
              <div
                key={step}
                className={`step-item ${active ? 'active' : ''} ${done ? 'done' : ''}`}
              >
                <span className="step-dot" />
                {step}
              </div>
            )
          })}
        </div>
      </div>

      <button className="sidebar-reset-btn" onClick={onReset}>
        ↺ Reset
      </button>
    </aside>
  )
}
