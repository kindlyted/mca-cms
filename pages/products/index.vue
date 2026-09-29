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
            divider: { base: 'ubreadcrumb-divider' }
          }"
          divider="/"
        />
      </ClientOnly>

      <!-- Page Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">{{ t('pages.products.title') }}</h1>
        <p class="text-lg text-gray-600">{{ t('pages.products.description') }}</p>
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
              <label for="product-search" class="block text-sm font-medium text-gray-700 mb-1">{{ t('pages.products.search.label') }}</label>
              <input
                v-model="searchQuery"
                type="text"
                id="product-search"
                name="search"
                :placeholder="t('pages.products.search.placeholder')"
                class="w-full px-3 py-2 rounded-md border input-jade"
                @keyup.enter="applyFilters"
              />
            </div>
            <div>
              <label for="product-category" class="block text-sm font-medium text-gray-700 mb-1">{{ t('pages.products.filter.typeLabel') }}</label>
              <select
                v-model="categoryFilter"
                id="product-category"
                name="category"
                class="w-full px-3 py-2 rounded-md border input-jade"
                @change="applyFilters"
              >
                <option value="">{{ t('pages.products.filter.allTypes') }}</option>
                <option v-for="cat in categoryOptions" :key="cat.id" :value="cat.id">
                  {{ categoryLabel(cat.id) }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <!-- Stats -->
        <div class="flex items-center justify-between mb-6">
          <div class="text-sm text-gray-500">
            <span class="font-medium text-gray-900">{{ pagination.total }}</span> {{ t('pages.products.pagination.showing', { from: (pagination.page - 1) * pagination.pageSize + 1, to: Math.min(pagination.page * pagination.pageSize, pagination.total), total: pagination.total }) }}
          </div>
        </div>

        <!-- Product Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div
            v-for="product in products"
            :key="product.id"
            class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300 flex flex-col"
          >
            <div class="aspect-w-16 aspect-h-9">
              <img
                :src="product.image"
                :alt="product.title"
                class="w-full h-48 object-cover"
              />
            </div>
            <div class="p-6 flex flex-col flex-1">
              <h3 class="text-xl font-semibold text-gray-900 mb-2">
                <NuxtLink
                  :to="localePath(`/products/${product.slug || product.id}`)"
                  class="transition-colors hover:text-[var(--mc-jade)]"
                >
                  {{ product.title }}
                </NuxtLink>
              </h3>
              <p class="text-gray-600 text-sm mb-4 line-clamp-3 flex-1">
                {{ product.description }}
              </p>
              <div v-if="typeof product.price === 'number'" class="mb-4">
                <span class="text-2xl font-bold" style="color: var(--mc-jade-dark);">
                  {{ formatPrice(product.price, product.currency) }}
                </span>
                <span v-if="typeof product.compareAtPrice === 'number'" class="ml-2 text-lg line-through text-gray-400">
                  {{ formatPrice(product.compareAtPrice, product.currency) }}
                </span>
                <span
                  v-if="typeof product.compareAtPrice === 'number' && product.compareAtPrice > product.price"
                  class="ml-2 text-xs font-semibold px-1.5 py-0.5 rounded-full text-white"
                  style="background: var(--mc-amber);"
                >
                  {{ discountPercent(product.price, product.compareAtPrice) }}% OFF
                </span>
              </div>
              <NuxtLink
                :to="localePath(`/products/${product.slug || product.id}`)"
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
        <div v-if="products.length === 0" class="text-center py-12">
          <p class="text-gray-600">{{ t('pages.products.noResults') }}</p>
        </div>

        <!-- Pagination -->
        <div v-if="pagination.totalPages > 1" class="mt-12">
          <nav class="flex justify-center items-center space-x-2 flex-wrap gap-y-2">
            <button
              @click="changePage(1)"
              :disabled="pagination.page === 1"
              class="px-3 py-2 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              :title="t('pages.products.pagination.first')"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              </svg>
            </button>
            <button
              @click="changePage(pagination.page - 1)"
              :disabled="pagination.page === 1"
              class="px-3 py-2 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              {{ t('pages.products.pagination.previous') }}
            </button>
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
            <button
              @click="changePage(pagination.page + 1)"
              :disabled="pagination.page === pagination.totalPages"
              class="px-3 py-2 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              {{ t('pages.products.pagination.next') }}
            </button>
            <button
              @click="changePage(pagination.totalPages)"
              :disabled="pagination.page === pagination.totalPages"
              class="px-3 py-2 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              :title="t('pages.products.pagination.last')"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
            </button>
          </nav>

          <!-- Quick Jump -->
          <div class="flex justify-center items-center mt-4 gap-2 text-sm">
            <span class="text-gray-500">{{ t('pages.products.pagination.goTo') }}</span>
            <input
              v-model.number="jumpPage"
              type="number"
              min="1"
              :max="pagination.totalPages"
              class="w-16 px-2 py-1 border border-gray-300 rounded-md text-center input-jade"
              @keyup.enter="handleJumpPage"
            />
            <span class="text-gray-500">{{ t('pages.products.pagination.page') }}</span>
            <button
              @click="handleJumpPage"
              class="px-3 py-1 text-white rounded-md btn-jade-solid"
            >
              {{ t('pages.products.pagination.go') }}
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
import { usePageHreflangs } from '~/composables/usePageHreflangs'
import { useOrganizationSchema } from '~/composables/useOrganizationSchema'
import { useI18n } from 'vue-i18n'
import { useLocalePath } from '#imports'

definePageMeta({
  title: 'Products'
})

const { t, locale } = useI18n()
const localePath = useLocalePath()
const runtimeConfig = useRuntimeConfig()
const siteUrl = runtimeConfig.public.siteUrl || companyInfo.siteUrl

const canonicalUrl = computed(() => {
  const prefix = locale.value === 'en' ? '' : `/${locale.value}`
  return `${siteUrl}${prefix}/products`
})

const { hreflangLinks } = usePageHreflangs('/products')

useSeoMeta({
  title: t('pages.products.title'),
  description: t('pages.products.description'),
  keywords: '',
  ogTitle: t('pages.products.title'),
  ogDescription: t('pages.products.description'),
  ogImage: `${siteUrl}/images/hero-bg.webp`,
  ogType: 'website',
  ogSiteName: companyInfo.shortName,
  ogUrl: canonicalUrl,
  twitterCard: 'summary_large_image',
  twitterTitle: t('pages.products.title'),
  twitterDescription: t('pages.products.description'),
  twitterImage: `${siteUrl}/images/hero-bg.webp`
})

// Organization Schema - Products listing page
const organizationSchema = useOrganizationSchema('product')
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
          { '@type': 'ListItem', position: 1, name: t('nav.home'), item: `${canonicalUrl.value.replace(/\/products$/, '')}/` },
          { '@type': 'ListItem', position: 2, name: t('nav.products'), item: canonicalUrl.value }
        ]
      })
    },
    {
      type: 'application/ld+json',
      innerHTML: () => JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        name: t('pages.products.title'),
        description: t('pages.products.description'),
        url: canonicalUrl.value
      })
    }
  ],
  link: [
    { rel: 'canonical', href: canonicalUrl },
    ...hreflangLinks.value
  ]
})

const { links } = useBreadcrumb()

interface Product {
  id: string
  slug?: string
  title: string
  description: string
  image: string
  category: string
  price?: number
  compareAtPrice?: number
  currency?: string
}

interface ApiResponse {
  success: boolean
  data: Product[]
  pagination: {
    page: number
    pageSize: number
    total: number
    totalPages: number
  }
}

const searchQuery = ref('')

// 支持 ?category= 查询参数（首页分类横幅跳转）
const routeCategory = useRoute().query.category as string | undefined
const categoryFilter = ref(routeCategory || '')
const currentPage = ref(1)

// 动态分类选项（来自 /api/products/filters，按 data/products/{category} 子目录）
const categoryOptions = ref<Array<{ id: string; count: number }>>([])

async function loadFilters() {
  try {
    const res = await $fetch<{ success: boolean; data: { categories: Array<{ id: string; count: number }> } }>('/api/products/filters', {
      params: { lang: locale.value }
    })
    categoryOptions.value = res.data.categories || []
  } catch {
    categoryOptions.value = []
  }
}

function categoryLabel(id: string): string {
  // 分类目录名可能是 slug（如 "exercise-mats"），这里做可读化展示
  const pretty = id.replace(/[-_]/g, ' ')
  return pretty.charAt(0).toUpperCase() + pretty.slice(1)
}

onMounted(loadFilters)
const pageSize = 12
const loading = ref(false)
const error = ref('')
const jumpPage = ref(1)

const cacheKey = computed(() => `products-${currentPage.value}-${searchQuery.value}-${categoryFilter.value}-${locale.value}`)

const { data, refresh, pending } = await useAsyncData<ApiResponse>(
  () => cacheKey.value,
  () => $fetch<ApiResponse>('/api/products', {
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

const products = computed(() => data.value?.data || [])
const pagination = computed(() => data.value?.pagination || { page: 1, pageSize, total: 0, totalPages: 1 })

const itemListSchema = computed(() => {
  const prefix = locale.value === 'en' ? '' : `/${locale.value}`
  return {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: t('pages.products.title'),
    url: canonicalUrl.value,
    numberOfItems: pagination.value.total,
    itemListElement: products.value.map((item: Product, index: number) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.title,
      url: `${siteUrl}${prefix}/products/${item.slug || item.id}`
    }))
  }
})

useHead({
  script: [
    {
      type: 'application/ld+json',
      innerHTML: () => JSON.stringify(itemListSchema.value)
    }
  ]
})

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
    if (current > 4) pages.push('...')
    const start = Math.max(2, current - 2)
    const end = Math.min(total - 1, current + 2)
    for (let i = start; i <= end; i++) pages.push(i)
    if (current < total - 3) pages.push('...')
    pages.push(total)
  }
  return pages
})

const formatPrice = (value: number, currency?: string) => {
  const symbol = currency === 'EUR' ? '€' : currency === 'GBP' ? '£' : '$'
  return `${symbol}${Number(value).toFixed(2)}`
}

const discountPercent = (price: number, compareAt: number) => {
  if (!compareAt || compareAt <= price) return 0
  return Math.round((1 - price / compareAt) * 100)
}

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
  if (process.client) window.scrollTo({ top: 0, behavior: 'smooth' })
}

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
  if (process.client) window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleJumpPage = () => {
  let page = parseInt(String(jumpPage.value))
  if (isNaN(page)) return
  page = Math.max(1, Math.min(page, pagination.value.totalPages))
  changePage(page)
}
</script>
