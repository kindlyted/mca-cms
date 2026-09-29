<template>
  <div class="min-h-[calc(100vh-80px)] bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8 mt-20">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
        管理员登录
      </h2>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <form @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              管理员密码
            </label>
            <div class="mt-1">
              <input
                id="password"
                name="password"
                type="password"
                v-model="password"
                required
                class="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="请输入管理员密码"
              />
            </div>
          </div>

          <div v-if="error" class="text-red-600 text-sm">
            {{ error }}
          </div>

          <div>
            <button
              type="submit"
              :disabled="loading"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <span v-if="loading">登录中...</span>
              <span v-else>登录</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
useSeoMeta({ robots: 'noindex, nofollow' })

const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await $fetch('/api/auth/login', {
      method: 'POST',
      body: { password: password.value }
    })

    if (response.success) {
      // 保存token到localStorage
      localStorage.setItem('admin_token', response.token)
      // 登录成功，跳转到管理页面
      await navigateTo('/admin/contacts')
    } else {
      error.value = '登录失败'
    }
  } catch (err) {
    error.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>