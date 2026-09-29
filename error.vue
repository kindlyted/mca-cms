<template>
  <div class="min-h-[calc(100vh-80px)] flex items-center justify-center px-4 py-12 mt-20" style="background: var(--mc-jade-faint);">
    <div class="max-w-2xl w-full text-center">
      <div class="mb-8">
        <div class="relative inline-block">
          <svg class="w-32 h-32" style="color: var(--mc-jade-pale);" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-6xl font-bold" style="color: var(--mc-jade);">{{ error?.statusCode || 404 }}</span>
          </div>
        </div>
      </div>

      <h1 class="text-3xl font-bold mb-4" style="color: var(--mc-ink);">
        {{ is404 ? t('error.notFound.title') : t('error.serverError.title') }}
      </h1>
      <p class="text-lg mb-8" style="color: var(--mc-ink-muted);">
        {{ is404 ? t('error.notFound.description') : t('error.serverError.description') }}
      </p>

      <div class="flex flex-col sm:flex-row gap-4 justify-center mb-12">
        <NuxtLink
          :to="localePath('/')"
          class="btn btn-primary px-6 py-3 text-sm"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          {{ is404 ? t('error.notFound.backHome') : t('error.serverError.backHome') }}
        </NuxtLink>
        <NuxtLink
          v-if="is404"
          :to="localePath('/blogs')"
          class="btn btn-outline px-6 py-3 text-sm"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
          </svg>
          {{ t('error.notFound.browseContent') }}
        </NuxtLink>
        <button
          v-else
          @click="handleError"
          class="btn btn-outline px-6 py-3 text-sm"
        >
          {{ t('error.serverError.retry') }}
        </button>
      </div>

      <div v-if="is404" class="rounded-xl p-6 border" :style="{ background: 'var(--mc-surface-raised)', borderColor: 'var(--mc-border)' }">
        <h2 class="text-lg font-semibold mb-4" style="color: var(--mc-ink);">{{ t('error.notFound.popularContent') }}</h2>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <NuxtLink
            v-for="link in popularLinks"
            :key="link.to"
            :to="link.to"
            class="flex flex-col items-center p-4 rounded-lg card-hover group"
            :style="{ background: 'var(--mc-surface)', borderColor: 'var(--mc-border)' }"
          >
            <svg class="h-8 w-8 mb-2 group-hover:scale-110 transition-transform" style="color: var(--mc-jade);" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="link.icon" />
            </svg>
            <span class="text-sm" style="color: var(--mc-ink-soft);">{{ link.label }}</span>
          </NuxtLink>
        </div>
      </div>

      <p class="mt-8 text-sm" style="color: var(--mc-ink-faint);">
        {{ t('error.notFound.needHelp') }}
        <NuxtLink :to="localePath('/contact')" class="underline" style="color: var(--mc-jade);">
          {{ t('error.notFound.contactUs') }}
        </NuxtLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useLocalePath } from '#imports'

const props = defineProps({
  error: {
    type: Object,
    default: () => ({})
  }
})

const { t } = useI18n({ useScope: 'global' })
const localePath = useLocalePath()

const is404 = computed(() => props.error?.statusCode === 404)

useSeoMeta({
  title: is404.value
    ? t('error.notFound.title')
    : t('error.serverError.title'),
  description: is404.value
    ? t('error.notFound.description')
    : t('error.serverError.description'),
  robots: is404.value ? 'follow' : 'noindex, follow'
})

const popularLinks = computed(() => [
  {
    to: localePath('/services'),
    label: t('nav.services'),
    icon: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z'
  },
  {
    to: localePath('/partners'),
    label: t('nav.partners'),
    icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4'
  },
  {
    to: localePath('/blogs'),
    label: t('nav.stories'),
    icon: 'M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z'
  },
  {
    to: localePath('/contact'),
    label: t('nav.contact'),
    icon: 'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z'
  }
])

const handleError = () => clearError({ redirect: '/' })
</script>
