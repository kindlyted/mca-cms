import { ref } from 'vue'

// Get GA ID from runtime config
const getGaId = () => {
  const config = useRuntimeConfig()
  return config.public.gaId as string
}

// Analytics state
const isInitialized = ref(false)
const isAnalyticsEnabled = ref(false)

/**
 * Initialize Google Analytics 4
 */
export const initGA4 = () => {
  if (isInitialized.value || !isAnalyticsEnabled.value) return

  // Check if we're in browser environment
  if (typeof window === 'undefined') return

  const gaId = getGaId()
  if (!gaId) {
    console.warn('GA ID not configured')
    return
  }

  // Load gtag.js script
  const script = document.createElement('script')
  script.async = true
  script.src = `https://www.googletagmanager.com/gtag/js?id=${gaId}`
  document.head.appendChild(script)

  // Initialize dataLayer and gtag function
  window.dataLayer = window.dataLayer || []
  window.gtag = function() {
    window.dataLayer.push(arguments)
  }
  window.gtag('js', new Date())
  window.gtag('config', gaId, {
    send_page_view: false, // We'll handle page views manually for SPA navigation
    anonymize_ip: true,    // GDPR compliance
    cookie_flags: 'SameSite=None;Secure'
  })

  isInitialized.value = true

  // Track initial page view
  trackPageView()
}

/**
 * Track a page view
 */
export const trackPageView = (path?: string, title?: string) => {
  if (!isInitialized.value || !window.gtag) return

  const pagePath = path || window.location.pathname + window.location.search
  const pageTitle = title || document.title

  window.gtag('event', 'page_view', {
    page_path: pagePath,
    page_title: pageTitle,
    page_location: window.location.href
  })
}

/**
 * Track a custom event
 */
export const trackEvent = (
  eventName: string,
  params?: Record<string, any>
) => {
  if (!isInitialized.value || !window.gtag) return

  window.gtag('event', eventName, params)
}

/**
 * Enable analytics (called when user consents)
 */
export const enableAnalytics = () => {
  isAnalyticsEnabled.value = true
  initGA4()
}

/**
 * Disable analytics (called when user rejects)
 */
export const disableAnalytics = () => {
  isAnalyticsEnabled.value = false
  
  // Clear GA cookies if they exist
  if (typeof document !== 'undefined') {
    const cookies = document.cookie.split(';')
    cookies.forEach(cookie => {
      const [name] = cookie.split('=')
      const trimmedName = name.trim()
      if (trimmedName.startsWith('_ga') || trimmedName.startsWith('_gid') || trimmedName.startsWith('_gat')) {
        document.cookie = `${trimmedName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`
      }
    })
  }
}

/**
 * Check if analytics is enabled
 */
export const getAnalyticsStatus = () => {
  return {
    initialized: isInitialized.value,
    enabled: isAnalyticsEnabled.value
  }
}

// Type definitions for gtag
declare global {
  interface Window {
    dataLayer: any[]
    gtag: (...args: any[]) => void
  }
}
