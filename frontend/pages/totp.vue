<template>
  <main class="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-lg">
      <img class="mx-auto h-10 w-auto" src="https://tailwindui.com/plus-assets/img/logos/mark.svg?color=lime&shade=800"
        :alt="t('common.title')" />
      <h2 class="mt-10 text-center text-2xl/9 font-bold tracking-tight text-gray-900">{{ t("totp.title") }}</h2>
      <p class="text-sm text-center font-medium text-hops-500 hover:text-hops-600 mt-6">
        {{ t("totp.prompt1") }}
      </p>
    </div>
    <div class="sm:mx-auto sm:w-full sm:max-w-lg">
      <div class="mt-8">
        <div class="mt-6">
          <Form @submit="submit" :validation-schema="schema" class="space-y-6">
            <div>
              <label for="claim" class="block text-sm font-medium text-gray-700">{{ t("totp.code") }}</label>
              <div class="mt-1 group relative inline-block w-full">
                <Field id="claim" name="claim" type="text" autocomplete="off"
                  class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-hops-600 focus:outline-none focus:ring-hops-600 sm:text-sm" />
              </div>
            </div>
            <div>
              <button type="submit"
                class="flex w-full justify-center rounded-md border border-transparent bg-hops-500 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-hops-700 focus:outline-none focus:ring-2 focus:ring-hops-600 focus:ring-offset-2">
                {{ t("forms.submit") }}
              </button>
            </div>
          </Form>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
  import { useAuthStore } from "@/stores/auth"
  import { useTokenStore } from "@/stores/tokens"
  import { useCreatorStore } from "@/stores/creator"
  import { tokenIsTOTP } from "@/utilities"

  definePageMeta({
    layout: "authentication",
    middleware: ["anonymous"],
  });

  const { locale, t } = useI18n()
  const authStore = useAuthStore()
  const tokenStore = useTokenStore()
  const creatorStore = useCreatorStore()
  const redirectRoute = "/"
  const schema = {
    claim: { required: true, min: 6, max: 7 }
  }

  async function submit(values: any) {
    await authStore.totpLogin(values.claim)
    if (authStore.loggedIn) {
      await creatorStore.getActors(locale.value)
      return await navigateTo(redirectRoute)
    }
  }

  onMounted(async () => {
    // Check if token exists
    if (!tokenStore.token || !tokenIsTOTP(tokenStore.token))
      return await navigateTo("/")
  })
</script>