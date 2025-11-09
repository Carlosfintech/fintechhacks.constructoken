<template>
    <main class="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 py-12 px-4">
        <div class="mx-auto w-full max-w-md">
            <div class="rounded-2xl bg-white p-8 shadow-xl text-center">
                <!-- Loading state -->
                <div v-if="processing" class="space-y-4">
                    <div class="flex justify-center">
                        <div class="h-16 w-16 animate-spin rounded-full border-4 border-emerald-600 border-t-transparent"></div>
                    </div>
                    <h2 class="text-2xl font-bold text-gray-900">Procesando pago...</h2>
                    <p class="text-gray-600">{{ statusMessage }}</p>
                </div>

                <!-- Success state -->
                <div v-else-if="success" class="space-y-4">
                    <div class="flex justify-center">
                        <div class="flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
                            <span class="text-3xl">✅</span>
                        </div>
                    </div>
                    <h2 class="text-2xl font-bold text-green-600">¡Compra Completada!</h2>
                    <div class="rounded-lg bg-green-50 p-4 text-left">
                        <p class="text-sm text-green-900">
                            <strong>Pago exitoso:</strong><br />
                            • De: FINSUS (MXN) 🇲🇽<br />
                            • A: MERCHANT (MXN) 🇲🇽<br />
                            • Transaction ID: {{ route.params.transaction_id }}<br />
                            • Status: COMPLETED ✅
                        </p>
                    </div>
                    <button
                        @click="$router.push('/caso2')"
                        class="w-full rounded-lg bg-emerald-600 py-3 font-semibold text-white transition hover:bg-emerald-700"
                    >
                        Hacer otra compra
                    </button>
                </div>

                <!-- Error state -->
                <div v-else class="space-y-4">
                    <div class="flex justify-center">
                        <div class="flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
                            <span class="text-3xl">❌</span>
                        </div>
                    </div>
                    <h2 class="text-2xl font-bold text-red-600">Error en el pago</h2>
                    <div class="rounded-lg bg-red-50 p-4">
                        <p class="text-sm text-red-800">{{ errorMessage }}</p>
                    </div>
                    <button
                        @click="$router.push('/caso2')"
                        class="w-full rounded-lg bg-gray-600 py-3 font-semibold text-white transition hover:bg-gray-700"
                    >
                        Intentar de nuevo
                    </button>
                </div>
            </div>
        </div>
    </main>
</template>

<script setup lang="ts">
import { apiOpenPayments } from "@/api"

const route = useRoute()
const processing = ref(true)
const success = ref(false)
const statusMessage = ref("Verificando autorización...")
const errorMessage = ref("")
const hasRun = ref(false) // Prevenir ejecución múltiple

onMounted(async () => {
    // Prevenir llamadas duplicadas
    if (hasRun.value) {
        console.log("⚠️ onMounted ya ejecutado, ignorando...")
        return
    }
    hasRun.value = true
    const transaction_id = route.params.transaction_id as string
    const hash = route.query.hash as string
    const interact_ref = route.query.interact_ref as string

    console.log("Transaction ID:", transaction_id)
    console.log("Hash:", hash)
    console.log("Interact Ref:", interact_ref)

    if (!transaction_id || !hash || !interact_ref) {
        processing.value = false
        errorMessage.value = "Faltan parámetros requeridos (transaction_id, hash, interact_ref)"
        return
    }

    try {
        statusMessage.value = "Completando el pago..."
        
        console.log("🚀 Llamando a completePurchasePayment con:", {
            transaction_id,
            hash,
            interact_ref
        })
        
        // Usar $fetch en lugar de useFetch en onMounted
        const config = useRuntimeConfig()
        const url = `${config.public.apiUrl}/v1/payments/purchase/callback?transaction_id=${transaction_id}&hash=${encodeURIComponent(hash)}&interact_ref=${interact_ref}`
        
        console.log("📡 URL:", url)
        
        const data = await $fetch(url, {
            method: "GET"
        })

        console.log("📊 Respuesta del backend:", data)

        if (!data) {
            throw new Error("No se recibió respuesta del servidor")
        }

        // Pago exitoso
        processing.value = false
        success.value = true
        console.log("✅ Payment completed:", data)
        
    } catch (error: any) {
        processing.value = false
        success.value = false
        errorMessage.value = error.message || "Error desconocido al procesar el pago"
        console.error("Error completing payment:", error)
    }
})
</script>

