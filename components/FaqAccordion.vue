<template>
  <div v-if="items && items.length > 0" class="mb-8">
    <h2 class="text-2xl font-bold text-gray-900 mb-6">{{ title }}</h2>
    <div class="divide-y divide-gray-200 rounded-lg border border-gray-200 bg-white">
      <div
        v-for="(item, index) in items"
        :key="index"
        class="faq-item"
      >
        <button
          type="button"
          class="flex w-full items-center justify-between px-6 py-4 text-left hover:bg-gray-50 transition-colors"
          @click="toggle(index)"
        >
          <span class="text-base font-semibold text-gray-900 pr-4">{{ item.question }}</span>
          <svg
            class="h-5 w-5 flex-shrink-0 text-gray-500 transition-transform duration-200"
            :class="{ 'rotate-180': openIndex === index }"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        <div
          v-show="openIndex === index"
          class="px-6 pb-4 text-sm text-gray-600 leading-relaxed"
        >
          {{ item.answer }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface FaqItem {
  question: string
  answer: string
}

withDefaults(defineProps<{
  items?: FaqItem[]
  title?: string
}>(), {
  title: 'Frequently Asked Questions'
})

const openIndex = ref<number | null>(null)

const toggle = (index: number) => {
  openIndex.value = openIndex.value === index ? null : index
}
</script>
