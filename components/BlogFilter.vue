<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
    <!-- Popular Tags (flat, one per group) -->
    <div v-if="!showAllTags" class="flex flex-wrap gap-2">
      <button
        v-for="tag in topTags"
        :key="tag.id"
        @click="toggleTag(tag.id)"
        :class="[
          'px-3 py-1.5 rounded-full text-sm font-medium transition-colors',
          isTagSelected(tag.id)
            ? 'text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        ]"
        :style="isTagSelected(tag.id) ? { background: 'var(--mc-jade)' } : {}"
      >
        {{ getTagName(tag.id) }}
      </button>
      <!-- Also show any selected tags not in topTags -->
      <button
        v-for="tagId in selectedNonTopTags"
        :key="tagId"
        @click="toggleTag(tagId)"
        class="px-3 py-1.5 rounded-full text-sm font-medium text-white transition-colors"
        style="background: var(--mc-jade);"
      >
        {{ getTagName(tagId) }}
      </button>
      <button
        @click="showAllTags = true"
        class="px-3 py-1.5 rounded-full text-xs transition-colors"
        style="color: var(--mc-jade);"
      >
        {{ t('blogFilter.showMore') }} ▾
      </button>
    </div>

    <!-- All Tags (grouped) -->
    <div v-else>
      <div v-for="(group, groupKey) in tagGroups" :key="groupKey" class="mb-4 last:mb-0">
        <label class="block text-xs font-medium text-gray-500 mb-1.5">{{ getGroupLabel(groupKey as string) }}</label>
        <div class="flex flex-wrap gap-1.5">
          <button
            v-for="tag in getGroupTags(groupKey as string)"
            :key="tag.id"
            @click="toggleTag(tag.id)"
            :class="[
              'px-2.5 py-1 rounded-full text-sm transition-colors',
              isTagSelected(tag.id)
                ? 'text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
            :style="isTagSelected(tag.id) ? { background: 'var(--mc-jade)' } : {}"
          >
            {{ getTagName(tag.id) }}
          </button>
        </div>
      </div>
      <button
        @click="showAllTags = false"
        class="mt-2 px-3 py-1.5 rounded-full text-xs transition-colors"
        style="color: var(--mc-jade);"
      >
        {{ t('blogFilter.showLess') }} ▴
      </button>
    </div>

    <!-- Search -->
    <div class="mt-4 pt-4 border-t border-gray-100">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('blogFilter.search') }}</label>
          <UInput
            v-model="filters.keyword"
            :placeholder="t('blogFilter.searchPlaceholder')"
            icon="i-heroicons-magnifying-glass"
            @keyup.enter="applyFilters"
          />
        </div>
      </div>
    </div>

    <!-- Selected filters & action buttons -->
    <div class="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-gray-100 mt-4">
      <!-- Selected tags -->
      <div class="flex flex-wrap items-center gap-2">
        <span v-if="selectedFiltersCount > 0" class="text-sm text-gray-500">{{ t('blogFilter.selected') }}:</span>
        <span
          v-for="tagId in filters.tags"
          :key="tagId"
          class="inline-flex items-center px-2 py-1 text-xs rounded-full"
          style="background: var(--mc-jade-pale); color: var(--mc-jade-dark);"
        >
          {{ getTagName(tagId) }}
          <button @click="toggleTag(tagId)" class="ml-1" style="color: var(--mc-jade);">
            <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </span>
        <span
          v-if="filters.keyword"
          class="inline-flex items-center px-2 py-1 text-xs rounded-full"
          style="background: var(--mc-jade-pale); color: var(--mc-jade-dark);"
        >
          {{ t('blogFilter.search') }}: {{ filters.keyword }}
          <button @click="filters.keyword = ''" class="ml-1" style="color: var(--mc-jade);">
            <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </span>
        <button
          v-if="selectedFiltersCount > 0"
          @click="clearAllFilters"
          class="text-sm text-gray-500 hover:text-gray-700 underline"
        >
          {{ t('blogFilter.clearAll') }}
        </button>
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-2">
        <UButton color="gray" variant="soft" @click="clearAllFilters">
          {{ t('blogFilter.reset') }}
        </UButton>
        <UButton color="primary" @click="applyFilters" :loading="loading">
          {{ t('blogFilter.applyFilters') }}
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import tagsDictionary from '~/config/tags.json'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface Tag {
  id: string
  name: string
  slug: string
  group: string
}

interface Filters {
  keyword: string
  tags: string[]
}

const props = defineProps<{
  modelValue: Filters
  loading?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Filters]
  'apply': [value: Filters]
}>()

// Local filter state
const filters = reactive<Filters>({
  keyword: props.modelValue.keyword || '',
  tags: [...(props.modelValue.tags || [])]
})

// Toggle between top-tags-only and full grouped view
const showAllTags = ref(false)

// Watch external changes
watch(() => props.modelValue, (newVal) => {
  filters.keyword = newVal.keyword || ''
  filters.tags = [...(newVal.tags || [])]
}, { deep: true })

// Get tag groups (exclude _label / _labelKey meta keys)
const tagGroups = computed(() => tagsDictionary.tag_groups)


// Get all tags for a specific group
const getGroupTags = (groupKey: string): Tag[] => {
  const group = tagsDictionary.tag_groups[groupKey as keyof typeof tagsDictionary.tag_groups]
  if (!group) return []
  return Object.entries(group)
    .filter(([key]) => !key.startsWith('_'))
    .map(([, value]) => value as Tag)
}

// Top tags: one per group (first from _popular array)
const topTags = computed(() => {
  const result: Tag[] = []
  for (const groupKey of Object.keys(tagsDictionary.tag_groups)) {
    const group = tagsDictionary.tag_groups[groupKey as keyof typeof tagsDictionary.tag_groups] as any
    const popularIds: string[] = group?._popular || []
    if (popularIds.length === 0) continue
    const topId = popularIds[0]
    const tag = group[topId]
    if (tag) result.push(tag as Tag)
  }
  return result
})

// Selected tags that are NOT in topTags
const selectedNonTopTags = computed(() => {
  const topIds = new Set(topTags.value.map(t => t.id))
  return filters.tags.filter(id => !topIds.has(id))
})

// Resolve tag name with i18n fallback
const getTagName = (tagId: string): string => {
  const i18nName = t(`tags.${tagId}`)
  return i18nName && !i18nName.startsWith('tags.')
    ? i18nName
    : tagId
}

// Get group label (use i18n key from _labelKey, fallback to _label, then key)
const getGroupLabel = (groupKey: string): string => {
  const group = tagsDictionary.tag_groups[groupKey as keyof typeof tagsDictionary.tag_groups] as any
  if (group?._labelKey) {
    const i18nLabel = t(group._labelKey)
    if (i18nLabel && !i18nLabel.startsWith('blogFilter.')) return i18nLabel
  }
  if (group?._label) return group._label
  return groupKey
}

// Toggle tag selection
const toggleTag = (tagId: string) => {
  const index = filters.tags.indexOf(tagId)
  if (index > -1) {
    filters.tags.splice(index, 1)
  } else {
    filters.tags.push(tagId)
  }
}

// Check if tag is selected
const isTagSelected = (tagId: string) => filters.tags.includes(tagId)

// Count selected filters
const selectedFiltersCount = computed(() => {
  let count = filters.tags.length
  if (filters.keyword) count++
  return count
})

// Clear all filters
const clearAllFilters = () => {
  filters.keyword = ''
  filters.tags = []
  emit('update:modelValue', { ...filters })
  emit('apply', { ...filters })
}

// Apply filters
const applyFilters = () => {
  emit('update:modelValue', { ...filters })
  emit('apply', { ...filters })
}
</script>
