<template>
    <button class="inline-flex items-center rounded-full cursor-pointer" @click="replytoStatus">
        <ChatBubbleLeftIcon
            class="size-4 rounded-full hover:text-hops-500 hover:bg-hops-100 hover:ring-hops-100 hover:ring-2"
            aria-hidden="true" />
        <span v-if="status.repliesCount" class="text-xs ml-0.5 text-gray-600">
            {{ readableNumber(status.repliesCount) }}
        </span>
    </button>
</template>

<script setup lang="ts">
    import { ChatBubbleLeftIcon } from "@heroicons/vue/24/outline"
    import type { IStatusPost } from "@/interfaces"
    import { readableNumber } from "@/utilities"

    const { t } = useI18n()

    async function replytoStatus() {
        console.log("Replying")
    }

    const props = defineProps<{
        status: IStatusPost
    }>()
</script>