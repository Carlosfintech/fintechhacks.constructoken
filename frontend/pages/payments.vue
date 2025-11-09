<template>
    <main class="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50 py-12 px-4">
        <div class="mx-auto max-w-4xl">
            <!-- Header -->
            <div class="mb-12 text-center">
                <h1 class="text-5xl font-bold text-gray-900 mb-4">🏗️ Constructoken</h1>
                <p class="text-xl text-gray-600">Sistema de Pagos con Open Payments</p>
                <p class="mt-2 text-gray-500">MVP - Hackathon Interledger</p>
            </div>

            <!-- Unified Payment Card -->
            <div class="mx-auto max-w-2xl">
                <div class="rounded-2xl bg-white p-8 shadow-xl transition hover:shadow-2xl">
                    <div class="mb-6 flex items-center justify-center space-x-4">
                        <div class="flex h-16 w-16 items-center justify-center rounded-full bg-blue-100">
                            <span class="text-3xl">💸</span>
                        </div>
                        <div class="text-4xl font-bold text-gray-300">+</div>
                        <div class="flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
                            <span class="text-3xl">🏗️</span>
                        </div>
                    </div>
                    
                    <h2 class="mb-3 text-center text-3xl font-bold text-gray-900">Sistema de Pagos</h2>
                    <p class="mb-6 text-center text-gray-600">
                        Ahorra para tu construcción y compra materiales
                    </p>
                    
                    <div class="mb-8 grid gap-4 md:grid-cols-2">
                        <div class="rounded-lg bg-blue-50 p-4">
                            <p class="mb-2 font-semibold text-blue-900">💰 Ahorro para la construcción</p>
                            <ul class="list-disc list-inside text-sm text-blue-800 space-y-1">
                                <li>Remesa internacional</li>
                                <li>USD → MXN</li>
                                <li>MIGRANTE → FINSUS</li>
                            </ul>
                        </div>
                        <div class="rounded-lg bg-green-50 p-4">
                            <p class="mb-2 font-semibold text-green-900">🛒 Compra de materiales</p>
                            <ul class="list-disc list-inside text-sm text-green-800 space-y-1">
                                <li>Dispersión local</li>
                                <li>MXN → MXN</li>
                                <li>FINSUS → MERCHANT</li>
                            </ul>
                        </div>
                    </div>

                    <button
                        @click="$router.push('/payment')"
                        class="w-full rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 py-4 text-lg font-semibold text-white transition hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-4 focus:ring-indigo-300 shadow-lg"
                    >
                        🚀 Iniciar Pago
                    </button>
                </div>
            </div>

            <!-- Info adicional -->
            <div class="mt-12 rounded-2xl bg-white p-8 shadow-xl">
                <h3 class="mb-4 text-xl font-bold text-gray-900">ℹ️ Información del Sistema</h3>
                <div class="space-y-2 text-gray-600">
                    <p><strong>🔒 Seguridad:</strong> Todos los pagos son procesados a través de Interledger Test Wallet</p>
                    <p><strong>✅ Estado:</strong> Ambos casos probados y funcionando (COMPLETED)</p>
                    <p><strong>🚀 Tecnología:</strong> Backend FastAPI + Frontend Nuxt.js + Open Payments Protocol</p>
                    <p><strong>💻 Repositorio:</strong> Constructoken Hackathon</p>
                </div>
            </div>
        </div>
    </main>
</template>

<script setup lang="ts">
// Página de inicio del sistema de pagos
</script>

