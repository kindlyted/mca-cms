<template>
  <!-- 悬浮固定模式 -->
  <div v-if="mode === 'floating'" class="fixed bottom-6 right-6 z-50">
    <!-- 展开状态的分享按钮组 -->
    <transition-group
      name="share-fade"
      tag="div"
      class="flex flex-col items-end gap-3 mb-3"
    >
      <template v-if="isExpanded">
        <!-- 原生分享（Web Share API） -->
        <button
          v-if="isShareSupported"
          @click="shareNative"
          class="share-fab native"
          title="Share"
        >
          <UIcon name="i-mdi-share-variant" class="w-5 h-5" />
          <span class="share-label">Share</span>
        </button>

        <!-- 复制链接 -->
        <button
          @click="copyToClipboard"
          class="share-fab copy"
          title="Copy Link"
        >
          <UIcon name="i-mdi-link-variant" class="w-5 h-5" />
          <span class="share-label">{{ copied ? 'Copied' : 'Copy Link' }}</span>
        </button>

        <!-- LinkedIn -->
        <a
          :href="linkedInUrl"
          target="_blank"
          rel="noreferrer"
          class="share-fab linkedin"
          title="Share on LinkedIn"
        >
          <UIcon name="i-mdi-linkedin" class="w-5 h-5" />
          <span class="share-label">LinkedIn</span>
        </a>

        <!-- Facebook -->
        <a
          :href="facebookUrl"
          target="_blank"
          rel="noreferrer"
          class="share-fab facebook"
          title="Share on Facebook"
        >
          <UIcon name="i-mdi-facebook" class="w-5 h-5" />
          <span class="share-label">Facebook</span>
        </a>

        <!-- Twitter/X -->
        <a
          :href="twitterUrl"
          target="_blank"
          rel="noreferrer"
          class="share-fab twitter"
          title="Share on X (Twitter)"
        >
          <UIcon name="i-mdi-twitter" class="w-5 h-5" />
          <span class="share-label">X</span>
        </a>

        <!-- Email -->
        <a
          :href="emailUrl"
          class="share-fab email"
          title="Share via Email"
        >
          <UIcon name="i-mdi-email" class="w-5 h-5" />
          <span class="share-label">Email</span>
        </a>
      </template>
    </transition-group>

    <!-- 主按钮 -->
    <button
      @click="isExpanded = !isExpanded"
      class="main-fab"
      :class="{ 'active': isExpanded }"
      title="Share"
    >
      <UIcon
        :name="isExpanded ? 'i-mdi-close' : 'i-mdi-share-variant'"
        class="w-6 h-6 transition-transform duration-300"
        :class="{ 'rotate-180': isExpanded }"
      />
    </button>
  </div>

  <!-- 横向内嵌模式 -->
  <div v-else class="share-inline">
    <span class="share-label-text">Share</span>
    <div class="share-buttons-row">
      <!-- 原生分享（Web Share API） -->
      <button
        v-if="isShareSupported"
        @click="shareNative"
        class="share-btn-inline native"
        title="Share via native share"
      >
        <UIcon name="i-mdi-share-variant" class="w-5 h-5" />
      </button>

      <!-- Email -->
      <a
        :href="emailUrl"
        class="share-btn-inline email"
        title="Share via Email"
      >
        <UIcon name="i-mdi-email" class="w-5 h-5" />
      </a>

      <!-- Twitter/X -->
      <a
        :href="twitterUrl"
        target="_blank"
        rel="noreferrer"
        class="share-btn-inline twitter"
        title="Share on X (Twitter)"
      >
        <UIcon name="i-mdi-twitter" class="w-5 h-5" />
      </a>

      <!-- Facebook -->
      <a
        :href="facebookUrl"
        target="_blank"
        rel="noreferrer"
        class="share-btn-inline facebook"
        title="Share on Facebook"
      >
        <UIcon name="i-mdi-facebook" class="w-5 h-5" />
      </a>

      <!-- LinkedIn -->
      <a
        :href="linkedInUrl"
        target="_blank"
        rel="noreferrer"
        class="share-btn-inline linkedin"
        title="Share on LinkedIn"
      >
        <UIcon name="i-mdi-linkedin" class="w-5 h-5" />
      </a>

      <!-- 复制链接 -->
      <button
        @click="copyToClipboard"
        class="share-btn-inline copy"
        :title="copied ? 'Copied' : 'Copy Link'"
      >
        <UIcon :name="copied ? 'i-mdi-check' : 'i-mdi-link-variant'" class="w-5 h-5" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  title: string
  url: string
  description?: string
  image?: string
  mode?: 'floating' | 'inline'
}>()

const mode = computed(() => props.mode || 'floating')
const copied = ref(false)
const isExpanded = ref(false)

const isShareSupported = computed(() => typeof navigator !== 'undefined' && !!navigator.share)

const isFileShareSupported = computed(() => {
  return typeof navigator !== 'undefined' && !!navigator.canShare
})

const absoluteImageUrl = computed(() => {
  if (!props.image) return null
  if (props.image.startsWith('http')) return props.image
  const config = useRuntimeConfig()
  const baseUrl = config.public.siteUrl || companyInfo.siteUrl
  return `${baseUrl.replace(/\/+$/, '')}/${props.image.replace(/^\/+/, '')}`
})

async function shareNative() {
  if (absoluteImageUrl.value && isFileShareSupported.value) {
    try {
      const response = await fetch(absoluteImageUrl.value, { mode: 'cors' })
      if (response.ok) {
        const blob = await response.blob()
        const file = new File([blob], 'share.webp', { type: blob.type })
        await navigator.share({
          title: props.title,
          text: props.description || '',
          url: props.url,
          files: [file]
        })
        return
      }
    } catch {
      // fallback to simple share
    }
  }

  try {
    await navigator.share({
      title: props.title,
      text: props.description || '',
      url: props.url
    })
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') return
    useToast().add({
      title: 'Share failed',
      description: 'Could not share this content',
      icon: 'i-mdi-alert-circle',
      color: 'red'
    })
  }
}

// Twitter/X 分享链接
const twitterUrl = computed(() => {
  const params = new URLSearchParams({
    url: props.url,
    text: props.title
  })
  return `https://twitter.com/intent/tweet?${params.toString()}`
})

// Facebook 分享链接
const facebookUrl = computed(() => {
  const params = new URLSearchParams({
    u: props.url
  })
  return `https://www.facebook.com/sharer/sharer.php?${params.toString()}`
})

// LinkedIn 分享链接
const linkedInUrl = computed(() => {
  const params = new URLSearchParams({
    url: props.url,
    title: props.title,
    summary: props.description || '',
    source: companyInfo.shortName
  })
  return `https://www.linkedin.com/sharing/share-offsite/?${params.toString()}`
})

// Email 分享链接
const emailUrl = computed(() => {
  const subject = encodeURIComponent(props.title)
  const body = encodeURIComponent(`${props.description || ''}\n\n${props.url}`)
  return `mailto:?subject=${subject}&body=${body}`
})

// 复制链接
const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(props.url)
    copied.value = true
    useToast().add({
      title: 'Copied!',
      description: 'Link copied to clipboard',
      icon: 'i-mdi-check-circle',
      color: 'green',
      timeout: 2000
    })
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    useToast().add({
      title: 'Copy Failed',
      description: 'Please copy the link manually',
      icon: 'i-mdi-alert-circle',
      color: 'red'
    })
  }
}
</script>

<style scoped>
/* ========== 悬浮固定模式样式 ========== */
.main-fab {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
}

.main-fab:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
}

.main-fab.active {
  background: linear-gradient(135deg, #6b7280, #4b5563);
  box-shadow: 0 4px 12px rgba(107, 114, 128, 0.4);
}

.share-fab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
  text-decoration: none;
  white-space: nowrap;
}

.share-fab:hover {
  transform: translateX(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.share-fab.native {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}
.share-fab.native:hover {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
}

.share-fab.twitter {
  background-color: #000000;
}
.share-fab.twitter:hover {
  background-color: #1a1a1a;
}

.share-fab.facebook {
  background-color: #1877f2;
}
.share-fab.facebook:hover {
  background-color: #166fe5;
}

.share-fab.linkedin {
  background-color: #0a66c2;
}
.share-fab.linkedin:hover {
  background-color: #0958a8;
}

.share-fab.email {
  background-color: #ea4335;
}
.share-fab.email:hover {
  background-color: #d33b2f;
}

.share-fab.copy {
  background-color: #6b7280;
}
.share-fab.copy:hover {
  background-color: #4b5563;
}

/* 动画效果 */
.share-fade-enter-active,
.share-fade-leave-active {
  transition: all 0.3s ease;
}

.share-fade-enter-from,
.share-fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* ========== 横向内嵌模式样式 ========== */
.share-inline {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
}

.share-label-text {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.share-buttons-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.share-btn-inline {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  color: white;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
  text-decoration: none;
}

.share-btn-inline:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.share-btn-inline.native {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}
.share-btn-inline.native:hover {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
}

.share-btn-inline.twitter {
  background-color: #000000;
}
.share-btn-inline.twitter:hover {
  background-color: #1a1a1a;
}

.share-btn-inline.facebook {
  background-color: #1877f2;
}
.share-btn-inline.facebook:hover {
  background-color: #166fe5;
}

.share-btn-inline.linkedin {
  background-color: #0a66c2;
}
.share-btn-inline.linkedin:hover {
  background-color: #0958a8;
}

.share-btn-inline.email {
  background-color: #ea4335;
}
.share-btn-inline.email:hover {
  background-color: #d33b2f;
}

.share-btn-inline.copy {
  background-color: #6b7280;
}
.share-btn-inline.copy:hover {
  background-color: #4b5563;
}
</style>
