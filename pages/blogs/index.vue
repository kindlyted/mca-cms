<template>
  <div class="pb-12" style="background: linear-gradient(135deg, var(--mc-jade-faint), var(--mc-surface), var(--mc-jade-faint));">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24">
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
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">{{ t('pages.stories.title') }}</h1>
        <p class="text-lg text-gray-600">{{ t('pages.stories.description') }}</p>
      </div>

      <!-- Filter Component -->
      <BlogFilter
        v-model="filters"
        :loading="filterLoading"
        @apply="onFilterApply"
      />

      <!-- View Toggle & Stats -->
      <div class="flex flex-col sm:flex-row justify-between items-center mb-8 gap-4">
        <div class="text-sm text-gray-500">
          <span class="font-medium text-gray-900">{{ pagination.total }}</span> {{ t('pages.stories.stats.stories') }}
          <span v-if="pagination.totalPages > 1" class="ml-2">
            {{ t('pages.stories.stats.pageOf', { current: pagination.page, total: pagination.totalPages }) }}
          </span>
        </div>
        
        <!-- View Toggle Buttons -->
        <div class="flex items-center bg-white rounded-lg shadow-sm border border-gray-200 p-1">
          <button
            @click="setViewMode('grid')"
            :class="[
              'flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors',
              viewMode === 'grid'
                ? 'text-white'
                : 'text-gray-600 hover:bg-gray-100'
            ]"
            :style="viewMode === 'grid' ? { backgroundColor: 'var(--mc-jade)' } : {}"
          >
            <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2-2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2-2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2-2h-2a2 2 0 01-2-2v-2z" />
            </svg>
            {{ t('pages.stories.viewMode.grid') }}
          </button>
          <button
            @click="setViewMode('list')"
            :class="[
              'flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors',
              viewMode === 'list'
                ? 'text-white'
                : 'text-gray-600 hover:bg-gray-100'
            ]"
            :style="viewMode === 'list' ? { backgroundColor: 'var(--mc-jade)' } : {}"
          >
            <svg class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            {{ t('pages.stories.viewMode.list') }}
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="spinner-jade inline-block animate-spin rounded-full h-8 w-8"></div>
        <p class="mt-4 text-gray-600">{{ t('common.loading') }}</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12 bg-red-50 rounded-lg">
        <p class="text-red-600">{{ error }}</p>
      </div>

      <!-- Grid View -->
      <div v-else-if="viewMode === 'grid'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <div
          v-for="article in articles"
          :key="article.id"
          class="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow flex flex-col"
        >
          <div class="aspect-video overflow-hidden bg-gray-100">
            <img
              :src="article.image"
              :alt="article.title"
              class="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
              loading="lazy"
            />
          </div>
          <div class="p-5 flex flex-col flex-1">
            <div class="flex items-center text-sm text-gray-500 mb-2">
              <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span>{{ formatDate(article.publishedAt) }}</span>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">{{ article.title }}</h3>
            <p class="text-gray-600 text-sm mb-4 line-clamp-3 flex-1">{{ article.excerpt }}</p>
            <div class="flex flex-wrap gap-2 mb-4">
              <span
                v-for="(tag, idx) in article.tags.slice(0, 3)"
                :key="`${article.id}-tag-${idx}`"
                class="px-2 py-1 text-xs rounded-full" style="background: oklch(52% 0.16 185 / 0.1); color: var(--mc-jade);"
              >
                {{ tag.name }}
              </span>
            </div>
            <NuxtLink
              :to="localePath(`/blogs/${article.slug || article.id}`)"
              class="inline-flex items-center font-medium text-sm mt-auto" style="color: var(--mc-jade);"
            >
              {{ t('common.readMore') }}
              <svg class="ml-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- List View -->
      <div v-else class="space-y-4">
        <div
          v-for="article in articles"
          :key="article.id"
          class="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow"
        >
          <div class="flex flex-col sm:flex-row">
            <!-- Image -->
            <div class="sm:w-48 md:w-56 flex-shrink-0">
              <img
                :src="article.image"
                :alt="article.title"
                class="w-full h-48 sm:h-full object-cover"
                loading="lazy"
              />
            </div>
            <!-- Content -->
            <div class="p-5 flex-1 flex flex-col">
              <div class="flex items-center text-sm text-gray-500 mb-2">
                <svg class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span>{{ formatDate(article.publishedAt) }}</span>
              </div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">{{ article.title }}</h3>
              <p class="text-gray-600 text-sm mb-4 line-clamp-2 flex-1">{{ article.excerpt }}</p>
              <div class="flex flex-wrap items-center justify-between gap-4">
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="(tag, idx) in article.tags.slice(0, 5)"
                    :key="`${article.id}-tag-${idx}`"
                    class="px-2 py-1 text-xs rounded-full" style="background: oklch(52% 0.16 185 / 0.1); color: var(--mc-jade);"
                  >
                    {{ tag }}
                  </span>
                </div>
                <NuxtLink
                  :to="`/blogs/${article.slug || article.id}`"
                  class="inline-flex items-center font-medium text-sm whitespace-nowrap" style="color: var(--mc-jade);"
                >
                  {{ t('common.readMore') }}
                  <svg class="ml-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </NuxtLink>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && !error && articles.length === 0" class="text-center py-12">
        <div class="text-gray-400 mb-4">
          <svg class="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
          </svg>
        </div>
        <p class="text-gray-600 text-lg">{{ t('pages.stories.empty.title') }}</p>
        <p class="text-gray-500 text-sm mt-2">{{ t('pages.stories.empty.subtitle') }}</p>
      </div>

      <!-- Pagination -->
      <div v-if="!loading && !error && pagination.totalPages > 1" class="mt-12">
        <!-- Page Info -->
        <div class="text-center text-sm text-gray-500 mb-4">
          {{ t('pages.stories.pagination.showing', { from: (pagination.page - 1) * pagination.pageSize + 1, to: Math.min(pagination.page * pagination.pageSize, pagination.total), total: pagination.total }) }}
        </div>
        
        <!-- Page Navigation -->
        <nav class="flex justify-center items-center space-x-2 flex-wrap gap-y-2">
          <!-- First Page -->
          <button
            @click="changePage(1)"
            :disabled="pagination.page === 1"
            class="px-3 py-2 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            :title="t('pages.stories.pagination.first')"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
            </svg>
          </button>
          
          <!-- Previous Page -->
          <button
            @click="changePage(pagination.page - 1)"
            :disabled="pagination.page === 1"
            class="px-3 py-2 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
          >
            {{ t('pages.stories.pagination.previous') }}
          </button>
          
          <!-- Page Numbers -->
          <template v-for="p in displayedPages" :key="p">
            <button
              v-if="p !== '...'"
              @click="changePage(p as number)"
              :class="[
                'px-4 py-2 rounded-md text-sm font-medium min-w-[40px]',
                p === pagination.page
                  ? 'text-white'
                  : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
              ]"
              :style="p === pagination.page ? { backgroundColor: 'var(--mc-jade)' } : {}"
            >
              {{ p }}
            </button>
            <span v-else class="px-2 text-gray-400">...</span>
          </template>
          
          <!-- Next Page -->
          <button
            @click="changePage(pagination.page + 1)"
            :disabled="pagination.page === pagination.totalPages"
            class="px-3 py-2 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
          >
            {{ t('pages.stories.pagination.next') }}
          </button>
          
          <!-- Last Page -->
          <button
            @click="changePage(pagination.totalPages)"
            :disabled="pagination.page === pagination.totalPages"
            class="px-3 py-2 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            :title="t('pages.stories.pagination.last')"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
            </svg>
          </button>
        </nav>
        
        <!-- Quick Jump -->
        <div class="flex justify-center items-center mt-4 gap-2 text-sm">
          <span class="text-gray-500">{{ t('pages.stories.pagination.goTo') }}</span>
          <input
            v-model.number="jumpPage"
            type="number"
            min="1"
            :max="pagination.totalPages"
            class="w-16 px-2 py-1 border border-gray-300 rounded-md text-center input-jade"
            @keyup.enter="handleJumpPage"
          />
          <span class="text-gray-500">{{ t('pages.stories.pagination.page') }}</span>
          <button
            @click="handleJumpPage"
            class="px-3 py-1 text-white rounded-md btn-jade-solid"
          >
            {{ t('pages.stories.pagination.go') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Line clamp utilities */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 2;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 3;
}

/* Hide number input arrows */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
  appearance: textfield;
}

/* Smooth transitions */
.transition-shadow {
  transition: box-shadow 0.2s ease-in-out;
}
</style>

<script setup lang="ts">
import { useBreadcrumb } from '~/composables/useBreadcrumb'
import { useI18n } from 'vue-i18n'
import { useLocalePath } from '#i18n'

definePageMeta({
  title: 'Medical Tourism Blog & Cost Guides'
})

const { t, locale } = useI18n()
const localePath = useLocalePath()
const runtimeConfig = useRuntimeConfig()
const siteUrl = runtimeConfig.public.siteUrl || companyInfo.siteUrl

const canonicalUrl = computed(() => {
  const prefix = locale.value === 'en' ? '' : `/${locale.value}`
  return `${siteUrl}${prefix}/blogs`
})

useSeoMeta({
  title: t('pages.stories.title'),
  description: t('pages.stories.description'),
  keywords: '',
  ogTitle: t('pages.stories.title'),
  ogDescription: t('pages.stories.description'),
  ogImage: `${siteUrl}/images/hero-bg.webp`,
  ogType: 'website',
  ogSiteName: companyInfo.shortName,
  ogUrl: canonicalUrl,
  twitterCard: 'summary_large_image',
  twitterTitle: t('pages.stories.title'),
  twitterDescription: t('pages.stories.description'),
  twitterImage: `${siteUrl}/images/hero-bg.webp`
})

// Organization Schema - Blog listing page
import { useOrganizationSchema } from '~/composables/useOrganizationSchema'
const organizationSchema = useOrganizationSchema('blog')
useHead({
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify(organizationSchema)
    },
    {
      type: 'application/ld+json',
      innerHTML: () => JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        itemListElement: [
          { '@type': 'ListItem', position: 1, name: t('nav.home'), item: `${canonicalUrl.value.replace(/\/blog$/, '')}/` },
          { '@type': 'ListItem', position: 2, name: t('nav.stories'), item: canonicalUrl.value }
        ]
      })
    },
    {
      type: 'application/ld+json',
      innerHTML: () => JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        name: t('pages.stories.title'),
        description: t('pages.stories.description'),
        url: canonicalUrl.value
      })
    }
  ],
  link: [
    { rel: 'canonical', href: canonicalUrl },
    { rel: 'alternate', hreflang: 'x-default', href: `${siteUrl}/blogs` },
    { rel: 'alternate', hreflang: 'en', href: `${siteUrl}/blogs` },
    { rel: 'alternate', hreflang: 'fr', href: `${siteUrl}/fr/blogs` },
    { rel: 'alternate', hreflang: 'de', href: `${siteUrl}/de/blogs` }
  ]
})

const { links } = useBreadcrumb()

interface Article {
  id: number
  slug?: string
  title: string
  excerpt: string
  publishedAt: string
  image: string
  tags: string[]
  country?: string
}

interface ApiResponse {
  data: Article[]
  pagination: {
    page: number
    pageSize: number
    total: number
    totalPages: number
  }
}

// View mode: grid = card view, list = list view
const viewMode = ref<'grid' | 'list'>('grid')
const currentPage = ref(1)
const loading = ref(false)
const filterLoading = ref(false)
const error = ref<string | null>(null)
const jumpPage = ref(1)

// Filter state
const filters = reactive({
  keyword: '',
  tags: [] as string[]
})

// Set page size based on view mode
const pageSize = computed(() => viewMode.value === 'grid' ? 12 : 20)

// Read user preference from localStorage
onMounted(() => {
  const savedViewMode = localStorage.getItem('blog-view-mode')
  if (savedViewMode === 'grid' || savedViewMode === 'list') {
    viewMode.value = savedViewMode
  }
})

// Generate cache key
const cacheKey = computed(() => {
  const filterStr = `${filters.keyword}-${filters.tags.join(',')}`
  return `blog-articles-${viewMode.value}-${currentPage.value}-${filterStr}`
})

// Fetch article data from blog API
const { data, refresh } = await useAsyncData<ApiResponse>(
  () => cacheKey.value,
  () => $fetch<ApiResponse>('/api/blogs', {
    params: {
      page: currentPage.value,
      pageSize: pageSize.value,
      lang: locale.value,
      keyword: filters.keyword || undefined,
      tags: filters.tags.length > 0 ? filters.tags.join(',') : undefined
    }
  }),
  {
    watch: [currentPage, pageSize, locale]
  }
)

const articles = computed(() => data.value?.data || [])
const pagination = computed(() => data.value?.pagination || { page: 1, pageSize: pageSize.value, total: 0, totalPages: 1 })

// Calculate displayed page numbers (smart pagination for large datasets)
const displayedPages = computed(() => {
  const total = pagination.value.totalPages
  const current = pagination.value.page
  const pages: (number | string)[] = []
  
  if (total <= 7) {
    // Show all page numbers if total is 7 or less
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // Smart pagination display
    pages.push(1)
    
    if (current > 4) {
      pages.push('...')
    }
    
    // Show page numbers around current page
    const start = Math.max(2, current - 2)
    const end = Math.min(total - 1, current + 2)
    
    for (let i = start; i <= end; i++) {
      pages.push(i)
    }
    
    if (current < total - 3) {
      pages.push('...')
    }
    
    pages.push(total)
  }
  
  return pages
})

// Switch view mode
const setViewMode = async (mode: 'grid' | 'list') => {
  if (viewMode.value === mode) return
  
  viewMode.value = mode
  currentPage.value = 1 // Reset to first page when switching views
  jumpPage.value = 1
  
  // Save user preference
  if (process.client) {
    localStorage.setItem('blog-view-mode', mode)
  }
  
  // Reload data
  loading.value = true
  await refresh()
  loading.value = false
}

// Format date
const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Change page
const changePage = async (page: number) => {
  if (page < 1 || page > pagination.value.totalPages) return
  
  currentPage.value = page
  jumpPage.value = page
  loading.value = true
  error.value = null
  
  try {
    await refresh()
  } catch (err: any) {
    error.value = err.message || 'Failed to load'
  } finally {
    loading.value = false
  }
  
  // Scroll to top
  if (process.client) {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// Handle jump to page
const handleJumpPage = () => {
  let page = parseInt(String(jumpPage.value))
  if (isNaN(page)) return

  page = Math.max(1, Math.min(page, pagination.value.totalPages))
  changePage(page)
}

// Handle filter application
interface FilterValues {
  keyword: string
  tags: string[]
}

const onFilterApply = async (newFilters: FilterValues) => {
  // Update filter state
  filters.keyword = newFilters.keyword
  filters.tags = newFilters.tags

  filterLoading.value = true
  currentPage.value = 1
  jumpPage.value = 1
  error.value = null

  try {
    await refresh()
  } catch (err: any) {
    error.value = err.message || 'Filter failed'
  } finally {
    filterLoading.value = false
  }

  // Scroll to top
  if (process.client) {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}
</script>
