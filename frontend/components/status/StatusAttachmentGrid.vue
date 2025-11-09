<template>
    <div class="my-2 mx-10">
        <div v-if="attachments.length === 1 && attachments[0]">
            <StatusAttachmentPanel :attachment="attachments[0]" />
        </div>
        <div v-else class="grid grid-cols-2 gap-4">
            <StatusAttachmentPanel v-for="attachment in attachments" :key="attachment.url" :attachment="attachment" />
        </div>
    </div>
</template>

<script setup lang="ts">
    const props = defineProps<{
        attachments: {
            [key: string]: any | any[]
        }[]
    }>()
</script>