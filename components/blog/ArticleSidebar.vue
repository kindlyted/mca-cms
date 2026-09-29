<template>
  <aside class="space-y-6">
    <!-- Loading State -->
    <div v-if="loading" class="bg-white rounded-lg shadow-sm p-6">
      <div class="animate-pulse space-y-4">
        <div class="h-4 bg-gray-200 rounded w-1/2"></div>
        <div class="h-20 bg-gray-200 rounded"></div>
        <div class="h-20 bg-gray-200 rounded"></div>
      </div>
    </div>

    <template v-else-if="recommendations">
      <!-- Related Articles -->
      <div v-if="recommendations.relatedArticles?.length" class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center mb-4">
          <svg class="h-5 w-5 text-gray-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 class="text-lg font-semibold text-gray-900">Related Articles</h3>
        </div>
        <div class="space-y-4">
          <NuxtLink
            v-for="article in recommendations.relatedArticles"
            :key="article.id"
            :to="article.link"
            class="flex items-start group"
          >
            <img
              v-if="article.coverImage"
              :src="article.coverImage"
              :alt="article.title"
              width="80" height="56"
              class="w-20 h-14 object-cover rounded flex-shrink-0"
              loading="lazy"
            />
            <div v-else class="w-20 h-14 bg-gray-100 rounded flex-shrink-0 flex items-center justify-center">
              <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="ml-3 flex-1 min-w-0">
              <h4 class="text-sm font-medium text-gray-900 group-hover:text-blue-600 line-clamp-2">
                {{ article.title }}
              </h4>
              <p class="text-xs text-gray-500 mt-1">{{ formatDate(article.publishedAt) }}</p>
            </div>
          </NuxtLink>
        </div>
      </div>

      <!-- Popular Articles -->
      <div v-if="recommendations.hotArticles?.length" class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center mb-4">
          <svg class="h-5 w-5 text-orange-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clip-rule="evenodd" />
          </svg>
          <h3 class="text-lg font-semibold text-gray-900">Trending Now</h3>
        </div>
        <div class="space-y-3">
          <NuxtLink
            v-for="(article, index) in recommendations.hotArticles"
            :key="article.id"
            :to="article.link"
            class="flex items-center group"
          >
            <span
              class="w-6 h-6 rounded flex items-center justify-center text-sm font-bold flex-shrink-0"
              :class="index < 3 ? 'bg-orange-100 text-orange-600' : 'bg-gray-100 text-gray-500'"
            >
              {{ index + 1 }}
            </span>
            <h4 class="ml-3 text-sm text-gray-700 group-hover:text-blue-600 line-clamp-1 flex-1">
              {{ article.title }}
            </h4>
          </NuxtLink>
        </div>
      </div>

    </template>
  </aside>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

interface ArticleItem {
  id: string
  title: string
  excerpt?: string
  coverImage?: string
  publishedAt: string
  link: string
  views?: number
}

interface Recommendations {
  relatedArticles: ArticleItem[]
  hotArticles: ArticleItem[]
}

const props = defineProps<{
  articleSlug: string
}>()

const { locale } = useI18n()
const loading = ref(true)
const recommendations = ref<Recommendations | null>(null)

const fetchRecommendations = async () => {
  loading.value = true
  try {
    const response = await $fetch<{
      success: boolean
      analysis: {
        detectedCountries: string[]
        detectedTopics: string[]
        recommendationTypes: string[]
      }
      recommendations: Recommendations
    }>(`/api/blogs/${props.articleSlug}/recommendations`, {
      params: {
        lang: locale.value
      }
    })

    if (response.success) {
      recommendations.value = response.recommendations
    }
  } catch (error) {
    console.error('Failed to fetch recommendations:', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
}

// 组件挂载时获取推荐
onMounted(() => {
  fetchRecommendations()
})

// 文章ID变化时重新获取
watch(() => props.articleSlug, () => {
  fetchRecommendations()
})

defineExpose({ recommendations, loading })
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
