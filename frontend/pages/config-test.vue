<template>
  <div class="min-h-screen bg-gray-50 p-8">
    <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6">
      <h1 class="text-2xl font-bold mb-4">🔧 Diagnóstico de Configuración</h1>
      
      <div class="space-y-4">
        <div class="border-l-4 border-blue-500 pl-4">
          <h2 class="font-semibold text-gray-700">API URL:</h2>
          <p class="font-mono text-sm bg-gray-100 p-2 rounded">{{ apiUrl }}</p>
        </div>

        <div class="border-l-4 border-green-500 pl-4">
          <h2 class="font-semibold text-gray-700">API Root URL:</h2>
          <p class="font-mono text-sm bg-gray-100 p-2 rounded">{{ apiRootUrl }}</p>
        </div>

        <div class="border-l-4 border-purple-500 pl-4">
          <h2 class="font-semibold text-gray-700">App Name:</h2>
          <p class="font-mono text-sm bg-gray-100 p-2 rounded">{{ appName }}</p>
        </div>

        <div class="border-l-4 border-yellow-500 pl-4">
          <h2 class="font-semibold text-gray-700">Prueba de Endpoint:</h2>
          <p class="font-mono text-sm bg-gray-100 p-2 rounded break-all">
            {{ testUrl }}
          </p>
          <button 
            @click="testEndpoint"
            class="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            🧪 Probar Conexión
          </button>
        </div>

        <div v-if="testResult" class="border-l-4 border-red-500 pl-4">
          <h2 class="font-semibold text-gray-700">Resultado:</h2>
          <pre class="text-xs bg-gray-100 p-2 rounded overflow-auto">{{ testResult }}</pre>
        </div>
      </div>

      <div class="mt-6 p-4 bg-blue-50 rounded">
        <p class="text-sm text-gray-700">
          ✅ <strong>URL Correcta:</strong> <code>http://localhost</code>
        </p>
        <p class="text-sm text-gray-700 mt-1">
          ❌ <strong>URL Incorrecta:</strong> <code>http://localhost:3000</code> o <code>http://localhost:8888</code>
        </p>
      </div>

      <div class="mt-4">
        <NuxtLink to="/payments" class="text-blue-600 hover:underline">
          ← Volver a Payments
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()
const apiUrl = computed(() => config.public.apiUrl || 'NO CONFIGURADO')
const apiRootUrl = computed(() => config.public.apiRootUrl || 'NO CONFIGURADO')
const appName = computed(() => config.public.appName || 'NO CONFIGURADO')
const testUrl = computed(() => `${apiUrl.value}/v1/payments/migrante/start`)

const testResult = ref('')

async function testEndpoint() {
  testResult.value = 'Probando...'
  try {
    const response = await fetch(testUrl.value, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ amount: '1500' })
    })
    
    const contentType = response.headers.get('content-type')
    let data
    
    if (contentType && contentType.includes('application/json')) {
      data = await response.json()
    } else {
      data = await response.text()
    }
    
    testResult.value = `Status: ${response.status} ${response.statusText}\n\n${
      typeof data === 'string' ? data : JSON.stringify(data, null, 2)
    }`
  } catch (error: any) {
    testResult.value = `ERROR: ${error.message}\n${error.stack || ''}`
  }
}
</script>

