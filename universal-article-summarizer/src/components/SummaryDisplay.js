import React from 'react'

function SummaryDisplay({summary, url, onReset}) {
  return (
    <div className="card">
      <div className="summary-header">
        <h2>📄 Research Summary</h2>
        <div className="action-buttons">
          <button onClick={onReset} className="btn btn-outline">
            🔄 New Search
          </button>
        </div>
      </div>

      <div className="source-url">
        <strong>Source:</strong>{' '}
        <a href={url} target="_blank" rel="noopener noreferrer">
          {url}
        </a>
      </div>

      {summary.keyPoints && summary.keyPoints.length > 0 && (
        <div className="key-points">
          <h3>🎯 Key Points</h3>
          <ul>
            {summary.keyPoints.map((point, index) => (
              <li key={index}>{point}</li>
            ))}
          </ul>
        </div>
      )}

      {summary.fullSummary && (
        <div className="full-summary">
          <h3>📝 Full Summary</h3>
          <p>{summary.fullSummary}</p>
        </div>
      )}
    </div>
  )
}

export default SummaryDisplay
