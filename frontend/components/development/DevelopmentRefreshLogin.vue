<template>
    <button type="button" @click="refresh"
        class="inline-flex items-center gap-x-1.5 rounded-md bg-hops-600 px-2.5 py-1.5 text-sm font-semibold text-white shadow-xs hover:bg-hops-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-hops-600 dark:bg-hops-500 dark:shadow-none dark:hover:bg-hops-400 dark:focus-visible:outline-hops-500">
        <ArrowPathRoundedSquareIcon class="-ml-0.5 size-5" aria-hidden="true" />
        Refresh auth
    </button>
</template>

<script setup lang="ts">
    import { ArrowPathRoundedSquareIcon } from '@heroicons/vue/20/solid'
    import { useAuthStore } from "@/stores/auth"
    import { useCreatorStore } from "@/stores/creator"

    const { locale } = useI18n()
    const authStore = useAuthStore()
    const creatorStore = useCreatorStore()

    async function refresh() {
        if (authStore.loggedIn) {
            await creatorStore.getActors(locale.value)
        }
    }

</script>