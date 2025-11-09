<template>
    <div>
        <!-- TOP BAR -->
        <Disclosure as="nav" class="fixed top-0 z-30 w-full bg-white/95 sm:px-6 md:hidden" v-slot="{ open }">
            <div class="mx-auto max-w-7xl px-2 sm:px-4 lg:px-8">
                <div class="relative flex h-16 items-center justify-between">
                    <div class="flex lg:hidden">
                        <!-- Mobile menu button -->
                        <DisclosureButton
                            class="relative inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-white/5 hover:text-white focus:outline-none">
                            <span class="absolute -inset-0.5" />
                            <span class="sr-only">{{ t("nav.open") }}</span>
                            <Bars3Icon v-if="!open" class="block size-6" aria-hidden="true" />
                            <XMarkIcon v-else class="block size-6" aria-hidden="true" />
                        </DisclosureButton>
                    </div>
                    <div class="flex flex-1 justify-center px-2 lg:ml-6 lg:justify-end">
                        <LayoutsDefaultNavigationSearch />
                    </div>
                    <NuxtLinkLocale to="/special"
                        class="text-hops-600 hover:text-hops-500 focus:outline-none group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold">
                        <HashtagIcon class="h-7 w-7 shrink-0" />
                    </NuxtLinkLocale>
                </div>
            </div>
            <transition enter-active-class="transition ease-out duration-200"
                enter-from-class="transform opacity-0 scale-95" enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75" leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95">
                <DisclosurePanel class="lg:hidden">
                    <div class="border-t border-white/10 pt-4 pb-3">
                        <AuthenticationPersonaCard />
                        <!-- <NuxtLinkLocale to="/profile" class="flex items-center p-2">
                            <div class="shrink-0">
                                <img class="size-10 rounded-full bg-gray-800 outline -outline-offset-1 outline-white/10"
                                    src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
                                    alt="" />
                            </div>
                            <div class="ml-3">
                                <div class="text-base font-medium text-gray-700">Tom Cook</div>
                                <div class="text-sm font-medium text-gray-400">tom@example.com</div>
                            </div>
                        </NuxtLinkLocale> -->
                    </div>
                    <div class="w-full border-t border-gray-300 mb-2" aria-hidden="true" />
                    <NuxtLinkLocale v-for="(item, i) in leadNavigation" :key="`scndrynav-${i}`" :to="item.to" :class="[!(authStore.loggedIn || !item.login)
                        ? 'pointer-events-none text-gray-500'
                        : item.name === headingTerm.name
                            ? 'bg-gray-50 text-ochre-600'
                            : 'text-gray-700 hover:text-ochre-600 hover:bg-gray-50',
                        'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold']"
                        :disabled="!(authStore.loggedIn || !item.login)">
                        <component :is="item.icon"
                            :class="[item.name === headingTerm.name ? 'text-ochre-600' : 'text-gray-400 group-hover:text-ochre-600', 'h-6 w-6 shrink-0']"
                            aria-hidden="true" />
                        {{ item.name }}
                    </NuxtLinkLocale>
                    <NuxtLinkLocale v-for="(item, i) in secondaryNavigation" :key="`scndrynav-${i}`" :to="item.to"
                        :class="[!(authStore.loggedIn || !item.login)
                            ? 'pointer-events-none text-gray-500'
                            : item.name === headingTerm.name
                                ? 'bg-gray-50 text-ochre-600'
                                : 'text-gray-700 hover:text-ochre-600 hover:bg-gray-50',
                            'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold']"
                        :disabled="!(authStore.loggedIn || !item.login)">
                        <component :is="item.icon"
                            :class="[item.name === headingTerm.name ? 'text-ochre-600' : 'text-gray-400 group-hover:text-ochre-600', 'h-6 w-6 shrink-0']"
                            aria-hidden="true" />
                        {{ item.name }}
                    </NuxtLinkLocale>
                    <div class="w-full border-t border-gray-300 my-2" aria-hidden="true" />
                    <LocalePopup />
                    <div class="flex flex-wrap justify-center bg-gray-100 mt-2 py-3">
                        <div v-for="item in footerNavigation" :key="item.name">
                            <NuxtLinkLocale :to="item.to" class="text-sm text-gray-400 hover:text-gray-300">{{ item.name
                            }}
                            </NuxtLinkLocale>
                            <span v-show="item.dot" class="text-sm text-gray-400 px-2">&middot;</span>
                        </div>
                    </div>
                </DisclosurePanel>
            </transition>
        </Disclosure>
        <!-- BOTTOM BAR -->
        <div class="z-30 fixed md:hidden inset-x-0 bottom-0 w-full bg-white">
            <div class="max-w-full mx-auto">
                <nav class="relative grid grid-cols-4 gap-4 justify-center py-1" aria-label="Global">
                    <NuxtLinkLocale v-for="(item, i) in baseNavigation" :key="`basenav-${i}`" :to="item.to" :class="[!(authStore.loggedIn || !item.login)
                        ? 'pointer-events-none text-gray-500'
                        : item.name === headingTerm.name
                            ? 'bg-gray-50 text-ochre-600'
                            : 'text-gray-700 hover:text-ochre-600 hover:bg-gray-50',
                        'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold justify-center']"
                        :disabled="!(authStore.loggedIn || !item.login)">
                        <component :is="item.icon"
                            :class="[item.name === headingTerm.name ? 'text-ochre-600' : 'text-gray-400 group-hover:text-ochre-600', 'h-6 w-6 shrink-0 inline-flex items-center']"
                            aria-hidden="true" />
                    </NuxtLinkLocale>
                </nav>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { Disclosure, DisclosureButton, DisclosurePanel, Menu, MenuButton, MenuItem, MenuItems } from "@headlessui/vue"
    import {
        Bars3Icon,
        XMarkIcon,
        BellIcon,
        BookmarkIcon,
        Cog8ToothIcon,
        HomeIcon,
        AtSymbolIcon,
        HeartIcon,
        MagnifyingGlassIcon,
        UserIcon,
        HashtagIcon
    } from "@heroicons/vue/24/outline"
    import { useAuthStore } from "@/stores/auth"

    const { t } = useI18n()
    const authStore = useAuthStore()
    const route = useRoute()
    const headingTerm = ref({} as INav)

    interface INav {
        name: string
        to: string
        icon: any
        login: boolean
    }

    const leadNavigation = [
        { name: t("nav.home"), to: "/", icon: HomeIcon, login: false },
        { name: t("nav.notifications"), to: "/notifications", icon: BellIcon, login: true },
        { name: t("nav.conversations"), to: "/conversations", icon: AtSymbolIcon, login: true },
        { name: t("nav.favourites"), to: "/favourites", icon: HeartIcon, login: true },
        { name: t("nav.bookmarks"), to: "/bookmarks", icon: BookmarkIcon, login: true },
    ]
    const secondaryNavigation = [
        { name: t("account.settings"), to: "/settings", icon: Cog8ToothIcon, login: true },
    ]
    const baseNavigation: INav[] = [
        { name: t("nav.home"), to: "/", icon: HomeIcon, login: false },
        { name: t("nav.search"), to: "/", icon: MagnifyingGlassIcon, login: false },
        { name: t("nav.notifications"), to: "/notifications", icon: BellIcon, login: true },
        { name: t("nav.conversations"), to: "/conversations", icon: AtSymbolIcon, login: true },
    ]
    const footerNavigation = [
        { name: t("nav.about"), to: "/about", dot: true },
        { name: t("nav.privacy"), to: "/privacy", dot: true },
        { name: t("nav.contact"), to: "/contact", dot: false },
    ]

    function getCurrent() {
        const navigationObjects = [...baseNavigation, ...leadNavigation, ...secondaryNavigation]
        const response = navigationObjects.find((item) => route.path.endsWith(item.to))
        if (response) return response
        return {} as INav
    }

    watch(() => route.path, () => {
        headingTerm.value = getCurrent()
    })

    onMounted(() => {
        headingTerm.value = getCurrent()
    })
</script>