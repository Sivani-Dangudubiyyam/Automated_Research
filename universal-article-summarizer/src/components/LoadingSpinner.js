import React from 'react'

function LoadingSpinner() {
  return (
    <div className="card loading-spinner">
      <div className="spinner"></div>
      <p>Analyzing article and extracting key insights...</p>
    </div>
  )
}

export default LoadingSpinner
