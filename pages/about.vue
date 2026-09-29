<template>
  <div class="pb-12 min-h-screen" style="background: linear-gradient(135deg, var(--mc-jade-faint), var(--mc-surface), var(--mc-jade-faint));">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24">

      <!-- Breadcrumb -->
      <ClientOnly>
        <UBreadcrumb
          :links="[
            { label: t('nav.home'), to: localePath('/') },
            { label: t('pages.about.title') }
          ]"
          :ui="{
            wrapper: 'breadcrumb-jade mb-6 text-sm',
            base: 'ubreadcrumb-base',
            active: 'ubreadcrumb-active',
            label: 'ubreadcrumb-label',
            divider: { base: 'ubreadcrumb-divider' }
          }"
          divider="/"
        />
      </ClientOnly>

      <!-- Hero Section -->
      <div class="text-center mb-16">
        <h1 class="text-5xl font-bold text-gray-900 mb-6">
          {{ t('pages.about.hero.title') }}
        </h1>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
          {{ t('pages.about.hero.subtitle') }}
        </p>
      </div>

      <!-- Mission & Vision -->
      <div class="grid md:grid-cols-2 gap-8 mb-16">
        <div class="bg-white rounded-xl shadow-lg p-8" style="border-top: 4px solid var(--mc-jade);">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 rounded-lg flex items-center justify-center mr-4" style="background: oklch(52% 0.16 185 / 0.1);">
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--mc-jade);">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-gray-900">{{ t('pages.about.mission.title') }}</h2>
          </div>
          <p class="text-gray-600 leading-relaxed">{{ t('pages.about.mission.description') }}</p>
        </div>

        <div class="bg-white rounded-xl shadow-lg p-8" style="border-top: 4px solid var(--mc-amber);">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 rounded-lg flex items-center justify-center mr-4" style="background: oklch(72% 0.14 78 / 0.1);">
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--mc-amber);">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-gray-900">{{ t('pages.about.vision.title') }}</h2>
          </div>
          <p class="text-gray-600 leading-relaxed">{{ t('pages.about.vision.description') }}</p>
        </div>
      </div>

      <!-- Who We Are -->
      <div class="bg-white rounded-xl shadow-lg p-10 mb-16">
        <h2 class="text-3xl font-bold text-gray-900 mb-6 text-center">
          {{ t('pages.about.whoWeAre.title') }}
        </h2>
        <div class="prose prose-lg max-w-none text-gray-600">
          <p class="text-lg leading-relaxed mb-4">{{ t('pages.about.whoWeAre.paragraph1') }}</p>
          <p class="text-lg leading-relaxed mb-4">{{ t('pages.about.whoWeAre.paragraph2') }}</p>
          <p class="text-lg leading-relaxed">{{ t('pages.about.whoWeAre.paragraph3') }}</p>
        </div>
      </div>

      <!-- Core Values -->
      <div class="mb-16">
        <h2 class="text-3xl font-bold text-gray-900 mb-8 text-center">
          {{ t('pages.about.values.title') }}
        </h2>
        <div class="grid md:grid-cols-3 gap-6">
          <div v-for="(value, index) in coreValues" :key="index" 
               class="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow duration-300">
            <div class="text-4xl mb-4">{{ value.icon }}</div>
            <h3 class="text-xl font-semibold text-gray-900 mb-2">{{ value.title }}</h3>
            <p class="text-gray-600 text-sm">{{ value.description }}</p>
          </div>
        </div>
      </div>

      <!-- Editorial Team -->
      <div class="rounded-xl shadow-lg p-10 mb-16 text-white" style="background: linear-gradient(135deg, var(--mc-jade), var(--mc-jade-dark));">
        <h2 class="text-3xl font-bold mb-6 text-center">
          {{ t('pages.about.team.title') }}
        </h2>
        <p class="text-lg text-center mb-8 max-w-3xl mx-auto" style="color: oklch(85% 0.05 185);">
          {{ t('pages.about.team.subtitle') }}
        </p>
        
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="(member, index) in teamMembers" :key="index" 
               class="bg-white/10 backdrop-blur-sm rounded-lg p-6 hover:bg-white/20 transition-all duration-300">
            <div class="flex items-center mb-4">
              <div class="w-14 h-14 bg-white/20 rounded-full flex items-center justify-center text-2xl font-bold mr-4">
                {{ member.initials }}
              </div>
              <div>
                <h3 class="font-semibold text-lg">{{ member.name }}</h3>
                <p class="text-sm" style="color: oklch(80% 0.06 185);">{{ member.role }}</p>
              </div>
            </div>
            <p class="text-sm" style="color: oklch(85% 0.05 185);">{{ member.bio }}</p>
          </div>
        </div>
      </div>

      <!-- Why Choose Us -->
      <div class="mb-16">
        <h2 class="text-3xl font-bold text-gray-900 mb-8 text-center">
          {{ t('pages.about.whyChooseUs.title') }}
        </h2>
        <div class="grid md:grid-cols-2 gap-6">
          <div v-for="(reason, index) in reasons" :key="index" 
               class="flex items-start space-x-4 bg-white rounded-lg shadow-md p-6">
            <div class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center mt-1" style="background: oklch(72% 0.14 78 / 0.1);">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--mc-amber);">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 mb-1">{{ reason.title }}</h3>
              <p class="text-gray-600 text-sm">{{ reason.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Statistics -->
      <div class="bg-white rounded-xl shadow-lg p-10 mb-16">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div v-for="(stat, index) in statistics" :key="index">
            <div class="text-4xl font-bold mb-2" style="color: var(--mc-jade);">{{ stat.value }}</div>
            <div class="text-gray-600 text-sm">{{ stat.label }}</div>
          </div>
        </div>
      </div>

      <!-- CTA Section -->
      <div class="text-center rounded-xl shadow-lg p-10" style="background: linear-gradient(135deg, var(--mc-amber), #b8860b);">
        <h2 class="text-3xl font-bold text-white mb-4">
          {{ t('pages.about.cta.title') }}
        </h2>
        <p class="text-lg mb-8 max-w-2xl mx-auto" style="color: oklch(85% 0.1 78);">
          {{ t('pages.about.cta.description') }}
        </p>
        <UButton
          :to="localePath('/contact')"
          size="xl"
          class="px-8 py-4 bg-white font-semibold rounded-lg shadow-lg transition-all duration-200" style="color: var(--mc-amber);"
        >
          {{ t('pages.about.cta.button') }} →
        </UButton>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { useOrganizationSchema } from '~/composables/useOrganizationSchema'
import { useI18n } from 'vue-i18n'
import { useLocalePath } from '#imports'

const { t, locale } = useI18n({ useScope: 'global' })
const localePath = useLocalePath()
const runtimeConfig = useRuntimeConfig()
const siteUrl = runtimeConfig.public.siteUrl || companyInfo.siteUrl
const pagePath = locale.value === 'en' ? '/about' : `/${locale.value}/about`

const coreValues = computed(() =>
  companyInfo.aboutPage.coreValues.map(v => ({
    icon: v.icon,
    title: t(v.titleKey),
    description: t(v.descriptionKey)
  }))
)

const teamMembers = computed(() =>
  companyInfo.aboutPage.teamMembers.map(m => ({
    initials: m.initials,
    name: t(m.nameKey),
    role: t(m.roleKey),
    bio: t(m.bioKey)
  }))
)

const reasons = computed(() =>
  companyInfo.aboutPage.reasons.map(r => ({
    title: t(r.titleKey),
    description: t(r.descriptionKey)
  }))
)

const statistics = computed(() =>
  companyInfo.aboutPage.statistics.map(s => ({
    value: s.value,
    label: t(s.labelKey)
  }))
)

const breadcrumbSchema = {
  '@context': 'https://schema.org',
  '@type': 'BreadcrumbList',
  itemListElement: [
    { '@type': 'ListItem', position: 1, name: t('nav.home'), item: `${siteUrl}/` },
    { '@type': 'ListItem', position: 2, name: t('pages.about.title'), item: `${siteUrl}${pagePath}` }
  ]
}

useSeoMeta({
  title: t('pages.about.seo.title'),
  description: t('pages.about.seo.description'),
  ogTitle: t('pages.about.seo.title'),
  ogDescription: t('pages.about.seo.description'),
  ogImage: `${siteUrl}/images/hero-bg.webp`,
  ogType: 'website',
  ogUrl: `${siteUrl}${pagePath}`,
  twitterCard: 'summary_large_image',
  twitterTitle: t('pages.about.seo.title'),
  twitterDescription: t('pages.about.seo.description'),
  twitterImage: `${siteUrl}/images/hero-bg.webp`
})

useHead({
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify(useOrganizationSchema('about'))
    },
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'WebPage',
        name: t('pages.about.seo.title'),
        description: t('pages.about.seo.description'),
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
    { rel: 'alternate', hreflang: 'x-default', href: `${siteUrl}/about` },
    { rel: 'alternate', hreflang: 'en', href: `${siteUrl}/about` },
    { rel: 'alternate', hreflang: 'fr', href: `${siteUrl}/fr/about` },
    { rel: 'alternate', hreflang: 'de', href: `${siteUrl}/de/about` }
  ]
})
</script>
