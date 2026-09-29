<template>
  <Transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="transform translate-y-full opacity-0"
    enter-to-class="transform translate-y-0 opacity-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="transform translate-y-0 opacity-100"
    leave-to-class="transform translate-y-full opacity-0"
  >
    <div
      v-if="!hasConsent"
      class="fixed bottom-0 left-0 right-0 z-50 bg-white border-t shadow-2xl" style="border-color: var(--mc-border);"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
          <!-- Content -->
          <div class="flex-1 pr-0 lg:pr-8">
            <div class="flex items-start gap-3">
              <div class="flex-shrink-0 mt-0.5">
                <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--mc-jade);">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <div>
                <h3 class="text-base font-semibold text-gray-900 mb-1">
                  {{ $t('cookie.title') }}
                </h3>
                <p class="text-sm text-gray-600 leading-relaxed">
                  {{ $t('cookie.description') }}
                  <NuxtLink 
                    :to="localePath('/privacy')" 
                     class="underline font-medium" style="color: var(--mc-jade);"
                    @click="hasConsent = true"
                  >
                    {{ $t('cookie.privacyLink') }}
                  </NuxtLink>
                </p>
              </div>
            </div>
          </div>

          <!-- Buttons -->
          <div class="flex flex-col sm:flex-row gap-3 w-full lg:w-auto flex-shrink-0">
            <button
              @click="rejectCookies"
              class="px-5 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 whitespace-nowrap" style="color: var(--mc-ink-soft); background: var(--mc-jade-faint);"
            >
              {{ $t('cookie.reject') }}
            </button>
            <button
              @click="acceptCookies"
              class="px-5 py-2.5 text-sm font-medium text-white rounded-lg transition-all duration-200 whitespace-nowrap shadow-sm btn-jade-solid"
            >
              {{ $t('cookie.accept') }}
            </button>
          </div>
        </div>

        <!-- Cookie Preferences Link (Optional advanced settings) -->
        <div v-if="showDetails" class="mt-4 pt-4 border-t border-gray-100">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <div class="font-medium text-gray-900 text-sm">{{ $t('cookie.types.necessary.title') }}</div>
                <div class="text-xs text-gray-500">{{ $t('cookie.types.necessary.description') }}</div>
              </div>
              <div class="text-green-600 text-sm font-medium">{{ $t('cookie.alwaysOn') }}</div>
            </div>
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <div class="font-medium text-gray-900 text-sm">{{ $t('cookie.types.analytics.title') }}</div>
                <div class="text-xs text-gray-500">{{ $t('cookie.types.analytics.description') }}</div>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="preferences.analytics" class="sr-only peer">
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked" style="--peer-checked-bg: var(--mc-jade);" :class="preferences.analytics ? 'bg-[var(--mc-jade)]' : ''"></div>
              </label>
            </div>
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <div class="font-medium text-gray-900 text-sm">{{ $t('cookie.types.marketing.title') }}</div>
                <div class="text-xs text-gray-500">{{ $t('cookie.types.marketing.description') }}</div>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="preferences.marketing" class="sr-only peer">
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked" :class="preferences.marketing ? 'bg-[var(--mc-jade)]' : ''"></div>
              </label>
            </div>
          </div>
          <div class="mt-4 flex justify-end">
            <button
              @click="savePreferences"
              class="px-5 py-2 text-sm font-medium text-white rounded-lg transition-all duration-200 btn-jade-solid"
            >
              {{ $t('cookie.savePreferences') }}
            </button>
          </div>
        </div>

        <!-- Toggle Details Link -->
        <div class="mt-3 text-center lg:text-right">
          <button
            @click="showDetails = !showDetails"
            class="text-xs text-gray-500 hover:text-gray-700 underline"
          >
            {{ showDetails ? $t('cookie.hideDetails') : $t('cookie.showDetails') }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useLocalePath } from '#imports'
import { enableAnalytics, disableAnalytics } from '~/composables/useAnalytics'

const localePath = useLocalePath()
const hasConsent = ref(true)
const showDetails = ref(false)
const preferences = ref({
  necessary: true,
  analytics: false,
  marketing: false
})

// Check if user has already given consent
onMounted(() => {
  const consent = localStorage.getItem('cookie-consent')
  if (consent) {
    hasConsent.value = true
    try {
      const parsed = JSON.parse(consent)
      preferences.value = { ...preferences.value, ...parsed }
      // Initialize analytics if previously consented
      if (preferences.value.analytics) {
        enableAnalytics()
      }
    } catch (e) {
      // Invalid JSON, treat as basic consent
    }
  } else {
    hasConsent.value = false
  }
})

const acceptCookies = () => {
  preferences.value.analytics = true
  preferences.value.marketing = true
  saveConsent()
}

const rejectCookies = () => {
  preferences.value.analytics = false
  preferences.value.marketing = false
  saveConsent()
}

const savePreferences = () => {
  saveConsent()
}

const saveConsent = () => {
  localStorage.setItem('cookie-consent', JSON.stringify(preferences.value))
  hasConsent.value = true
  
  // Dispatch event for other components/scripts to listen to
  window.dispatchEvent(new CustomEvent('cookie-consent-updated', { 
    detail: preferences.value 
  }))
  
  // Initialize or disable analytics based on preference
  if (preferences.value.analytics) {
    enableAnalytics()
  } else {
    disableAnalytics()
  }
}
</script>
