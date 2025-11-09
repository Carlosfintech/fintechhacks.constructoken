<template>
    <div class="hidden md:fixed md:inset-y-0 md:z-30 md:flex md:flex-col md:w-24 lg:w-60">
        <div class="flex grow flex-col gap-y-5 px-6">
            <div class="flex h-16 shrink-0 items-center">
                <img class="block h-8 w-auto lg:hidden"
                    src="https://tailwindui.com/plus-assets/img/logos/mark.svg?color=lime&shade=800"
                    :alt="t('common.title')" />
                <img class="hidden h-8 w-auto lg:block"
                    src="https://tailwindui.com/plus-assets/img/logos/mark.svg?color=lime&shade=800"
                    :alt="t('common.title')" />
            </div>
            <DevelopmentRefreshLogin />
            <nav class="flex flex-1 flex-col">
                <ul role="list" class="flex flex-1 flex-col gap-y-7">
                    <li>
                        <ul role="list" class="-mx-2 space-y-1">
                            <li v-for="item in leadNavigation" :key="item.name">
                                <NuxtLinkLocale :to="item.to" :class="[!(authStore.loggedIn || !item.login)
                                    ? 'pointer-events-none text-gray-500'
                                    : route.path.endsWith(item.to)
                                        ? 'bg-gray-50 text-hops-600'
                                        : 'text-gray-700 hover:text-hops-600 hover:bg-gray-50',
                                    'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold']"
                                    :disabled="!(authStore.loggedIn || !item.login)">
                                    <component :is="item.icon"
                                        :class="[route.path.endsWith(item.to) ? 'text-hops-600' : 'text-gray-400 group-hover:text-hops-600', 'h-6 w-6 shrink-0']"
                                        aria-hidden="true" />
                                    <span class="hidden lg:block">{{ item.name }}</span>
                                </NuxtLinkLocale>
                            </li>
                        </ul>
                    </li>
                    <li>
                        <ul role="list" class="-mx-2 mt-2 space-y-1">
                            <li v-for="item in secondaryNavigation" :key="item.name">
                                <NuxtLinkLocale :to="item.to" :class="[!(authStore.loggedIn || !item.login)
                                    ? 'pointer-events-none text-gray-500'
                                    : route.path.endsWith(item.to)
                                        ? 'bg-gray-50 text-hops-600'
                                        : 'text-gray-700 hover:text-hops-600 hover:bg-gray-50',
                                    'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold']"
                                    :disabled="!(authStore.loggedIn || !item.login)">
                                    <component :is="item.icon"
                                        :class="[route.path.endsWith(item.to) ? 'text-hops-600' : 'text-gray-400 group-hover:text-hops-600', 'h-6 w-6 shrink-0']"
                                        aria-hidden="true" />
                                    <span class="hidden lg:block">{{ item.name }}</span>
                                </NuxtLinkLocale>
                            </li>
                        </ul>
                    </li>
                    <li class="-mx-6 mt-auto">
                        <AuthenticationNavigationSidebar />
                    </li>
                </ul>
            </nav>
        </div>
    </div>
</template>

<script setup lang="ts">
    import {
        BellIcon,
        BookmarkIcon,
        Cog8ToothIcon,
        HomeIcon,
        AtSymbolIcon,
        HeartIcon,
        MagnifyingGlassIcon,
    } from "@heroicons/vue/24/outline"
    import { useAuthStore } from "@/stores/auth"
    import DevelopmentRefreshLogin from "~/components/development/DevelopmentRefreshLogin.vue"

    const { t } = useI18n()
    const authStore = useAuthStore()
    const route = useRoute()

    const leadNavigation = [
        { name: t("nav.home"), to: "/", icon: HomeIcon, login: false },
        { name: t("nav.notifications"), to: "/notifications", icon: BellIcon, login: true },
        { name: t("nav.conversations"), to: "/conversations", icon: AtSymbolIcon, login: true },
        { name: t("nav.favourites"), to: "/favourites", icon: HeartIcon, login: true },
        { name: t("nav.bookmarks"), to: "/bookmarks", icon: BookmarkIcon, login: true },
        { name: "test", to: "/test", icon: BookmarkIcon, login: false },
    ]

    const secondaryNavigation = [
        { name: t("account.settings"), to: "/settings", icon: Cog8ToothIcon, login: true },
    ]
</script>