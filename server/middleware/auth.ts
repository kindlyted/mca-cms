import { defineEventHandler, getHeader, createError } from 'h3'

/**
 * API Authentication Middleware
 * Validates API Key for mutating operations and admin endpoints
 */
export default defineEventHandler((event) => {
  const path = event.path || event.node.req.url || ''
  const method = event.node.req.method || ''

  const isAdminPath = /^\/api\/(blog|services|partners|products)\/manage/.test(path)
  const isMutatingMethod = ['POST', 'PATCH', 'DELETE'].includes(method)
  const isApiEntityPath = /^\/api\/(blog|services|partners|products)(\/|$)/.test(path)

  if (!isAdminPath && !(isMutatingMethod && isApiEntityPath)) return

  const config = useRuntimeConfig()
  const validApiKey = config.adminApiKey

  if (!validApiKey) {
    if (process.env.NODE_ENV === 'production') {
      throw createError({ statusCode: 500, statusMessage: 'Server configuration error: API Key not set' })
    }
    console.warn('[Auth] Warning: ADMIN_API_KEY not set, allowing request in development mode')
    return
  }

  const authHeader = getHeader(event, 'authorization')
  const apiKey = authHeader?.replace('Bearer ', '').trim()

  if (!apiKey) {
    throw createError({ statusCode: 401, statusMessage: 'Unauthorized: API Key required' })
  }

  if (apiKey !== validApiKey) {
    throw createError({ statusCode: 403, statusMessage: 'Forbidden: Invalid API Key' })
  }

  console.log(`[Auth] Authenticated ${method} ${path}`)
})
