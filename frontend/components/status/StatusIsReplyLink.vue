<template>
    <div
        :class="[isShare ? 'ml-8' : 'ml-5', 'cursor-pointer flex text-xs items-center w-fit p-1 text-hops-500 hover:bg-gray-100 hover:rounded-md']">
        <ChatBubbleLeftRightIcon class="size-4 mr-1" aria-hidden="true" />
        {{ t("status.inreply") }}
    </div>
</template>

<script setup lang="ts">
    import { ChatBubbleLeftRightIcon } from "@heroicons/vue/24/outline"

    const { t } = useI18n()
    const props = defineProps<{
        isShare: boolean,
        replyURI: string
    }>()
</script>