<template>
  <main class="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center p-4">
    <div class="text-center">
      <div class="mb-8 animate-bounce">
        <span class="text-8xl">🏗️</span>
      </div>
      <h1 class="text-5xl font-bold text-white mb-4">Constructoken</h1>
      <p class="text-xl text-purple-100 mb-8">Sistema de Pagos con Open Payments</p>
      <p class="text-purple-200 mb-8">Redirigiendo...</p>
    </div>
  </main>
</template>

<script setup lang="ts">
// Redirect to payments page
onMounted(() => {
  navigateTo('/payments')
})
</script>
