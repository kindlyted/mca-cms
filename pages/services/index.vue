<template>
  <div class="pb-12" style="background: linear-gradient(135deg, var(--mc-jade-faint), var(--mc-surface), var(--mc-jade-faint));">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24">
      <!-- Breadcrumb -->
      <ClientOnly>
          <UBreadcrumb
            v-if="links && links.length > 1"
            :links="links"
            :ui="{
              wrapper: 'mb-4 text-sm breadcrumb-jade',
              base: 'ubreadcrumb-base',
              active: 'ubreadcrumb-active',
              label: 'ubreadcrumb-label',
              divider: {
                base: 'ubreadcrumb-divider'
              }
            }"
            divider="/"
          />
      </ClientOnly>

      <!-- Page Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">{{ t('pages.services.title') }}</h1>
        <p class="text-lg text-gray-600">{{ t('pages.services.description') }}</p>
      </div>

      <!-- Loading State -->
      <div v-if="pending || loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 spinner-jade"></div>
        <p class="mt-4 text-gray-600">{{ t('common.loading') }}</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12 bg-red-50 rounded-lg">
        <p class="text-red-600">{{ error }}</p>
      </div>

      <template v-else>
        <!-- Search and Filter -->
        <div class="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label for="service-search" class="block text-sm font-medium text-gray-700 mb-1">{{ t('pages.services.search.label') }}</label>
              <input
                v-model="searchQuery"
                type="text"
                id="service-search"
                name="search"
                :placeholder="t('pages.services.search.placeholder')"
                class="w-full px-3 py-2 rounded-md border input-jade"
                @keyup.enter="applyFilters"
              />
            </div>
            <div>
              <label for="service-category" class="block text-sm font-medium text-gray-700 mb-1">{{ t('pages.services.filter.typeLabel') }}</label>
              <select
                v-model="categoryFilter"
                id="service-category"
                name="category"
                class="w-full px-3 py-2 rounded-md border input-jade"
                @change="applyFilters"
              >
                <option value="">{{ t('pages.services.filter.allTypes') }}</option>
                <option value="consulting">{{ t('pages.services.filter.consulting') }}</option>
                <option value="implementation">{{ t('pages.services.filter.implementation') }}</option>
                <option value="training">{{ t('pages.services.filter.training') }}</option>
                <option value="support">{{ t('pages.services.filter.support') }}</option>
                <option value="product">{{ t('pages.services.filter.product') }}</option>
                <option value="custom">{{ t('pages.services.filter.custom') }}</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Stats -->
        <div class="flex items-center justify-between mb-6">
          <div class="text-sm text-gray-500">
            <span class="font-medium text-gray-900">{{ pagination.total }}</span> {{ t('pages.services.pagination.showing', { from: (pagination.page - 1) * pagination.pageSize + 1, to: Math.min(pagination.page * pagination.pageSize, pagination.total), total: pagination.total }) }}
          </div>
        </div>

        <!-- Service Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div
            v-for="service in services"
            :key="service.id"
            class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300"
          >
            <div class="aspect-w-16 aspect-h-9">
              <img
                :src="service.image"
                :alt="service.title"
                class="w-full h-48 object-cover"
              />
            </div>
            <div class="p-6">
              <h3 class="text-xl font-semibold text-gray-900 mb-2">
                <NuxtLink
                  :to="localePath(`/services/${service.slug || service.id}`)"
                  class="transition-colors hover:text-[var(--mc-jade)]"
                >
                  {{ service.title }}
                </NuxtLink>
              </h3>
              <p class="text-gray-600 text-sm mb-4 line-clamp-3">
                {{ service.description }}
              </p>
              <NuxtLink
                :to="localePath(`/services/${service.slug || service.id}`)"
                class="inline-flex items-center font-medium"
                style="color: var(--mc-jade);"
              >
                {{ t('common.learnMore') }}
                <svg class="ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
              </NuxtLink>
            </div>
          </div>
        </div>

        <!-- No Results -->
        <div v-if="services.length === 0" class="text-center py-12">
          <p class="text-gray-600">{{ t('pages.services.noResults') }}</p>
        </div>

        <!-- Pagination -->
        <div v-if="pagination.totalPages > 1" class="mt-12">
          <nav class="flex justify-center items-center space-x-2 flex-wrap gap-y-2">
            <!-- First Page -->
            <button
              @click="changePage(1)"
              :disabled="pagination.page === 1"
              class="px-3 py-2 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              :title="t('pages.services.pagination.first')"
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
              {{ t('pages.services.pagination.previous') }}
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
                    : 'border text-gray-700 hover:bg-gray-50'
                ]"
                :style="p === pagination.page ? { background: 'var(--mc-jade)', borderColor: 'var(--mc-jade)' } : { borderColor: 'var(--mc-border)' }"
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
              {{ t('pages.services.pagination.next') }}
            </button>

            <!-- Last Page -->
            <button
              @click="changePage(pagination.totalPages)"
              :disabled="pagination.page === pagination.totalPages"
              class="px-3 py-2 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              :title="t('pages.services.pagination.last')"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
            </button>
          </nav>

          <!-- Quick Jump -->
          <div class="flex justify-center items-center mt-4 gap-2 text-sm">
            <span class="text-gray-500">{{ t('pages.services.pagination.goTo') }}</span>
            <input
              v-model.number="jumpPage"
              type="number"
              min="1"
              :max="pagination.totalPages"
              class="w-16 px-2 py-1 border rounded-md text-center input-jade"
              @keyup.enter="handleJumpPage"
            />
            <span class="text-gray-500">{{ t('pages.services.pagination.page') }}</span>
            <button
              @click="handleJumpPage"
              class="px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              {{ t('pages.services.pagination.go') }}
            </button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 3;
}

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
</style>

<script setup lang="ts">
import { useBreadcrumb } from '~/composables/useBreadcrumb'
import { useI18n } from 'vue-i18n'

definePageMeta({
  title: 'Services'
})

const { t, locale } = useI18n()
import { useLocalePath } from '#imports'
const localePath = useLocalePath()
const runtimeConfig = useRuntimeConfig()
const siteUrl = runtimeConfig.public.siteUrl || companyInfo.siteUrl

const canonicalUrl = computed(() => {
  const prefix = locale.value === 'en' ? '' : `/${locale.value}`
  return `${siteUrl}${prefix}/services`
})

useSeoMeta({
  title: t('pages.services.title'),
  description: t('pages.services.description'),
  keywords: '',
  ogTitle: t('pages.services.title'),
  ogDescription: t('pages.services.description'),
  ogImage: `${siteUrl}/images/hero-bg.webp`,
  ogType: 'website',
  ogSiteName: companyInfo.shortName,
  ogUrl: canonicalUrl,
  twitterCard: 'summary_large_image',
  twitterTitle: t('pages.services.title'),
  twitterDescription: t('pages.services.description'),
  twitterImage: `${siteUrl}/images/hero-bg.webp`
})

// Organization Schema - Services listing page
import { useOrganizationSchema } from '~/composables/useOrganizationSchema'
const organizationSchema = useOrganizationSchema('service')
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
          { '@type': 'ListItem', position: 1, name: t('nav.home'), item: `${canonicalUrl.value.replace(/\/services$/, '')}/` },
          { '@type': 'ListItem', position: 2, name: t('nav.services'), item: canonicalUrl.value }
        ]
      })
    },
    {
      type: 'application/ld+json',
      innerHTML: () => JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        name: t('pages.services.title'),
        description: t('pages.services.description'),
        url: canonicalUrl.value
      })
    }
  ],
  link: [
    { rel: 'canonical', href: canonicalUrl },
    { rel: 'alternate', hreflang: 'x-default', href: `${siteUrl}/services` },
    { rel: 'alternate', hreflang: 'en', href: `${siteUrl}/services` },
    { rel: 'alternate', hreflang: 'fr', href: `${siteUrl}/fr/services` },
    { rel: 'alternate', hreflang: 'de', href: `${siteUrl}/de/services` }
  ]
})

const { links } = useBreadcrumb()

interface Service {
  id: string
  slug?: string
  title: string
  description: string
  image: string
  category: string
  readTime: number
}

interface ApiResponse {
  success: boolean
  data: Service[]
  pagination: {
    page: number
    pageSize: number
    total: number
    totalPages: number
  }
}

const searchQuery = ref('')
const categoryFilter = ref('')
const currentPage = ref(1)
const pageSize = 12
const loading = ref(false)
const error = ref('')
const jumpPage = ref(1)

// Generate cache key based on filters and page
const cacheKey = computed(() => `services-${currentPage.value}-${searchQuery.value}-${categoryFilter.value}-${locale.value}`)

// Fetch data with server-side pagination
const { data, refresh, pending } = await useAsyncData<ApiResponse>(
  () => cacheKey.value,
  () => $fetch<ApiResponse>('/api/services', {
    params: {
      page: currentPage.value,
      pageSize,
      lang: locale.value,
      keyword: searchQuery.value || undefined,
      category: categoryFilter.value || undefined
    }
  }),
  {
    watch: [currentPage, locale]
  }
)

const services = computed(() => data.value?.data || [])
const pagination = computed(() => data.value?.pagination || { page: 1, pageSize, total: 0, totalPages: 1 })

// Calculate displayed page numbers (smart pagination for large datasets)
const displayedPages = computed(() => {
  const total = pagination.value.totalPages
  const current = pagination.value.page
  const pages: (number | string)[] = []

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    pages.push(1)

    if (current > 4) {
      pages.push('...')
    }

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

// Apply search/filter changes
const applyFilters = async () => {
  currentPage.value = 1
  jumpPage.value = 1
  error.value = ''
  loading.value = true

  try {
    await refresh()
  } catch (err: any) {
    error.value = err.message || 'Failed to load'
  } finally {
    loading.value = false
  }

  if (process.client) {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// Change page
const changePage = async (page: number) => {
  if (page < 1 || page > pagination.value.totalPages) return

  currentPage.value = page
  jumpPage.value = page
  loading.value = true
  error.value = ''

  try {
    await refresh()
  } catch (err: any) {
    error.value = err.message || 'Failed to load'
  } finally {
    loading.value = false
  }

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
</script>
