// Centralized API configuration
const getApiBaseUrl = (): string => {
  // Use environment variable if available, otherwise default to '/api' for development
  return import.meta.env.VITE_API_BASE_URL || '/api'
}

// QRZ lookup configuration
const getQrzLookupUrl = (): string => {
  // Use environment variable if available, otherwise default to QRZ.com
  return import.meta.env.VITE_QRZ_LOOKUP_URL || 'https://www.qrz.com/db/{CALLSIGN}'
}

export const API_BASE_URL = getApiBaseUrl()
export const QRZ_LOOKUP_URL_TEMPLATE = getQrzLookupUrl()