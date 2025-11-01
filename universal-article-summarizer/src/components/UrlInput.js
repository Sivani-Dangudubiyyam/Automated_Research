import React, {useState} from 'react'

function UrlInput({onSubmit}) {
  const [url, setUrl] = useState('')

  const handleSubmit = e => {
    e.preventDefault()
    if (url.trim()) {
      onSubmit(url.trim())
    }
  }

  return (
    <div className="card">
      <form onSubmit={handleSubmit} className="url-input-form">
        <div>
          <label
            htmlFor="url"
            style={{
              display: 'block',
              marginBottom: '0.5rem',
              color: '#374151',
              fontWeight: '500',
            }}
          >
            Enter Article URL
          </label>
          <div className="input-group">
            <input
              id="url"
              type="url"
              className="url-input"
              placeholder="https://example.com/article"
              value={url}
              onChange={e => setUrl(e.target.value)}
              required
            />
            <button type="submit" className="btn btn-primary">
              Analyze
            </button>
          </div>
        </div>
        <p style={{fontSize: '0.875rem', color: '#6b7280'}}>
          📌 Paste any article URL to extract key insights and important points
        </p>
      </form>
    </div>
  )
}

export default UrlInput
