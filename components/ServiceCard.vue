<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
    <!-- Card Image -->
    <div v-if="service.cardImage" class="h-48 bg-gray-100 overflow-hidden">
      <img 
        :src="service.cardImage" 
        :alt="service.overview.title"
        width="640" height="400"
        class="w-full h-full object-cover"
        loading="lazy"
      />
    </div>
    <div class="p-6">
      <h3 class="text-xl font-semibold text-gray-900 mb-3">{{ service.overview.title }}</h3>
      <div class="rounded-full inline-block px-4 py-1 text-sm font-medium mb-4" style="background: var(--mc-jade-pale); color: var(--mc-jade-dark);">
        {{ service.meta?.investment || 'Contact for Pricing' }}
      </div>
      <ul class="space-y-2 mb-6">
        <li v-for="(feature, index) in features" :key="index" class="flex items-start space-x-2">
          <svg class="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span class="text-gray-600 text-sm">{{ feature }}</span>
        </li>
      </ul>
      <NuxtLink 
        :to="`/services/${service.id}`" 
        class="inline-flex items-center font-medium text-sm" style="color: var(--mc-jade);"
      >
        Learn More
        <svg class="ml-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
interface Service {
  id: string
  overview: {
    title: string
    description: string
  }
  cardImage?: string
  meta?: {
    investment: string
    tags?: Array<{
      id: string
      name: string
      slug: string
    }>
  }
  conditions?: {
    items?: Array<{
      key: string
      value: string
    }>
  }
}

const props = defineProps<{
  service: Service
}>()

// Extract features from JSON tags
const features = computed(() => {
  const defaultFeatures = ["Professional Consultation", "One-on-One Guidance", "High Success Rate"]
  
  // 优先使用meta中的tags
  if (props.service.meta?.tags && props.service.meta.tags.length > 0) {
    return props.service.meta.tags.slice(0, 3).map(tag => tag.name)
  }
  
  // 如果没有tags，从conditions中提取一些关键信息作为features
  if (props.service.conditions?.items) {
    const conditionFeatures = props.service.conditions.items
      .filter(item => item.value.length < 20)
      .map(item => item.value)
    
    return [...defaultFeatures, ...conditionFeatures].slice(0, 3)
  }
  
  return defaultFeatures
})
</script>