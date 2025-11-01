import React, {useState} from 'react'
import UrlInput from './components/UrlInput'
import SummaryDisplay from './components/SummaryDisplay'
import LoadingSpinner from './components/LoadingSpinner'
import {fetchSummary} from './services/api'

function App() {
  const [url, setUrl] = useState('')
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleFetchSummary = async articleUrl => {
    setLoading(true)
    setError('')
    setSummary(null)

    try {
      const data = await fetchSummary(articleUrl)
      setSummary(data)
      setUrl(articleUrl)
    } catch (err) {
      setError(err.message || 'Failed to fetch summary. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setUrl('')
    setSummary(null)
    setError('')
  }

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🔍 AI Research Summarizer</h1>
          <p>Extract key insights from any article instantly</p>
        </header>

        {!summary && !loading && <UrlInput onSubmit={handleFetchSummary} />}

        {loading && <LoadingSpinner />}

        {error && (
          <div className="error-message">
            <span>⚠️</span> {error}
          </div>
        )}

        {summary && !loading && (
          <SummaryDisplay summary={summary} url={url} onReset={handleReset} />
        )}
      </div>
    </div>
  )
}

export default App
