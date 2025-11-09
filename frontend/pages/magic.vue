<template>
  <main class="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-lg">
      <div>
        <EnvelopeIcon class="text-hops-500 h-12 w-12 mx-auto" aria-hidden="true" />
        <h2 class="mt-4 text-center text-2xl/9 font-bold tracking-tight text-gray-900">{{ t("magic.title") }}</h2>
        <p class="text-sm font-medium text-hops-500 hover:text-hops-600 mt-6">
          {{ t("magic.prompt1") }}
        </p>
        <p class="text-sm font-medium text-hops-500 hover:text-hops-600 mt-2">
          {{ t("magic.prompt2") }}
        </p>
      </div>

      <NuxtLinkLocale to="/login?oauth=true" class="mt-8 flex">
        <component :is="LinkIcon" class="text-hops-500 h-4 w-4 mr-1" aria-hidden="true" />
        <p class="text-sm text-hops-500 align-middle">
          {{ t("magic.prompt3") }}
        </p>
      </NuxtLinkLocale>
    </div>
  </main>
</template>

<script setup lang="ts">
  import { LinkIcon, EnvelopeIcon } from "@heroicons/vue/24/outline"
  import { useTokenStore } from "@/stores/tokens"
  import { tokenIsMagic } from "@/utilities"

  definePageMeta({
    layout: "authentication",
    middleware: ["anonymous"],
  });

  const { t } = useI18n()
  const tokenStore = useTokenStore()
  const redirectRoute = "/login"


  onMounted(async () => {
    if (!tokenIsMagic(tokenStore.token)) {
      return await navigateTo(redirectRoute)
    }
  })
</script>