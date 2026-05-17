import { useState } from 'react'

// ============================================================
// AI-Generated Landing Page Preview — renders HTML in iframe
// (section was commented-out in Streamlit, now fully working)
// ============================================================
export default function LandingPagePreview({ html }) {
  const [open, setOpen] = useState(false)

  if (!html) return null

  // Create a blob URL for the iframe src
  const blob = new Blob([html], { type: 'text/html' })
  const blobUrl = URL.createObjectURL(blob)

  return (
    <div className="landing-preview-section">
      <div
        className="landing-preview-header"
        onClick={() => setOpen(o => !o)}
        role="button"
        aria-expanded={open}
        id="landing-page-preview-toggle"
      >
        <div className="landing-preview-title">
          🌐 AI-Generated Landing Page Preview
        </div>
        <div className="landing-preview-toggle">
          {open ? 'Hide' : 'Show'} <span className={`chevron ${open ? 'open' : ''}`}>▼</span>
        </div>
      </div>

      {open && (
        <iframe
          id="landing-page-iframe"
          className="landing-iframe"
          srcDoc={html}
          title="AI-Generated Landing Page"
          sandbox="allow-scripts allow-same-origin"
        />
      )}
    </div>
  )
}
