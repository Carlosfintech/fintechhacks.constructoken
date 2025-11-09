<template>
    <div class="flex">
        <!-- Profile dropdown -->
        <Menu as="div" class="relative">
            <div class="flex">
                <MenuButton class="inline-flex items-center hover:bg-gray-50 rounded-full text-sm focus:outline-none">
                    <span class="sr-only">{{ t("account.menu") }}</span>
                    <button type="button"
                        class="cursor-pointer align-middle rounded-full bg-white p-1 text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:shadow-none dark:inset-ring-white/5 dark:hover:bg-white/20">
                        <EllipsisHorizontalIcon class="size-4" aria-hidden="true" />
                    </button>
                </MenuButton>
                <NuxtLinkLocale :to="`/settings/profile/@${handle}`"
                    class="-space-x-1 self-center justify-self-end ml-1">
                    <button type="button"
                        class="cursor-pointer rounded-full bg-white px-2.5 py-0.5 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:shadow-none dark:inset-ring-white/5 dark:hover:bg-white/20">
                        {{ t("actor.edit") }}
                    </button>
                </NuxtLinkLocale>
            </div>
            <transition enter-active-class="transition ease-out duration-200"
                enter-from-class="transform opacity-0 scale-95" enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75" leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95">
                <MenuItems
                    class="-top-4 transform -translate-y-full absolute lg:right-2 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-md ring-1 ring-black ring-opacity-5 focus:outline-none overflow-x-visible">
                    <MenuItem v-for="(nav, i) in actorNavigation" :key="`nav-${i}`" v-slot="{ active }">
                    <NuxtLinkLocale :to="nav.to"
                        :class="[active ? 'bg-gray-100' : '', 'block px-4 py-2 text-sm text-gray-700']">
                        {{
                            nav.name }}
                    </NuxtLinkLocale>
                    </MenuItem>
                </MenuItems>
            </transition>
        </Menu>
    </div>
</template>

<script setup lang="ts">
    import { Menu, MenuButton, MenuItem, MenuItems } from "@headlessui/vue"
    import { EllipsisHorizontalIcon } from "@heroicons/vue/24/outline"

    const { t } = useI18n()
    const route = useRoute()
    const actorNavigation = [
        { name: t("account.settings"), to: "/settings" },
        { name: t("actor.featured"), to: "/settings" },
        { name: t("actor.favourites"), to: "/settings" },
        { name: t("actor.muted"), to: "/settings" },
        { name: t("actor.blocked"), to: "/settings" },
    ]
    const handle = ref("")

    onMounted(async () => {
        if (route.params.actorRoute === null) {
            throw createError({
                statusCode: 404,
                message: t("notfound.actor"),
            })
        }
        handle.value = route.params.actorRoute as string
    })
</script>