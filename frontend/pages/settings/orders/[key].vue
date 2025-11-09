<template>
    <div>
        <div class="mx-auto lg:grid lg:grid-cols-3 lg:gap-x-4 py-10 lg:pb-3">
            <!-- Actor details -->
            <div class="col-span-2">
                <div class="flex items-center gap-x-4">
                    <img v-if="actor.iconURL" class="size-24 rounded-full" :src="actor.iconURL as string"
                        :alt="actorRoute" />
                    <img v-else class="size-24 rounded-full" src="/images/hops/default_avatar.jpg"
                        alt="Fallback image" />
                    <div>
                        <h1 class="text-xl font-bold tracking-tight text-gray-900 sm:text-2xl">{{ actor.name }}</h1>
                        <ActorCopyableLink :actorURI="actorRoute" />
                        <div class="flex items-center ml-1 text-xs text-gray-500">
                            <span>{{ actor.followersCount ? readableNumber(actor.followersCount as number) : 0 }}
                                followers</span>
                            <span class="text-sm text-gray-400 px-1">&middot;</span>
                            <span>{{ actor.followingCount ? readableNumber(actor.followingCount as number) : 0 }}
                                following</span>
                            <span class="text-sm text-gray-400 px-1">&middot;</span>
                            <span>{{ actor.statusCount ? readableNumber(actor.statusCount as number) : 0 }} posts</span>
                        </div>
                    </div>
                </div>
                <section class="mt-4 max-w-full">
                    <div class="text-base text-gray-500" v-html="actor.summary"></div>
                </section>
            </div>
            <!-- Standout image -->
            <div class="self-start lg:justify-self-end lg:ml-2 lg:pl-2 xl:pl-0">
                <div class="mt-10 lg:mt-0 w-full hidden lg:block">
                    <img v-if="actor.standoutURL" :src="actor.standoutURL as string" :alt="actorRoute"
                        class="aspect-square w-full rounded-lg object-cover" />
                    <img v-else src="/images/hops/meg-macdonald-Z3AbEf69nA8-unsplash.jpg" alt="Fallback image"
                        class="aspect-square w-full rounded-lg object-cover" />
                </div>
            </div>
        </div>
        <div v-if="actor.attachment && actor.attachment.length">
            <ul role="list" class="list-disc space-y-1 pl-5 text-sm/6 text-gray-500 marker:text-gray-300">
                <li v-for="item in actor.attachment" :key="item.name" class="pl-2">
                    <span>{{ item.name }} | </span>
                    <span v-html="stripInvisibility(item.value)"
                        class="text-hops-500 hover:text-hops-900 visited:text-hops-300"></span>
                </li>
            </ul>
        </div>
        <!-- Persona management -->
        <div class="flex justify-between flex-row-reverse mb-4">
            <!--- Edit panel, if owned -->
            <ActorEditPanel v-if="canModify" />
            <!--- Else Follow panel, if not owned -->
            <ActorFollowPanel v-else :actor="actor" />
            <!--- List of Creator Works, if exist -->
            <ActorPersonaList
                v-if="actorType === 'persona' && ((actor.works && actor.works.length) || creatorStore.hasActor(actor.id))"
                list-type="work" :actor-links="actorStore.associations" :show-add="canModify" :actor_id="actor.id" />
            <!--- List of Contributors, if exist -->
            <ActorPersonaList v-if="actorType === 'work' && actor.maker_id && creatorStore.hasActor(actor.maker_id)"
                :list-type="listPanelType" :actor-links="actorStore.associations" :show-add="false"
                :actor_id="actor.id" />
        </div>
        <!-- Tab panel -->
        <div>
            <div class="border-b border-gray-200 dark:border-white/10">
                <div class="-mb-px flex space-x-8 focus:outline-none focus:ring-0">
                    <button v-for="tab in tabs" :key="tab.name" @click="fetchRemotePosts(tab.name, tab.to)" :class="[
                        tab.selected ?
                            'border-hops-500 text-hops-600 dark:border-hops-400 dark:text-hops-400' :
                            'border-transparent text-gray-500 hover:border-gray-200 hover:text-gray-700 dark:text-gray-400 dark:hover:border-white/20 dark:hover:text-white',
                        'cursor-pointer flex border-b-2 px-1 py-4 text-sm font-medium whitespace-nowrap']">
                        {{ tab.name }}
                    </button>
                </div>
            </div>
        </div>
        <!-- Statuses, including featured statuses -->
        <div>
            <!-- Products -->
            <section aria-labelledby="products-heading" class="mt-10">
                <h2 id="products-heading" class="sr-only">Product options</h2>
                <div class="grid grid-cols-1 gap-2">
                    <div v-for="product in products" :key="product.id"
                        class="cursor-pointer rounded-lg p-1 border border-gray-200 bg-gray-50 hover:bg-gray-100 hover:border-gray-500">
                        <div class="flex items-center justify-between px-2">
                            <div class="flex items-center">
                                <ArrowDownTrayIcon class="size-4 text-gray-900 mr-2" aria-hidden="true" />
                                <span class="text-sm font-medium text-gray-900">{{ product.name }} - </span>
                                <span class="text-sm text-gray-500">{{ product.description }}</span>
                            </div>
                            <span class="text-sm font-medium text-gray-900 shrink">
                                ({{ product.volume }}) {{ product.currency }}{{ product.price }}
                            </span>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ArrowDownTrayIcon } from "@heroicons/vue/24/outline"
    import type { IActorProfile, IKeyable, IStatus } from "@/interfaces"
    import { useAuthStore } from "@/stores/auth"
    import { useCreatorStore } from "@/stores/creator"
    import { useActorStore } from "@/stores/actor"
    import { useTokenStore } from "@/stores/tokens"
    import { readableNumber } from "@/utilities"

    definePageMeta({
        middleware: ["refresh"],
    });

    const { t, locale } = useI18n()
    const route = useRoute()

    const creatorStore = useCreatorStore()
    const actorStore = useActorStore()
    const actor = ref<IActorProfile>({} as IActorProfile)
    const maker = ref<IActorProfile>({} as IActorProfile)
    const actorRoute = ref("")
    const extractor = useExtractor()
    const actorType = ref("")
    const canModify = ref(false)
    const listPanelType = ref("")
    const tabs = ref([] as IKeyable[])
    const handle = ref("")
    const statuses = ref([] as IStatus[])
    const featured = ref([] as IStatus[])

    const products: IKeyable[] = [
        { id: "01K66D4JD67CRDXV750450V6P4", name: "Bulk", description: "5 kg, vaccuum-sealed for freshness.", volume: 2, price: 51, currency: "€" },
    ]

    function stripInvisibility(html: string) {
        return html.replace("class=\"invisible\"", "class=\"hidden\"")
    }

    async function fetchRemotePosts(name: string, url: string) {
        for (const item of tabs.value) {
            item.selected = false
            if (item.name === name) item.selected = true
        }
    }

    onMounted(async () => {
        // lookup the actor
        handle.value = "francehops@mollusk-modest-sharply.ngrok-free.app"
        if (!actorStore.hasActor(handle.value)) await actorStore.lookupActor(handle.value, locale.value)
        if (actorStore.hasActor(handle.value)) {
            actor.value = actorStore.actors[handle.value] as IActorProfile
            if (actor.value.summary) {
                actor.value.summary = extractor.localiseSummary(actor.value.summary, actor.value.URL as string, "font-medium text-hops-500 hover:text-hops-600 visited:font-normal")
            }
            actorRoute.value = `${actor.value.preferredUsername}`
            if (actor.value.domain) actorRoute.value = `${actor.value.preferredUsername}@${actor.value.domain}`
            if (actor.value.type === "Service") {
                actorType.value = "work"
                canModify.value = creatorStore.hasWork(actor.value.id)
                if (actor.value.maker_id) maker.value = creatorStore.getMaker(actor.value.maker_id as string) as IActorProfile
                listPanelType.value = "contributor"
                tabs.value.push({
                    name: t("commerce.purchases"),
                    to: actor.value.works,
                    selected: true
                })
            }
        } else {
            throw createError({
                statusCode: 404,
                message: t("notfound.actor"),
            })
        }
    })
</script>
