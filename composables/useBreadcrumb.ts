import { computed } from 'vue'
import { useRoute } from 'vue-router'

interface BreadcrumbLink {
  label: string
  to?: string
  icon?: string
  [key: string]: any
}

const LOCALE_CODES = ['en', 'fr', 'de']

function stripLocalePrefix(path: string): string {
  for (const code of LOCALE_CODES) {
    if (path === `/${code}`) return '/'
    if (path.startsWith(`/${code}/`)) return path.slice(code.length + 1)
  }
  return path
}

export function useBreadcrumb() {
  const route = useRoute()

  const { t } = useI18n()
  const localePath = useLocalePath()

  const links = computed<BreadcrumbLink[]>(() => {
    const meta = route.meta as any
    if (meta?.breadcrumb && Array.isArray(meta.breadcrumb)) {
      return meta.breadcrumb
    }

    const contentParams = Object.keys(route.params).filter(k => k !== 'locale')
    const hasContentParams = contentParams.length > 0

    const crumbs: BreadcrumbLink[] = []
    let accumulatedPath = ''

    route.matched.forEach((record, idx) => {
      const recordMeta: any = record.meta || {}

      let path = record.path
      Object.entries(route.params).forEach(([k, v]) => {
        path = path.replace(`:${k}`, String(v))
      })

      if (!path.startsWith('/')) {
        accumulatedPath += `/${path}`
      } else {
        accumulatedPath = path
      }

      const normalizedPath = stripLocalePrefix(accumulatedPath)

      const staticPageLabels: Record<string, string> = {
        '/services': 'nav.services',
        '/partners': 'nav.partners',
        '/blogs': 'nav.stories',
        '/contact': 'nav.contact',
        '/about': 'nav.about',
        '/privacy': 'nav.privacy',
        '/terms': 'nav.terms',
        '/disclaimer': 'nav.disclaimer',
      }
      const englishTitleMap: Record<string, string> = {
        'Services': 'nav.services',
        'Partners': 'nav.partners',
        'Health Insights': 'nav.stories',
        'Contact Us': 'nav.contact',
        'About Us': 'nav.about',
        'Privacy Policy': 'nav.privacy',
        'Terms & Conditions': 'nav.terms',
        'Legal Disclaimer': 'nav.disclaimer',
      }

      const isLeafCrumb = idx === route.matched.length - 1
      const isStaticPage = !!staticPageLabels[normalizedPath]

      let label: string

      if (isLeafCrumb && route.meta && route.meta.title && hasContentParams) {
        label = String(route.meta.title)
      } else {
        label = recordMeta.breadcrumbLabel || recordMeta.title || record.name || record.path
        if (typeof label !== 'string') {
          label = String(label)
        }
      }

      if (staticPageLabels[normalizedPath]) {
        label = t(staticPageLabels[normalizedPath])
      } else if (englishTitleMap[label]) {
        label = t(englishTitleMap[label])
      }

      if (idx === 0 && normalizedPath !== '/') {
        crumbs.push({ label: t('nav.home'), to: localePath('/') })
      }

      if (idx === route.matched.length - 1) {
        crumbs.push({ label })
      } else {
        crumbs.push({ label, to: localePath(normalizedPath) })
      }
    })

    if (crumbs.length === 0) {
      crumbs.push({ label: t('nav.home'), to: localePath('/') })
    }

    return crumbs
  })

  return { links }
}
