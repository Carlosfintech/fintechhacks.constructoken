<template>
    <button class="inline-flex items-center rounded-full cursor-pointer" @click="toggleLike">
        <HeartIconSolid v-if="status.has_liked"
            class="size-4 rounded-full text-thunderbird-500 hover:bg-thunderbird-100 hover:ring-thunderbird-100 hover:ring-2"
            aria-hidden="true" />
        <HeartIcon v-else
            class="size-4 rounded-full hover:text-thunderbird-500 hover:bg-thunderbird-100 hover:ring-thunderbird-100 hover:ring-2"
            aria-hidden="true" />
        <span v-if="status.likesCount"
            :class="[status.has_shared ? 'text-thunderbird-500' : 'text-gray-600', 'text-xs ml-0.5']">
            {{ readableNumber(status.likesCount) }}
        </span>
    </button>
</template>

<script setup lang="ts">
    import { HeartIcon } from "@heroicons/vue/24/outline"
    import { HeartIcon as HeartIconSolid } from "@heroicons/vue/20/solid"
    import type { IStatusPost } from "@/interfaces"
    import { readableNumber } from "@/utilities"

    const { t } = useI18n()

    async function toggleLike() {
        console.log("Toggled")
    }

    const props = defineProps<{
        status: IStatusPost
    }>()
</script>