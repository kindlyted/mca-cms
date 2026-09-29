import { computed } from 'vue'
import { companyInfo } from '~/utils/config'

/**
 * Generate alternate hreflang <link> tags for a listing/static page.
 * Mirrors the per-entity hreflang logic in useEntitySeo but for non-detail pages.
 */
export function usePageHreflangs(basePath: string) {
  const { locales } = useI18n()
  const config = useRuntimeConfig()
  const baseUrl = config.public.siteUrl || companyInfo.siteUrl

  const hreflangLinks = computed(() => {
    const links = (locales.value as Array<{ code: string }>).map(loc => ({
      rel: 'alternate',
      hreflang: loc.code,
      href: `${baseUrl}${loc.code === 'en' ? '' : `/${loc.code}`}${basePath}`
    }))
    links.push({
      rel: 'alternate',
      hreflang: 'x-default',
      href: `${baseUrl}${basePath}`
    })
    return links
  })

  return { hreflangLinks }
}
