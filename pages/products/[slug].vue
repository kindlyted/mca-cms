<template>
  <ProductDetailLayout
    :loading="loading"
    :error="error"
    :entity="product"
    :links="links"
    entity-type="product"
  >
    <template #buyBox>
      <!-- 价格 -->
      <div class="flex flex-wrap items-center gap-3 mb-3">
        <span class="text-4xl font-bold" style="color: var(--mc-jade-dark);">{{ formatPrice(currentPrice, product?.currency) }}</span>
        <span v-if="currentCompareAtPrice" class="text-xl line-through" style="color: var(--mc-ink-faint);">{{ formatPrice(currentCompareAtPrice, product?.currency) }}</span>
      </div>
      <p class="text-sm mb-4" :style="{ color: product?.inStock === false ? 'var(--mc-amber)' : 'var(--mc-jade-dark)' }">
        {{ product?.inStock === false ? t('pages.products.detail.outOfStock') : t('pages.products.detail.inStock') }}
      </p>

      <!-- 卖点短句 -->
      <ul v-if="buyPoints.length > 0" class="mb-6 space-y-2">
        <li v-for="(point, idx) in buyPoints" :key="idx" class="flex items-start text-sm" style="color: var(--mc-ink-soft);">
          <span class="flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center mr-2 text-xs text-white" style="background: var(--mc-jade);">&#10003;</span>
          <span><strong style="color: var(--mc-ink);">{{ point.label }}:</strong> {{ point.value }}</span>
        </li>
      </ul>

      <!-- 尺寸选择 -->
      <div v-if="sizes.length > 0" class="mb-4">
        <p class="text-sm font-medium mb-2" style="color: var(--mc-ink-soft);">{{ t('pages.products.detail.sizeVariant') }}</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="size in sizes"
            :key="size.label"
            type="button"
            @click="selectedSize = size"
            class="px-3 py-1.5 rounded-lg border text-sm font-medium transition-all"
            :style="selectedSize?.label === size.label
              ? { background: 'var(--mc-jade)', borderColor: 'var(--mc-jade)', color: 'white' }
              : { background: 'var(--mc-surface-raised)', borderColor: 'var(--mc-border)', color: 'var(--mc-ink)' }"
          >
            {{ size.label }}
            <span v-if="size.price" class="ml-1">— {{ formatPrice(size.price, product?.currency) }}</span>
          </button>
        </div>
      </div>

      <!-- 颜色选择 -->
      <div v-if="colors.length > 0" class="mb-4">
        <p class="text-sm font-medium mb-2" style="color: var(--mc-ink-soft);">{{ t('pages.products.detail.selectColor') }}</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="c in colors"
            :key="c"
            type="button"
            @click="selectedColor = c"
            class="px-3 py-1.5 rounded-lg border text-sm font-medium transition-all"
            :style="selectedColor === c
              ? { borderColor: 'var(--mc-jade)', boxShadow: '0 0 0 2px var(--mc-jade)', color: 'var(--mc-ink)' }
              : { borderColor: 'var(--mc-border)', color: 'var(--mc-ink)' }"
          >
            {{ c }}
          </button>
        </div>
      </div>

      <!-- CTA -->
      <div class="mt-4">
        <UButton
          :to="localePath('/contact')"
          size="xl"
          class="w-full font-semibold"
          :style="{ background: 'var(--mc-jade)', color: 'white' }"
        >
          {{ t('common.contactUs') }}
        </UButton>
      </div>
    </template>

    <template #related>
      <div v-if="relatedProducts.length > 0" class="mb-10">
        <h2 class="text-2xl font-bold mb-6" style="color: var(--mc-ink);">{{ t('pages.products.detail.related') }}</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="related in relatedProducts"
            :key="related.id"
            class="rounded-2xl overflow-hidden border hover:shadow-lg transition-all duration-300"
            :style="{ background: 'var(--mc-surface-raised)', borderColor: 'var(--mc-border)' }"
          >
            <NuxtLink :to="localePath(`/products/${related.slug || related.id}`)" class="block">
              <img
                :src="related.coverImage || '/images/hero-bg.webp'"
                :alt="related.title"
                class="w-full aspect-square object-cover"
                loading="lazy"
              />
            </NuxtLink>
            <div class="p-5">
              <h3 class="font-semibold mb-1" style="color: var(--mc-ink);">
                <NuxtLink :to="localePath(`/products/${related.slug || related.id}`)" class="hover:underline">
                  {{ related.title }}
                </NuxtLink>
              </h3>
              <p class="text-sm mb-3 line-clamp-2" style="color: var(--mc-ink-muted);">{{ related.excerpt }}</p>
              <NuxtLink
                :to="localePath(`/products/${related.slug || related.id}`)"
                class="inline-flex items-center font-medium text-sm"
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
      </div>
    </template>
  </ProductDetailLayout>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 2;
}
</style>

<script setup lang="ts">
import { useBreadcrumb } from '~/composables/useBreadcrumb'
import { useOrganizationSchema } from '~/composables/useOrganizationSchema'
import { useEntitySeo } from '~/composables/useEntitySeo'
import { useI18n } from 'vue-i18n'
import { useLocalePath } from '#imports'

const localePath = useLocalePath()
const route = useRoute()
const productSlug = route.params.slug as string
const { t, locale } = useI18n({ useScope: 'global' })
const runtimeConfig = useRuntimeConfig()
const siteUrl = runtimeConfig.public.siteUrl || companyInfo.siteUrl

const relatedProducts = ref<any[]>([])
const selectedSize = ref<any>(null)
const selectedColor = ref('')

const sizes = computed<{ label: string; price: number; compareAtPrice?: number }[]>(
  () => product.value?.sizes || []
)
const colors = computed<string[]>(() => product.value?.colors || [])

const currentPrice = computed(() => {
  if (sizes.value.length > 0 && selectedSize.value) return selectedSize.value.price
  return product.value?.price || 0
})
const currentCompareAtPrice = computed(() => {
  if (sizes.value.length > 0 && selectedSize.value) return selectedSize.value.compareAtPrice
  return product.value?.compareAtPrice
})

const buyPoints = computed(() =>
  (product.value?.highlights || [])
    .filter((h: any) => h.label !== 'Category')
    .map((h: any) => ({ label: h.label, value: h.value }))
)

const { links: rawLinks } = useBreadcrumb()

const links = computed(() =>
  rawLinks.value
    .filter((link): link is { label: string; to?: string } => Boolean(link.label))
)

const buildProductUrl = (slug: string, lang: string): string => {
  const prefix = lang === 'en' ? '' : `/${lang}`
  return `${siteUrl}${prefix}/products/${slug}`
}

const buildProductIndexUrl = (lang: string): string => {
  const prefix = lang === 'en' ? '' : `/${lang}`
  return `${siteUrl}${prefix}/products`
}

const normalizeProduct = (data: any): any => {
  if (!data) return data
  return {
    ...data,
    body: typeof data.body === 'string' ? data.body : data.body?.content || '',
    description: data.description || '',
    introduction: data.introduction || '',
    comparison: data.comparison || null,
    faq: (data.faq || []).map((item: any) => ({
      q: item.q || item.question || '',
      a: item.a || item.answer || ''
    })),
    cover: data.cover || data.visuals?.cover || { url: '', alt: '' },
    sizes: data.sizes || []
  }
}

const formatPrice = (value: number, currency?: string) => {
  if (value == null) return ''
  const symbol = currency === 'EUR' ? '€' : currency === 'GBP' ? '£' : '$'
  return `${symbol}${Number(value).toFixed(2)}`
}

const buildProductOffers = (price: number, productUrl: string, validUntil: Date, productData: any): Record<string, any> => {
  const inclusions = (productData.pricing?.inclusions || productData.geo?.keyFacts || [])
    .map((i: any) => typeof i === 'string' ? i : (i?.label || ''))
    .filter(Boolean)
  const hasFreeShipping = inclusions.some((s: string) => /free.*shipping/i.test(s))
  const returnMatch = inclusions
    .map((s: string) => s.match(/(\d+)[-\s]*(day|month)/i))
    .find(Boolean)

  const offers: Record<string, any> = {
    '@type': 'Offer',
    priceCurrency: productData.currency || 'USD',
    price,
    url: productUrl,
    availability: productData.inStock === false ? 'https://schema.org/OutOfStock' : 'https://schema.org/InStock',
    itemCondition: 'https://schema.org/NewCondition',
    priceValidUntil: validUntil.toISOString(),
    seller: { '@type': 'Organization', name: companyInfo.shortName, url: siteUrl }
  }

  offers.shippingDetails = {
    '@type': 'OfferShippingDetails',
    ...(hasFreeShipping ? {
      shippingRate: { '@type': 'MonetaryAmount', value: 0, currency: productData.currency || 'USD' }
    } : {}),
    shippingDestination: { '@type': 'DefinedRegion', addressCountry: 'US' }
  }
  offers.shippingDetails.deliveryTime = {
    '@type': 'ShippingDeliveryTime',
    handlingTime: { '@type': 'QuantitativeValue', minValue: 1, maxValue: 3, unitCode: 'DAY' },
    transitTime: { '@type': 'QuantitativeValue', minValue: 3, maxValue: 5, unitCode: 'DAY' }
  }

  const returnDays = returnMatch ? Number(returnMatch[1]) : 60
  const returnUnit = returnMatch ? returnMatch[2] : 'day'
  offers.hasMerchantReturnPolicy = {
    '@type': 'MerchantReturnPolicy',
    merchantReturnDays: returnUnit === 'month' ? returnDays * 30 : returnDays,
    returnMethod: 'https://schema.org/ReturnByMail',
    returnPolicyCategory: 'https://schema.org/MerchantReturnFiniteReturnWindow',
    applicableCountry: 'US'
  }

  offers.validFrom = new Date().toISOString()

  return offers
}

const generateProductStructuredData = (productData: any, currentLocale: string): Record<string, any>[] => {
  const schemas: Record<string, any>[] = []
  const title = productData.seo?.title || productData.overview?.title
  const description = productData.seo?.description || productData.overview?.excerpt
  const productUrl = buildProductUrl(productData.meta?.slug || productSlug, currentLocale)

  schemas.push(useOrganizationSchema('product'))
  schemas.push({
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: t('nav.home'), item: `${siteUrl}/` },
      { '@type': 'ListItem', position: 2, name: t('nav.products'), item: buildProductIndexUrl(currentLocale) },
      { '@type': 'ListItem', position: 3, name: title, item: productUrl }
    ]
  })

  const coverUrl = productData.cover?.url || productData.visuals?.cover?.url
  const price = productData.sizes?.length > 0 && productData.sizes[0] ? productData.sizes[0].price : productData.price

  if (typeof price === 'number') {
    const absoluteImage = coverUrl && !/^https?:\/\//.test(coverUrl) ? `${siteUrl}${coverUrl}` : coverUrl
    const validUntil = new Date()
    validUntil.setFullYear(validUntil.getFullYear() + 1)

    const productSchema: Record<string, any> = {
      '@context': 'https://schema.org',
      '@type': 'Product',
      name: title,
      description,
      url: productUrl,
      image: absoluteImage,
      sku: productData.meta?.id || productData.meta?.slug || productSlug,
      identifierExists: false,
      brand: { '@type': 'Brand', name: productData.brand || productData.meta?.brand || companyInfo.shortName },
      offers: buildProductOffers(price, productUrl, validUntil, productData)
    }

    if (Array.isArray(productData.specs) && productData.specs.length > 0) {
      productSchema.additionalProperty = productData.specs
        .filter((s: any) => s?.label && s?.value)
        .map((s: any) => ({
          '@type': 'PropertyValue',
          name: s.label,
          value: s.value
        }))
    }

    schemas.push(productSchema)
  }

  if (productData.faq && productData.faq.length > 0) {
    schemas.push({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: productData.faq.map((item: { q?: string; question?: string; a?: string; answer?: string }) => ({
        '@type': 'Question',
        name: item.q || item.question,
        acceptedAnswer: { '@type': 'Answer', text: item.a || item.answer }
      }))
    })
  }

  return schemas
}

const fetchProduct = async (): Promise<any> => {
  const response: any = await $fetch(`/api/products/${productSlug}`, {
    params: { lang: locale.value }
  })
  if (response.success && response.data) return response.data
  throw new Error('Product not found')
}

const { data: productData, pending: loading, error: fetchError } = await useAsyncData<any>(
  `product-${productSlug}`,
  fetchProduct,
  { server: true, default: () => null }
)

const product = computed(() => normalizeProduct(productData.value))
const error = computed(() => {
  if (!fetchError.value) return ''
  if ((fetchError.value as any).statusCode === 404) return ''
  return (fetchError.value as any).message || 'Failed to load product details'
})

watch(() => [product.value?.sizes, product.value?.colors] as any, ([s, c]) => {
  if (s?.length && !selectedSize.value) selectedSize.value = s[0]
  if (c?.length && !selectedColor.value) selectedColor.value = c[0]
}, { immediate: true })

const { applySeo } = useEntitySeo(product, 'product')

watchEffect(() => {
  if (fetchError.value && (fetchError.value as any).statusCode === 404) {
    throw createError({ statusCode: 404, statusMessage: 'Product not found' })
  }
})

const fetchRelatedProducts = async () => {
  try {
    const response: any = await $fetch('/api/related', {
      params: { entityType: 'product', slug: productSlug, lang: locale.value }
    })
    if (response.success) {
      relatedProducts.value = (response.relatedProducts || [])
        .filter((p: any) => (p.slug || p.id) !== productSlug)
        .slice(0, 6)
    }
  } catch (err) {
    console.error('Error fetching related products:', err)
  }
}

watch(productData, (rawData) => {
  if (!rawData) return
  const newData = normalizeProduct(rawData)
  const title = newData.seo?.title || newData.overview?.title
  const description = newData.seo?.description || newData.overview?.excerpt
  const rawKw = newData.seo?.keywords
  const keywords = (Array.isArray(rawKw) ? rawKw.join(', ') : (rawKw || ''))
  const rawCoverUrl = newData.cover?.url || '/images/hero-bg.webp'
  const coverUrl = rawCoverUrl.startsWith('http') ? rawCoverUrl : `${siteUrl}${rawCoverUrl}`

  route.meta.title = title
  route.meta.breadcrumb = [
    { label: t('nav.home'), to: localePath('/') },
    { label: t('nav.products'), to: localePath('/products') },
    { label: title }
  ]

  const seoPrice = (newData.sizes?.length > 0 && newData.sizes[0]?.price != null)
    ? newData.sizes[0].price
    : newData.price

  applySeo({
    title,
    description,
    keywords,
    image: coverUrl,
    price: typeof seoPrice === 'number' ? seoPrice : undefined,
    currency: newData.currency || 'USD'
  })

  const schemas = generateProductStructuredData(newData, locale.value)
  if (schemas.length > 0) {
    useHead({
      script: schemas.map(schema => ({
        type: 'application/ld+json',
        innerHTML: JSON.stringify(schema)
      }))
    })
  }

  fetchRelatedProducts()
}, { immediate: true })
</script>
