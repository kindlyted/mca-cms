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
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">{{ t('pages.partners.title') }}</h1>
        <p class="text-lg text-gray-600">{{ t('pages.partners.description') }}</p>
      </div>

      <!-- Loading State -->
      <div v-if="pending || loading" class="text-center py-12">
        <div class="spinner-jade inline-block animate-spin rounded-full h-8 w-8"></div>
        <p class="mt-4 text-gray-600">{{ t('common.loading') }}</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12 bg-red-50 rounded-lg">
        <p class="text-red-600">{{ error }}</p>
      </div>

      <template v-else>
        <!-- Search and Filter -->
        <div class="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label for="partner-search" class="block text-sm font-medium text-gray-700 mb-1">{{ t('pages.partners.search.label') }}</label>
              <input
                v-model="searchQuery"
                type="text"
                id="partner-search"
                name="search"
                :placeholder="t('pages.partners.search.placeholder')"
                class="w-full px-3 py-2 border input-jade"
                @keyup.enter="applyFilters"
              />
            </div>
            <div>
              <label for="partner-type" class="block text-sm font-medium text-gray-700 mb-1">{{ t('pages.partners.filter.typeLabel') }}</label>
              <select
                v-model="typeFilter"
                id="partner-type"
                name="type"
                class="w-full px-3 py-2 border input-jade"
                @change="applyFilters"
              >
                <option value="">{{ t('pages.partners.filter.allTypes') }}</option>
                <option v-for="type in filterOptions.types" :key="type" :value="type">{{ typeLabel(type) }}</option>
              </select>
            </div>
            <div>
              <label for="partner-city" class="block text-sm font-medium text-gray-700 mb-1">{{ t('pages.partners.filter.cityLabel') }}</label>
              <select
                v-model="cityFilter"
                id="partner-city"
                name="city"
                class="w-full px-3 py-2 border input-jade"
                @change="applyFilters"
              >
                <option value="">{{ t('pages.partners.filter.allCities') }}</option>
                <option v-for="city in filterOptions.cities" :key="city" :value="city">{{ city }}</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Stats -->
        <div class="flex items-center justify-between mb-6">
          <div class="text-sm text-gray-500">
            <span class="font-medium text-gray-900">{{ pagination.total }}</span> {{ t('pages.partners.pagination.showing', { from: (pagination.page - 1) * pagination.pageSize + 1, to: Math.min(pagination.page * pagination.pageSize, pagination.total), total: pagination.total }) }}
          </div>
        </div>

        <!-- Partner Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div
            v-for="partner in partners"
            :key="partner.id"
            class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300"
          >
            <div class="aspect-w-16 aspect-h-9">
              <img
                :src="partner.image"
                :alt="partner.title"
                class="w-full h-48 object-cover"
              />
            </div>
            <div class="p-6">
              <div class="flex items-center justify-between mb-2">
                <span class="inline-block px-2 py-1 text-xs font-medium rounded-full" style="background: oklch(52% 0.16 185 / 0.1); color: var(--mc-jade);">
                  {{ typeLabel(partner.type) }}
                </span>
                <span v-if="partner.city" class="text-sm text-gray-500">
                  {{ partner.city }}
                </span>
              </div>
              <h3 class="text-xl font-semibold text-gray-900 mb-2">
                <NuxtLink
                  :to="localePath(`/partners/${partner.slug || partner.id}`)"
                  class="hover:text-[var(--mc-jade)] transition-colors"
                >
                  {{ partner.title }}
                </NuxtLink>
              </h3>
              <p class="text-gray-600 text-sm mb-4 line-clamp-3">
                {{ partner.description }}
              </p>
              <NuxtLink
                :to="localePath(`/partners/${partner.slug || partner.id}`)"
                class="inline-flex items-center font-medium" style="color: var(--mc-jade);"
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
        <div v-if="!loading && !error && partners.length === 0" class="text-center py-12">
          <p class="text-gray-600">{{ t('pages.partners.noResults') }}</p>
        </div>

        <!-- Pagination -->
        <div v-if="!loading && !error && pagination.totalPages > 1" class="mt-12">
          <nav class="flex justify-center items-center space-x-2 flex-wrap gap-y-2">
            <!-- First Page -->
            <button
              @click="changePage(1)"
              :disabled="pagination.page === 1"
              class="px-3 py-2 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              :title="t('pages.partners.pagination.first')"
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
              {{ t('pages.partners.pagination.previous') }}
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
              {{ t('pages.partners.pagination.next') }}
            </button>

            <!-- Last Page -->
            <button
              @click="changePage(pagination.totalPages)"
              :disabled="pagination.page === pagination.totalPages"
              class="px-3 py-2 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              :title="t('pages.partners.pagination.last')"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
            </button>
          </nav>

          <!-- Quick Jump -->
          <div class="flex justify-center items-center mt-4 gap-2 text-sm">
            <span class="text-gray-500">{{ t('pages.partners.pagination.goTo') }}</span>
            <input
              v-model.number="jumpPage"
              type="number"
              min="1"
              :max="pagination.totalPages"
               class="w-16 px-2 py-1 border border-gray-300 rounded-md text-center input-jade"
              @keyup.enter="handleJumpPage"
            />
            <span class="text-gray-500">{{ t('pages.partners.pagination.page') }}</span>
            <button
              @click="handleJumpPage"
               class="px-3 py-1 text-white rounded-md btn-jade-solid"
            >
              {{ t('pages.partners.pagination.go') }}
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
  title: 'Partners'
})

const { t, locale } = useI18n()
import { useLocalePath } from '#imports'
const localePath = useLocalePath()
const runtimeConfig = useRuntimeConfig()
const siteUrl = runtimeConfig.public.siteUrl || companyInfo.siteUrl

const canonicalUrl = computed(() => {
  const prefix = locale.value === 'en' ? '' : `/${locale.value}`
  return `${siteUrl}${prefix}/partners`
})

useSeoMeta({
  title: t('pages.partners.title'),
  description: t('pages.partners.description'),
  keywords: '',
  ogTitle: t('pages.partners.title'),
  ogDescription: t('pages.partners.description'),
  ogImage: `${siteUrl}/images/hero-bg.webp`,
  ogType: 'website',
  ogSiteName: companyInfo.shortName,
  ogUrl: canonicalUrl,
  twitterCard: 'summary_large_image',
  twitterTitle: t('pages.partners.title'),
  twitterDescription: t('pages.partners.description'),
  twitterImage: `${siteUrl}/images/hero-bg.webp`
})

// Organization Schema - Partners listing page
import { useOrganizationSchema } from '~/composables/useOrganizationSchema'
const organizationSchema = useOrganizationSchema('partner')
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
          { '@type': 'ListItem', position: 1, name: t('nav.home'), item: `${canonicalUrl.value.replace(/\/partners$/, '')}/` },
          { '@type': 'ListItem', position: 2, name: t('nav.partners'), item: canonicalUrl.value }
        ]
      })
    },
    {
      type: 'application/ld+json',
      innerHTML: () => JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        name: t('pages.partners.title'),
        description: t('pages.partners.description'),
        url: canonicalUrl.value
      })
    }
  ],
  link: [
    { rel: 'canonical', href: canonicalUrl },
    { rel: 'alternate', hreflang: 'x-default', href: `${siteUrl}/partners` },
    { rel: 'alternate', hreflang: 'en', href: `${siteUrl}/partners` },
    { rel: 'alternate', hreflang: 'fr', href: `${siteUrl}/fr/partners` },
    { rel: 'alternate', hreflang: 'de', href: `${siteUrl}/de/partners` }
  ]
})

const { links } = useBreadcrumb()

interface Partner {
  id: string
  slug?: string
  title: string
  description: string
  image: string
  type: string
  city: string
  region: string
  featured: boolean
  priority: number
}

interface ApiResponse {
  success: boolean
  data: Partner[]
  pagination: {
    page: number
    pageSize: number
    total: number
    totalPages: number
  }
}

const searchQuery = ref('')
const typeFilter = ref('')
const cityFilter = ref('')
const currentPage = ref(1)
const pageSize = 12
const loading = ref(false)
const error = ref('')
const jumpPage = ref(1)

interface FilterOptions {
  types: string[]
  cities: string[]
}

const filterOptions = ref<FilterOptions>({ types: [], cities: [] })

async function loadFilters() {
  try {
    const res = await $fetch<{ success: boolean; data: FilterOptions }>('/api/partners/filters', {
      params: { lang: locale.value }
    })
    filterOptions.value = res.data
  } catch {
    filterOptions.value = { types: [], cities: [] }
  }
}

watch(locale, () => {
  loadFilters()
}, { immediate: true })

const typeLabelMap: Record<string, string> = {
  company: 'pages.partners.filter.company',
  institution: 'pages.partners.filter.institution',
  partner: 'pages.partners.filter.partner',
  consultant: 'pages.partners.filter.consultant',
  'training-center': 'pages.partners.filter.trainingCenter'
}

function typeLabel(type: string): string {
  return typeLabelMap[type] ? t(typeLabelMap[type]) : type
}

// Generate cache key based on filters and page
const cacheKey = computed(() => `partners-${currentPage.value}-${searchQuery.value}-${typeFilter.value}-${cityFilter.value}-${locale.value}`)

// Fetch data with server-side pagination
const { data, refresh, pending } = await useAsyncData<ApiResponse>(
  () => cacheKey.value,
  () => $fetch<ApiResponse>('/api/partners', {
    params: {
      page: currentPage.value,
      pageSize,
      lang: locale.value,
      keyword: searchQuery.value || undefined,
      type: typeFilter.value || undefined,
      city: cityFilter.value || undefined
    }
  }),
  {
    watch: [currentPage, locale]
  }
)

const partners = computed(() => data.value?.data || [])
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
