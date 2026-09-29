<template>
  <div>
    <!-- Hero Section -->
    <section class="relative min-h-screen flex items-center justify-center text-white overflow-hidden">
      <div class="absolute inset-0">
        <img
          ref="heroBg"
          src="/images/hero-bg-1920.webp"
          :alt="companyInfo.shortName + ' background'"
          width="1920" height="1280"
          srcset="/images/hero-bg-640.webp 640w, /images/hero-bg-1280.webp 1280w, /images/hero-bg-1920.webp 1920w"
          sizes="100vw"
          fetchpriority="high"
          class="w-full h-full object-cover"
          :style="{ transform: `scale(1.05) translateY(${parallaxY}px)` }"
        />
        <div class="absolute inset-0 bg-gradient-to-r from-[var(--mc-jade-dark)]/90 via-[var(--mc-jade)]/75 to-[var(--mc-deep-warm)]/60"></div>
        <div class="absolute inset-0 opacity-[0.15]">
          <div class="absolute top-10 left-10 w-40 h-40 bg-white rounded-full animate-pulse" style="animation-duration: 4s;"></div>
          <div class="absolute bottom-10 right-10 w-60 h-60 bg-white rounded-full animate-pulse" style="animation-duration: 5s; animation-delay: 1s;"></div>
          <div class="absolute top-1/3 left-2/3 w-24 h-24 bg-white rounded-full animate-pulse" style="animation-duration: 3.5s; animation-delay: 2s;"></div>
        </div>
      </div>

      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div class="space-y-8">
            <div
              class="hero-reveal inline-flex items-center gap-2 bg-white/15 backdrop-blur-md rounded-full px-5 py-2 text-sm font-medium"
            >
              <span class="w-2 h-2 rounded-full bg-[var(--mc-amber)] animate-pulse" style="animation-duration: 2s;"></span>
              {{ t('pages.home.hero.badge') }}
            </div>

            <h1
              class="hero-reveal text-4xl md:text-5xl lg:text-6xl font-bold leading-tight"
              style="animation-delay: 0.15s;"
            >
              {{ t('pages.home.hero.title') }}
            </h1>

            <p
              class="hero-reveal text-xl leading-relaxed max-w-xl"
              style="animation-delay: 0.3s; color: oklch(90% 0.015 185);"
            >
              {{ t('pages.home.hero.subtitle') }}
            </p>

            <div
              class="hero-reveal flex flex-wrap gap-4 pt-4"
              style="animation-delay: 0.45s;"
            >
              <NuxtLink
                :to="localePath('/services')"
                class="btn btn-amber px-8 py-4 text-base"
              >
                {{ t('pages.home.hero.exploreServices') }}
              </NuxtLink>
              <NuxtLink
                :to="localePath('/contact')"
                class="btn btn-outline-light px-8 py-4 text-base"
              >
                {{ t('pages.home.hero.getConsultation') }}
              </NuxtLink>
            </div>
          </div>

          <div
            class="hero-reveal hidden lg:block"
            style="animation-delay: 0.6s;"
          >
            <div class="relative">
              <div class="absolute inset-0 bg-white/10 rounded-3xl transform rotate-3"></div>
              <div class="backdrop-blur-sm rounded-3xl p-8 border" style="background: oklch(100% 0 0 / 0.08); border-color: oklch(100% 0 0 / 0.15);">
                <div class="grid grid-cols-2 gap-8">
                  <div v-for="stat in stats" :key="stat.label" class="text-center">
                    <div class="text-4xl font-bold" style="color: var(--mc-amber);">{{ stat.value }}</div>
                    <div class="text-sm mt-1" style="color: oklch(85% 0.01 185);">{{ t(stat.label) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Services Section -->
    <section class="section" style="background: var(--mc-surface);">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div ref="servicesHead" class="section-head">
          <span class="inline-block text-xs font-semibold tracking-widest uppercase mb-3" style="color: var(--mc-jade-lighter); letter-spacing: 0.15em;">
            {{ t('pages.home.services.badge') }}
          </span>
          <h2>{{ t('pages.home.services.title') }}</h2>
          <p>{{ t('pages.home.services.description') }}</p>
        </div>

        <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="i in 12" :key="i" class="rounded-xl overflow-hidden border" style="background: var(--mc-surface-raised); border-color: var(--mc-border);">
            <div class="aspect-[16/10]" style="background: var(--mc-jade-faint);"></div>
            <div class="p-5 space-y-3">
              <div class="h-5 rounded w-3/4" style="background: var(--mc-jade-pale);"></div>
              <div class="h-3 rounded w-full" style="background: var(--mc-jade-faint);"></div>
              <div class="h-3 rounded w-2/3" style="background: var(--mc-jade-faint);"></div>
            </div>
          </div>
        </div>

        <div v-else-if="servicesError" class="text-center py-12">
          <p style="color: var(--mc-error);" class="mb-4">{{ t('common.loadingError') }}</p>
          <button
            @click="refreshServices"
            class="btn btn-primary px-6 py-3 text-sm"
          >
            {{ t('common.retry') }}
          </button>
        </div>

        <div
          v-else
          ref="servicesGrid"
          class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          <NuxtLink
            v-for="(service, index) in featuredServices"
            :key="service.id"
            :to="localePath(`/services/${service.slug || service.id}`)"
            class="group rounded-xl border card-hover cursor-pointer flex flex-col"
            :style="{
              background: 'var(--mc-surface-raised)',
              borderColor: 'var(--mc-border)',
              transitionDelay: `${index * 80}ms`,
              opacity: servicesRevealed ? 1 : 0,
              transform: servicesRevealed ? 'translateY(0)' : 'translateY(24px)',
              transition: 'opacity 0.7s var(--mc-ease-out), transform 0.7s var(--mc-ease-out), border-color 0.4s var(--mc-ease-out), box-shadow 0.4s var(--mc-ease-out)'
            }"
          >
            <div class="img-zoom aspect-[16/10]" style="background: linear-gradient(135deg, var(--mc-jade-faint), var(--mc-jade-pale));">
              <img
                v-if="service.image"
                :src="service.image"
                :alt="service.overview?.title || service.id"
                width="16" height="10"
                class="w-full h-full object-cover"
                loading="lazy"
              />
              <div v-else class="w-full h-full flex items-center justify-center">
                <svg class="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--mc-jade-lighter);">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
            </div>
            <div class="p-5 flex-1 flex flex-col">
              <h3 class="text-base font-bold mb-2 line-clamp-1 transition-colors duration-300" style="color: var(--mc-ink);">
                {{ service.title || service.id }}
              </h3>
              <p class="text-sm line-clamp-2 flex-1" style="color: var(--mc-ink-muted);">
                {{ service.description || service.excerpt || '' }}
              </p>
              <div class="mt-4 flex items-center text-sm font-medium transition-all duration-300 group-hover:translate-x-1" style="color: var(--mc-jade);">
                {{ t('common.learnMore') }}
                <svg class="ml-1 h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </NuxtLink>
        </div>

        <div class="text-center mt-12">
          <NuxtLink
            :to="localePath('/services')"
            class="inline-flex items-center font-medium text-base transition-all duration-300 hover:translate-x-1"
            style="color: var(--mc-jade);"
          >
            {{ t('pages.home.services.viewAll') }}
            <svg class="ml-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- Why Choose Us + Articles Section -->
    <section ref="educationSection" class="section" style="background: var(--mc-jade-faint);">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="section-head">
          <h2>{{ t('pages.home.education.articles.title') || 'Latest Articles & Insights' }}</h2>
          <p>{{ t('pages.home.education.articles.description') || 'Expert guides and insights to help you make informed decisions' }}</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
          <div class="space-y-6 reveal reveal-left" :class="{ visible: advantagesVisible }" ref="advantagesCol">
            <div
              v-for="(advantage, index) in advantages"
              :key="advantage.title"
              class="card-hover rounded-xl p-6 border"
              :style="{
                background: 'var(--mc-surface-raised)',
                borderColor: 'var(--mc-border)',
                transitionDelay: advantagesVisible ? `${index * 100}ms` : '0ms'
              }"
            >
              <div class="flex items-start gap-4">
                <div
                  class="p-3 rounded-xl flex-shrink-0 transition-all duration-300"
                  :style="{ background: advantage.iconBg }"
                >
                  <svg
                    class="h-6 w-6 transition-transform duration-300 group-hover:scale-110"
                    :style="{ color: advantage.iconColor }"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="advantage.iconPath" />
                  </svg>
                </div>
                <div>
                  <h3 class="text-lg font-bold mb-1.5" style="color: var(--mc-ink);">{{ t(advantage.title) }}</h3>
                  <p class="text-sm leading-relaxed" style="color: var(--mc-ink-muted);">{{ t(advantage.description) }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="reveal reveal-right" :class="{ visible: articlesRevealed }" ref="articlesCol">
            <div class="rounded-xl p-6 border" :style="{ background: 'var(--mc-surface-raised)', borderColor: 'var(--mc-border)' }">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div v-if="articlesLoading" v-for="i in 4" :key="'skel-'+i" class="rounded-lg overflow-hidden" style="background: var(--mc-jade-faint);">
                  <div class="aspect-[16/10]" style="background: var(--mc-jade-pale);"></div>
                  <div class="p-4 space-y-2">
                    <div class="h-4 rounded w-3/4" style="background: var(--mc-jade-pale);"></div>
                    <div class="h-3 rounded w-full" style="background: var(--mc-jade-faint);"></div>
                  </div>
                </div>

                <NuxtLink
                  v-for="(article, index) in featuredArticles"
                  :key="article.id"
                  :to="localePath(`/blogs/${article.slug || article.id}`)"
                  class="group rounded-lg overflow-hidden border card-hover"
                  :style="{
                    background: 'var(--mc-surface-raised)',
                    borderColor: 'var(--mc-border)',
                    transitionDelay: articlesRevealed ? `${index * 80}ms` : '0ms',
                    opacity: articlesRevealed ? 1 : 0,
                    transform: articlesRevealed ? 'translateY(0)' : 'translateY(16px)',
                    transition: 'opacity 0.6s var(--mc-ease-out), transform 0.6s var(--mc-ease-out), box-shadow 0.4s var(--mc-ease-out), border-color 0.4s var(--mc-ease-out)'
                  }"
                >
                  <div class="img-zoom aspect-[16/10]" style="background: linear-gradient(135deg, var(--mc-jade-faint), var(--mc-jade-pale));">
                    <img
                      v-if="article.image"
                      :src="article.image"
                      :alt="article.title"
                      width="16" height="10"
                      class="w-full h-full object-cover"
                      loading="lazy"
                    />
                    <div v-else class="w-full h-full flex items-center justify-center">
                      <svg class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--mc-jade-lighter);">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                      </svg>
                    </div>
                  </div>
                  <div class="p-4">
                    <div class="font-semibold text-sm line-clamp-2 mb-1 transition-colors duration-300 group-hover" style="color: var(--mc-ink);">
                      {{ article.title }}
                    </div>
                    <div class="text-xs line-clamp-2" style="color: var(--mc-ink-muted);">
                      {{ article.excerpt }}
                    </div>
                  </div>
                </NuxtLink>
              </div>

              <div class="mt-6 text-center">
                <NuxtLink
                  :to="localePath('/blogs')"
                  class="btn btn-primary px-6 py-3 text-sm"
                >
                  {{ t('pages.home.education.articles.viewAll') || 'View All Articles' }}
                  <svg class="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </NuxtLink>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Featured Partners Section -->
    <section class="section" style="background: var(--mc-surface);">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div ref="partnersHead" class="section-head">
          <span class="inline-block text-xs font-semibold tracking-widest uppercase mb-3" style="color: var(--mc-jade-lighter); letter-spacing: 0.15em;">
            {{ t('pages.home.featuredPartners.badge') || 'Featured Partners' }}
          </span>
          <h2>{{ t('pages.home.featuredPartners.title') || 'Our Partners' }}</h2>
          <p>{{ t('pages.home.featuredPartners.description') || 'We work with trusted organizations and experts across our industry.' }}</p>
        </div>

        <div v-if="featuredPartners.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <NuxtLink
            v-for="(partner, index) in featuredPartners"
            :key="partner.id"
            :to="localePath(`/partners/${partner.slug || partner.id}`)"
            class="group rounded-xl border card-hover overflow-hidden"
            :style="{
              background: 'var(--mc-surface-raised)',
              borderColor: 'var(--mc-border)',
              transitionDelay: partnersRevealed ? `${index * 100}ms` : '0ms',
              opacity: partnersRevealed ? 1 : 0,
              transform: partnersRevealed ? 'translateY(0)' : 'translateY(24px)',
              transition: 'opacity 0.7s var(--mc-ease-out), transform 0.7s var(--mc-ease-out), box-shadow 0.4s var(--mc-ease-out), border-color 0.4s var(--mc-ease-out)'
            }"
          >
            <div class="img-zoom aspect-[4/3]" style="background: var(--mc-jade-faint);">
              <img
                :src="partner.image || '/images/placeholder.svg'"
                :alt="partner.title"
                width="4" height="3"
                class="w-full h-full object-cover"
                loading="lazy"
              />
            </div>
            <div class="p-5">
              <span
                v-if="partner.type"
                class="inline-block px-2 py-0.5 text-xs font-medium rounded mb-2"
                :style="{ background: 'var(--mc-jade-pale)', color: 'var(--mc-jade-dark)' }"
              >
                {{ partner.type }}
              </span>
              <h3
                class="font-semibold mb-1 line-clamp-2 transition-colors duration-300"
                :style="{ color: 'var(--mc-ink)' }"
              >
                {{ partner.title }}
              </h3>
              <p class="text-sm line-clamp-2" style="color: var(--mc-ink-muted);">
                {{ partner.description }}
              </p>
              <div v-if="partner.city" class="mt-3 flex items-center text-xs" style="color: var(--mc-ink-faint);">
                <svg class="w-3.5 h-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                {{ partner.city }}
              </div>
            </div>
          </NuxtLink>
        </div>
        <div v-else-if="!partnersLoading && featuredPartners.length === 0" class="text-center py-12" style="color: var(--mc-ink-faint);">
          No featured partners yet.
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="section text-center text-white relative overflow-hidden" :style="{ background: 'linear-gradient(135deg, var(--mc-jade-dark), var(--mc-deep-warm))' }">
      <div class="absolute inset-0 opacity-10">
        <div class="absolute top-5 left-1/4 w-32 h-32 bg-white rounded-full animate-pulse" style="animation-duration: 6s;"></div>
        <div class="absolute bottom-5 right-1/4 w-48 h-48 bg-white rounded-full animate-pulse" style="animation-duration: 8s; animation-delay: 2s;"></div>
      </div>
      <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <h2 ref="ctaHead" class="text-3xl md:text-4xl font-bold mb-4 reveal reveal-up" :class="{ visible: ctaRevealed }">
          {{ t('pages.home.cta.title') }}
        </h2>
        <p class="text-lg mb-8 reveal reveal-up" :class="{ visible: ctaRevealed }" style="color: oklch(85% 0.01 185); transition-delay: 0.1s;">
          {{ t('pages.home.cta.description') }}
        </p>
        <div class="flex flex-wrap justify-center gap-4 reveal reveal-up" :class="{ visible: ctaRevealed }" style="transition-delay: 0.2s;">
          <NuxtLink
            :to="localePath('/contact')"
            class="btn btn-amber px-8 py-4 text-base"
          >
            {{ t('pages.home.cta.freeConsultation') }}
          </NuxtLink>
          <a
            :href="'tel:' + companyInfo.phone.replace(/[^+\d]/g, '')"
            class="btn btn-outline-light px-8 py-4 text-base"
          >
            {{ t('pages.home.cta.callNow') }}
          </a>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()
import { useLocalePath } from '#imports'
const localePath = useLocalePath()

const isMounted = ref(false)

const runtimeConfig = useRuntimeConfig()
const siteUrl = runtimeConfig.public.siteUrl || companyInfo.siteUrl

const canonicalUrl = computed(() => {
  const prefix = locale.value === 'en' ? '' : `/${locale.value}`
  return `${siteUrl}${prefix}`
})

useSeoMeta({
  title: t('seo.homeTitle'),
  description: t('seo.homeDescription'),
  keywords: '',
  ogTitle: t('seo.homeTitle'),
  ogDescription: t('seo.homeDescription'),
  ogImage: `${siteUrl}/images/hero-bg.webp`,
  ogType: 'website',
  ogSiteName: companyInfo.shortName,
  ogUrl: canonicalUrl,
  twitterCard: 'summary_large_image',
  twitterTitle: t('seo.homeTitle'),
  twitterDescription: t('seo.homeDescription'),
  twitterImage: `${siteUrl}/images/hero-bg.webp`
})

import { useOrganizationSchema } from '~/composables/useOrganizationSchema'
const organizationSchema = useOrganizationSchema('home')
useHead({
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify(organizationSchema)
    }
  ],
  link: [
    { rel: 'canonical', href: canonicalUrl },
    { rel: 'alternate', hreflang: 'x-default', href: `${siteUrl}` },
    { rel: 'alternate', hreflang: 'en', href: `${siteUrl}` },
    { rel: 'alternate', hreflang: 'fr', href: `${siteUrl}/fr` },
    { rel: 'alternate', hreflang: 'de', href: `${siteUrl}/de` }
  ]
})

const stats = [
  { value: '15+', label: 'pages.home.hero.stats.experience' },
  { value: '500+', label: 'pages.home.hero.stats.projects' },
  { value: '120+', label: 'pages.home.hero.stats.clients' },
  { value: '98%', label: 'pages.home.hero.stats.satisfaction' },
]

const advantages = [
  {
    title: 'pages.home.education.costSavings.title',
    description: 'pages.home.education.costSavings.description',
    iconPath: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
    iconBg: 'oklch(52% 0.16 185 / 0.1)',
    iconColor: 'var(--mc-jade)',
  },
  {
    title: 'pages.home.education.facilities.title',
    description: 'pages.home.education.facilities.description',
    iconPath: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    iconBg: 'oklch(72% 0.14 78 / 0.1)',
    iconColor: 'var(--mc-amber)',
  },
  {
    title: 'pages.home.education.waitingTime.title',
    description: 'pages.home.education.waitingTime.description',
    iconPath: 'M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z',
    iconBg: 'oklch(62% 0.12 230 / 0.1)',
    iconColor: 'var(--mc-info)',
  },
]

interface Service {
  id: string
  slug?: string
  title?: string
  description?: string
  excerpt?: string
  image?: string
  overview?: {
    title: string
    description: string
    excerpt?: string
  }
  highlights?: string[]
  meta?: {
    investment: string
  }
  conditions?: {
    items?: Array<{
      key: string
      value: string
    }>
  }
}

interface Partner {
  id: string
  slug?: string
  title: string
  description: string
  image?: string
  type?: string
  city?: string
}

interface Article {
  id: string
  slug?: string
  title: string
  excerpt: string
  image?: string
}

const { data: featuredServices, pending: loading, error: servicesError, refresh: refreshServices } = await useAsyncData<Service[]>('services', async () => {
  const response: any = await $fetch('/api/services', { params: { lang: locale.value, pageSize: 999 } })
  if (response.success && response.data) {
    return response.data.slice(0, 12)
  }
  return []
})

const { data: featuredPartners, pending: partnersLoading } = await useAsyncData<Partner[]>('partners', async () => {
  const response: any = await $fetch('/api/partners', { params: { lang: locale.value, pageSize: 999 } })
  if (response.success && response.data) {
    return response.data
      .filter((p: any) => p.featured === true)
      .sort((a: any, b: any) => (b.priority || 0) - (a.priority || 0))
      .slice(0, 4)
  }
  return []
})

const { data: featuredArticles, pending: articlesLoading } = await useAsyncData<Article[]>('articles', async () => {
  const response: any = await $fetch('/api/blogs', { params: { lang: locale.value, pageSize: 50 } })
  if (response.data) {
    return response.data
      .filter((a: any) => a.featured === true)
      .sort((a: any, b: any) => (b.priority || 0) - (a.priority || 0))
      .slice(0, 4)
  }
  return []
})

// --- Parallax ---
const heroBg = ref<HTMLElement | null>(null)
const parallaxY = ref(0)
let parallaxHandler: (() => void) | null = null

// --- Scroll Reveal refs ---
const servicesHead = ref<HTMLElement | null>(null)
const servicesGrid = ref<HTMLElement | null>(null)
const educationSection = ref<HTMLElement | null>(null)
const advantagesCol = ref<HTMLElement | null>(null)
const articlesCol = ref<HTMLElement | null>(null)
const partnersHead = ref<HTMLElement | null>(null)
const ctaHead = ref<HTMLElement | null>(null)

const servicesRevealed = ref(false)
const advantagesVisible = ref(false)
const articlesRevealed = ref(false)
const partnersRevealed = ref(false)
const ctaRevealed = ref(false)

// --- Intersection Observers ---
let servicesObserver: IntersectionObserver | null = null
let advantagesObserver: IntersectionObserver | null = null
let articlesObserver: IntersectionObserver | null = null
let partnersObserver: IntersectionObserver | null = null
let ctaObserver: IntersectionObserver | null = null

const createObserver = (
  el: HTMLElement,
  callback: () => void,
  threshold = 0.1,
  rootMargin = '0px 0px -60px 0px'
) => {
  const observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        callback()
        observer.unobserve(entry.target)
      }
    },
    { threshold, rootMargin }
  )
  observer.observe(el)
  return observer
}

onMounted(() => {
  isMounted.value = true

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

  if (!reducedMotion) {
    parallaxHandler = () => {
      const scrollY = window.scrollY
      parallaxY.value = scrollY * 0.15
    }
    window.addEventListener('scroll', parallaxHandler, { passive: true })
  }

  if (servicesGrid.value) {
    servicesObserver = createObserver(servicesGrid.value, () => { servicesRevealed.value = true })
  }
  if (advantagesCol.value) {
    advantagesObserver = createObserver(advantagesCol.value, () => { advantagesVisible.value = true })
  }
  if (articlesCol.value) {
    articlesObserver = createObserver(articlesCol.value, () => { articlesRevealed.value = true })
  }
  if (partnersHead.value) {
    partnersObserver = createObserver(partnersHead.value, () => { partnersRevealed.value = true })
  }
  if (ctaHead.value) {
    ctaObserver = createObserver(ctaHead.value, () => { ctaRevealed.value = true })
  }
})

// Retry services observer after loading finishes (handles client navigation where servicesGrid is initially hidden)
watch(loading, (isLoading) => {
  if (!isLoading && !servicesObserver) {
    nextTick(() => {
      if (servicesGrid.value) {
        servicesObserver = createObserver(servicesGrid.value, () => { servicesRevealed.value = true })
      }
    })
  }
})

onUnmounted(() => {
  if (parallaxHandler) window.removeEventListener('scroll', parallaxHandler)
  if (servicesObserver) servicesObserver.disconnect()
  if (advantagesObserver) advantagesObserver.disconnect()
  if (articlesObserver) articlesObserver.disconnect()
  if (partnersObserver) partnersObserver.disconnect()
  if (ctaObserver) ctaObserver.disconnect()
})
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 1;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 2;
}

.hero-reveal {
  opacity: 0;
  transform: translateY(20px);
  filter: blur(4px);
  animation: heroEntrance 0.9s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes heroEntrance {
  0% {
    opacity: 0;
    transform: translateY(20px);
    filter: blur(4px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
    filter: blur(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero-reveal {
    opacity: 1;
    transform: none;
    filter: none;
    animation: none;
  }
}
</style>
