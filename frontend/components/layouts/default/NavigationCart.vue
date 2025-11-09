<template>
    <div class="mt-2 grid grid-cols-1">
        <input type="text" name="search" id="search"
            class="col-start-1 row-start-1 block w-full rounded-md border border-gray-300 placeholder-gray-400 shadow-sm focus-within:border-hops-600 focus-within:outline-none focus-within:ring-hops-600 sm:text-sm"
            aria-invalid="true" />
        <MagnifyingGlassIcon
            class="pointer-events-none col-start-1 row-start-1 mr-3 size-5 self-center justify-self-end text-gray-400 sm:size-4"
            aria-hidden="true" />
    </div>
</template>

<script setup lang="ts">
    import { ShoppingCartIcon } from "@heroicons/vue/24/outline"
    const currencies = ['CAD', 'USD', 'AUD', 'EUR', 'GBP']
</script>