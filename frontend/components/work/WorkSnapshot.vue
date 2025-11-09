<template>
    <!-- Product snapshot for use in grids -->
    <a :href="product.url as string" class="group">
        <img :src="product.imageUrl as string" :alt="product.imageAlt"
            class="aspect-square w-full rounded-lg bg-gray-200 object-cover group-hover:opacity-75 xl:aspect-7/8" />
        <h3 class="mt-4 text-sm text-gray-700">{{ product.name }}</h3>
        <p class="text-sm text-gray-500">{{ product.summary }}</p>
        <div class="flex flex-1 flex-col justify-end">
            <p class="text-base font-medium text-gray-900">{{ product.price }}</p>
        </div>
    </a>
</template>

<script setup lang="ts">
    import type { APActor } from "activitypub-types"
    import type {
        IWellKnownActor,
    } from "~/interfaces"

    const props = defineProps<{ work: APActor }>()
    const product = ref<IWellKnownActor>({} as IWellKnownActor)
    const snapshot = useSnapshot()

    onMounted(async () => {
        product.value = snapshot.get(props.work)
    })
</script>
