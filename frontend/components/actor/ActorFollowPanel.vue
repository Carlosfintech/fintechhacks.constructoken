<template>
    <div class="flex">
        <!-- Profile dropdown -->
        <Menu as="div" class="relative">
            <div class="flex items-center">
                <div v-if="actor!.locked" class="flex items-center text-xs text-gray-500 mr-4">
                    <LockClosedIcon class="size-4" aria-hidden="true" />
                    {{ t("actor.locked") }}
                </div>
                <MenuButton class="inline-flex items-center hover:bg-gray-50 rounded-full text-sm focus:outline-none">
                    <span class="sr-only">{{ t("account.menu") }}</span>
                    <button type="button"
                        class="cursor-pointer align-middle rounded-full bg-white p-1 text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:shadow-none dark:inset-ring-white/5 dark:hover:bg-white/20">
                        <EllipsisHorizontalIcon class="size-4" aria-hidden="true" />
                    </button>
                </MenuButton>
                <div class="-space-x-1 self-center justify-self-end ml-1">
                    <button type="button" :data-hover="afterText"
                        :class="[!actor.is_followed && !actor.is_following
                            ? 'bg-hops-500 text-white hover:bg-white hover:text-hops-500 inset-ring-hops-500'
                            : actor.is_followed && actor.is_following ? 'text-gray-900 bg-white inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white' : '',
                            'button cursor-pointer rounded-full px-2.5 py-1 text-sm font-semibold shadow-xs inset-ring  dark:shadow-none dark:inset-ring-white/5 dark:hover:bg-white/20']">
                        <span>{{ beforeText }}</span>
                    </button>
                </div>
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
                        {{ nav.name }}
                    </NuxtLinkLocale>
                    </MenuItem>
                </MenuItems>
            </transition>
        </Menu>
    </div>
</template>

<script setup lang="ts">
    import { Menu, MenuButton, MenuItem, MenuItems } from "@headlessui/vue"
    import { EllipsisHorizontalIcon, LockClosedIcon } from "@heroicons/vue/24/outline"
    import type { IActorProfile } from "@/interfaces"

    const { t } = useI18n()
    const props = defineProps<{
        actor: IActorProfile
    }>()
    const beforeText = ref(t("actor.follow"))
    const afterText = ref(t("actor.follow"))

    const actorNavigation = [
        { name: t("account.settings"), to: "/settings" },
    ]

    onMounted(async () => {
        if (props.actor.is_followed && props.actor.is_following) {
            beforeText.value = t("actor.mutuals")
            afterText.value = t("actor.unfollow")
        }
        if (!props.actor.is_followed && props.actor.is_following) {
            beforeText.value = t("actor.followsYou")
            afterText.value = t("actor.followBack")
        }
        if (props.actor.is_followed && !props.actor.is_following) {
            beforeText.value = t("actor.following")
            afterText.value = t("actor.unfollow")
        }
        if (!props.actor.is_followed && !props.actor.is_following && props.actor.locked) {
            beforeText.value = t("actor.followRequest")
            afterText.value = t("actor.followRequest")
        }
    })
</script>

<style lang="css">

    /* 
    References:
    https://codepen.io/Jintos/pen/jOVaOZ
*/
    .button:before,
    .button:after {
        content: '';
        position: absolute;
        text-align: center;
        opacity: 0;
    }

    /* :before */

    .button:before {
        content: attr(data-hover);
    }

    /* :after */

    .button:after {
        content: attr(data-active);
    }

    .button:hover span,
    .button:active span {
        opacity: 0;
    }

    .button:hover:before,
    .button:active:after {
        opacity: 1;
    }
</style>