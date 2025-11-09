<template>
    <button class="inline-flex items-center rounded-full cursor-pointer" @click="toggleShare">
        <ArrowPathRoundedSquareIconSolid v-if="status.has_shared"
            class="size-4 text-pelorous-500 rounded-full hover:bg-pelorous-100 hover:ring-pelorous-100 hover:ring-2"
            aria-hidden="true" />
        <ArrowPathRoundedSquareIcon v-else
            class="size-4 hover:text-pelorous-500 rounded-full hover:bg-pelorous-100 hover:ring-pelorous-100 hover:ring-2"
            aria-hidden="true" />
        <span v-if="status.sharesCount"
            :class="[status.has_shared ? 'text-pelorous-500' : 'text-gray-600', 'text-xs ml-0.5']">
            {{ readableNumber(status.sharesCount) }}
        </span>
    </button>
</template>

<script setup lang="ts">
    import { ArrowPathRoundedSquareIcon } from "@heroicons/vue/24/outline"
    import { ArrowPathRoundedSquareIcon as ArrowPathRoundedSquareIconSolid } from "@heroicons/vue/20/solid"
    import type { IStatusPost } from "@/interfaces"
    import { readableNumber } from "@/utilities"

    const { t } = useI18n()

    async function toggleShare() {
        console.log("Toggled")
    }

    const props = defineProps<{
        status: IStatusPost
    }>()
</script>