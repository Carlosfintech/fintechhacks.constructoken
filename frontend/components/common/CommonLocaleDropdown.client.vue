<template>
    <Listbox as="div" class="relative inline-block text-left">
        <div>
            <ListboxButton
                class="inline-flex items-center w-full justify-center -ml-px gap-x-1.5 rounded-md px-3 py-2 text-sm text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                <GlobeEuropeAfricaIcon class="md:-ml-0.5 h-4 w-4 text-gray-400" aria-hidden="true" />
                <span v-if="currentLocale && currentLocale.hasOwnProperty('name')" class="hidden md:block">
                    {{ currentLocale.name }}
                </span>
                <ChevronUpDownIcon class="md:-ml h-4 w-4 text-gray-400" aria-hidden="true" />
            </ListboxButton>
        </div>
        <transition leave-active-class="transition ease-in duration-100" leave-from-class="opacity-100"
            leave-to-class="opacity-0">
            <ListboxOptions
                class="absolute z-10 mt-1 max-h-56 w-30 overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                <ListboxOption as="template" v-for="loc in supportedLocales" :key="loc.code" :value="loc.code"
                    v-slot="{ active, selected }">
                    <li @click="watchLocaleSelect(loc)"
                        :class="[active ? 'bg-hops-600 text-white' : 'text-gray-900', 'relative cursor-default select-none py-2 pl-3 pr-9']">
                        <div class="flex items-center">
                            <span :class="[selected ? 'font-semibold' : 'font-normal', 'ml-3 block truncate']">{{
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
    </Listbox>
</template>

<script setup lang="ts">
    import { Listbox, ListboxButton, ListboxOption, ListboxOptions } from "@headlessui/vue"
    import { CheckIcon, ChevronUpDownIcon } from "@heroicons/vue/20/solid"
    import { GlobeEuropeAfricaIcon } from "@heroicons/vue/24/outline"
    import { useActorStore } from "@/stores/actor"

    const { locale, locales } = useI18n()
    const actorStore = useActorStore()
    const supportedLocales = locales.value as Array<any>
    const currentLocale = shallowRef({} as any)
    const props = defineProps<{
        language?: string,
    }>()
    const emit = defineEmits<{ setLocaleSelect: [select: string] }>()

    function watchLocaleSelect(select: any) {
        currentLocale.value = select
        emit("setLocaleSelect", select.language)
    }

    async function setLocale(term: string) {
        currentLocale.value = await supportedLocales.find((l) => l.iso === term || l.code === term || l.language === term) as any
    }

    watch(() => actorStore.editingLocale, async () => {
        if (actorStore.editingLocale !== currentLocale.value.language) await setLocale(actorStore.editingLocale)
    })

    onMounted(async () => {
        if (props.language) await setLocale(props.language)
        else await setLocale(locale.value)
    })
</script>