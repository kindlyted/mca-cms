import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export interface LanguageOption {
  code: string
  label: string
  available: boolean
  url: string | null
  isCurrent: boolean
}

interface TranslationSwitchResponse {
  success: boolean
  data?: {
    success: boolean
    targetUrl: string | null
    fallbackUrl?: string
    availableLanguages: string[]
    message?: string
  }
  translations?: Record<string, string | null>
  availableLanguages?: string[]
  currentContent?: {
    slug: string
    lang: string
    category: string
  }
}

interface LanguageStatus {
  available: boolean
  url: string | null
  willRedirect: boolean
  redirectTarget?: string
}

const CACHE_TTL = 5 * 60 * 1000  // 5 分钟缓存
let cacheData: {
  languages: LanguageOption[]
  timestamp: number
  slug: string
  category: string
} | null = null

export function useLanguageSwitch() {
  const route = useRoute()
  const router = useRouter()

  const loading = ref(false)
  const error = ref<string | null>(null)
  const availableLanguages = ref<LanguageOption[]>([])

  const currentLang = computed(() => {
    return (route.params.lang as string) || 'en'
  })

  const currentSlug = computed(() => {
    return (route.params.id as string) || (route.params.slug as string) || ''
  })

  const currentCategory = computed(() => {
    const path = route.path
    if (path.includes('/services')) return 'services'
    if (path.includes('/partners')) return 'partners'
    if (path.includes('/blogs') || path.includes('/blog')) return 'blogs'
    return ''
  })

  function getTranslationFunction() {
    try {
      const { t } = useI18n()
      return t
    } catch {
      return (key: string, fallback?: string) => fallback || key
    }
  }

  function getLocalePathFunction() {
    try {
      return useLocalePath()
    } catch {
      return (path: string) => path
    }
  }

  async function loadAvailableLanguages(forceRefresh = false): Promise<void> {
    if (!currentSlug.value || !currentCategory.value) {
      console.warn('⚠️  Cannot load languages: missing slug or category')
      return
    }

    const cacheKey = `${currentSlug.value}:${currentCategory.value}`
    
    if (!forceRefresh && cacheData && 
        cacheData.slug === currentSlug.value && 
        cacheData.category === currentCategory.value &&
        Date.now() - cacheData.timestamp < CACHE_TTL) {
      availableLanguages.value = cacheData.languages
      return
    }

    loading.value = true
    error.value = null

    try {
      const response: TranslationSwitchResponse = await $fetch('/api/translation/switch', {
        method: 'GET',
        query: {
          slug: currentSlug.value,
          currentLang: currentLang.value,
          category: currentCategory.value
        }
      })

      if (response.success && response.translations && response.availableLanguages) {
        const t = getTranslationFunction()
        const supportedLangs = ['en', 'fr', 'de']
        
        const languages: LanguageOption[] = supportedLangs.map(langCode => ({
          code: langCode,
          label: t(`languages.${langCode}`, langCode.toUpperCase()),
          available: response.availableLanguages!.includes(langCode),
          url: response.translations![langCode] || null,
          isCurrent: langCode === currentLang.value
        }))

        availableLanguages.value = languages
        
        cacheData = {
          languages,
          timestamp: Date.now(),
          slug: currentSlug.value,
          category: currentCategory.value
        }
      } else {
        throw new Error('Invalid response structure from translation API')
      }
    } catch (err: any) {
      console.error('❌ Failed to load language options:', err)
      error.value = err.message || 'Failed to load languages'
      
      availableLanguages.value = []
    } finally {
      loading.value = false
    }
  }

  async function switchLanguage(targetLang: string): Promise<boolean> {
    const localePath = getLocalePathFunction()
    const targetOption = availableLanguages.value.find(opt => opt.code === targetLang)

    if (!targetOption) {
      console.error(`❌ Language ${targetLang} not found in options`)
      error.value = `Language option ${targetLang} not available`
      return false
    }

    if (!targetOption.available) {
      console.warn(`⚠️  Language ${targetLang} not available for this content`)
      
      if (currentCategory.value === 'blogs') {
        const fallbackUrl = localePath(`/${targetLang}/blogs`)
        console.log(`🔄 Redirecting to blog listing: ${fallbackUrl}`)
        await router.push(fallbackUrl)
        return true
      }
      
      error.value = `Translation not available in ${targetLang}. This content only exists in: ${availableLanguages.value.filter(l => l.available).map(l => l.code).join(', ')}`
      return false
    }

    if (targetOption.url) {
      console.log(`🔄 Switching to ${targetLang}: ${targetOption.url}`)
      await router.push(targetOption.url)
      return true
    }

    console.error(`❌ No URL available for language ${targetLang}`)
    error.value = `Cannot switch to ${targetLang}: no target URL`
    return false
  }

  function getLanguageStatus(langCode: string): LanguageStatus {
    const localePath = getLocalePathFunction()
    const option = availableLanguages.value.find(opt => opt.code === langCode)
    
    if (!option) {
      return {
        available: false,
        url: null,
        willRedirect: false
      }
    }

    const willRedirect = !option.available && currentCategory.value === 'blogs'
    
    return {
      available: option.available,
      url: option.url,
      willRedirect,
      redirectTarget: willRedirect ? localePath(`/${langCode}/blogs`) : undefined
    }
  }

  function clearCache(): void {
    cacheData = null
    console.log('🗑️  Language switch cache cleared')
  }

  function getCacheInfo(): { cached: boolean; age: number | null; slug: string } | null {
    if (!cacheData) return null
    
    return {
      cached: true,
      age: Date.now() - cacheData.timestamp,
      slug: cacheData.slug
    }
  }

  return {
    loading,
    error,
    availableLanguages,
    currentLang,
    currentSlug,
    currentCategory,
    loadAvailableLanguages,
    switchLanguage,
    getLanguageStatus,
    clearCache,
    getCacheInfo
  }
}
