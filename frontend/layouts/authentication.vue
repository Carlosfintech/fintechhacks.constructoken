<template>
    <Html :lang="htmlAttrs.lang" :dir="htmlAttrs.dir">
        <Body>
            <div class="h-full">
                <slot />
                <slot name="footer" >
                    <LayoutsNotification />
                </slot>
            </div>
        </Body>
    </Html>
</template>

<script setup lang="ts">
const head = useLocaleHead({
    dir: true,
    seo: true,
})
const htmlAttrs = computed(() => head.value.htmlAttrs!)
</script>