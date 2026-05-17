import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

// ============================================================
// Single result card — mirrors Streamlit card()
// ============================================================
function Card({ title, icon, content, colorClass }) {
  return (
    <div className={`result-card ${colorClass}`}>
      <div className="card-header">
        <div className={`card-icon ${colorClass}`}>{icon}</div>
        <div className="card-title">{title}</div>
      </div>
      <div className="card-body">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {content || '_No data_'}
        </ReactMarkdown>
      </div>
    </div>
  )
}

// ============================================================
// ResultCards — 2-column grid, mirrors Streamlit col1 / col2
// ============================================================
export default function ResultCards({ result }) {
  return (
    <div className="results-grid">
      <Card
        title="Market Research"
        icon="📈"
        content={String(result.market_research || '')}
        colorClass="blue"
      />
      <Card
        title="Competitor Analysis"
        icon="🔍"
        content={String(result.competitors || '')}
        colorClass="purple"
      />
      <Card
        title="Revenue Model"
        icon="💰"
        content={String(result.revenue_model || '')}
        colorClass="green"
      />
      <Card
        title="MVP Plan"
        icon="🗺"
        content={String(result.mvp_plan || '')}
        colorClass="orange"
      />
    </div>
  )
}
