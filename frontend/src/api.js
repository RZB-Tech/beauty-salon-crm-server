import { getInitData } from './telegram'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export class ApiError extends Error {
  constructor(status, body) {
    super(body?.detail || `HTTP ${status}`)
    this.status = status
    this.code = body?.error_code   // e.g. GLOBAL_CLIENT_NOT_REGISTERED, VALIDATION_ERROR
    this.metadata = body?.metadata
  }
}

async function request(path, { method = 'GET', body } = {}) {
  const response = await fetch(`${BASE_URL}/api/v1/mini-app${path}`, {
    method,
    headers: {
      Authorization: `tma ${getInitData()}`,
      ...(body ? { 'Content-Type': 'application/json' } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  })
  const data = await response.json().catch(() => null)
  if (!response.ok) throw new ApiError(response.status, data)
  return data
}

export const getProfile = () => request('/me')
export const register = (data) => request('/me', { method: 'POST', body: data })
