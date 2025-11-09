<template>
  <main class="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-lg">
      <h2 class="mt-10 text-center text-2xl/9 font-bold tracking-tight text-gray-900">
        <span v-if="!oauth">{{ t("login.with_email") }}</span>
        <span v-else>{{ t("login.with_password") }}</span>
      </h2>
      <p v-if="!oauth" class="text-sm text-center font-medium text-hops-500 hover:text-hops-600 mt-6">
        <span v-if="!create">{{ t("login.prompt1") }}</span><span v-else>{{ t("login.prompt2") }}</span>
      </p>
    </div>
    <div class="mt-10 sm:mx-auto sm:w-full sm:max-w-lg">
      <Form v-if="!generate" @submit="submit" :validation-schema="schema" class="space-y-6">
        <div v-if="create && !oauth">
          <label for="name" class="block text-sm font-medium text-gray-700">{{
            t("login.identity") }}</label>
          <div class="mt-1 group relative inline-block w-full">
            <Field id="name" name="name" type="text" v-slot="{ field }">
              <div
                class="flex items-center rounded-md border border-gray-300 placeholder-gray-400 shadow-sm focus-within:border-hops-600 focus-within:outline-none focus-within:ring-hops-600 sm:text-sm">
                <input v-bind="field"
                  class="block min-w-0 grow py-2 px-3 border-transparent rounded-l-md focus:border-transparent focus:outline-none focus:ring-transparent sm:text-sm/6" />
                <div class="shrink-0 pr-3 py-2 text-gray-500 select-none outline-none sm:text-sm/6">
                  @ {{ useRuntimeConfig().public.appDomain }}
                </div>
              </div>
            </Field>
            <ErrorMessage name="name"
              class="absolute left-5 top-6 translate-y-full w-60 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700" />
            <Field id="new" name="new" type="hidden" :value="create" />
          </div>
        </div>
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">{{ t("login.email_address") }}</label>
          <div class="mt-1 group relative inline-block w-full">
            <Field id="email" name="email" type="email" autocomplete="email"
              class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-hops-600 focus:outline-none focus:ring-hops-600 sm:text-sm" />
            <ErrorMessage name="email"
              class="absolute left-5 top-5 translate-y-full w- px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700" />
          </div>
        </div>
        <div v-if="oauth && !create" class="space-y-1">
          <label for="password" class="block text-sm font-medium text-gray-700">{{ t("login.password") }}</label>
          <div class="mt-1 group relative inline-block w-full">
            <Field id="password" name="password" type="password" autocomplete="password"
              class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-hops-600 focus:outline-none focus:ring-hops-600 sm:text-sm" />
            <ErrorMessage name="password"
              class="absolute left-5 top-0 translate-y-full w-48 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700" />
          </div>
          <div class="text-sm text-right">
            <NuxtLinkLocale to="/recover-password" class="font-medium text-hops-500 hover:text-hops-600">{{
              t("login.forgot") }}</NuxtLinkLocale>
          </div>
        </div>

        <div>
          <button type="submit"
            class="flex w-full justify-center rounded-md border border-transparent bg-hops-500 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-hops-700 focus:outline-none focus:ring-2 focus:ring-hops-600 focus:ring-offset-2">
            {{ t("forms.submit") }}
          </button>
        </div>
      </Form>

      <!-- GENERATOR - REMOVE WHEN DEVELOPMENT COMPLETE -->
      <div v-if="generate">
        <button type="submit" @click.prevent="generatePersona"
          class="flex w-full justify-center rounded-md border border-transparent bg-autumn-500 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-autumn-700 focus:outline-none focus:ring-2 focus:ring-autumn-600 focus:ring-offset-2">
          {{ t("forms.submit") }}
        </button>
      </div>
      <!-- GENERATOR - REMOVE WHEN DEVELOPMENT COMPLETE -->

      <div v-if="!create" class="mt-8 flex items-center justify-between">
        <p class="text-sm text-hops-500 align-middle">
          {{ t("login.toggle_password") }}
        </p>
        <Switch v-model="oauth"
          class="group relative inline-flex h-5 w-10 flex-shrink-0 cursor-pointer items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-hops-600 focus:ring-offset-2">
          <span class="sr-only">{{ t("login.use_setting") }}</span>
          <span aria-hidden="true" class="pointer-events-none absolute h-full w-full rounded-md bg-white" />
          <span aria-hidden="true"
            :class="[oauth ? 'bg-hops-500' : 'bg-gray-200', 'pointer-events-none absolute mx-auto h-4 w-9 rounded-full transition-colors duration-200 ease-in-out']" />
          <span aria-hidden="true"
            :class="[oauth ? 'translate-x-5' : 'translate-x-0', 'pointer-events-none absolute left-0 inline-block h-5 w-5 transform rounded-full border border-gray-200 bg-white shadow ring-0 transition-transform duration-200 ease-in-out']" />
        </Switch>
      </div>
      <!-- GENERATOR - REMOVE WHEN DEVELOPMENT COMPLETE -->
      <div v-if="create" :class="[create ? 'mt-8' : 'mt-2', 'flex items-center justify-between']">
        <p class="text-sm text-hops-500 align-middle">
          {{ t("generate.new_persona") }}
        </p>
        <Switch v-model="generate"
          class="group relative inline-flex h-5 w-10 flex-shrink-0 cursor-pointer items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-hops-600 focus:ring-offset-2">
          <span class="sr-only">{{ t("login.use_setting") }}</span>
          <span aria-hidden="true" class="pointer-events-none absolute h-full w-full rounded-md bg-white" />
          <span aria-hidden="true"
            :class="[generate ? 'bg-hops-500' : 'bg-gray-200', 'pointer-events-none absolute mx-auto h-4 w-9 rounded-full transition-colors duration-200 ease-in-out']" />
          <span aria-hidden="true"
            :class="[generate ? 'translate-x-5' : 'translate-x-0', 'pointer-events-none absolute left-0 inline-block h-5 w-5 transform rounded-full border border-gray-200 bg-white shadow ring-0 transition-transform duration-200 ease-in-out']" />
        </Switch>
      </div>
      <!-- GENERATOR - REMOVE WHEN DEVELOPMENT COMPLETE -->
      <div class="mt-2 flex items-center justify-between">
        <p class="text-sm text-hops-500 align-middle">
          {{ t("login.identity_create") }}
        </p>
        <Switch v-model="create"
          class="group relative inline-flex h-5 w-10 flex-shrink-0 cursor-pointer items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-hops-600 focus:ring-offset-2">
          <span class="sr-only">{{ t("login.use_setting") }}</span>
          <span aria-hidden="true" class="pointer-events-none absolute h-full w-full rounded-md bg-white" />
          <span aria-hidden="true"
            :class="[create ? 'bg-hops-500' : 'bg-gray-200', 'pointer-events-none absolute mx-auto h-4 w-9 rounded-full transition-colors duration-200 ease-in-out']" />
          <span aria-hidden="true"
            :class="[create ? 'translate-x-5' : 'translate-x-0', 'pointer-events-none absolute left-0 inline-block h-5 w-5 transform rounded-full border border-gray-200 bg-white shadow ring-0 transition-transform duration-200 ease-in-out']" />
        </Switch>
      </div>
    </div>
    <div class="mt-10 sm:mx-auto sm:w-full sm:max-w-lg">
      <CommonRuleList />
    </div>

  </main>
</template>

<script setup lang="ts">
  import { Switch } from '@headlessui/vue'
  import { useAuthStore } from "@/stores/auth"
  import { useTokenStore } from "@/stores/tokens"
  import { useCreatorStore } from "@/stores/creator"
  import { tokenIsTOTP, tokenIsMagic } from "@/utilities"
  // GENERATOR - REMOVE WHEN DEVELOPMENT COMPLETE
  import { apiGenerate } from "@/api"

  definePageMeta({
    // layout: "authentication",
    middleware: ["anonymous"],
  });

  const { locale, t } = useI18n()
  const authStore = useAuthStore()
  const tokenStore = useTokenStore()
  const creatorStore = useCreatorStore()
  const route = useRoute()
  const redirectAfterLogin = "/"
  const redirectAfterMagic = "/magic"
  const redirectTOTP = "/totp"
  const redirectAfterGenerate = "/settings"

  const oauth = ref(false)
  const create = ref(false)
  const generate = ref(false)
  const schema = {
    name: { identity: "new" },
    email: { email: true, required: true },
    password: { min: 8, max: 64 },
  }

  async function generatePersona() {
    if (generate.value && create.value) {
      // Create the new persona, and then login to that persona
      try {
        const { data: response } = await apiGenerate.generateNewPersona()
        if (response.value) {
          await authStore.logIn({ username: response.value.email, password: response.value.password })
          if (authStore.loggedIn) return await navigateTo(redirectAfterGenerate)
        }
      } catch (error) { console.log(error) }

    }
  }

  async function submit(values: any) {
    await authStore.logIn({ username: values.email, password: values.password })
    if (!values.password && !authStore.loggedIn && !tokenStore.token) {
      create.value = true
    }
    if (authStore.loggedIn) {
      await creatorStore.getActors(locale.value)
      return await navigateTo(redirectAfterLogin)
    }
    if (tokenStore.token && tokenIsTOTP(tokenStore.token))
      return await navigateTo(redirectTOTP)
    if (tokenStore.token && tokenIsMagic(tokenStore.token))
      return await navigateTo(redirectAfterMagic)
  }

  onMounted(async () => {
    // Check if password requested
    if (route.query && route.query.oauth) oauth.value = true
  })
</script>