// ============================================================
// API HELPERS — mirrors Streamlit submit_idea + poll_status
// ============================================================

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

/**
 * POST /analyze
 * Returns { job_id, status, progress, current_step }
 */
export async function submitIdea(startupIdea) {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ startup_idea: startupIdea }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Server error ${res.status}`)
  }

  return res.json()
}

/**
 * GET /status/{job_id}
 * Returns { job_id, status, progress, current_step, result, error }
 */
export async function pollStatus(jobId) {
  const res = await fetch(`${API_BASE}/status/${jobId}`)

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Status error ${res.status}`)
  }

  return res.json()
}
