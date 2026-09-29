<template>
  <div class="min-h-[calc(100vh-80px)] bg-gray-50 py-8 mt-20">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="bg-white shadow rounded-lg">
        <div class="px-4 py-5 sm:p-6">
          <div class="flex items-center justify-between mb-6">
            <h1 class="text-2xl font-bold text-gray-900">联系信息管理</h1>
          </div>

          <div v-if="loading" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p class="mt-2 text-gray-600">加载中...</p>
          </div>

          <div v-else-if="error" class="text-center py-8">
            <p class="text-red-600">{{ error }}</p>
          </div>

          <div v-else>
            <div class="mb-4">
              <p class="text-sm text-gray-600">总共 {{ contacts.length }} 条联系信息</p>
            </div>

            <div class="space-y-4">
              <div
                v-for="contact in contacts"
                :key="contact.id"
                class="border border-gray-200 rounded-lg p-4"
              >
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h3 class="font-medium text-gray-900">{{ contact.name }}</h3>
                    <p class="text-sm text-gray-600">电话: {{ contact.phone }}</p>
                    <p class="text-sm text-gray-600">邮箱: {{ contact.email }}</p>
                    <p class="text-sm text-gray-600">类型: {{ contact.type || '其他咨询' }}</p>
                    <p class="text-sm text-gray-500">提交时间: {{ formatDate(contact.submittedAt) }}</p>
                  </div>
                  <div>
                    <h4 class="font-medium text-gray-900 mb-2">咨询内容:</h4>
                    <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ contact.message }}</p>
                  </div>
                </div>
                <!-- Browser & IP info -->
                <div v-if="contact.ipAddress || contact.userAgent" class="mt-3 pt-3 border-t border-gray-100">
                  <details class="text-xs text-gray-500">
                    <summary class="cursor-pointer hover:text-gray-700 font-medium">设备与来源信息</summary>
                    <div class="mt-2 space-y-1">
                      <p v-if="contact.ipAddress">IP: {{ contact.ipAddress }}</p>
                      <p v-if="contact.browserLanguage">语言: {{ contact.browserLanguage }}</p>
                      <p v-if="contact.platform">平台: {{ contact.platform }}</p>
                      <p v-if="contact.screenResolution">屏幕分辨率: {{ contact.screenResolution }}</p>
                      <p v-if="contact.timezone">时区: {{ contact.timezone }}</p>
                      <p v-if="contact.userAgent" class="break-all">UA: {{ contact.userAgent }}</p>
                    </div>
                  </details>
                </div>
              </div>
            </div>

            <div v-if="contacts.length === 0" class="text-center py-8">
              <p class="text-gray-500">暂无联系信息</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
useSeoMeta({ robots: 'noindex, nofollow' })

const contacts = ref([])
const loading = ref(true)
const error = ref('')
const token = ref('')

// 检查是否已登录
onMounted(async () => {
  const savedToken = localStorage.getItem('admin_token')
  if (savedToken) {
    token.value = savedToken
    await loadContacts()
  } else {
    // 未登录，跳转到登录页面
    await navigateTo('/admin')
  }
})

const loadContacts = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await $fetch('/api/contacts', {
      headers: {
        'Authorization': `Bearer ${token.value}`
      }
    })

    if (response.success) {
      contacts.value = response.data
    } else {
      error.value = response.error || '获取数据失败'
      // 如果token无效，清除并跳转到登录
      if (response.error?.includes('token')) {
        localStorage.removeItem('admin_token')
        await navigateTo('/admin')
      }
    }
  } catch (err) {
    error.value = '网络错误，请稍后重试'
    console.error('获取联系信息失败:', err)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}
</script>