<template>
  <ProductDetailLayout
    :loading="loading"
    :error="error"
    :entity="partner"
    :links="links"
    entity-type="partner"
  >
    <template #stats>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-green-50 rounded-lg p-6 text-center shadow-sm border border-green-100">
          <div class="text-2xl font-bold text-green-600 mb-2">{{ partner.institution?.established || '—' }}</div>
          <div class="text-sm text-gray-600">Established</div>
        </div>
        <div class="bg-blue-50 rounded-lg p-6 text-center shadow-sm border border-blue-100">
          <div class="text-2xl font-bold text-blue-600 mb-2">{{ partner.team?.length || '50+' }}</div>
          <div class="text-sm text-gray-600">Team Members</div>
        </div>
        <div class="bg-purple-50 rounded-lg p-6 text-center shadow-sm border border-purple-100">
          <div class="text-2xl font-bold text-purple-600 mb-2">{{ partner.services?.length || '—' }}</div>
          <div class="text-sm text-gray-600">Services</div>
        </div>
        <div class="bg-orange-50 rounded-lg p-6 text-center shadow-sm border border-orange-100">
          <div class="text-2xl font-bold text-orange-600 mb-2">{{ partner.institution?.rating?.value || '4.8' }}</div>
          <div class="text-sm text-gray-600">Client Rating</div>
        </div>
      </div>
    </template>

    <template #related>
      <div v-if="relatedServices.length > 0" class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">Related Services</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="svc in relatedServices"
            :key="svc.id"
            class="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors"
          >
            <h3 class="font-semibold text-gray-900 mb-2">
              <NuxtLink
                :to="localePath(`/services/${svc.slug || svc.id}`)"
                class="hover:text-blue-600"
              >
                {{ svc.title }}
              </NuxtLink>
            </h3>
            <p class="text-sm text-gray-600 mb-3">{{ svc.excerpt }}</p>
            <NuxtLink
              :to="localePath(`/services/${svc.slug || svc.id}`)"
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
import { useOrganizationSchema } from '~/composables/useOrganizationSchema'
import { useEntitySeo } from '~/composables/useEntitySeo'
import { useI18n } from 'vue-i18n'
import { useLocalePath } from '#imports'

const localePath = useLocalePath()
const route = useRoute()
const partnerSlug = route.params.slug as string
const { t, locale } = useI18n({ useScope: 'global' })
const runtimeConfig = useRuntimeConfig()
const siteUrl = runtimeConfig.public.siteUrl || companyInfo.siteUrl

const relatedServices = ref<any[]>([])
const { links: rawLinks } = useBreadcrumb()

const links = computed(() =>
  rawLinks.value
    .filter((link): link is { label: string; to?: string } =>
      Boolean(link.label)
    )
)

function normalizePartner(raw: any): any {
  return {
    _type: 'partner',
    meta: raw.meta,
    seo: {
      title: raw.seo?.title || raw.overview?.title || '',
      description: raw.seo?.description || raw.overview?.excerpt || '',
      keywords: raw.seo?.keywords || ''
    },
    cover: {
      url: raw.cover?.url || raw.visuals?.cover?.url || '/images/placeholder.svg',
      alt: raw.cover?.alt || raw.visuals?.cover?.alt || raw.overview?.title || ''
    },
    overview: raw.overview,
    institution: raw.institution,
    team: raw.team || raw.doctors,
    relatedServices: raw.relatedServices || raw.content?.relatedServices || [],
    description: raw.description || '',
    highlights: raw.highlights || [],
    services: raw.services || [],
    faq: (raw.faq || []).map((f: any) => ({
      question: f.question ?? f.q ?? '',
      answer: f.answer ?? f.a ?? ''
    })),
    references: raw.references || [],
    cta: raw.cta || { enabled: true, text: 'Contact Us', link: '/contact' }
  }
}

const buildPartnerUrl = (slug: string, lang: string): string => {
  const prefix = lang === 'en' ? '' : `/${lang}`
  return `${siteUrl}${prefix}/partners/${slug}`
}

function generateStructuredData(p: any): Record<string, any>[] {
  const schemas: Record<string, any>[] = []

  schemas.push(useOrganizationSchema('service'))

  const partnerUrl = buildPartnerUrl(p.meta?.slug || partnerSlug, locale.value)
  const partnerTitle = p.seo?.title || p.overview?.title

  schemas.push({
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: t('nav.home'), item: `${siteUrl}/` },
      { '@type': 'ListItem', position: 2, name: t('nav.partners'), item: `${siteUrl}/partners` },
      { '@type': 'ListItem', position: 3, name: partnerTitle, item: partnerUrl }
    ]
  })

  const partnerSchemaMap: Record<string, string> = {
    company: 'ProfessionalService',
    institution: 'Organization',
    partner: 'Organization',
    consultant: 'ProfessionalService',
    'training-center': 'EducationalOrganization'
  }
  const partnerType = partnerSchemaMap[p.meta?.type as string] || 'Organization'
  const inst = p.institution || {}

  schemas.push({
    '@context': 'https://schema.org',
    '@type': partnerType,
    name: p.seo?.title || p.overview?.title,
    description: p.seo?.description || p.overview?.excerpt,
    url: partnerUrl,
    image: p.cover?.url,
    dateModified: p.meta?.updatedAt || new Date().toISOString(),
    foundingDate: inst.established ? String(inst.established) : undefined,
    telephone: inst.contact?.phone,
    address: {
      '@type': 'PostalAddress',
      streetAddress: inst.address?.street,
      addressLocality: inst.address?.city || p.meta?.city,
      addressRegion: inst.address?.province,
      postalCode: inst.address?.postalCode,
      addressCountry: inst.address?.country || p.meta?.country || undefined
    },
    geo: inst.geo?.latitude ? {
      '@type': 'GeoCoordinates',
      latitude: inst.geo.latitude,
      longitude: inst.geo.longitude
    } : undefined,
    aggregateRating: inst.rating?.value ? {
      '@type': 'AggregateRating',
      ratingValue: String(inst.rating.value),
      reviewCount: String(inst.rating.count || inst.rating.reviewCount || '100')
    } : undefined,
    publisher: {
      '@type': 'Organization',
      name: companyInfo.shortName,
      url: '/about',
      logo: { '@type': 'ImageObject', url: `${siteUrl}/logo.png` }
    }
  })

  if (p.faq && p.faq.length > 0) {
    schemas.push({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: p.faq.map((item: { question: string; answer: string }) => ({
        '@type': 'Question',
        name: item.question,
        acceptedAnswer: { '@type': 'Answer', text: item.answer }
      }))
    })
  }

  return schemas
}

const fetchPartner = async (): Promise<any> => {
  const response: any = await $fetch(`/api/partners/${partnerSlug}`, {
    params: { lang: locale.value }
  })
  if (response.success && response.data) {
    return normalizePartner(response.data)
  }
  throw new Error('Partner not found')
}

const { data: partnerData, pending: loading, error: fetchError } = await useAsyncData<any>(
  `partner-${partnerSlug}`,
  fetchPartner,
  { server: true, default: () => null }
)

const partner = computed(() => partnerData.value)
const error = computed(() => {
  if (!fetchError.value) return ''
  if ((fetchError.value as any).statusCode === 404) return ''
  return (fetchError.value as any).message || 'Failed to load partner details'
})

const { applySeo } = useEntitySeo(partner, 'partner')

watchEffect(() => {
  if (fetchError.value && (fetchError.value as any).statusCode === 404) {
    throw createError({ statusCode: 404, statusMessage: 'Partner not found' })
  }
})

watch(partnerData, (newData) => {
  if (!newData) return

  const partnerUrl = buildPartnerUrl(newData.meta?.slug || partnerSlug, locale.value)
  const pTitle = newData.seo?.title || newData.overview?.title
  const pDescription = newData.seo?.description || newData.overview?.excerpt
  const rawCoverImage = newData.cover?.url || '/images/hero-bg.webp'
  const coverImage = rawCoverImage.startsWith('http') ? rawCoverImage : `${siteUrl}${rawCoverImage}`

  route.meta.title = pTitle
  route.meta.breadcrumb = [
    { label: t('nav.home'), to: localePath('/') },
    { label: t('nav.partners'), to: localePath('/partners') },
    { label: pTitle }
  ]

  applySeo({ title: pTitle, description: pDescription, keywords: newData.seo?.keywords || '', image: coverImage })

  const schemas = generateStructuredData(newData)
  if (schemas.length > 0) {
    useHead({
      script: schemas.map(schema => ({
        type: 'application/ld+json',
        innerHTML: JSON.stringify(schema)
      }))
    })
  }

  // Fetch related services via text-matching API
  $fetch('/api/related', {
    params: {
      entityType: 'partner',
      slug: newData.meta?.slug || partnerSlug,
      lang: locale.value
    }
  }).then((res: any) => {
    if (res.success) {
      relatedServices.value = res.relatedServices || []
    }
  }).catch(err => {
    console.error('Error fetching related services:', err)
  })
}, { immediate: true })
</script>
