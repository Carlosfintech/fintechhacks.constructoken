<template>
    <main class="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 py-12 px-4">
        <div class="mx-auto max-w-md">
            <div class="rounded-2xl bg-white p-8 shadow-xl">
                <!-- Header -->
                <div class="mb-6 text-center">
                    <h1 class="text-3xl font-bold text-gray-900">🏗️ Compra de Materiales</h1>
                    <p class="mt-2 text-gray-600">FINSUS (MXN) → MERCHANT (MXN)</p>
                </div>

                <!-- Form -->
                <div v-if="!loading" class="space-y-6">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Monto a pagar en MXN
                        </label>
                        <div class="relative">
                            <span class="absolute left-3 top-3 text-gray-500">$</span>
                            <input
                                v-model="amount"
                                type="number"
                                step="0.01"
                                class="w-full rounded-lg border border-gray-300 py-2 pl-8 pr-16 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500"
                                placeholder="15.00"
                            />
                            <span class="absolute right-3 top-3 text-gray-500">MXN</span>
                        </div>
                        <p class="mt-2 text-sm text-gray-500">
                            Monto en centavos: {{ amountInCents }}
                        </p>
                    </div>

                    <div class="rounded-lg bg-green-50 p-4">
                        <p class="text-sm text-green-900">
                            <strong>ℹ️ Información:</strong><br />
                            • Pagarás desde tu cuenta FINSUS (MXN)<br />
                            • El Merchant recibirá {{ displayAmount }} MXN<br />
                            • Sin conversión de moneda
                        </p>
                    </div>

                    <button
                        @click="startPayment"
                        class="w-full rounded-lg bg-emerald-600 py-3 font-semibold text-white transition hover:bg-emerald-700 focus:outline-none focus:ring-4 focus:ring-emerald-300"
                    >
                        🛒 Pagar Materiales
                    </button>
                </div>

                <!-- Loading state -->
                <div v-else class="space-y-4 text-center">
                    <div class="flex justify-center">
                        <div class="h-12 w-12 animate-spin rounded-full border-4 border-emerald-600 border-t-transparent"></div>
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
                <button
                    @click="$router.push('/')"
                    class="text-emerald-600 hover:text-emerald-800"
                >
                    ← Volver al inicio
                </button>
            </div>
        </div>
    </main>
</template>

<script setup lang="ts">
import { apiOpenPayments } from "@/api"

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

        const { data, error: fetchError } = await apiOpenPayments.startPurchasePayment(amountInCents.value)

        if (fetchError.value || !data.value) {
            throw new Error(fetchError.value?.message || "Error al iniciar el pago")
        }

        loadingMessage.value = "Redirigiendo a Interledger..."
        
        // Redirigir a Interledger para autorización
        window.location.href = data.value.redirect_url
    } catch (e: any) {
        loading.value = false
        error.value = e.message || "Error desconocido"
        console.error("Error:", e)
    }
}
</script>

