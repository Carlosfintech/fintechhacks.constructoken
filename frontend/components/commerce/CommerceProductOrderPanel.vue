<template>
    <div>
        <!-- Products -->
        <section aria-labelledby="products-heading" class="mt-10">
            <h2 id="products-heading" class="sr-only">Product options</h2>
            <div class="grid grid-cols-1 gap-2">
                <div v-for="product in products" @click="watchProductSelect(product.id)" :key="product.id" :class="[
                    selected === product.id ?
                        'border-hops-600 bg-hops-100' :
                        'border-gray-200 bg-gray-50 hover:bg-gray-100 hover:border-gray-500',
                    'cursor-pointer rounded-lg p-1 border']">
                    <div class="flex">
                        <div>
                            <span class="text-sm font-medium text-gray-900">{{ product.name }} - </span>
                            <span class="text-sm text-gray-500">{{ product.description }}</span>
                        </div>
                        <span class="text-sm font-medium text-gray-900 shrink">
                            {{ product.currency }}{{ product.price }}
                        </span>
                    </div>
                </div>
            </div>
        </section>
        <!-- Buy -->
        <div class="shrink-0 flex gap-x-3 mt-2 justify-end">
            <div
                class="flex items-center rounded-md border border-gray-300 placeholder-gray-400 shadow-sm focus-within:border-hops-600 focus-within:outline-none focus-within:ring-hops-600 sm:text-sm">
                <div class="cursor-pointer px-2">
                    <MinusIcon @click="watchVolumeChange(-1)"
                        class="size-4 self-center text-gray-400 hover:text-gray-800 dark:text-gray-500 outline-none"
                        aria-hidden="true" />
                </div>
                <div
                    class="block min-w-0 grow px-2 border-transparent rounded-l-md focus:border-transparent focus:outline-none focus:ring-transparent sm:text-sm/6">
                    {{ volume }}</div>
                <div class="cursor-pointer px-2">
                    <PlusIcon @click="watchVolumeChange(1)"
                        class="size-4 self-center text-gray-400 hover:text-gray-800 dark:text-gray-500 outline-none"
                        aria-hidden="true" />
                </div>
            </div>
            <CommercePurchaseOrderModal :product_id="selected" :volume="volume" />
        </div>
    </div>
</template>

<script setup lang="ts">
    import { PlusIcon, MinusIcon } from "@heroicons/vue/24/outline"
    import { useToastStore } from "@/stores/toasts"
    import { useActorStore } from "@/stores/actor"
    import type { IKeyable } from "@/interfaces"
    import CommercePurchaseOrderModal from "./CommercePurchaseOrderModal.vue"

    const { t } = useI18n()
    const toast = useToastStore()
    const actorStore = useActorStore()
    const selected = ref<string>("")
    const volume = ref<number>(1)

    const products: IKeyable[] = [
        { id: "01K24SCPT4JG59FYRVE5RXPX7J", name: "Standard", description: "1 kg, vaccuum-sealed for freshness.", price: 15, currency: "€" },
        { id: "01K66D4JD67CRDXV750450V6P4", name: "Bulk", description: "5 kg, vaccuum-sealed for freshness.", price: 25, currency: "€" },
    ]

    function watchVolumeChange(change: number) {
        if (volume.value > 0 && change === -1) {
            volume.value -= 1
        }
        if (change === 1) {
            volume.value += 1
        }
    }

    function watchProductSelect(choice: string) {
        if (selected.value !== choice) {
            volume.value = 1
        }
        selected.value = choice
    }

    onMounted(async () => {
    })
</script>