export interface SeoMetaInput {
  title?: string
  description?: string
  keywords?: string | string[]
  image?: string
  price?: number
  currency?: string
}

export function useEntitySeo(
  entityData: Ref<any>,
  entityType: 'service' | 'partner' | 'blog' | 'product'
) {
  const route = useRoute()
  const { locale, locales } = useI18n()
  const config = useRuntimeConfig()

  const baseUrl = config.public.siteUrl || companyInfo.siteUrl

  const canonical = computed(() => {
    if (entityData.value?.seo?.canonical) {
      return entityData.value.seo.canonical
    }

    const path = route.fullPath.split('?')[0]
    return `${baseUrl}${path}`
  })

  const hreflangLinks = computed(() => {
    if (entityData.value?.seo?.hreflang?.length > 0) {
      return entityData.value.seo.hreflang.map((alt: any) => ({
        rel: 'alternate',
        hreflang: alt.lang,
        href: alt.url
      }))
    }

    const basePath = `/${entityType}s/${entityData.value?.meta?.slug || entityData.value?.meta?.id || ''}`
    const links = (locales.value as Array<{ code: string }>).map(loc => {
      let href = `${baseUrl}`
      if (loc.code !== 'en') {
        href += `/${loc.code}`
      }
      href += basePath

      return {
        rel: 'alternate',
        hreflang: loc.code,
        href
      }
    })

    links.push({
      rel: 'alternate',
      hreflang: 'x-default',
      href: `${baseUrl}${basePath}`
    })

    return links
  })

  function applySeo(seoMeta?: SeoMetaInput) {
    useHead({
      link: [
        { rel: 'canonical', href: canonical.value },
        ...hreflangLinks.value
      ]
    })

    if (seoMeta) {
      const keywords = Array.isArray(seoMeta.keywords)
        ? seoMeta.keywords.join(', ')
        : (seoMeta.keywords || '')
      const ogType = entityType === 'blog' ? 'article' : entityType === 'product' ? 'product' : 'website'
      useSeoMeta({
        title: seoMeta.title,
        description: seoMeta.description,
        keywords,
        ogTitle: seoMeta.title,
        ogDescription: seoMeta.description,
        ogImage: seoMeta.image,
        ogType,
        ogSiteName: companyInfo.shortName,
        ogUrl: canonical,
        twitterCard: 'summary_large_image',
        twitterTitle: seoMeta.title,
        twitterDescription: seoMeta.description,
        twitterImage: seoMeta.image
      })

      if (entityType === 'product' && typeof seoMeta.price === 'number') {
        useHead({
          meta: [
            { property: 'product:price:amount', content: seoMeta.price.toFixed(2) },
            { property: 'product:price:currency', content: seoMeta.currency || 'USD' }
          ]
        })
      }
    }
  }

  return {
    canonical,
    hreflangLinks,
    applySeo
  }
}
