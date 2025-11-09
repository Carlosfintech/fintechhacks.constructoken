<template>
    <div class="self-center justify-self-end ml-0.5">
        <button type="button" @click="openModal" :title="t('actor.add')"
            class="cursor-pointer align-middle rounded-full bg-white p-1 text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:shadow-none dark:inset-ring-white/5 dark:hover:bg-white/20">
            <PlusIcon class="size-4" aria-hidden="true" />
        </button>
        <TransitionRoot appear :show="isOpen" as="template">
            <Dialog as="div" :open="isOpen" @close="toggleModal" class="relative z-10">
                <TransitionChild as="template" enter="duration-300 ease-out" enter-from="opacity-0"
                    enter-to="opacity-100" leave="duration-200 ease-in" leave-from="opacity-100" leave-to="opacity-0">
                    <div class="fixed inset-0 bg-black/25" />
                </TransitionChild>
                <div class="fixed inset-0 overflow-y-auto">
                    <div class="flex min-h-full items-center justify-center p-4 text-center">
                        <TransitionChild as="template" enter="duration-300 ease-out" enter-from="opacity-0 scale-95"
                            enter-to="opacity-100 scale-100" leave="duration-200 ease-in"
                            leave-from="opacity-100 scale-100" leave-to="opacity-0 scale-95">
                            <DialogPanel
                                class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                                <div class="min-w-0 flex-1">
                                    <Form @submit="submit" :validation-schema="schema">
                                        <div>
                                            <label for="name" class="block text-sm font-medium text-gray-700">{{
                                                t("login.identity") }}</label>
                                            <div class="mt-1 group relative inline-block w-full">
                                                <Field id="name" name="name" type="text" v-slot="{ field }">
                                                    <div
                                                        class="flex items-center rounded-md border border-gray-300 placeholder-gray-400 shadow-sm focus-within:border-hops-600 focus-within:outline-none focus-within:ring-hops-600 sm:text-sm">
                                                        <input v-bind="field"
                                                            class="block min-w-0 grow py-2 px-3 border-transparent rounded-l-md focus:border-transparent focus:outline-none focus:ring-transparent sm:text-sm/6" />
                                                        <div
                                                            class="shrink-0 pr-3 py-2 text-gray-500 select-none outline-none sm:text-sm/6">
                                                            @ {{ useRuntimeConfig().public.appDomain }}
                                                        </div>
                                                    </div>
                                                </Field>
                                                <ErrorMessage name="name"
                                                    class="absolute left-5 top-6 translate-y-full w-60 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700" />
                                                <Field id="new" name="new" type="hidden" :value="true" />
                                            </div>
                                        </div>
                                        <div
                                            class="flex justify-between py-2 pr-2 pl-3 focus:outline-none focus:border-none focus:ring-0">
                                            <div class="flex items-center text-sm text-gray-500 italic">
                                                {{ getLanguage() }}
                                            </div>
                                            <div class="shrink-0 flex gap-x-6">
                                                <button type="submit" @click.prevent="closeModal"
                                                    :title="t('forms.cancel')"
                                                    class="inline-flex items-center rounded-md bg-thunderbird-300 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-thunderbird-400">
                                                    {{ t("forms.cancel") }}
                                                </button>
                                                <button type="submit" :title="t('forms.create')"
                                                    class="inline-flex items-center rounded-md bg-hops-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-hops-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-hops-600 dark:bg-hops-500 dark:shadow-none dark:hover:bg-hops-400 dark:focus-visible:outline-hops-500">
                                                    {{ t("forms.create") }}
                                                </button>
                                            </div>
                                        </div>
                                    </Form>
                                </div>
                            </DialogPanel>
                        </TransitionChild>
                    </div>
                </div>
            </Dialog>
        </TransitionRoot>
    </div>
</template>

<script setup lang="ts">
    import { TransitionRoot, TransitionChild, Dialog, DialogPanel } from "@headlessui/vue"
    import { PlusIcon } from "@heroicons/vue/24/outline"
    import { apiActivity } from "@/api"

    const { t, locales } = useI18n()
    const actorStore = useActorStore()
    const toastStore = useToastStore()
    const tokenStore = useTokenStore()
    const supportedLocales = locales.value as Array<any>
    const props = defineProps<{ maker_id?: string }>()
    const preferredUsername = ref<string>("")
    const validated = ref(false)
    const schema = {
        name: { identity: "new" },
    }

    onMounted(async () => {
        console.log("PreferredUsername", preferredUsername.value)
    })

    function getCurrentLanguage() {
        const currentLanguage = supportedLocales.find((l) => l.iso === actorStore.editingLocale || l.code === actorStore.editingLocale || l.language === actorStore.editingLocale) as any
        if (currentLanguage) return currentLanguage
        return ""
    }

    function getLanguage() {
        const currentLanguage = getCurrentLanguage()
        if (currentLanguage) return currentLanguage.name
        return ""
    }

    function getLanguageCode() {
        const currentLanguage = getCurrentLanguage()
        if (currentLanguage) return currentLanguage.language
        return ""
    }

    async function submit(values: any) {
        console.log("submitModal", values)
        await tokenStore.refreshTokens()
        try {
            console.log(values.name, getLanguageCode(), props.maker_id)
            await apiActivity.createActor(values.name, tokenStore.token, getLanguageCode(), props.maker_id)
            toggleModal(false)
            return await navigateTo(`/settings/profile/@${values.name}@${useRuntimeConfig().public.appDomain}`)
        } catch (error) {
            toastStore.addNotice({
                title: "Create error",
                content: error as string,
                icon: "error"
            })
        }
    }
    // MODAL
    const isOpen = ref(false)

    function toggleModal(value: boolean) {
        isOpen.value = value
    }

    function openModal(event: MouseEvent) {
        event.stopPropagation()
        isOpen.value = true
    }

    function closeModal() {
        toggleModal(false)
    }
</script>