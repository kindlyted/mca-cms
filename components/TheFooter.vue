<template>
  <footer class="bg-[var(--mc-deep)] text-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div>
          <h3 class="text-lg font-semibold mb-4 text-[var(--mc-jade-lighter)]">{{ t('footer.quickLinks') }}</h3>
          <ul class="space-y-2">
            <li v-for="link in quickLinks" :key="link.to">
              <template v-if="isMounted">
                <NuxtLink :to="localePath(link.to)" class="text-white/70 hover:text-[var(--mc-amber-light)] transition-colors duration-300">{{ t(link.labelKey) }}</NuxtLink>
              </template>
              <span v-else class="text-white/70">{{ t(link.labelKey) }}</span>
            </li>
          </ul>
        </div>

        <div>
          <h3 class="text-lg font-semibold mb-4 text-[var(--mc-jade-lighter)]">{{ t('footer.resources') }}</h3>
          <ul class="space-y-2">
            <li v-for="link in companyInfo.externalLinks" :key="link.url">
              <a :href="link.url" target="_blank" rel="noopener noreferrer" class="text-white/70 hover:text-[var(--mc-amber-light)] transition-colors duration-300">{{ link.name }}</a>
            </li>
          </ul>
        </div>

        <div>
          <h3 class="text-lg font-semibold mb-4 text-[var(--mc-jade-lighter)]">{{ t('footer.contact') }}</h3>
          <div class="space-y-2 text-white/70">
            <div class="flex items-center space-x-2">
              <svg class="h-4 w-4 text-[var(--mc-jade-lighter)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              <span>{{ companyInfo.phone }}</span>
              <a :href="whatsAppUrl" target="_blank" rel="noopener noreferrer" class="inline-flex items-center hover:opacity-80 transition-opacity" title="WhatsApp">
                <svg class="h-4 w-4 text-[#25D366]" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
                </svg>
              </a>
            </div>
            <div class="flex items-center space-x-2">
              <svg class="h-4 w-4 text-[var(--mc-jade-lighter)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span>{{ companyInfo.email }}</span>
            </div>
            <div class="flex items-center space-x-2">
              <svg class="h-4 w-4 text-[var(--mc-jade-lighter)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span>{{ companyInfo.address }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="border-t border-white/10 mt-8 pt-8">
        <div class="flex flex-col md:flex-row justify-between items-center gap-4">
          <p class="text-white/50 text-sm">{{ companyInfo.copyright }}</p>
          <div class="flex flex-wrap justify-center gap-4 text-white/50 text-sm">
            <template v-if="isMounted">
              <NuxtLink v-for="link in legalLinks" :key="link.to" :to="localePath(link.to)" class="hover:text-[var(--mc-amber-light)] transition-colors duration-300">{{ t(link.labelKey) }}</NuxtLink>
            </template>
            <template v-else>
              <span v-for="link in legalLinks" :key="link.to" class="cursor-default">{{ t(link.labelKey) }}</span>
            </template>
          </div>
        </div>

        <p v-if="poweredBy" class="mt-4 text-center text-white/40 text-xs">
          <a
            :href="poweredBy.url"
            target="_blank"
            :rel="poweredBy.rel || 'noopener noreferrer'"
            class="hover:text-[var(--mc-amber-light)] transition-colors duration-300"
          >{{ t(poweredBy.labelKey || 'footer.poweredBy') }}</a>
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { companyInfo } from '~/utils/config'
import { useI18n } from 'vue-i18n'
import { useLocalePath } from '#imports'
import siteConfig from '../site.config.json'

const isMounted = ref(false)
onMounted(() => { isMounted.value = true })

const { t } = useI18n()
const localePath = useLocalePath()

const quickLinks = computed(() => (siteConfig.footer?.quickLinks ?? []).filter((link: any) => link.enabled !== false))
const legalLinks = computed(() => (siteConfig.footer?.legalLinks ?? []).filter((link: any) => link.enabled !== false))
const poweredBy = computed(() => {
  const pb = siteConfig.footer?.poweredBy as { enabled?: boolean; url?: string; rel?: string; labelKey?: string } | undefined
  return pb && pb.enabled !== false && pb.url ? pb : null
})

const whatsAppUrl = computed(() => {
  const digits = companyInfo.phone.replace(/\D/g, '')
  return `https://wa.me/${digits}`
})
</script>
