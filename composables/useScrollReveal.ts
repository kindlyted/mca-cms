import { ref, onMounted, onUnmounted } from 'vue'

export function useScrollReveal(options?: {
  threshold?: number
  rootMargin?: string
  triggerOnce?: boolean
}) {
  const el = ref<HTMLElement | null>(null)
  const isVisible = ref(false)

  const { threshold = 0.1, rootMargin = '0px 0px -60px 0px', triggerOnce = true } = options || {}

  let observer: IntersectionObserver | null = null

  onMounted(() => {
    if (!el.value) return
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      isVisible.value = true
      if (el.value) el.value.classList.add('visible')
      return
    }
    observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          isVisible.value = true
          if (el.value) el.value.classList.add('visible')
          if (triggerOnce && observer && el.value) {
            observer.unobserve(el.value)
          }
        } else if (!triggerOnce) {
          isVisible.value = false
          if (el.value) el.value.classList.remove('visible')
        }
      },
      { threshold, rootMargin }
    )
    observer.observe(el.value)
  })

  onUnmounted(() => {
    if (observer) observer.disconnect()
  })

  return { el, isVisible }
}
