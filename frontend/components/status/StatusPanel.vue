<template>
    <ClientOnly fallbackTag="div">
        <div class="p-2 m-2">
            <div v-if="featured">
                <div class="ml-5 flex text-xs items-center w-fit p-1 text-amber-500">
                    <LightBulbIcon class="size-4 mr-1" aria-hidden="true" />
                    {{ t("status.featured") }}
                </div>
            </div>
            <div v-else>
                <StatusIsReplyLink v-if="isReply" :is-share="isShare"
                    :reply-u-r-i="statusPost.inReplyToURI as string" />
                <NuxtLinkLocale v-if="isShare" :to="`/@${status.actor!.preferredUsername}@${status.actor!.domain}`"
                    class="ml-5 relative flex items-center hover:bg-gray-100 rounded-full pr-3 w-fit">
                    <div class="relative">
                        <img class="flex size-8 items-center justify-center rounded-full"
                            :src="status!.actor!.iconURL as string" :alt="status!.actor!.preferredUsername" />
                        <span class="absolute -left-4 -top-0.5 rounded-tl px-0.5 py-px dark:bg-gray-900">
                            <ArrowPathRoundedSquareIconSolid class="size-5 text-hops-400 bg-amber-100/15 rounded-full"
                                aria-hidden="true" />
                        </span>
                    </div>
                    <div class="ml-1">
                        <p class="cursor-pointer text-xs font-medium truncate w-fit p-0.5">
                            <span class="text-gray-800">{{ status!.actor!.name }}</span>
                            <span class="text-gray-500 ml-0.5">
                                @{{ status!.actor!.preferredUsername }}@{{ status!.actor!.domain }}
                            </span>
                        </p>
                    </div>
                </NuxtLinkLocale>
            </div>
            <div class="flex justify-between">
                <NuxtLinkLocale :to="`/@${statusPost.actor!.preferredUsername}@${statusPost.actor!.domain}`"
                    class="group flex items-center hover:bg-gray-100 rounded-full pr-3">
                    <div class="shrink-0">
                        <img class="size-12 rounded-full bg-gray-800 outline -outline-offset-1 outline-white/10"
                            :src="statusPost.actor!.iconURL as string" :alt="statusPost.actor!.preferredUsername" />
                    </div>
                    <div class="ml-2">
                        <p class="text-sm font-medium text-gray-700 group-hover:text-gray-900 truncate">{{
                            statusPost.actor!.name }}</p>
                        <p class="text-xs font-medium text-gray-500 group-hover:text-gray-700 truncate">
                            @{{ statusPost.actor!.preferredUsername }}@{{ statusPost.actor!.domain }}
                        </p>
                    </div>
                </NuxtLinkLocale>
                <div class="flex">
                    <!-- Profile dropdown -->
                    <Menu as="div" class="relative">
                        <div class="flex items-center">
                            <LockClosedIcon v-if="statusPost.actor!.locked" class="size-4 text-gray-500 mr-2"
                                aria-hidden="true" />
                            <time :datetime="statusPost.created"
                                class="flex-none py-0.5 text-xs/5 text-gray-500 dark:text-gray-400 mr-2">
                                {{ readableDate(statusPost.created as string) }}
                            </time>
                            <MenuButton
                                class="inline-flex items-center hover:bg-gray-50 rounded-full text-sm focus:outline-none">
                                <span class="sr-only">{{ t("account.menu") }}</span>
                                <button type="button"
                                    class="cursor-pointer align-middle rounded-full bg-white p-1 text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:shadow-none dark:inset-ring-white/5 dark:hover:bg-white/20">
                                    <EllipsisHorizontalIcon class="size-4" aria-hidden="true" />
                                </button>
                            </MenuButton>
                        </div>
                        <transition enter-active-class="transition ease-out duration-200"
                            enter-from-class="transform opacity-0 scale-95"
                            enter-to-class="transform opacity-100 scale-100"
                            leave-active-class="transition ease-in duration-75"
                            leave-from-class="transform opacity-100 scale-100"
                            leave-to-class="transform opacity-0 scale-95">
                            <MenuItems
                                class="-top-4 transform -translate-y-full absolute lg:right-2 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-md ring-1 ring-black ring-opacity-5 focus:outline-none overflow-x-visible">
                                <MenuItem v-for="(nav, i) in actorNavigation" :key="`nav-${i}`" v-slot="{ active }">
                                <NuxtLinkLocale :to="nav.to"
                                    :class="[active ? 'bg-gray-100' : '', 'block px-4 py-2 text-sm text-gray-700']">
                                    {{ nav.name }}
                                </NuxtLinkLocale>
                                </MenuItem>
                            </MenuItems>
                        </transition>
                    </Menu>
                </div>
            </div>
            <div class="min-w-0 flex-1 sm:ml-12">
                <div class="text-sm text-gray-700 dark:text-gray-200 my-3">
                    <p v-html="statusPost.content"></p>
                </div>
                <StatusAttachmentGrid v-if="statusPost.attachments && statusPost.attachments.length"
                    :attachments="statusPost.attachments" />
                <div class="flex justify-between">
                    <StatusReplyToken :status="statusPost" />
                    <StatusShareToken :status="statusPost" />
                    <StatusLikeToken :status="statusPost" />
                    <StatusBookmarkToken :status="statusPost" />
                </div>
            </div>
        </div>
        <template #fallback>
            <p>{{ t("status.loading") }}</p>
        </template>
    </ClientOnly>
</template>

<script setup lang="ts">
    import { Menu, MenuButton, MenuItem, MenuItems } from "@headlessui/vue"
    import { EllipsisHorizontalIcon, ChatBubbleLeftIcon, ArrowPathRoundedSquareIcon, HeartIcon, BookmarkIcon, LightBulbIcon, LockClosedIcon } from "@heroicons/vue/24/outline"
    import { HeartIcon as HeartIconSolid, BookmarkIcon as BookmarkIconSolid, ArrowPathRoundedSquareIcon as ArrowPathRoundedSquareIconSolid } from "@heroicons/vue/20/solid"
    import { readableDate, readableNumber } from "@/utilities"
    import type { IActorProfile, IStatus, IStatusPost } from "@/interfaces"
    import StatusBookmarkToken from "./StatusBookmarkToken.vue"
    import StatusLikeToken from "./StatusLikeToken.vue"
    import StatusShareToken from "./StatusShareToken.vue"

    const { t } = useI18n()
    const actorNavigation = [
        { name: t("account.settings"), to: "/settings" },
    ]
    const props = defineProps<{
        status: IStatus
        featured?: boolean
    }>()
    // parts of the status
    const isShare = ref(false)
    const isReply = ref(false)
    const statusPost = ref({} as IStatusPost)

    onMounted(async () => {
        if (props.status.share!.URI) {
            isShare.value = true
            statusPost.value = props.status.share as IStatusPost
        } else {
            statusPost.value = props.status as IStatusPost
        }
        if (statusPost.value.inReplyToURI) isReply.value = true
    })
</script>