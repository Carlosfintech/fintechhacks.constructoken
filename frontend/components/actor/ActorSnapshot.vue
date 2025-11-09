<template>
    <!-- Product snapshot for use in grids -->
    <div>
        <img class="aspect-4/5 w-52 flex-none rounded-2xl bg-gray-200 object-cover group-hover:opacity-75"
            :src="actor.iconUrl as string" :alt="actor.iconAlt" />
        <div class="max-w-xl flex-auto">
            <NuxtLinkLocale :to="actorRoute" class="group">
                <h3 class="text-lg/8 font-semibold tracking-tight text-gray-900" v-html="actor.name"></h3>
                <p class="text-base/7 text-gray-600">@{{ actor.preferredUsername }}<span v-if="actor.domain">@{{
                    actor.domain }}</span></p>
            </NuxtLinkLocale>
            <p class="mt-6 text-base/7 text-gray-600" v-html="actor.summary"></p>
        </div>
    </div>
</template>

<script setup lang="ts">
    import type { APActor } from "activitypub-types"
    import type { IWellKnownActor } from "@/interfaces"

    const props = defineProps<{ source: APActor }>()
    const actor = ref<IWellKnownActor>({} as IWellKnownActor)
    const actorRoute = ref("")
    const extractor = useExtractor()

    onMounted(async () => {
        actor.value = extractor.getSnapshot(props.source)
        if (actor.value.summary) {
            actor.value.summary = extractor.localiseSummary(actor.value.summary, actor.value.url as string, "font-medium text-hops-500 hover:text-hops-600 visited:font-normal")
        }
        actorRoute.value = `/@${actor.value.preferredUsername}`
        if (actor.value.domain) actorRoute.value = `/@${actor.value.preferredUsername}@${actor.value.domain}`
    })
</script>