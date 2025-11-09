<template>
    <main class="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
        <div class="sm:mx-auto sm:w-full sm:max-w-lg">
            <ul role="list">
                <li v-for="identity in identities" :key="identity.id">
                    <NuxtLinkLocale :to="`/@${identity.preferredUsername}@${identity.domain}`"
                        class="relative flex items-center space-x-3 my-2 rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-xs focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 hover:border-gray-400">
                        <div class="flex items-center gap-x-6">
                            <img class="size-14 rounded-full" :src="identity.iconURL as string" alt="" />
                            <div>
                                <h3 class="text-base/7 font-semibold tracking-tight text-gray-900"
                                    v-html="identity.name">
                                </h3>
                                <p class="text-sm/6 text-gray-500">@{{ identity.preferredUsername }}<span
                                        v-if="identity.domain">@{{
                                            identity.domain }}</span></p>
                            </div>
                        </div>
                    </NuxtLinkLocale>
                </li>
            </ul>
        </div>
    </main>
</template>

<script setup lang="ts">
    import { EnvelopeIcon } from "@heroicons/vue/24/outline"
    import { apiActivity, apiAuth } from "@/api"
    import { useAuthStore } from "@/stores/auth"
    import type { IActorProfile } from "@/interfaces"

    definePageMeta({
        middleware: ["authenticated"],
    });

    const { locale, t } = useI18n()
    const authStore = useAuthStore()
    const redirectRoute = "/login"
    const identities = ref<IActorProfile[]>([])

    onMounted(async () => {
        try {
            await authStore.tokenStore.refreshTokens()
            const { data: response } = await apiActivity.getCreatorPersonas(authStore.tokenStore.token, locale.value)
            if (response.value) identities.value = response.value
        } catch (error) { console.log(error) }
    })
</script>