<template>
    <div>
        <div class="mx-auto lg:grid lg:grid-cols-3 lg:gap-x-4 py-10 lg:pb-6">
            <!-- Actor details -->
            <div class="bg-amber-50 col-span-2">
                <div class="flex items-center gap-x-4">
                    <img class="size-24 rounded-full" :src="actor.iconURL as string" :alt="actorRoute" />
                    <div>
                        <h1 class="text-xl font-bold tracking-tight text-gray-900 sm:text-2xl">{{ actor.name }}</h1>
                        <ActorCopyableLink :actorURI="actorRoute" />
                        <div class="flex items-center ml-1 text-xs text-gray-500">
                            <span>{{ readableNumber(actor.followersCount as number) }} followers</span>
                            <span class="text-sm text-gray-400 px-1">&middot;</span>
                            <span>{{ readableNumber(actor.followingCount as number) }} following</span>
                            <span class="text-sm text-gray-400 px-1">&middot;</span>
                            <span>{{ readableNumber(actor.statusCount as number) }} posts</span>
                        </div>
                    </div>
                </div>
                <section class="mt-4 max-w-full">
                    <div class="text-base text-gray-500" v-html="actor.summary"></div>
                </section>
            </div>
            <!-- Standout image -->
            <div class="self-start justify-self-end mt-10 lg:mt-0 w-full md:ml-2 md:pl-2 xl:pl-0 hidden lg:block">
                <img v-if="actor.standoutURL" :src="actor.standoutURL as string" :alt="actorRoute"
                    class="aspect-square w-full rounded-lg object-cover" />
                <img v-else src="/images/hops/meg-macdonald-Z3AbEf69nA8-unsplash.jpg" alt="Fallback image"
                    class="aspect-square w-full rounded-lg object-cover" />
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
        <div v-if="actorType === 'persona'" class="flex justify-between flex-row-reverse">
            <!--- Edit panel, if owned -->
            <ActorEditPanel v-if="creatorStore.hasActor(actor.id)" />
            <!--- Else Follow panel, if not owned -->
            <ActorFollowPanel v-else />
            <!--- List of Creator Works, if exist -->
            <ActorPersonaList v-if="(actor.works && actor.works.length) || creatorStore.hasActor(actor.id)"
                list-type="work" :actor-links="actor.works" :show-add="canModify" />
        </div>
        <div class="flex justify-between flex-row-reverse">
            <!-- show-add="creatorStore.hasWork(actor.id)"-->
            <ActorPersonaList v-if="actor.works && actor.works.length" :list-type="listPanelType"
                :actor-links="actor.works" :show-add="true" />
            <div v-if="actor.works && actor.works.length" class="flex">
                <p class="text-sm font-medium text-gray-700 dark:text-gray-300 self-center justify-self-end mr-2">Works
                </p>
                <div class="isolate flex -space-x-1 overflow-hidden">
                    <NuxtLinkLocale :to="actor.URL" class="-space-x-1">
                        <img v-for="work, idx in actor.works.slice(0, 3)" :key="work.id"
                            :class="`relative -z-[${idx * 10}] inline-block size-8 rounded-full ring-2 ring-white outline -outline-offset-1 outline-black/5 dark:ring-gray-900 dark:outline-white/10`"
                            :src="work.iconURL" :alt="work.name" />
                    </NuxtLinkLocale>
                </div>
                <NuxtLinkLocale to="/more" class="-space-x-1 self-center justify-self-end ml-0.5">
                    <button type="button"
                        class="cursor-pointer align-middle rounded-full bg-white p-1 text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:shadow-none dark:inset-ring-white/5 dark:hover:bg-white/20">
                        <ArrowLongRightIcon class="size-4" aria-hidden="true" />
                    </button>
                </NuxtLinkLocale>
                <NuxtLinkLocale to="/more" class="-space-x-1 self-center justify-self-end mx-1">
                    <button type="button"
                        class="cursor-pointer align-middle rounded-full bg-white p-1 text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:shadow-none dark:inset-ring-white/5 dark:hover:bg-white/20">
                        <PlusIcon class="size-4" aria-hidden="true" />
                    </button>
                </NuxtLinkLocale>
                <NuxtLinkLocale to="/more" class="-space-x-1 self-center justify-self-end ml-1">
                    <button type="button"
                        class="rounded-full bg-white px-2.5 py-1 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:shadow-none dark:inset-ring-white/5 dark:hover:bg-white/20">
                        edit
                    </button>
                </NuxtLinkLocale>
            </div>
            <ActorFollowPanel />
        </div>
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
        <StatusPanel :actor="actor" :status="status" />
    </div>
</template>

<script setup lang="ts">
    import { TabGroup, TabList, Tab, TabPanels, TabPanel, Menu, MenuButton, MenuItem, MenuItems } from "@headlessui/vue"
    import { ArrowLongRightIcon, EllipsisHorizontalCircleIcon, PlusCircleIcon, PlusIcon, EllipsisHorizontalIcon } from "@heroicons/vue/24/outline"
    import type { IActorProfile, IKeyable } from "@/interfaces"
    import { useAuthStore } from "@/stores/auth"
    import { useCreatorStore } from "@/stores/creator"
    import { useTokenStore } from "@/stores/tokens"
    import { apiActivity, apiAuth } from "@/api"
    import { readableNumber, readableDate } from "@/utilities"

    definePageMeta({
        middleware: ["refresh"],
    });

    const { t, locale } = useI18n()
    const route = useRoute()

    const authStore = useAuthStore()
    const creatorStore = useCreatorStore()
    const tokenStore = useTokenStore()
    const actor = ref<IActorProfile>({} as IActorProfile)
    const actorRoute = ref("")
    const extractor = useExtractor()
    const actorType = ref("")
    const canModify = ref(false)
    const listPanelType = ref("")


    const actorNavigation = [
        { name: t("account.settings"), to: "/settings" },
    ]

    const tabs = ref([] as IKeyable[])

    const cactor = {
        "id": "01K2CSZ1WSS41XGQ1QXHYWF36K",
        "created": "2022-11-06T00:00:00Z",
        "type": "Person",
        "preferredUsername": "elizabethtasker",
        "name": "Elizabeth Tasker",
        "domain": "mastodon.online",
        "URI": "https://mastodon.online/users/elizabethtasker",
        "URL": "https://mastodon.online/@elizabethtasker",
        "iconURL": "https://files.mastodon.online/accounts/avatars/109/297/010/526/408/850/original/1823b15e74825a23.jpg",
        "standoutURL": "https://files.mastodon.online/accounts/headers/109/297/010/526/408/850/original/de5093efd515fea9.jpeg",
        "followersCount": 3253,
        "followingCount": 391,
        "statusCount": 4975,
        "lastStatus": "2025-08-11T14:14:27Z",
        "locked": false,
        "discoverable": true,
        "memorial": false,
        "language": "en",
        "summary": "<p>UK astrophysicist working at the Japan Aerospace Exploration Agency (JAXA). Author of 'The Planet Factory'. Very into planets, cats and virtual reality (sometimes together). @girlandkat on twitter.</p>",
        "attachment": [
            {
                "name": "Personal web",
                "type": "PropertyValue",
                "value": "<a href=\"https://girlandkat.com/\" target=\"_blank\" rel=\"me noreferrer nofollow noopener\" translate=\"no\"><span class=\"invisible\">https://</span><span>girlandkat.com/</span><span class=\"invisible\"></span></a>"
            }, {
                "name": "Professional web",
                "type": "PropertyValue",
                "value": "<a href=\"https://www.elizabethtasker.com/\" target=\"_blank\" rel=\"me noreferrer nofollow noopener\" translate=\"no\"><span class=\"invisible\">https://www.</span><span>elizabethtasker.com/</span><span class=\"invisible\"></span></a>"
            }, {
                "name": "The Planet Factory", "type": "PropertyValue", "value": "<a href=\"https://www.bloomsbury.com/uk/planet-factory-9781472917744/\" target=\"_blank\" rel=\"me noreferrer nofollow noopener\" translate=\"no\"><span class=\"invisible\">https://www.</span><span>bloomsbury.com/uk/planet-facto</span><span class=\"invisible\">ry-9781472917744/</span></a>"
            }, {
                "name": "Planetary Diversity",
                "type": "PropertyValue",
                "value": "<a href=\"https://store.ioppublishing.org/page/detail/Planetary-Diversity//?k=9780750321389\" target=\"_blank\" rel=\"me noreferrer nofollow noopener\" translate=\"no\"><span class=\"invisible\">https://</span><span>store.ioppublishing.org/page/d</span><span class=\"invisible\">etail/Planetary-Diversity//?k=9780750321389</span></a>"
            }
        ],
        "works": [
            {
                "id": "01K2CSZ1WSS41XGQ1QXHYWF36K",
                "created": "2022-11-06T00:00:00Z",
                "preferredUsername": "elizabethtasker",
                "name": "Elizabeth Tasker",
                "domain": "mastodon.online",
                "URI": "https://mastodon.online/users/elizabethtasker",
                "URL": "https://mastodon.online/@elizabethtasker",
                "iconURL": "https://files.mastodon.online/accounts/avatars/109/297/010/526/408/850/original/1823b15e74825a23.jpg",
                "standoutURL": "https://files.mastodon.online/accounts/headers/109/297/010/526/408/850/original/de5093efd515fea9.jpeg",
                "language": "en",
                "summary": "<p>UK astrophysicist working at the Japan Aerospace Exploration Agency (JAXA). Author of 'The Planet Factory'. Very into planets, cats and virtual reality (sometimes together). @girlandkat on twitter.</p>",
            },
            {
                "id": "01K2CSZ1WSS41XGQ1QXHYWF36K",
                "created": "2022-11-06T00:00:00Z",
                "preferredUsername": "elizabethtasker",
                "name": "Elizabeth Tasker",
                "domain": "mastodon.online",
                "URI": "https://mastodon.online/users/elizabethtasker",
                "URL": "https://mastodon.online/@elizabethtasker",
                "iconURL": "https://files.mastodon.online/accounts/avatars/109/297/010/526/408/850/original/1823b15e74825a23.jpg",
                "standoutURL": "https://files.mastodon.online/accounts/headers/109/297/010/526/408/850/original/de5093efd515fea9.jpeg",
                "language": "en",
                "summary": "<p>UK astrophysicist working at the Japan Aerospace Exploration Agency (JAXA). Author of 'The Planet Factory'. Very into planets, cats and virtual reality (sometimes together). @girlandkat on twitter.</p>",
            },
            {
                "id": "01K2CSZ1WSS41XGQ1QXHYWF36K",
                "created": "2022-11-06T00:00:00Z",
                "preferredUsername": "elizabethtasker",
                "name": "Elizabeth Tasker",
                "domain": "mastodon.online",
                "URI": "https://mastodon.online/users/elizabethtasker",
                "URL": "https://mastodon.online/@elizabethtasker",
                "iconURL": "https://files.mastodon.online/accounts/avatars/109/297/010/526/408/850/original/1823b15e74825a23.jpg",
                "standoutURL": "https://files.mastodon.online/accounts/headers/109/297/010/526/408/850/original/de5093efd515fea9.jpeg",
                "language": "en",
                "summary": "<p>UK astrophysicist working at the Japan Aerospace Exploration Agency (JAXA). Author of 'The Planet Factory'. Very into planets, cats and virtual reality (sometimes together). @girlandkat on twitter.</p>",
            },
        ],
        "default_persona": false,
        "is_following": null,
        "can_edit": null
    } as IKeyable

    function stripInvisibility(html: string) {
        return html.replace("class=\"invisible\"", "class=\"hidden\"")
    }

    async function fetchRemotePosts(name: string, url: string) {
        for (const item of tabs.value) {
            item.selected = false
            if (item.name === name) item.selected = true
        }
    }

    const status = {
        '@context': ['https://www.w3.org/ns/activitystreams',
            {
                'ostatus': 'http://ostatus.org#',
                'atomUri': 'ostatus:atomUri',
                'inReplyToAtomUri': 'ostatus:inReplyToAtomUri',
                'conversation': 'ostatus:conversation',
                'sensitive': 'as:sensitive',
                'toot': 'http://joinmastodon.org/ns#',
                'votersCount': 'toot:votersCount',
                'blurhash': 'toot:blurhash',
                'focalPoint': { '@container': '@list', '@id': 'toot:focalPoint' },
                'Hashtag': 'as:Hashtag'
            }],
        'id': 'https://mediapart.social/users/mediapart/statuses/115044298809022980',
        'type': 'Note',
        'summary': null,
        'inReplyTo': null,
        'published': '2025-08-17T13:18:08Z',
        'url': 'https://mediapart.social/@mediapart/115044298809022980',
        'attributedTo': 'https://mediapart.social/users/mediapart',
        'domain': 'mediapart.social',
        'preferredUsername': 'mediapart',
        'name': 'MediaPart',
        'to': ['https://www.w3.org/ns/activitystreams#Public'],
        'cc': ['https://mediapart.social/users/mediapart/followers'],
        'sensitive': false,
        'atomUri': 'https://mediapart.social/users/mediapart/statuses/115044298809022980',
        'inReplyToAtomUri': null,
        'conversation': 'tag:mediapart.social,2025-08-17:objectId=2435481:objectType=Conversation',
        'content': '<p>Ukraine: Zelensky et ses alliés européens à la Maison Blanche lundi </p><p>Les alliés européens de l’Ukraine ont affiché leur volonté de faire bloc autour du président ukrainien <a href="https://mediapart.social/tags/VolodymyrZelensky" class="mention hashtag" rel="tag">#<span>VolodymyrZelensky</span></a> en annonçant qu’ils l’accompagneraient à la Maison-Blanche lundi pour une rencontre avec Donald Trump. </p><p>Par Agence France-Presse, La rédaction de Mediapart › <a href="https://www.mediapart.fr/journal/international/170825/ukraine-zelensky-et-ses-allies-europeens-la-maison-blanche-lundi?at_medium=rs-cm&amp;at_campaign=mastodon&amp;at_account=mediapart" target="_blank" rel="nofollow noopener noreferrer" translate="no"><span class="invisible">https://www.</span><span class="ellipsis">mediapart.fr/journal/internati</span><span class="invisible">onal/170825/ukraine-zelensky-et-ses-allies-europeens-la-maison-blanche-lundi?at_medium=rs-cm&amp;at_campaign=mastodon&amp;at_account=mediapart</span></a></p>',
        'contentMap': { 'fr': '<p>Ukraine: Zelensky et ses alliés européens à la Maison Blanche lundi </p><p>Les alliés européens de l’Ukraine ont affiché leur volonté de faire bloc autour du président ukrainien <a href="https://mediapart.social/tags/VolodymyrZelensky" class="mention hashtag" rel="tag">#<span>VolodymyrZelensky</span></a> en annonçant qu’ils l’accompagneraient à la Maison-Blanche lundi pour une rencontre avec Donald Trump. </p><p>Par Agence France-Presse, La rédaction de Mediapart › <a href="https://www.mediapart.fr/journal/international/170825/ukraine-zelensky-et-ses-allies-europeens-la-maison-blanche-lundi?at_medium=rs-cm&amp;at_campaign=mastodon&amp;at_account=mediapart" target="_blank" rel="nofollow noopener noreferrer" translate="no"><span class="invisible">https://www.</span><span class="ellipsis">mediapart.fr/journal/internati</span><span class="invisible">onal/170825/ukraine-zelensky-et-ses-allies-europeens-la-maison-blanche-lundi?at_medium=rs-cm&amp;at_campaign=mastodon&amp;at_account=mediapart</span></a></p>' },
        'attachment': [{
            'type': 'Document',
            'mediaType': 'image/jpeg',
            'url': 'https://static.mediapart.social/media_attachments/files/115/044/298/746/019/939/original/b7add0670add9c28.jpg',
            'name': 'Volodymyr Zelensky accueilli par Ursula Von der Leyen à Bruxelles, dimanche 17 août 2025. © Photo Simon Wohlfahrt / AFP',
            'blurhash': 'UMA,q@tpJ?~Wo,IvIWRpNE$_-gNCRpWFa#WF',
            'width': 661,
            'height': 440
        }],
        'tag': [{
            'type': 'Hashtag',
            'href': 'https://mediapart.social/tags/volodymyrzelensky',
            'name': '#volodymyrzelensky'
        }],
        'replies': {
            'id': 'https://mediapart.social/users/mediapart/statuses/115044298809022980/replies',
            'type': 'Collection',
            'first': {
                'type': 'CollectionPage',
                'next': 'https://mediapart.social/users/mediapart/statuses/115044298809022980/replies?only_other_accounts=true&page=true',
                'partOf': 'https://mediapart.social/users/mediapart/statuses/115044298809022980/replies',
                'items': []
            }
        },
        'likes': {
            'id': 'https://mediapart.social/users/mediapart/statuses/115044298809022980/likes',
            'type': 'Collection',
            'totalItems': 0
        },
        'shares': {
            'id': 'https://mediapart.social/users/mediapart/statuses/115044298809022980/shares',
            'type': 'Collection',
            'totalItems': 0
        }
    } as IKeyable

    onMounted(async () => {
        actor.value = cactor
        console.log(actor.value)
        if (actor.value.summary) {
            actor.value.summary = extractor.localiseSummary(actor.value.summary, actor.value.URL as string, "font-medium text-hops-500 hover:text-hops-600 visited:font-normal")
        }
        actorRoute.value = `${actor.value.preferredUsername}`
        if (actor.value.domain) actorRoute.value = `${actor.value.preferredUsername}@${actor.value.domain}`
        tabs.value.push({
            name: t("actor.posts"),
            to: actor.value.outbox,
            selected: true
        })
        if (actor.value.featured) tabs.value.push({
            name: t("actor.featured"),
            to: actor.value.featured,
            selected: false
        })
        if (actor.value.type === "Person") {
            actorType.value = "persona"
            canModify.value = creatorStore.hasPersona(actor.value.id)
            listPanelType.value = "work"
        }
        if (actor.value.type === "Service") {
            actorType.value = "work"
            canModify.value = creatorStore.hasWork(actor.value.id)
            listPanelType.value = "contributor"
        }
    })
</script>