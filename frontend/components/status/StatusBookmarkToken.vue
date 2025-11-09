<template>
    <button class="inline-flex items-center rounded-full cursor-pointer" @click="toggleBookmark">
        <BookmarkIconSolid v-if="status.has_bookmarked"
            class="size-4 rounded-full text-autumn-500 hover:bg-autumn-100 hover:ring-autumn-100 hover:ring-2"
            aria-hidden="true" />
        <BookmarkIcon v-else
            class="size-4 rounded-full hover:text-autumn-500 hover:bg-autumn-100 hover:ring-autumn-100 hover:ring-2"
            aria-hidden="true" />
    </button>
</template>

<script setup lang="ts">
    import { BookmarkIcon } from "@heroicons/vue/24/outline"
    import { BookmarkIcon as BookmarkIconSolid } from "@heroicons/vue/20/solid"
    import type { IStatusPost } from "@/interfaces"

    const { t } = useI18n()

    async function toggleBookmark() {
        console.log("Toggled")
    }

    const props = defineProps<{
        status: IStatusPost
    }>()
</script>