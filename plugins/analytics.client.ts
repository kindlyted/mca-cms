import { defineNuxtPlugin, useRouter } from '#imports'
import { trackPageView, enableAnalytics } from '~/composables/useAnalytics'

export default defineNuxtPlugin(() => {
  // Only run on client side
  if (process.server) return

  const router = useRouter()

  // Check if user has previously consented to analytics
  const checkAndInitAnalytics = () => {
    try {
      const raw = localStorage.getItem('cookie-consent')
      if (!raw) return
      let parsed: any
      try {
        parsed = JSON.parse(raw)
      } catch {
        return
      }
      if (parsed?.analytics) {
        enableAnalytics()
      }
    } catch {}
  }

  // Initialize on plugin load (page refresh)
  checkAndInitAnalytics()

  // Listen for consent updates
  window.addEventListener('cookie-consent-updated', ((event: CustomEvent) => {
    const { analytics } = event.detail
    if (analytics) {
      enableAnalytics()
    }
  }) as EventListener)

  // Track page views on route changes
  router.afterEach((to, from) => {
    // Only track if analytics is enabled
    const consent = localStorage.getItem('cookie-consent')
    if (!consent) return

    try {
      const parsed = JSON.parse(consent)
      if (!parsed.analytics) return
    } catch (e) {
      return
    }

    // Small delay to ensure page title is updated
    setTimeout(() => {
      trackPageView(to.fullPath, document.title)
    }, 100)
  })
})
