<template>
    <div>
        <NuxtLinkLocale v-if="!authStore.loggedIn" to="/login"
            class="text-hops-600 hover:text-hops-500 focus:outline-none group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold">
            <UserCircleIcon class="h-6 w-6 shrink-0" />
            <span class="hidden lg:block">{{ t("account.login") }}</span>
        </NuxtLinkLocale>
        <NuxtLinkLocale v-else :to="`/@${persona.preferredUsername}@${persona.domain}`">
            <div class="flex items-center p-2">
                <div class="shrink-0">
                    <img class="size-12 rounded-full bg-gray-800 outline -outline-offset-1 outline-white/10"
                        :src="persona.iconURL" :alt="persona.preferredUsername" />
                </div>
                <div class="ml-3">
                    <p class="text-sm font-medium text-gray-700 group-hover:text-gray-900 truncate">{{
                        persona.name }}</p>
                    <p class="text-xs font-medium text-gray-500 group-hover:text-gray-700 truncate">@{{
                        persona.preferredUsername }}</p>
                </div>
            </div>
        </NuxtLinkLocale>
    </div>
</template>


<script setup lang="ts">
    import { UserCircleIcon } from "@heroicons/vue/24/outline"
    import { useCreatorStore } from "@/stores/creator"
    import { useAuthStore } from "@/stores/auth"
    import type { IActorProfile } from "@/interfaces"

    const { t } = useI18n()
    const authStore = useAuthStore()
    const creatorStore = useCreatorStore()
    const persona = ref({} as IActorProfile)

    onMounted(async () => {
        // Check if user is logged in
        // await creatorStore.getConnectedActors()
        if (authStore.loggedIn && creatorStore.persona && Object.hasOwn(creatorStore.persona, "iconURL") && creatorStore.persona.iconURL)
            persona.value = creatorStore.persona
    })
</script>