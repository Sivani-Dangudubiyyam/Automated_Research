import axios from 'axios'

// API base URL - replace with your actual backend if needed
const API_BASE_URL =
  process.env.REACT_APP_API_URL || 'http://localhost:5000/api'

/**
 * Fetch summary from the backend
 * @param {string} url - Article URL to summarize
 * @returns {Promise<Object>} - Summary data with keyPoints and fullSummary
 */
export const fetchSummary = async url => {
  try {
    const response = await axios.post(`${API_BASE_URL}/summarize`, {url})
    return response.data
  } catch (error) {
    console.error('Error fetching summary:', error)

    // For development/demo: Return mock data
    if (process.env.NODE_ENV === 'development') {
      return getMockSummary()
    }

    throw new Error(
      error.response?.data?.message ||
        'Failed to fetch summary. Please check the URL and try again.',
    )
  }
}

/**
 * Mock data for development/testing
 */
const getMockSummary = () => {
  return {
    keyPoints: [
      'Artificial Intelligence is transforming multiple industries including healthcare, finance, and transportation',
      'Machine learning algorithms can process vast amounts of data much faster than humans',
      'Ethical considerations around AI include privacy concerns, bias in algorithms, and job displacement',
      'AI-powered automation is expected to increase productivity by 40% in the next decade',
      'Investment in AI research has grown by 300% over the past five years',
    ],
    fullSummary:
      'This article explores the revolutionary impact of Artificial Intelligence across various sectors. It highlights how AI technologies are being integrated into everyday applications, from virtual assistants to autonomous vehicles. The piece discusses both the tremendous opportunities AI presents for solving complex problems and the important ethical challenges that must be addressed. Key themes include the acceleration of AI adoption in business, the need for regulatory frameworks, and the importance of developing AI systems that are transparent, fair, and beneficial to society as a whole.',
  }
}
