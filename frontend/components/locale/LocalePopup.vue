<template>
    <div class="flex items-center justify-center">
        <button type="button" @click="openModal"
            class="inline-flex rounded-full cursor-pointer text-gray-400 hover:text-gray-300 text-sm focus:outline-none">
            <GlobeEuropeAfricaIcon class="w-7 pr-2" aria-hidden="true" />
            <span>{{ currentLocale.name }}</span>
            <span class="text-sm text-gray-400 px-2">&middot;</span>
            <span>{{ currentCurrency }}</span>
        </button>
    </div>
    <TransitionRoot appear :show="isOpen" as="template">
        <Dialog as="div" @close="closeModal" class="relative z-40">
            <TransitionChild as="template" enter="duration-300 ease-out" enter-from="opacity-0" enter-to="opacity-100"
                leave="duration-200 ease-in" leave-from="opacity-100" leave-to="opacity-0">
                <div class="fixed inset-0 bg-black/25" />
            </TransitionChild>

            <div class="fixed inset-0 overflow-y-auto">
                <div class="flex min-h-full items-center justify-center p-4 text-center">
                    <TransitionChild as="template" enter="duration-300 ease-out" enter-from="opacity-0 scale-95"
                        enter-to="opacity-100 scale-100" leave="duration-200 ease-in" leave-from="opacity-100 scale-100"
                        leave-to="opacity-0 scale-95">
                        <DialogPanel
                            class="w-full max-w-md transform rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                            <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                                {{ t("localisation.title") }}
                            </DialogTitle>
                            <div class="flex justify-between">
                                <Listbox as="div">
                                    <div class="relative mt-2 w-36">
                                        <ListboxButton
                                            class="relative w-full cursor-default rounded-md bg-white py-1.5 pl-3 pr-10 text-left text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:outline-none focus:ring-2 focus:ring-hops-500 sm:text-sm sm:leading-6">
                                            <span class="flex items-center">
                                                <GlobeEuropeAfricaIcon class="h-5 w-5 flex-shrink-0"
                                                    aria-hidden="true" />
                                                <span class="ml-1">{{ currentLocale.name }}</span>
                                            </span>
                                            <span
                                                class="pointer-events-none absolute inset-y-0 right-0 ml-3 flex items-center pr-2">
                                                <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
                                            </span>
                                        </ListboxButton>
                                        <transition leave-active-class="transition ease-in duration-100"
                                            leave-from-class="opacity-100" leave-to-class="opacity-0">
                                            <ListboxOptions
                                                class="absolute z-40 mt-1 max-h-56 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                                                <ListboxOption as="template" v-for="loc in supportedLocales"
                                                    :key="loc.name" :value="loc" v-slot="{ active, selected }">
                                                    <li @click="onLocaleChanged(loc)"
                                                        :class="[active ? 'bg-hops-600 text-white' : 'text-gray-900', 'relative cursor-default select-none py-2 pl-3 pr-9']">
                                                        <div class="flex items-center">
                                                            <span
                                                                :class="[selected ? 'font-semibold' : 'font-normal', 'ml-3 block truncate']">{{
                                                                    loc.name }}</span>
                                                        </div>
                                                        <span v-if="selected"
                                                            :class="[active ? 'text-white' : 'text-hops-600', 'absolute inset-y-0 right-0 flex items-center pr-4']">
                                                            <CheckIcon class="h-5 w-5" aria-hidden="true" />
                                                        </span>
                                                    </li>
                                                </ListboxOption>
                                            </ListboxOptions>
                                        </transition>
                                    </div>
                                </Listbox>
                                <!-- Currency selector -->
                                <Listbox as="div">
                                    <div class="relative mt-2 w-36">
                                        <ListboxButton
                                            class="relative w-full cursor-default rounded-md bg-white py-1.5 pl-3 pr-10 text-left text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:outline-none focus:ring-2 focus:ring-hops-500 sm:text-sm sm:leading-6">
                                            <span class="flex items-center">
                                                <BanknotesIcon class="h-5 w-5 flex-shrink-0" aria-hidden="true" />
                                                <span class="ml-1">{{ currentCurrency }}</span>
                                            </span>
                                            <span
                                                class="pointer-events-none absolute inset-y-0 right-0 ml-3 flex items-center pr-2">
                                                <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
                                            </span>
                                        </ListboxButton>
                                        <transition leave-active-class="transition ease-in duration-100"
                                            leave-from-class="opacity-100" leave-to-class="opacity-0">
                                            <ListboxOptions
                                                class="absolute z-40 mt-1 max-h-56 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                                                <ListboxOption as="template" v-for="currency in currencies"
                                                    :key="currency" :value="currency" v-slot="{ active, selected }">
                                                    <li
                                                        :class="[active ? 'bg-hops-600 text-white' : 'text-gray-900', 'relative cursor-default select-none py-2 pl-3 pr-9']">
                                                        <div class="flex items-center">
                                                            <span
                                                                :class="[selected ? 'font-semibold' : 'font-normal', 'ml-3 block truncate']">{{
                                                                    currency }}</span>
                                                        </div>
                                                        <span v-if="selected"
                                                            :class="[active ? 'text-white' : 'text-hops-600', 'absolute inset-y-0 right-0 flex items-center pr-4']">
                                                            <CheckIcon class="h-5 w-5" aria-hidden="true" />
                                                        </span>
                                                    </li>
                                                </ListboxOption>
                                            </ListboxOptions>
                                        </transition>
                                    </div>
                                </Listbox>
                                <div class="mt-2">
                                    <button type="button"
                                        class="flex w-full justify-center rounded-md border border-transparent bg-hops-500 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-hops-700 focus:outline-none focus:ring-2 focus:ring-hops-600 focus:ring-offset-2"
                                        @click="closeModal">
                                        {{ t("forms.submit") }}
                                    </button>
                                </div>
                            </div>
                        </DialogPanel>
                    </TransitionChild>
                </div>
            </div>
        </Dialog>
    </TransitionRoot>
</template>

<script setup lang="ts">
    import {
        TransitionRoot,
        TransitionChild,
        Dialog,
        DialogPanel,
        DialogTitle, Listbox, ListboxButton, ListboxOption, ListboxOptions,
    } from "@headlessui/vue"
    import { CheckIcon, ChevronUpDownIcon } from "@heroicons/vue/20/solid"
    import { GlobeEuropeAfricaIcon, BanknotesIcon } from "@heroicons/vue/24/outline"
    import { setLocale as setVeeLocale } from '@vee-validate/i18n'

    const { t, locale, locales } = useI18n()
    const supportedLocales = locales.value as Array<any>
    const switchLocalePath = useSwitchLocalePath()
    const currentLocale = ref({} as any)
    const currentCurrency = ref("EUR")
    const isOpen = ref(false)
    const currencies = ['CAD', 'USD', 'AUD', 'EUR', 'GBP']

    function closeModal() {
        isOpen.value = false
    }
    function openModal() {
        isOpen.value = true
    }

    // When the visitor selects a new locale, route to
    // to the new locale's path e.g. /en-CA/foo → /ar-EG/foo
    async function onLocaleChanged(term: any) {
        currentLocale.value = term
        // switchLocalePath('ar-EG') will return Arabic equivalent
        // for the *current* URL path e.g. if we're at /en-CA/about,
        // switchLocalePath('ar-EG') will return '/ar-EG/about'
        return await navigateTo({ path: switchLocalePath(term.code) })
    }

    function setLocale(term: string) {
        currentLocale.value = supportedLocales.find((l) => l.iso === term || l.code === term) as any
    }

    onMounted(async () => {
        setLocale(locale.value)
        // https://vee-validate.logaretm.com/v4/guide/i18n
        setVeeLocale(locale.value)
    })

</script>
