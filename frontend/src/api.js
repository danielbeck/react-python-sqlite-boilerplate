// API configuration for different environments
import { config } from './config.js'

const isDevelopment = import.meta.env.DEV

export const API_BASE_URL = isDevelopment
  ? '/api'  // Use Vite proxy in development
  : config.API_BASE_PATH  // Use configured path in production

export async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    console.error('API request failed:', error)
    throw error
  }
}
