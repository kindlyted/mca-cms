<template>
  <div class="min-h-screen flex flex-col">
    <TheHeader />
    <main class="flex-1">
      <div>
        <slot />
      </div>
    </main>
    <TheFooter />
    <CookieConsent />
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
</style>