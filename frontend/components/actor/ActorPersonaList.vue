<template>
    <div class="flex">
        <p class="text-sm font-medium text-gray-700 dark:text-gray-300 self-center justify-self-end mr-2">
            {{ t(listName) }}
        </p>
        <div v-if="actorLinks && actorLinks.length" class="isolate flex -space-x-1 overflow-hidden">
            <NuxtLinkLocale v-for="link, idx in actorList.slice(0, 3)" :key="link.id"
                :to="`/@${link.preferredUsername}@${link.domain}`" class="-space-x-1">
                <img v-if="link.iconURL"
                    :class="`relative -z-[${idx * 10}] inline-block size-8 rounded-full ring-2 ring-white outline -outline-offset-1 outline-black/5 dark:ring-gray-900 dark:outline-white/10`"
                    :src="link.iconURL" :alt="link.name" />
                <img v-else
                    :class="`relative -z-[${idx * 10}] inline-block size-8 rounded-full ring-2 ring-white outline -outline-offset-1 outline-black/5 dark:ring-gray-900 dark:outline-white/10`"
                    src="/images/hops/default_avatar.jpg" :alt="link.name" />
            </NuxtLinkLocale>
        </div>
        <NuxtLinkLocale v-if="actorLinks && actorLinks.length" to="/more"
            class="-space-x-1 self-center justify-self-end ml-0.5">
            <button type="button" :aria-label="t('actor.more')"
                class="cursor-pointer align-middle rounded-full bg-white p-1 text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:shadow-none dark:inset-ring-white/5 dark:hover:bg-white/20">
                <ArrowLongRightIcon class="size-4" aria-hidden="true" />
            </button>
        </NuxtLinkLocale>
        <ActorCreatePersonaModal v-if="showAdd && listType === 'work'" :maker_id="actor_id" />
    </div>
</template>

<script setup lang="ts">
    import { ArrowLongRightIcon } from "@heroicons/vue/24/outline"
    import type { IWorkSnapshot } from "@/interfaces"

    const { t } = useI18n()
    const actorStore = useActorStore()
    const props = defineProps<{
        listType: string,
        actorLinks?: string[],
        showAdd?: boolean,
        actor_id: string,
    }>()
    const listName = ref("")
    const actorList = ref<IWorkSnapshot[]>([])

    function findActor(id: string) {
        let actorArray = Object.keys(actorStore.actors).map((k) => actorStore.actors[k]) as IWorkSnapshot[]
        if (actorArray && actorArray.length) return actorArray.find((item) => item.id === id)
        return null
    }

    onMounted(async () => {
        if (actorStore.associations && actorStore.associations.length) {
            for (const id of actorStore.associations) {
                const association = findActor(id) as IWorkSnapshot
                if (association) {
                    actorList.value.push(association)

                }
            }
        }
        switch (props.listType) {
            case "work":
                listName.value = "actor.works"
                break
            case "contributor":
                listName.value = "actor.contributors"
                break
            case "persona":
                listName.value = "actor.personas"
                break
        }
    })

</script>