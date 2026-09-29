<template>
  <div class="py-12 min-h-screen bg-gray-50">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-24">
      <!-- Breadcrumb -->
      <ClientOnly>
        <UBreadcrumb
          v-if="links && links.length > 1"
          :links="links"
          :ui="{
            wrapper: 'breadcrumb-jade mb-4 text-sm',
            base: 'ubreadcrumb-base',
            active: 'ubreadcrumb-active',
            label: 'ubreadcrumb-label',
            divider: { base: 'ubreadcrumb-divider' }
          }"
          divider="/"
        />
      </ClientOnly>

      <!-- Page Header -->
      <div class="mb-10">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ t('legal.terms.title') }}</h1>
        <p class="text-sm text-gray-500">{{ t('legal.lastUpdated') }}: {{ t('legal.updateDate') }}</p>
      </div>

      <!-- Content -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-8 md:p-12 space-y-10">
        <!-- Service Usage -->
        <section>
          <h2 class="text-xl font-semibold text-gray-900 mb-3">{{ t('legal.terms.serviceUsage.title') }}</h2>
          <p class="text-gray-700 leading-relaxed">{{ t('legal.terms.serviceUsage.text') }}</p>
        </section>

        <!-- Intellectual Property -->
        <section>
          <h2 class="text-xl font-semibold text-gray-900 mb-3">{{ t('legal.terms.intellectualProperty.title') }}</h2>
          <p class="text-gray-700 leading-relaxed">{{ t('legal.terms.intellectualProperty.text', { company: companyInfo.name }) }}</p>
        </section>

        <!-- Limitation of Liability -->
        <section>
          <h2 class="text-xl font-semibold text-gray-900 mb-3">{{ t('legal.terms.limitationOfLiability.title') }}</h2>
          <p class="text-gray-700 leading-relaxed">{{ t('legal.terms.limitationOfLiability.text') }}</p>
        </section>

        <!-- Governing Law -->
        <section>
          <h2 class="text-xl font-semibold text-gray-900 mb-3">{{ t('legal.terms.governingLaw.title') }}</h2>
          <p class="text-gray-700 leading-relaxed">{{ t('legal.terms.governingLaw.text', { company: companyInfo.name }) }}</p>
        </section>

        <!-- Contact -->
        <section class="pt-6 border-t border-gray-200">
          <h2 class="text-xl font-semibold text-gray-900 mb-3">{{ t('legal.terms.contact.title') }}</h2>
          <div class="text-gray-700 space-y-1">
            <p>{{ t('legal.contactEmail', { email: companyInfo.email }) }}</p>
            <p>{{ t('legal.contactPhone', { phone: companyInfo.phone }) }}</p>
            <p>{{ t('legal.contactAddress', { address: companyInfo.address }) }}</p>
          </div>
        </section>
      </div>

      <!-- Back to Home -->
      <div class="mt-8">
        <NuxtLink :to="localePath('/')" class="inline-flex items-center text-[var(--mc-jade)] text-sm font-medium transition-colors">
          <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          {{ t('legal.backToHome') }}
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useLocalePath } from '#imports'
import { useOrganizationSchema } from '~/composables/useOrganizationSchema'
import { companyInfo } from '~/utils/config'

const { t, locale } = useI18n()
const localePath = useLocalePath()
const runtimeConfig = useRuntimeConfig()
const siteUrl = runtimeConfig.public.siteUrl || companyInfo.siteUrl
const pagePath = locale.value === 'en' ? '/terms' : `/${locale.value}/terms`
const { links } = useBreadcrumb()

useSeoMeta({
  title: () => t('legal.terms.seoTitle'),
  description: () => t('legal.terms.seoDescription'),
  keywords: () => t('legal.terms.seoKeywords'),
  ogTitle: () => t('legal.terms.seoTitle'),
  ogDescription: () => t('legal.terms.seoDescription'),
  ogImage: `${siteUrl}/images/hero-bg.webp`,
  ogType: 'website',
  ogSiteName: companyInfo.shortName,
  ogUrl: `${siteUrl}${pagePath}`,
  twitterCard: 'summary_large_image',
  twitterTitle: () => t('legal.terms.seoTitle'),
  twitterDescription: () => t('legal.terms.seoDescription'),
  twitterImage: `${siteUrl}/images/hero-bg.webp`
})

const breadcrumbSchema = {
  '@context': 'https://schema.org',
  '@type': 'BreadcrumbList',
  itemListElement: [
    { '@type': 'ListItem', position: 1, name: t('nav.home'), item: `${siteUrl}/` },
    { '@type': 'ListItem', position: 2, name: t('legal.terms.title'), item: `${siteUrl}${pagePath}` }
  ]
}

useHead({
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify(useOrganizationSchema('terms'))
    },
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'WebPage',
        name: t('legal.terms.seoTitle'),
        description: t('legal.terms.seoDescription'),
        url: `${siteUrl}${pagePath}`,
        publisher: {
          '@type': 'Organization',
          name: companyInfo.shortName,
          url: siteUrl
        }
      })
    },
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify(breadcrumbSchema)
    }
  ],
  link: [
    { rel: 'canonical', href: `${siteUrl}${pagePath}` },
    { rel: 'alternate', hreflang: 'x-default', href: `${siteUrl}/terms` },
    { rel: 'alternate', hreflang: 'en', href: `${siteUrl}/terms` },
    { rel: 'alternate', hreflang: 'fr', href: `${siteUrl}/fr/terms` },
    { rel: 'alternate', hreflang: 'de', href: `${siteUrl}/de/terms` }
  ]
})
</script>
