<template>
    <header
      ref="headerEl"
      class="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-b transition-shadow duration-500"
      :class="scrolled ? 'shadow-sm border-[var(--mc-jade-pale)]' : 'border-transparent'"
    >
    <div class="max-w-7xl mx-auto px-4 lg:px-8">
      <div class="flex h-20 items-center justify-between">
        <div class="flex items-center">
          <NuxtLink to="/" class="flex items-center space-x-3">
            <img 
              src="/images/logo/logo.png" 
              :alt="companyInfo.shortName" 
              width="168" height="56"
              class="h-14 w-auto sm:h-16"
            />
          </NuxtLink>
        </div>

        <nav class="hidden md:flex items-center gap-1 ml-8">
          <NuxtLink
            v-for="item in navItems"
            :key="item.to"
            :to="localePath(item.to)"
            class="px-4 py-2 text-sm font-medium rounded-lg transition-all duration-300"
            :class="[
              isMounted && isActive(item.to)
                ? 'text-white shadow-md'
                : 'hover:text-white hover:bg-[var(--mc-jade)]'
            ]"
            :style="isMounted && isActive(item.to)
              ? { backgroundColor: 'var(--mc-jade)' }
              : { color: 'var(--mc-ink)' }"
            >
            {{ t(item.labelKey) }}
          </NuxtLink>
          <div class="ml-4">
            <select
              :value="locale"
              @change="onLocaleChange($event)"
              class="px-3 py-2 rounded-lg text-sm transition-all duration-200 border bg-white focus:ring-2 focus:ring-[var(--mc-jade)]"
              style="color: var(--mc-ink); border-color: var(--mc-border-strong);"
            >
              <option v-for="l in availableLocales" :key="l" :value="l" class="text-[var(--mc-ink-soft)] bg-white">
                {{ localeLabels[l] || l }}
              </option>
            </select>
          </div>
        </nav>

        <div class="md:hidden">
          <button 
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            class="p-2 rounded-lg transition-all duration-200 hover:bg-[var(--mc-jade-faint)]"
            style="color: var(--mc-ink);"
          >
            <svg v-if="!isMobileMenuOpen" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg v-else class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="isMobileMenuOpen"
      class="md:hidden border-t bg-white/95 backdrop-blur-md"
      :class="scrolled ? 'border-[var(--mc-jade-pale)]' : 'border-white/10'"
    >
      <div class="px-4 py-3 space-y-1">
        <NuxtLink
          v-for="item in navItems"
          :key="item.to"
          :to="localePath(item.to)"
            class="block px-4 py-3 text-base font-medium rounded-lg transition-all duration-300"
              :class="isMounted && isActive(item.to)
                ? 'text-white shadow-md'
                : 'hover:text-white hover:bg-[var(--mc-jade)]'"
              :style="isMounted && isActive(item.to)
                ? { backgroundColor: 'var(--mc-jade)' }
                : { color: 'var(--mc-ink)' }"
          @click="isMobileMenuOpen = false"
        >
          {{ t(item.labelKey) }}
        </NuxtLink>
        <div class="px-4 py-3">
          <select
            :value="locale"
            @change="onLocaleChange($event)"
            class="w-full px-3 py-2 rounded-lg border bg-white text-sm focus:outline-none focus:ring-2 focus:ring-[var(--mc-jade)]" style="color: var(--mc-ink); border-color: var(--mc-border-strong);"
          >
            <option v-for="l in availableLocales" :key="l" :value="l">
              {{ localeLabels[l] || l }}
            </option>
          </select>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { navigateTo, useLocalePath, useSwitchLocalePath, useRoute } from '#imports'
import siteConfig from '../site.config.json'

const isMounted = ref(false)
const isMobileMenuOpen = ref(false)
const scrolled = ref(true)
const headerEl = ref<HTMLElement | null>(null)
const route = useRoute()
const { t, locale, availableLocales } = useI18n({ useScope: 'global' })
const localePath = useLocalePath()
const switchLocalePath = useSwitchLocalePath()
const localeLabels: Record<string, string> = {
  en: 'English',
  fr: 'Français',
  de: 'Deutsch',
  es: 'Español'
}

const navItems = computed(() => {
  const items = siteConfig.nav?.items ?? []
  return items.filter((item: any) => item.enabled !== false)
})

const currentSlug = computed(() => {
  return (route.params.slug as string) || (route.params.id as string) || ''
})

const currentCategory = computed(() => {
  const path = route.path
  if (path.includes('/services')) return 'services'
  if (path.includes('/partners')) return 'partners'
  if (path.includes('/blogs') || path.includes('/blog')) return 'blogs'
  return ''
})

const isDetailPage = computed(() => {
  return !!currentSlug.value && !!currentCategory.value
})

function isActive(path: string): boolean {
  const fullPath = localePath(path)
  if (path === '/') {
    return route.path === '/' || route.path === fullPath
  }
  return route.path.startsWith(fullPath)
}

const onLocaleChange = async (event: Event) => {
  const target = event.target as HTMLSelectElement
  const newLocale = target.value as 'en' | 'fr' | 'de'

  if (!isDetailPage.value || newLocale === locale.value) {
    navigateTo(switchLocalePath(newLocale))
    return
  }

  try {
    const result = await $fetch('/api/translation/switch', {
      method: 'GET',
      query: {
        slug: currentSlug.value,
        currentLang: locale.value,
        targetLang: newLocale,
        category: currentCategory.value
      }
    })

    if (result.success && result.data?.targetUrl) {
      navigateTo(result.data.targetUrl)
    } else if (result.data?.fallbackUrl) {
      navigateTo(result.data.fallbackUrl)
    } else {
      navigateTo(switchLocalePath(newLocale))
    }
  } catch {
    navigateTo(switchLocalePath(newLocale))
  }
}

let scrollHandler: (() => void) | null = null

onMounted(() => {
  isMounted.value = true
  scrolled.value = window.scrollY > 20
  scrollHandler = () => {
    scrolled.value = window.scrollY > 20
  }
  window.addEventListener('scroll', scrollHandler, { passive: true })
})

onUnmounted(() => {
  if (scrollHandler) {
    window.removeEventListener('scroll', scrollHandler)
  }
})
</script>
