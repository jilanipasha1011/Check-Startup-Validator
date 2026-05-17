import { useState } from 'react'

// ============================================================
// Full report expandable + download — mirrors Streamlit expander
// and st.download_button
// ============================================================
export default function FullReport({ result }) {
  const [open, setOpen] = useState(false)

  const fullReport = `STARTUP IDEA:
${result.startup_idea || ''}


MARKET RESEARCH:
${result.market_research || ''}


COMPETITOR ANALYSIS:
${result.competitors || ''}


REVENUE MODEL:
${result.revenue_model || ''}


MVP PLAN:
${result.mvp_plan || ''}
`

  function handleDownload() {
    const blob = new Blob([fullReport], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'startup_report.txt'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="full-report-section">
      <div
        className={`full-report-header ${open ? 'open' : ''}`}
        onClick={() => setOpen(o => !o)}
        role="button"
        aria-expanded={open}
        id="full-report-toggle"
      >
        <div className="full-report-title">
          📄 View Full AI Report
        </div>
        <span className={`chevron ${open ? 'open' : ''}`}>▼</span>
      </div>

      {open && (
        <div className="full-report-body">
          <pre className="full-report-pre">{fullReport}</pre>
        </div>
      )}

      <div style={{ padding: '1rem 1.5rem', borderTop: open ? '1px solid var(--border-subtle)' : 'none' }}>
        <button
          id="download-report-btn"
          className="download-btn"
          onClick={handleDownload}
        >
          ⬇ Download Full Report
        </button>
      </div>
    </div>
  )
}
