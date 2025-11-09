<template>
    <!-- Profile dropdown -->
    <Menu as="div" class="relative ml-3">
        <div v-if="!authStore.loggedIn">
            <NuxtLinkLocale to="/login" class="p-1 text-white hover:text-gray-200 focus:outline-none">
                <UserCircleIcon class="size-7 shrink-0" />
            </NuxtLinkLocale>
        </div>
        <div v-else>
            <MenuButton class="flex rounded-full text-sm focus:outline-none">
                <span class="sr-only">{{ t("account.menu") }}</span>
                <img class="h-8 w-8 rounded-full"
                    src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
                    alt="" />
            </MenuButton>
        </div>
        <transition enter-active-class="transition ease-out duration-200"
            enter-from-class="transform opacity-0 scale-95" enter-to-class="transform opacity-100 scale-100"
            leave-active-class="transition ease-in duration-75" leave-from-class="transform opacity-100 scale-100"
            leave-to-class="transform opacity-0 scale-95">
            <MenuItems
                class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                <MenuItem v-for="(nav, i) in navigation" :key="`nav-${i}`" v-slot="{ active }">
                <NuxtLinkLocale :to="nav.to"
                    :class="[active ? 'bg-gray-100' : '', 'block px-4 py-2 text-sm text-gray-700']">{{ nav.name }}
                </NuxtLinkLocale>
                </MenuItem>
                <MenuItem v-slot="{ active }">
                <a :class="[active ? 'bg-gray-100 cursor-pointer' : '', 'block px-4 py-2 text-sm text-gray-700 cursor-pointer']"
                    @click="logout">
                    {{ t("account.logout") }}
                </a>
                </MenuItem>
            </MenuItems>
        </transition>
    </Menu>
</template>


<script setup lang="ts">
    import { Menu, MenuButton, MenuItem, MenuItems } from "@headlessui/vue"
    import { UserCircleIcon } from "@heroicons/vue/24/outline"
    import { useAuthStore } from "@/stores/auth"

    const { t } = useI18n()
    const authStore = useAuthStore()
    const navigation = [
        { name: t("account.settings"), to: "/settings" },
        { name: t("account.identities"), to: "/identity" }
    ]
    const redirectRoute = "/"

    async function logout() {
        await authStore.logOut()
        await navigateTo(redirectRoute)
    }
</script>