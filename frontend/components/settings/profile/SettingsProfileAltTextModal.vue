<template>
    <div>
        <button type="button" @click="openModal" :title="t('forms.edit')"
            class="cursor-pointer rounded-full bg-white p-1 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-100">
            <PencilIcon class="size-5" aria-hidden="true" />
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
                                    <form action="#" class="relative">
                                        <div
                                            class="rounded-md bg-white outline-2 outline-gray-300 border-none focus-within:outline-hops-600">
                                            <label for="comment" class="sr-only">{{ t("forms.edit") }}</label>
                                            <textarea rows="3" name="comment" id="comment" v-model="altText"
                                                class="block w-full bg-transparent px-3 py-1.5 text-base text-gray-900 placeholder:text-gray-400 outline-none border-none  focus:outline-none focus:border-none focus:ring-0 sm:text-sm/6 dark:text-white dark:placeholder:text-gray-500" />
                                            <!-- Spacer element to match the height of the toolbar -->
                                            <div class="py-2" aria-hidden="true">
                                                <!-- Matches height of button in toolbar (1px border + 36px content height) -->
                                                <div class="py-px">
                                                    <div class="h-9" />
                                                </div>
                                            </div>
                                        </div>
                                        <div
                                            class="absolute inset-x-0 bottom-0 flex justify-between py-2 pr-2 pl-3 focus:outline-none focus:border-none focus:ring-0">
                                            <div class="flex items-center text-sm text-gray-500 italic">
                                                {{ getLanguage() }}
                                            </div>
                                            <div class="shrink-0 flex gap-x-6">
                                                <button type="submit" @click.prevent="resetAltText"
                                                    :title="t('forms.cancel')"
                                                    class="inline-flex items-center rounded-md bg-thunderbird-300 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-thunderbird-400">
                                                    {{ t("forms.cancel") }}
                                                </button>
                                                <button type="submit" @click.prevent="setAltText"
                                                    :title="t('forms.submit')"
                                                    class="inline-flex items-center rounded-md bg-hops-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-hops-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-hops-600 dark:bg-hops-500 dark:shadow-none dark:hover:bg-hops-400 dark:focus-visible:outline-hops-500">
                                                    {{ t("forms.submit") }}
                                                </button>
                                            </div>
                                        </div>
                                    </form>
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
    import { PencilIcon } from "@heroicons/vue/24/outline"
    import { useActorStore } from "@/stores/actor"


    const { t, locales } = useI18n()
    const actorStore = useActorStore()
    const supportedLocales = locales.value as Array<any>
    const props = defineProps<{ text?: string }>()
    const emit = defineEmits<{ setAltText: [response: string] }>()

    const altText = ref("")

    onMounted(async () => {
        resetAltText()
    })

    function getLanguage() {
        const currentLanguage = supportedLocales.find((l) => l.iso === actorStore.editingLocale || l.code === actorStore.editingLocale || l.language === actorStore.editingLocale) as any
        if (currentLanguage) return currentLanguage.name
        return ""
    }

    watch(() => props.text, () => {
        resetAltText()
    })

    // MODAL
    const isOpen = ref(false)

    function toggleModal(value: boolean) {
        isOpen.value = value
    }

    function openModal(event: MouseEvent) {
        event.stopPropagation()
        isOpen.value = true
    }

    function resetAltText() {
        if (props.text) altText.value = props.text as string
        else altText.value = ""
        toggleModal(false)
    }

    function setAltText() {
        emit("setAltText", altText.value)
        toggleModal(false)
    }
</script>