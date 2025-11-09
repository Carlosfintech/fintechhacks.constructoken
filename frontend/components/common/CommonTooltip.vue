<template>
    <div id="tooltip-default" role="tooltip"
        class="pointer-events-none absolute -left-20 top-0 translate-y-full w-48 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700 opacity-0 transition-opacity group-hover:opacity-100">
        {{ text }}
    </div>
</template>

<script setup lang="ts">
    defineProps<{ text: string }>()
</script>
