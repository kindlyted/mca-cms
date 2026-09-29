<template>
  <div class="pb-12 bg-gradient-to-br from-blue-50 via-white to-indigo-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24">
      <!-- Breadcrumb -->
      <ClientOnly>
        <UBreadcrumb
          v-if="links && links.length > 1"
          :links="links"
          :ui="{
            wrapper: 'mb-4 text-sm text-gray-600',
            base: 'hover:text-gray-800',
            active: 'text-gray-800',
            label: 'text-gray-600',
            divider: {
              base: 'text-gray-400'
            }
          }"
          divider="/"
        />
      </ClientOnly>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">{{ t('common.loading') }}</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-20 bg-red-50 rounded-lg">
        <h1 class="text-2xl font-bold text-gray-900 mb-4">{{ t('common.loadingError') }}</h1>
        <p class="text-gray-600 mb-8">{{ error }}</p>
        <NuxtLink
          :to="localePath('/blogs')"
          class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          {{ t('error.notFound.browseContent') }}
        </NuxtLink>
      </div>

      <!-- 404 Not Found State -->
      <div v-else-if="isNotFound" class="min-h-[60vh] flex items-center justify-center">
        <div class="text-center">
          <div class="mb-8">
            <div class="relative inline-block">
              <svg class="w-32 h-32 text-blue-200" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
              <div class="absolute inset-0 flex items-center justify-center">
                <span class="text-6xl font-bold text-blue-600">404</span>
              </div>
            </div>
          </div>
          <h1 class="text-3xl font-bold text-gray-900 mb-4">{{ t('error.notFound.title') }}</h1>
          <p class="text-lg text-gray-600 mb-8">{{ t('error.notFound.description') }}</p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <NuxtLink
              :to="localePath('/')"
              class="inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              {{ t('error.notFound.backHome') }}
            </NuxtLink>
            <NuxtLink
              :to="localePath('/blogs')"
              class="inline-flex items-center justify-center px-6 py-3 bg-white text-blue-600 border border-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors"
            >
              {{ t('error.notFound.browseContent') }}
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Main Content with Sidebar -->
      <div v-else-if="article" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left: Article Content -->
        <article class="lg:col-span-2 space-y-8">
          <!-- Cover Image -->
          <div v-if="article.cover?.url || article.visuals?.cover?.url" class="bg-white rounded-lg shadow-sm overflow-hidden">
            <img
              :src="article.cover?.url || article.visuals?.cover?.url"
              :alt="article.cover?.alt || article.visuals?.cover?.alt"
              class="w-full h-64 object-cover"
            />
          </div>

          <!-- Article Header -->
          <div class="bg-white rounded-lg shadow-sm p-8">
            <div class="flex items-center text-sm text-gray-500 mb-4">
              <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>{{ formatDate(article.meta?.createdAt) }}</span>
              <span class="mx-2">|</span>
              <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{{ article.meta?.readTime || 5 }} min read</span>
            </div>
            <h1 class="text-3xl font-bold text-gray-900 mb-4">{{ article.overview?.title }}</h1>
            <p v-if="article.overview?.subtitle" class="text-gray-600 mb-6">{{ article.overview.subtitle }}</p>
            <div v-if="primaryTags.length > 0 || secondaryTags.length > 0" class="flex flex-wrap gap-2 mb-6">
              <span
                v-for="tag in primaryTags"
                :key="tag.id"
                class="inline-block px-3 py-1 text-sm font-medium rounded-full"
                :style="{ background: 'var(--mc-jade-pale)', color: 'var(--mc-jade-dark)' }"
              >
                {{ tag.name }}
              </span>
              <span
                v-for="tag in secondaryTags"
                :key="tag.id"
                class="inline-block px-3 py-1 text-sm font-medium rounded-full"
                :style="{ background: 'var(--mc-surface-alt)', color: 'var(--mc-ink-muted)' }"
              >
                {{ tag.name }}
              </span>
            </div>
            <p v-if="article.overview?.excerpt" class="text-gray-600 leading-relaxed">{{ article.overview.excerpt }}</p>
          </div>

          <!-- Article Body -->
          <div class="bg-white rounded-lg shadow-sm p-8">
            <div class="prose prose-lg max-w-none">
              <div
                class="article-content"
                v-html="renderedContent"
              ></div>
            </div>
          </div>

          <!-- FAQ Accordion (same as service/partner detail) -->
          <FaqAccordion
            v-if="article.faq && article.faq.length > 0"
            :items="normalizedFaq"
            :title="t('common.faqTitle')"
          />

          <!-- Related Services -->
          <div v-if="sidebarData?.relatedServices?.length" class="bg-white rounded-lg shadow-sm p-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-6">Related Services</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <NuxtLink
                v-for="svc in sidebarData.relatedServices"
                :key="svc.id"
                :to="svc.link"
                class="flex items-start gap-4 p-4 rounded-lg border border-gray-100 hover:border-blue-200 hover:shadow-sm transition-all group"
              >
                <img
                  v-if="svc.coverImage"
                  :src="svc.coverImage"
                  :alt="svc.title"
                  class="w-16 h-16 object-cover rounded-lg flex-shrink-0"
                />
                <div v-else class="w-16 h-16 bg-blue-50 rounded-lg flex-shrink-0 flex items-center justify-center">
                  <svg class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="text-sm font-semibold text-gray-900 group-hover:text-blue-600 line-clamp-2">{{ svc.title }}</h3>
                  <p v-if="svc.excerpt" class="text-xs text-gray-500 mt-1 line-clamp-2">{{ svc.excerpt }}</p>
                </div>
              </NuxtLink>
            </div>
          </div>

          <!-- Related Partners -->
          <div v-if="sidebarData?.relatedPartners?.length" class="bg-white rounded-lg shadow-sm p-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-6">Related Partners</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <NuxtLink
                v-for="prov in sidebarData.relatedPartners"
                :key="prov.id"
                :to="prov.link"
                class="flex items-start gap-4 p-4 rounded-lg border border-gray-100 hover:border-blue-200 hover:shadow-sm transition-all group"
              >
                <img
                  v-if="prov.coverImage"
                  :src="prov.coverImage"
                  :alt="prov.title"
                  class="w-16 h-16 object-cover rounded-lg flex-shrink-0"
                />
                <div v-else class="w-16 h-16 bg-green-50 rounded-lg flex-shrink-0 flex items-center justify-center">
                  <svg class="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="text-sm font-semibold text-gray-900 group-hover:text-blue-600 line-clamp-2">{{ prov.title }}</h3>
                  <p class="text-xs text-gray-500 mt-1">
                    <span v-if="prov.city" class="mr-2">{{ prov.city }}</span>
                    <span v-if="prov.type" class="capitalize">{{ prov.type }}</span>
                  </p>
                </div>
              </NuxtLink>
            </div>
          </div>

          <!-- References (same style as service/partner detail) -->
          <div v-if="article.references && article.references.length > 0" class="mb-8">
            <h2 class="text-2xl font-bold mb-4" :style="{ color: 'var(--mc-ink)' }">References</h2>
            <ul class="space-y-2">
              <li
                v-for="(ref, idx) in article.references"
                :key="idx"
                class="flex items-start space-x-2"
              >
                <span class="text-sm mt-1" :style="{ color: 'var(--mc-ink-faint)' }">{{ idx + 1 }}.</span>
                <a
                  :href="ref.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-sm hover:underline"
                  :style="{ color: 'var(--mc-jade)' }"
                >
                  {{ ref.title }}
                </a>
              </li>
            </ul>
          </div>

          <!-- Author (same style as ProductDetailLayout) -->
          <div v-if="article.meta?.author" class="mb-8 p-4 rounded-lg border" :style="{ background: 'var(--mc-surface-alt)', borderColor: 'var(--mc-border)' }">
            <h2 class="text-lg font-bold mb-3" :style="{ color: 'var(--mc-ink)' }">Author</h2>
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 text-white rounded-full flex items-center justify-center font-bold text-lg flex-shrink-0" :style="{ background: 'var(--mc-jade)' }">
                {{ (article.meta.author.name || '?').charAt(0) }}
              </div>
              <div>
                <p class="font-medium" :style="{ color: 'var(--mc-ink)' }">{{ article.meta.author.name }}</p>
                <p class="text-sm" :style="{ color: 'var(--mc-ink-faint)' }">{{ article.meta.author.role }}</p>
                <a
                  v-if="article.meta.author.url"
                  :href="article.meta.author.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-xs hover:underline"
                  :style="{ color: 'var(--mc-jade)' }"
                >
                  {{ article.meta.author.url }}
                </a>
              </div>
            </div>
          </div>

          <!-- Disclaimer -->
          <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg">
            <p class="text-sm text-yellow-800">
              {{ t('common.disclaimer') }}
            </p>
          </div>

          <!-- CTA -->
          <div class="mt-10 p-8 md:p-10 rounded-xl text-center relative overflow-hidden" style="background: linear-gradient(135deg, var(--mc-jade), var(--mc-deep));">
            <h2 class="text-2xl md:text-3xl font-bold text-white mb-3">{{ t('common.ctaSection.title') }}</h2>
            <p class="text-white/80 mb-6 max-w-xl mx-auto">{{ t('common.ctaSection.description') }}</p>
            <UButton
              :to="localePath('/contact')"
              size="xl"
              class="bg-white font-semibold rounded-lg shadow-lg hover:bg-white/90 transition-all duration-200"
              style="padding: 1rem 2rem; font-size: 1.05rem; color: var(--mc-jade-dark);"
            >
              {{ t('common.ctaSection.button') }}
            </UButton>
          </div>

          <!-- Share Buttons - Horizontal share bar -->
          <ClientOnly>
            <div v-if="article?.overview" class="bg-white rounded-lg shadow-sm p-6">
              <ShareButtons
                :title="article.overview.title || 'Blog Article'"
                :url="currentUrl"
                :description="article.seo?.description || article.overview.excerpt || ''"
                :image="shareImage"
                mode="inline"
              />
            </div>
          </ClientOnly>
        </article>

        <!-- Right: Smart Sidebar -->
        <div class="lg:col-span-1">
          <div class="sticky top-24">
            <BlogArticleSidebar ref="sidebarRef" :article-slug="articleSlug" />
          </div>
        </div>
      </div>

      <!-- Not Found -->
      <div v-else class="text-center py-12">
        <h1 class="text-2xl font-bold text-gray-900 mb-4">{{ t('error.notFound.title') }}</h1>
        <p class="text-gray-600 mb-8">{{ t('error.notFound.description') }}</p>
        <NuxtLink
          :to="localePath('/blogs')"
          class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          {{ t('error.notFound.browseContent') }}
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.article-content :deep(h2) {
  font-size: 1.5rem;
  font-weight: 600;
  margin-top: 2rem;
  margin-bottom: 1rem;
  color: #1f2937;
}

.article-content :deep(h3) {
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  color: #374151;
}

.article-content :deep(p) {
  color: #4b5563;
  line-height: 1.75;
  margin-bottom: 1rem;
  text-align: justify;
}

.article-content :deep(ul),
.article-content :deep(ol) {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
  color: #4b5563;
}

.article-content :deep(li) {
  margin-bottom: 0.5rem;
}

.article-content :deep(strong) {
  font-weight: 600;
  color: #1f2937;
}

.article-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
}

.article-content :deep(th),
.article-content :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 0.75rem;
  text-align: left;
}

.article-content :deep(th) {
  background-color: #f9fafb;
  font-weight: 600;
}
</style>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

import { useI18n } from 'vue-i18n'
import { marked } from 'marked'
import { useOrganizationSchema } from '~/composables/useOrganizationSchema'
import { useEntitySeo } from '~/composables/useEntitySeo'
import { useLocalePath } from '#imports'
import FaqAccordion from '~/components/FaqAccordion.vue'

interface Tag {
  id: string
  name: string
  slug: string
}

const route = useRoute()
const articleSlug = route.params.slug as string

const { t, locale } = useI18n({ useScope: 'global' })
const localePath = useLocalePath()

const runtimeConfig = useRuntimeConfig()
const siteUrl = runtimeConfig.public.siteUrl || companyInfo.siteUrl

const buildArticleUrl = (slug: string, lang: string): string => {
  const prefix = lang === 'en' ? '' : `/${lang}`
  return `${siteUrl}${prefix}/blogs/${slug}`
}

const buildAboutUrl = (lang: string): string => {
  const prefix = lang === 'en' ? '' : `/${lang}`
  return `${siteUrl}${prefix}/about`
}

const buildBlogIndexUrl = (lang: string): string => {
  const prefix = lang === 'en' ? '' : `/${lang}`
  return `${siteUrl}${prefix}/blogs`
}

const normalizeBlog = (data: any): any => {
  if (!data) return data
  const coverUrl = data.cover?.url || data.visuals?.cover?.url
  const coverAlt = data.cover?.alt || data.visuals?.cover?.alt || data.overview?.title || ''
  const coverCaption = data.cover?.caption || data.visuals?.cover?.caption
  return {
    ...data,
    body: typeof data.body === 'string' ? { format: 'markdown', content: data.body } : data.body,
    faq: (data.faq || []).map((item: any) => ({
      q: item.q || item.question || '',
      a: item.a || item.answer || ''
    })),
    cover: coverUrl ? { url: coverUrl, alt: coverAlt, ...(coverCaption && { caption: coverCaption }) } : undefined,
    references: data.references || data.content?.references || []
  }
}

// Convert blog FAQ format ({q, a}) to FaqAccordion format ({question, answer})
const normalizedFaq = computed(() => {
  return (article.value?.faq || []).map((item: any) => ({
    question: item.q || item.question || '',
    answer: item.a || item.answer || ''
  }))
})

// Breadcrumb links - 响应式计算以支持动态更新
const links = computed(() => {
  const crumbs: Array<{ label: string; to?: string }> = [
    { label: t('nav.home'), to: localePath('/') },
    { label: t('nav.stories'), to: localePath('/blogs') }
  ]

  if (rawData.value?.overview?.title) {
    crumbs.push({
      label: rawData.value.overview.title,
      to: undefined
    })
  }

  return crumbs
})

// Generate structured data for SEO (derive from data, not from stored schema)
const getStructuredData = (normalized: any, currentLocale: string) => {
  if (!normalized?.overview) return {}

  const articleUrl = buildArticleUrl(normalized.meta?.slug || normalized.meta?.id, currentLocale)

  const structuredData: any = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    'headline': normalized.overview?.title || 'Blog Article',
    'description': normalized.seo?.description || normalized.overview?.excerpt || '',
    'datePublished': normalized.meta?.createdAt || new Date().toISOString(),
    'dateModified': normalized.meta?.updatedAt || new Date().toISOString(),
    'lastReviewed': normalized.meta?.lastReviewed || undefined,
    'author': {
      '@type': 'Person',
      'name': normalized.meta?.author?.name || companyInfo.shortName,
      'url': normalized.meta?.author?.url || buildAboutUrl(currentLocale)
    },
    'publisher': {
      '@type': 'Organization',
      'name': companyInfo.shortName,
      'url': buildAboutUrl(currentLocale),
      logo: {
        '@type': 'ImageObject',
        'url': `${siteUrl}/logo.png`
      }
    },
    'mainEntityOfPage': {
      '@type': 'WebPage',
      '@id': articleUrl
    }
  }

  if (normalized.cover?.url) {
    structuredData.image = normalized.cover.url
  }

  if (normalized.source) {
    structuredData.citation = normalized.source
  }

  if (normalized.references && normalized.references.length > 0) {
    structuredData.about = normalized.references.map((ref: any) => ({
      '@type': 'Thing',
      'name': ref.title,
      'url': ref.url
    }))
  }

  const breadcrumbSchema = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      {
        '@type': 'ListItem',
        position: 1,
        name: t('nav.home'),
        item: `${siteUrl}/`
      },
      {
        '@type': 'ListItem',
        position: 2,
        name: t('nav.stories'),
        item: buildBlogIndexUrl(currentLocale)
      },
      {
        '@type': 'ListItem',
        position: 3,
        name: normalized.overview?.title || 'Blog Article',
        item: articleUrl
      }
    ]
  }

  return { article: structuredData, breadcrumb: breadcrumbSchema }
}

// SEO settings - derive OG/twitter/schema from minimal data
const setSeoMeta = (normalized: any, currentLocale: string) => {
  if (!normalized) return

  const articleUrl = buildArticleUrl(normalized.meta?.slug || normalized.meta?.id, currentLocale)
  const rawCoverUrl = normalized.cover?.url || '/images/logo.png'
  const coverUrl = rawCoverUrl.startsWith('http') ? rawCoverUrl : `${siteUrl}${rawCoverUrl}`
  const title = normalized.seo?.title || normalized.overview?.title || 'Blog Details'
  const description = normalized.seo?.description || normalized.overview?.excerpt || ''
  const keywords = normalized.seo?.keywords

  applySeo({ title, description, keywords, image: coverUrl })

  const structuredDataResult = getStructuredData(normalized, currentLocale)

  const faqSchema = normalized.faq?.length > 0 ? {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: normalized.faq.map((item: { q: string; a: string }) => ({
      '@type': 'Question',
      name: item.q,
      acceptedAnswer: {
        '@type': 'Answer',
        text: item.a
      }
    }))
  } : null

  useHead({
    script: [
      {
        type: 'application/ld+json',
        innerHTML: JSON.stringify(useOrganizationSchema('blog'))
      },
      {
        type: 'application/ld+json',
        innerHTML: JSON.stringify(structuredDataResult.article)
      },
      {
        type: 'application/ld+json',
        innerHTML: JSON.stringify(structuredDataResult.breadcrumb)
      },
      ...(faqSchema ? [{
        type: 'application/ld+json' as const,
        innerHTML: JSON.stringify(faqSchema)
      }] : [])
    ]
  })
}

// Use useAsyncData to ensure SSR waits for data fetching
const fetchArticle = async (): Promise<any> => {
  const response = await $fetch<{ success: boolean; data: any }>(`/api/blogs/${articleSlug}`, {
    params: {
      lang: locale.value
    }
  })

  if (response.success && response.data) {
    return response.data
  }

  throw new Error('Failed to fetch article')
}

const { data: rawData, pending: loading, error: fetchError } = await useAsyncData<any>(
  `blog-${articleSlug}`,
  fetchArticle,
  {
    server: true,
    default: () => null
  }
)

const article = computed(() => normalizeBlog(rawData.value))
const error = computed(() => fetchError.value?.message || '')
const isNotFound = computed(() => !rawData.value && !fetchError.value)

const sidebarRef = ref<any>(null)
const sidebarData = computed(() => sidebarRef.value?.recommendations || null)

// useEntitySeo for canonical + hreflang
const { applySeo } = useEntitySeo(article as any, 'blog')

// Share image (absolute URL for Web Share API)
const shareImage = computed(() => {
  const raw = article.value?.cover?.url
  if (!raw) return ''
  if (raw.startsWith('http')) return raw
  return `${siteUrl}${raw}`
})

// Current page URL
const currentUrl = computed(() => {
  if (process.client) {
    return window.location.href
  }
  return buildArticleUrl(article.value?.meta?.slug || articleSlug, locale.value)
})

// When 404 error is caught, navigate to custom 404 page
watchEffect(() => {
  if (fetchError.value && fetchError.value.statusCode === 404) {
    throw createError({ statusCode: 404, statusMessage: 'Article not found' })
  }
})

// Merge all tags - separate primary and secondary for styling
const primaryTags = computed(() => {
  return article.value?.tags?.primary || []
})

const secondaryTags = computed(() => {
  return article.value?.tags?.secondary || []
})

// Render a sections item to HTML
const renderSection = (section: any): string => {
  switch (section.type) {
    case 'heading':
      return `<h${section.level || 2}>${section.text || ''}</h${section.level || 2}>`
    case 'paragraph':
      return `<p>${section.text || ''}</p>`
    case 'list': {
      const tag = section.style === 'numbered' ? 'ol' : 'ul'
      if (section.items && Array.isArray(section.items)) {
        return `<${tag}>${section.items.map((item: any) => {
          const text = typeof item === 'string' ? item : (item.title ? `<strong>${item.title}</strong>: ${item.description || ''}` : item.text || '')
          return `<li>${text}</li>`
        }).join('')}</${tag}>`
      }
      return ''
    }
    case 'table': {
      const thead = section.headers ? `<thead><tr>${section.headers.map((h: string) => `<th>${h}</th>`).join('')}</tr></thead>` : ''
      const tbody = section.rows ? `<tbody>${section.rows.map((row: string[]) => `<tr>${row.map((cell: string) => `<td>${cell}</td>`).join('')}</tr>`).join('')}</tbody>` : ''
      return `<table>${thead}${tbody}</table>${section.caption ? `<p class="text-sm text-gray-500 text-center">${section.caption}</p>` : ''}`
    }
    case 'steps':
      if (section.items && Array.isArray(section.items)) {
        return `<div class="space-y-4">${section.items.map((step: any) =>
          `<div class="bg-gray-50 rounded-lg p-4"><h4 class="font-semibold">${step.title || ''}</h4><p class="text-gray-600 mt-1">${step.description || ''}</p></div>`
        ).join('')}</div>`
      }
      return ''
    default:
      return ''
  }
}

// Calculate rendered markdown content
const renderedContent = computed(() => {
  const body = article.value?.body
  if (!body) return ''

  // Structured sections format
  if (body.format === 'sections' && body.sections && body.sections.length > 0) {
    return body.sections.map(renderSection).join('\n')
  }

  // Markdown format
  if (!body.content) return ''

  try {
    marked.setOptions({
      breaks: true,
      gfm: true
    })

    let md = body.content

    md = md.replace(/\{\{cta-button\}\}/g, '<div class="my-6"><a href="/contact" class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">Contact Us Now →</a></div>')

    md = md.replace(
      /(\|.+\|\n)\n+(\|[-:\s|]+\|\n)\n+/g,
      '$1$2'
    )

    md = md.replace(
      /(\|.+\|)\n\n+(?=\|)/g,
      '$1\n'
    )

    return marked.parse(md)
  } catch (err) {
    console.error('Error parsing markdown:', err)
    return `<p>${body.content}</p>`
  }
})

// Format date helper
const formatDate = (dateString?: string): string => {
  if (!dateString) return ''

  try {
    const date = new Date(dateString)
    return date.toLocaleDateString((locale.value as string) === 'zh' ? 'zh-CN' : 'en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch {
    return dateString
  }
}

watch(article, (newArticle) => {
  if (newArticle) {
    setSeoMeta(newArticle, locale.value)
  }
}, { immediate: true })
</script>
