<template>
  <div class="pb-12 min-h-screen" style="background: linear-gradient(135deg, var(--mc-jade-faint), var(--mc-surface), var(--mc-jade-faint));">
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
        />
      </ClientOnly>

      <!-- Page Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">{{ t('pages.contact.title') }}</h1>
        <p class="text-lg text-gray-600 max-w-2xl mx-auto">
          {{ t('pages.contact.description') }}
        </p>
      </div>

      <!-- Success Message -->
      <div v-if="success" class="mb-8 bg-green-50 border border-green-200 rounded-xl p-6 text-center">
        <div class="flex items-center justify-center gap-3 mb-2">
          <div class="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center">
            <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-green-800">{{ t('pages.contact.success') }}</h3>
        </div>
        <p class="text-green-700">{{ t('pages.contact.successMessage') }}</p>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="mb-8 bg-red-50 border border-red-200 rounded-xl p-6">
        <div class="flex items-center gap-3 mb-2">
          <div class="w-12 h-12 bg-red-500 rounded-full flex items-center justify-center">
            <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-red-800">{{ t('pages.contact.submitFailed') }}</h3>
        </div>
        <p class="text-red-700">{{ error }}</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Contact Form -->
        <div class="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
          <h2 class="text-2xl font-semibold text-gray-900 mb-2">{{ t('pages.contact.formTitle') }}</h2>
          <p class="text-gray-500 mb-6">{{ t('pages.contact.formSubtitle') }}</p>
          
          <form @submit.prevent="handleSubmit" class="space-y-5">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label for="contact-name" class="block text-sm font-medium text-gray-700 mb-2">{{ t('pages.contact.form.name') }} <span class="text-red-500">*</span></label>
                <input
                  v-model="form.name"
                  type="text"
                  id="contact-name"
                  name="name"
                  autocomplete="name"
                  required
                  :disabled="loading"
                  class="w-full px-4 py-3 border border-gray-200 rounded-xl input-jade transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  :placeholder="t('pages.contact.form.namePlaceholder')"
                />
              </div>
              <div>
                <label for="contact-phone" class="block text-sm font-medium text-gray-700 mb-2">{{ t('pages.contact.form.phone') }}</label>
                <input
                  v-model="form.phone"
                  type="tel"
                  id="contact-phone"
                  name="phone"
                  autocomplete="tel"
                  :disabled="loading"
                  class="w-full px-4 py-3 border border-gray-200 rounded-xl input-jade transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  :placeholder="t('pages.contact.form.phonePlaceholder')"
                  @input="formatPhoneNumber"
                />
                <div v-if="form.phone && !isValidPhone" class="text-red-500 text-xs mt-1">
                  Please enter a valid phone number
                </div>
              </div>
            </div>
            
            <div>
              <label for="contact-email" class="block text-sm font-medium text-gray-700 mb-2">{{ t('pages.contact.form.email') }} <span class="text-red-500">*</span></label>
              <input
                v-model="form.email"
                type="email"
                id="contact-email"
                name="email"
                autocomplete="email"
                required
                :disabled="loading"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl input-jade transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                :placeholder="t('pages.contact.form.emailPlaceholder')"
              />
              <div v-if="form.email && !isValidEmail" class="text-red-500 text-xs mt-1">
                Please enter a valid email address
              </div>
            </div>

            <div>
              <label for="contact-type" class="block text-sm font-medium text-gray-700 mb-2">{{ t('pages.contact.form.service') }}</label>
              <select
                v-model="form.type"
                id="contact-type"
                name="type"
                :disabled="loading"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl input-jade transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="">{{ t('pages.contact.form.selectInquiryType') }}</option>
                <option value="general">{{ t('pages.contact.form.general') }}</option>
                <option value="product">{{ t('pages.contact.form.product') }}</option>
                <option value="partnership">{{ t('pages.contact.form.partnership') }}</option>
                <option value="other">{{ t('pages.contact.form.other') }}</option>
              </select>
            </div>
            
            <div>
              <label for="contact-message" class="block text-sm font-medium text-gray-700 mb-2">{{ t('pages.contact.form.message') }} <span class="text-red-500">*</span></label>
              <textarea
                v-model="form.message"
                id="contact-message"
                name="message"
                rows="4"
                required
                :disabled="loading"
                class="w-full px-4 py-3 border border-gray-200 rounded-xl input-jade transition-all resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                :placeholder="t('pages.contact.form.messagePlaceholder')"
              ></textarea>
            </div>
            
            <div>
              <button 
                type="submit" 
                :disabled="loading"
                class="w-full text-white py-4 px-6 rounded-xl transition-all duration-300 font-medium text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none btn-jade-solid"
              >
                <span v-if="loading" class="flex items-center justify-center gap-2">
                  <svg class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V8a8 8 0 00-8 8h2.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                  </svg>
                  {{ t('pages.contact.submitting') }}
                </span>
                <span v-else>{{ t('pages.contact.form.submit') }}</span>
              </button>
            </div>
          </form>
        </div>

        <!-- Contact Info -->
        <div class="space-y-6">
          <!-- Quick Contact Cards -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="rounded-2xl p-6 text-white shadow-lg" style="background: var(--mc-jade);">
              <div class="flex items-center gap-3 mb-3">
                <div class="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                </div>
                <h3 class="font-semibold">{{ t('pages.contact.info.phoneConsultation') }}</h3>
              </div>
              <p class="text-sm mb-2" style="color: oklch(85% 0.05 185);">{{ t('pages.contact.info.phoneHint') }}</p>
              <p class="text-xl font-bold">{{ companyInfo.phone }}</p>
            </div>
            
            <div class="rounded-2xl p-6 text-white shadow-lg" style="background: var(--mc-jade-dark);">
              <div class="flex items-center gap-3 mb-3">
                <div class="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                  <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 class="font-semibold">{{ t('pages.contact.info.emailUs') }}</h3>
              </div>
              <p class="text-sm mb-2" style="color: oklch(85% 0.05 185);">{{ t('pages.contact.info.emailHint') }}</p>
              <p class="text-lg font-bold">{{ companyInfo.email }}</p>
            </div>
          </div>

          <!-- Company Info Card -->
          <div class="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            <h3 class="text-xl font-semibold text-gray-900 mb-6">{{ t('pages.contact.info.title') }}</h3>
            
            <div class="space-y-5">
              <div class="flex items-start gap-4">
                <div class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style="background: oklch(52% 0.16 185 / 0.1);">
                  <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--mc-jade);">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900 mb-1">{{ t('pages.contact.info.address') }}</h4>
                  <p class="text-gray-600">{{ companyInfo.address }}</p>
                </div>
              </div>
              
              <div class="flex items-start gap-4">
                <div class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style="background: oklch(72% 0.14 78 / 0.1);">
                  <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--mc-amber);">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900 mb-1">{{ t('pages.contact.info.hours') }}</h4>
                  <p class="text-gray-600">{{ companyInfo.workingHours }}</p>
                  <p class="text-sm text-gray-500 mt-1">Consultation available on weekends</p>
                </div>
              </div>
            </div>
          </div>

          <!-- What You'll Receive -->
          <div class="bg-gray-50 rounded-2xl p-6 border border-gray-200">
            <h3 class="font-semibold text-gray-900 mb-4">{{ t('pages.contact.whatYouGet') }}</h3>
            <ul class="space-y-3">
              <li class="flex items-start gap-3">
                <div class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style="background: var(--mc-amber);">
                  <svg class="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span class="text-gray-600 text-sm">{{ t('pages.contact.benefit1') }}</span>
              </li>
              <li class="flex items-start gap-3">
                <div class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style="background: var(--mc-amber);">
                  <svg class="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span class="text-gray-600 text-sm">{{ t('pages.contact.benefit2') }}</span>
              </li>
              <li class="flex items-start gap-3">
                <div class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style="background: var(--mc-amber);">
                  <svg class="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span class="text-gray-600 text-sm">{{ t('pages.contact.benefit3') }}</span>
              </li>
              <li class="flex items-start gap-3">
                <div class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style="background: var(--mc-amber);">
                  <svg class="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span class="text-gray-600 text-sm">{{ t('pages.contact.benefit4') }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useBreadcrumb } from '~/composables/useBreadcrumb'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

definePageMeta({
  title: `Contact ${companyInfo.shortName} - Free Medical Tourism Consultation`
})

const runtimeConfig = useRuntimeConfig()
const siteUrl = runtimeConfig.public.siteUrl || companyInfo.siteUrl
const pagePath = locale.value === 'en' ? '/contact' : `/${locale.value}/contact`

useSeoMeta({
  title: t('pages.contact.seo.title'),
  description: t('pages.contact.seo.description', { phone: companyInfo.phone }),
  keywords: '',
  ogTitle: t('pages.contact.seo.title'),
  ogDescription: t('pages.contact.seo.description', { phone: companyInfo.phone }),
  ogImage: `${siteUrl}/images/hero-bg.webp`,
  ogType: 'website',
  ogSiteName: companyInfo.shortName,
  ogUrl: `${siteUrl}${pagePath}`,
  twitterCard: 'summary_large_image',
  twitterTitle: t('pages.contact.seo.title'),
  twitterDescription: t('pages.contact.seo.description', { phone: companyInfo.phone }),
  twitterImage: `${siteUrl}/images/hero-bg.webp`
})

// Organization Schema + BreadcrumbList - Contact page
import { useOrganizationSchema } from '~/composables/useOrganizationSchema'
const organizationSchema = useOrganizationSchema('contact')

const breadcrumbSchema = {
  '@context': 'https://schema.org',
  '@type': 'BreadcrumbList',
  itemListElement: [
    { '@type': 'ListItem', position: 1, name: t('nav.home'), item: `${siteUrl}/` },
    { '@type': 'ListItem', position: 2, name: t('pages.contact.title'), item: `${siteUrl}${pagePath}` }
  ]
}

useHead({
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify(organizationSchema)
    },
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify(breadcrumbSchema)
    }
  ],
  link: [
    { rel: 'canonical', href: `${siteUrl}${pagePath}` },
    { rel: 'alternate', hreflang: 'x-default', href: `${siteUrl}/contact` },
    { rel: 'alternate', hreflang: 'en', href: `${siteUrl}/contact` },
    { rel: 'alternate', hreflang: 'fr', href: `${siteUrl}/fr/contact` },
    { rel: 'alternate', hreflang: 'de', href: `${siteUrl}/de/contact` }
  ]
})

const { links } = useBreadcrumb()

import { ref, computed } from 'vue'
import { companyInfo } from '~/utils/config'

interface FormData {
  name: string
  phone: string
  email: string
  type: string
  message: string
  userAgent?: string
  browserLanguage?: string
  platform?: string
  screenResolution?: string
  timezone?: string
}

const form = ref<FormData>({
  name: '',
  phone: '',
  email: '',
  type: '',
  message: ''
})

const loading = ref(false)
const error = ref('')
const success = ref(false)

// Phone validation (optional field)
const isValidPhone = computed(() => {
  if (!form.value.phone) return true // Empty is valid since it's optional
  // Remove all non-digit characters
  const phoneNumber = form.value.phone.replace(/\D/g, '')
  // Allow international formats (at least 8 digits)
  return phoneNumber.length >= 8
})

// Email validation (required field)
const isValidEmail = computed(() => {
  if (!form.value.email) return false
  // Standard email regex pattern
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(form.value.email)
})

// Phone formatting
const formatPhoneNumber = () => {
  if (!form.value.phone) return
  
  // Remove all non-digit characters
  const digits = form.value.phone.replace(/\D/g, '')
  
  // Keep as-is for international numbers
  form.value.phone = digits
}

const handleSubmit = async () => {
  loading.value = true
  error.value = ''
  success.value = false
  
  // Frontend validation
  if (!form.value.email) {
    error.value = t('pages.contact.errorEmailRequired')
    loading.value = false
    return
  }
  
  if (!isValidEmail.value) {
    error.value = t('pages.contact.errorEmailInvalid')
    loading.value = false
    return
  }
  
  if (!isValidPhone.value) {
    error.value = t('pages.contact.errorPhoneInvalid')
    loading.value = false
    return
  }
  
  // Collect browser info
  const browserInfo = {
    userAgent: navigator.userAgent,
    browserLanguage: navigator.language,
    platform: navigator.platform,
    screenResolution: `${screen.width}x${screen.height}`,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
  }
  
  try {
    const response = await $fetch<{ success: boolean; message?: string; error?: string }>('/api/contact', {
      method: 'POST',
      body: {
        ...form.value,
        ...browserInfo
      }
    })
    
    if (response.success) {
      success.value = true
      form.value = {
        name: '',
        phone: '',
        email: '',
        type: '',
        message: ''
      }
      setTimeout(() => {
        success.value = false
      }, 5000)
    } else {
      error.value = response.error || t('pages.contact.errorSubmitFailed')
    }
  } catch (err) {
    error.value = t('common.networkError')
    console.error('表单提交错误:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
</style>
