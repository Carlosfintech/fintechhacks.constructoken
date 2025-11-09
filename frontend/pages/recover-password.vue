<template>
  <main class="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-lg">
      <img class="mx-auto h-12 w-auto" src="https://tailwindui.com/plus-assets/img/logos/mark.svg?color=lime&shade=800"
        :alt="t('common.title')" />
      <h2 class="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">{{ t("recover.title") }}</h2>
    </div>
    <div class="sm:mx-auto sm:w-full sm:max-w-lg">
      <div class="mt-8">
        <div class="mt-6">
          <Form @submit="submit" :validation-schema="schema" class="space-y-6">
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700">{{ t("recover.email_address")
                }}</label>
              <div class="mt-1 group relative inline-block w-full">
                <Field id="email" name="email" type="email" autocomplete="email"
                  class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-hops-600 focus:outline-none focus:ring-hops-600 sm:text-sm" />
                <ErrorMessage name="email"
                  class="absolute left-5 top-5 translate-y-full w-48 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700" />
              </div>
              <div class="text-sm text-right">
                <NuxtLinkLocale to="/login" class="font-medium text-hops-500 hover:text-hops-600">{{
                  t("recover.prompt1") }}</NuxtLinkLocale>
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

  definePageMeta({
    layout: "authentication",
    middleware: ["anonymous"],
  });

  const { t } = useI18n()
  const authStore = useAuthStore()
  const redirectRoute = "/"
  const schema = {
    email: { email: true, required: true }
  }

  async function submit(values: any) {
    await authStore.recoverPassword(values.email)
    await new Promise((resolve) => {
      setTimeout(() => {
        resolve(true)
      }, 2000)
    })
    return await navigateTo(redirectRoute)
  }
</script>