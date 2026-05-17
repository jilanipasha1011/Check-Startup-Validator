import { useState } from 'react'

export default function IdeaForm({ onSubmit, disabled }) {
  const [idea, setIdea] = useState('')
  const [warn, setWarn] = useState(false)

  function handleSubmit(e) {
    e.preventDefault()
    if (!idea.trim()) {
      setWarn(true)
      setTimeout(() => setWarn(false), 3000)
      return
    }
    setWarn(false)
    onSubmit(idea.trim())
  }

  return (
    <form className="idea-form" onSubmit={handleSubmit}>
      <textarea
        id="startup-idea-input"
        className="idea-textarea"
        placeholder="Enter your startup idea... e.g. An AI-powered tool that helps freelancers find clients automatically"
        value={idea}
        onChange={e => setIdea(e.target.value)}
        disabled={disabled}
        rows={5}
      />
      <p className="char-count">{idea.length} characters</p>

      {warn && (
        <div className="warn-box">⚠ Please enter your startup idea before analyzing.</div>
      )}

      <button
        id="analyze-btn"
        type="submit"
        className="submit-btn"
        disabled={disabled}
      >
        {disabled ? (
          <>
            <span className="spinner" />
            Analyzing...
          </>
        ) : (
          <>🚀 Analyze My Startup Idea</>
        )}
      </button>
    </form>
  )
}
