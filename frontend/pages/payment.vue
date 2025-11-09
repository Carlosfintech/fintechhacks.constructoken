<template>
    <main class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
        <div class="mx-auto max-w-md">
            <div class="rounded-2xl bg-white p-8 shadow-xl">
                <!-- Header -->
                <div class="mb-6 text-center">
                    <h1 class="text-3xl font-bold text-gray-900">💸 Constructoken Payments</h1>
                    <p class="mt-2 text-gray-600">Selecciona el tipo de pago</p>
                </div>

                <!-- Payment Type Selector -->
                <div v-if="!loading" class="space-y-6">
                    <!-- Radio buttons para seleccionar tipo -->
                    <div class="space-y-3">
                        <label class="flex items-center rounded-lg border-2 p-4 cursor-pointer transition hover:bg-blue-50"
                               :class="paymentType === 'remesa' ? 'border-blue-600 bg-blue-50' : 'border-gray-200'">
                            <input
                                type="radio"
                                value="remesa"
                                v-model="paymentType"
                                class="h-4 w-4 text-blue-600 focus:ring-blue-500"
                            />
                            <div class="ml-3 flex-1">
                                <div class="flex flex-col">
                                    <span class="font-semibold text-gray-900">💵 Ahorro para la construcción</span>
                                    <span class="text-xs text-blue-600 mt-1">(Remesa internacional)</span>
                                </div>
                                <p class="text-sm text-gray-600 mt-2 flex items-center justify-between">
                                    <span>MIGRANTE/PANCHO → FINSUS</span>
                                    <span class="text-xs text-gray-500">USD → MXN</span>
                                </p>
                            </div>
                        </label>

                        <label class="flex items-center rounded-lg border-2 p-4 cursor-pointer transition hover:bg-green-50"
                               :class="paymentType === 'compra' ? 'border-green-600 bg-green-50' : 'border-gray-200'">
                            <input
                                type="radio"
                                value="compra"
                                v-model="paymentType"
                                class="h-4 w-4 text-green-600 focus:ring-green-500"
                            />
                            <div class="ml-3 flex-1">
                                <div class="flex flex-col">
                                    <span class="font-semibold text-gray-900">🛒 Compra de materiales</span>
                                    <span class="text-xs text-green-600 mt-1">(Dispersión local)</span>
                                </div>
                                <p class="text-sm text-gray-600 mt-2 flex items-center justify-between">
                                    <span>FINSUS → MERCHANT</span>
                                    <span class="text-xs text-gray-500">MXN → MXN</span>
                                </p>
                            </div>
                        </label>
                    </div>

                    <!-- Amount Input -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            {{ paymentType === 'remesa' ? 'Monto a recibir en MXN' : 'Monto a pagar en MXN' }}
                        </label>
                        <div class="relative">
                            <span class="absolute left-3 top-3 text-gray-500">$</span>
                            <input
                                v-model="amount"
                                type="number"
                                step="0.01"
                                class="w-full rounded-lg border border-gray-300 py-2 pl-8 pr-16 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500"
                                placeholder="15.00"
                            />
                            <span class="absolute right-3 top-3 text-gray-500">MXN</span>
                        </div>
                        <p class="mt-2 text-sm text-gray-500">
                            Monto en centavos: {{ amountInCents }}
                        </p>
                    </div>

                    <!-- Info Box -->
                    <div class="rounded-lg p-4"
                         :class="paymentType === 'remesa' ? 'bg-blue-50' : 'bg-green-50'">
                        <p class="text-sm"
                           :class="paymentType === 'remesa' ? 'text-blue-900' : 'text-green-900'">
                            <strong>ℹ️ Información:</strong><br />
                            <template v-if="paymentType === 'remesa'">
                                • Enviarás USD desde tu cuenta PANCHO (migrante) 🇺🇸<br />
                                • FINSUS recibirá {{ displayAmount }} MXN para tu ahorro 🇲🇽<br />
                                • Conversión automática USD → MXN<br />
                                • <strong>Ideal para:</strong> Guardar para tu proyecto de construcción
                            </template>
                            <template v-else>
                                • Pagarás {{ displayAmount }} MXN desde tu cuenta FINSUS<br />
                                • El MERCHANT recibirá {{ displayAmount }} MXN<br />
                                • Pago directo en pesos mexicanos (MXN → MXN)<br />
                                • <strong>Ideal para:</strong> Comprar materiales de construcción
                            </template>
                        </p>
                    </div>

                    <!-- Submit Button -->
                    <button
                        @click="startPayment"
                        class="w-full rounded-lg py-3 font-semibold text-white transition focus:outline-none focus:ring-4"
                        :class="paymentType === 'remesa' 
                            ? 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-300' 
                            : 'bg-green-600 hover:bg-green-700 focus:ring-green-300'"
                    >
                        {{ paymentType === 'remesa' ? '💰 Enviar Ahorro' : '🛒 Comprar Materiales' }}
                    </button>
                </div>

                <!-- Loading state -->
                <div v-else class="space-y-4 text-center">
                    <div class="flex justify-center">
                        <div class="h-12 w-12 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent"></div>
                    </div>
                    <p class="text-gray-600">{{ loadingMessage }}</p>
                </div>

                <!-- Error message -->
                <div v-if="error" class="mt-4 rounded-lg bg-red-50 p-4">
                    <p class="text-sm text-red-800">❌ {{ error }}</p>
                </div>
            </div>

            <!-- Back button -->
            <div class="mt-6 text-center">
                <NuxtLink
                    to="/payments"
                    class="text-indigo-600 hover:text-indigo-800 hover:underline"
                >
                    ← Volver al inicio
                </NuxtLink>
            </div>
        </div>
    </main>
</template>

<script setup lang="ts">
import { apiOpenPayments } from "@/api"

const paymentType = ref<'remesa' | 'compra'>('remesa')
const amount = ref("15.00")
const loading = ref(false)
const loadingMessage = ref("")
const error = ref("")

const amountInCents = computed(() => {
    const num = parseFloat(amount.value)
    return isNaN(num) ? "0" : Math.round(num * 100).toString()
})

const displayAmount = computed(() => {
    return parseFloat(amount.value || "0").toFixed(2)
})

async function startPayment() {
    try {
        loading.value = true
        loadingMessage.value = "Iniciando pago..."
        error.value = ""

        console.log('🚀 Iniciando pago:', paymentType.value, 'monto:', amountInCents.value)

        let data, fetchError

        if (paymentType.value === 'remesa') {
            const result = await apiOpenPayments.startMigrantePayment(amountInCents.value)
            data = result.data
            fetchError = result.error
        } else {
            const result = await apiOpenPayments.startPurchasePayment(amountInCents.value)
            data = result.data
            fetchError = result.error
        }

        console.log('📊 Respuesta:', { data: data.value, error: fetchError.value })

        if (fetchError.value) {
            console.error('❌ Error en fetch:', fetchError.value)
            throw new Error(`Error del servidor: ${fetchError.value.statusCode || 'desconocido'} - ${fetchError.value.message || fetchError.value.data || 'Error desconocido'}`)
        }
        
        if (!data.value) {
            throw new Error("No se recibió respuesta del servidor")
        }

        console.log('✅ Redirigiendo a:', data.value.redirect_url)
        loadingMessage.value = "Redirigiendo a Interledger..."
        
        // Redirigir a Interledger para autorización
        window.location.href = data.value.redirect_url
    } catch (e: any) {
        loading.value = false
        error.value = e.message || "Error desconocido"
        console.error("💥 Error completo:", e)
    }
}
</script>

