import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export interface HrefLangData {
  lang: string
  url: string
}

export function useHreflangs(contentId?: string) {
  const route = useRoute()
  const hreflangs = ref<HrefLangData[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const currentPath = computed(() => route.path)
  const segments = computed(() => currentPath.value.split('/').filter(Boolean))
  
  const currentLang = computed(() => {
    return segments.value[0] || 'en'
  })

  const category = computed(() => {
    if (segments.value[1] === 'services') return 'services'
    if (segments.value[1] === 'partners') return 'partners'
    if (segments.value[1] === 'blogs' || segments.value[1] === 'blog') return 'blogs'
    return ''
  })

  async function loadHreflangs(id?: string): Promise<void> {
    const targetId = id || contentId
    if (!targetId || !category.value) {
      return
    }

    loading.value = true
    error.value = null

    try {
      const response = await $fetch('/api/translation/hreflang', {
        method: 'GET',
        query: {
          contentId: targetId,
          category: category.value,
          currentLang: currentLang.value,
          baseUrl: ''
        }
      })

      if (response.success && response.data) {
        hreflangs.value = response.data

        generateMetaTags(response.data)
      }
    } catch (err: any) {
      console.error('Failed to load hreflangs:', err)
      error.value = err.message || 'Failed to load hreflang tags'
    } finally {
      loading.value = false
    }
  }

  function generateMetaTags(tags: HrefLangData[]): void {
    const linkTags = tags.map(tag => ({
      rel: 'alternate',
      hreflang: tag.lang,
      href: tag.url
    }))

    if (typeof useHead !== 'undefined') {
      useHead({
        link: linkTags
      })
    }
  }

  function getMetaTags(): { rel: string; hreflang: string; href: string }[] {
    return hreflangs.value.map(tag => ({
      rel: 'alternate',
      hreflang: tag.lang,
      href: tag.url
    }))
  }

  function getAlternateUrl(lang: string): string | null {
    const found = hreflangs.value.find(h => h.lang === lang)
    return found?.url || null
  }

  onMounted(() => {
    if (contentId) {
      loadHreflangs()
    }
  })

  return {
    hreflangs,
    loading,
    error,
    currentLang,
    category,
    loadHreflangs,
    getAlternateUrl,
    getMetaTags
  }
}
