<template>
  <ProductDetailLayout
    :loading="loading"
    :error="error"
    :entity="service"
    :links="links"
    entity-type="service"
  >
    <template #stats>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-green-50 rounded-lg p-6 text-center shadow-sm border border-green-100">
          <div class="text-2xl font-bold text-green-600 mb-2">{{ t('pages.services.detail.benefits.savings.title') }}</div>
          <div class="text-sm text-gray-600">{{ t('pages.services.detail.benefits.savings.description') }}</div>
        </div>
        <div class="bg-blue-50 rounded-lg p-6 text-center shadow-sm border border-blue-100">
          <div class="text-2xl font-bold text-blue-600 mb-2">{{ t('pages.services.detail.benefits.accredited.title') }}</div>
          <div class="text-sm text-gray-600">{{ t('pages.services.detail.benefits.accredited.description') }}</div>
        </div>
        <div class="bg-purple-50 rounded-lg p-6 text-center shadow-sm border border-purple-100">
          <div class="text-2xl font-bold text-purple-600 mb-2">{{ t('pages.services.detail.benefits.recovery.title') }}</div>
          <div class="text-sm text-gray-600">{{ t('pages.services.detail.benefits.recovery.description') }}</div>
        </div>
      </div>
    </template>

    <template #related>
      <div v-if="relatedPartners.length > 0" class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">{{ t('pages.services.detail.partners') }}</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="partner in relatedPartners"
            :key="partner.id"
            class="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors"
          >
            <h3 class="font-semibold text-gray-900 mb-2">
              <NuxtLink
                :to="localePath(`/partners/${partner.slug || partner.id}`)"
                class="hover:text-blue-600"
              >
                {{ partner.title }}
              </NuxtLink>
            </h3>
            <p class="text-sm text-gray-600 mb-3">{{ partner.description }}</p>
            <NuxtLink
              :to="localePath(`/partners/${partner.slug || partner.id}`)"
              class="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              View Details →
            </NuxtLink>
          </div>
        </div>
      </div>
    </template>
  </ProductDetailLayout>
</template>

<script setup lang="ts">
import { useBreadcrumb } from '~/composables/useBreadcrumb'
import { useHowToSchema } from '~/composables/useHowToSchema'
import { useOrganizationSchema } from '~/composables/useOrganizationSchema'
import { useEntitySeo } from '~/composables/useEntitySeo'
import { useI18n } from 'vue-i18n'
import { useLocalePath } from '#imports'

const localePath = useLocalePath()
const route = useRoute()
const serviceSlug = route.params.slug as string
const { t, locale } = useI18n({ useScope: 'global' })
const runtimeConfig = useRuntimeConfig()
const siteUrl = runtimeConfig.public.siteUrl || companyInfo.siteUrl

const relatedPartners = ref<any[]>([])

const { links: rawLinks } = useBreadcrumb()

const links = computed(() =>
  rawLinks.value
    .filter((link): link is { label: string; to?: string } =>
      Boolean(link.label)
    )
)

const buildServiceUrl = (slug: string, lang: string): string => {
  const prefix = lang === 'en' ? '' : `/${lang}`
  return `${siteUrl}${prefix}/services/${slug}`
}

const buildServiceIndexUrl = (lang: string): string => {
  const prefix = lang === 'en' ? '' : `/${lang}`
  return `${siteUrl}${prefix}/services`
}

const normalizeService = (data: any): any => {
  if (!data) return data
  return {
    ...data,
    body: typeof data.body === 'string' ? data.body : data.body?.content || '',
    description: data.description || '',
    introduction: data.introduction || '',
    procedure: data.procedure || '',
    outcome: data.outcome || '',
    comparison: data.comparison || null,
    pricing: data.pricing || { currency: 'USD', tiers: [], inclusions: [], exclusions: [], exampleTotal: {} },
    testimonials: data.testimonials || [],
    faq: (data.faq || []).map((item: any) => ({
      q: item.q || item.question || '',
      a: item.a || item.answer || ''
    })),
    cover: data.cover || data.visuals?.cover || { url: '', alt: '' }
  }
}

const generateServiceStructuredData = (serviceData: any, currentLocale: string): Record<string, any>[] => {
  const schemas: Record<string, any>[] = []
  const title = serviceData.seo?.title || serviceData.overview?.title
  const description = serviceData.seo?.description || serviceData.overview?.excerpt
  const serviceUrl = buildServiceUrl(serviceData.meta?.slug || serviceSlug, currentLocale)

  const organizationSchema = useOrganizationSchema('service')
  schemas.push(organizationSchema)

  schemas.push({
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: t('nav.home'), item: `${siteUrl}/` },
      { '@type': 'ListItem', position: 2, name: t('nav.services'), item: buildServiceIndexUrl(currentLocale) },
      { '@type': 'ListItem', position: 3, name: title, item: serviceUrl }
    ]
  })

  const coverUrl = serviceData.cover?.url || serviceData.visuals?.cover?.url

  schemas.push({
    '@context': 'https://schema.org',
    '@type': 'Service',
    name: title,
    description: description,
    url: serviceUrl,
    image: coverUrl,
    datePublished: serviceData.meta?.createdAt || new Date().toISOString(),
    dateModified: serviceData.meta?.updatedAt || new Date().toISOString(),
    lastReviewed: serviceData.meta?.updatedAt || new Date().toISOString(),
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': serviceUrl
    },
    provider: {
      '@type': 'Organization',
      name: companyInfo.shortName,
      url: siteUrl
    }
  })

  schemas.push({
    '@context': 'https://schema.org',
    '@type': 'ProfessionalService',
    name: companyInfo.shortName,
    description: description,
    url: serviceUrl,
    telephone: companyInfo.phone,
    email: companyInfo.email,
    areaServed: 'Worldwide',
    parentOrganization: {
      '@type': 'Organization',
      name: companyInfo.name
    }
  })

  if (serviceData.faq && serviceData.faq.length > 0) {
    schemas.push({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: serviceData.faq.map((item: { q?: string; question?: string; a?: string; answer?: string }) => ({
        '@type': 'Question',
        name: item.q || item.question,
        acceptedAnswer: {
          '@type': 'Answer',
          text: item.a || item.answer
        }
      }))
    })
  }

  const howToSchema = useHowToSchema({
    name: title || companyInfo.shortName,
    description: description || undefined,
    steps: serviceData.process?.steps?.map((step: any) => ({
      name: step.title || step.name || '',
      text: step.description || step.text || ''
    }))
  })
  if (howToSchema) {
    schemas.push(howToSchema)
  }

  return schemas
}

const fetchService = async (): Promise<any> => {
  const response: any = await $fetch(`/api/services/${serviceSlug}`, {
    params: { lang: locale.value }
  })
  if (response.success && response.data) {
    return response.data
  }
  throw new Error('Service not found')
}

const { data: serviceData, pending: loading, error: fetchError } = await useAsyncData<any>(
  `service-${serviceSlug}`,
  fetchService,
  { server: true, default: () => null }
)

const service = computed(() => normalizeService(serviceData.value))
const error = computed(() => {
  if (!fetchError.value) return ''
  if ((fetchError.value as any).statusCode === 404) return ''
  return (fetchError.value as any).message || 'Failed to load service details'
})

const { applySeo } = useEntitySeo(service, 'service')

// Throw 404 synchronously within Vue reactivity so Nuxt can catch it
watchEffect(() => {
  if (fetchError.value && (fetchError.value as any).statusCode === 404) {
    throw createError({ statusCode: 404, statusMessage: 'Service not found' })
  }
})

const fetchRelatedPartners = async () => {
  try {
    const response: any = await $fetch('/api/related', {
      params: {
        entityType: 'service',
        slug: serviceSlug,
        lang: locale.value
      }
    })
    if (response.success) {
      relatedPartners.value = response.relatedPartners || []
    }
  } catch (err) {
    console.error('Error fetching related partners:', err)
  }
}

watch(serviceData, (rawData) => {
  if (!rawData) return
  const newData = normalizeService(rawData)

  const title = newData.seo?.title || newData.overview?.title
  const description = newData.seo?.description || newData.overview?.excerpt
  const keywords = newData.seo?.keywords || ''
  const rawCoverUrl = newData.cover?.url || '/images/hero-bg.webp'
  const coverUrl = rawCoverUrl.startsWith('http') ? rawCoverUrl : `${siteUrl}${rawCoverUrl}`
  const serviceUrl = buildServiceUrl(newData.meta?.slug || serviceSlug, locale.value)
  route.meta.title = title
  route.meta.breadcrumb = [
    { label: t('nav.home'), to: localePath('/') },
    { label: t('nav.services'), to: localePath('/services') },
    { label: title }
  ]

  applySeo({ title, description, keywords, image: coverUrl })

  const schemas = generateServiceStructuredData(newData, locale.value)
  if (schemas.length > 0) {
    useHead({
      script: schemas.map(schema => ({
        type: 'application/ld+json',
        innerHTML: JSON.stringify(schema)
      }))
    })
  }

  fetchRelatedPartners()
}, { immediate: true })
</script>
