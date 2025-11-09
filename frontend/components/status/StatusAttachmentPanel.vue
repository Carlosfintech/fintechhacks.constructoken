<template>
    <div class="group relative">
        <video v-if="attachment.mediaType === 'video/mp4'" class="aspect-w-video sm:rounded-lg" preload="" :muted="true"
            :poster="attachment.url" :controls="true" :loop="true" :width="attachment.width"
            :height="attachment.height">
            <source :src="attachment.url" type="video/mp4">
        </video>
        <img v-else class="aspect-auto w-full object-cover sm:rounded-lg" :src="attachment.url as string"
            :alt="attachment.name" :width="attachment.width" :height="attachment.height" />
        <Popover v-if="attachment.name" class="absolute -inset-2 -top-3 flex items-start p-6">
            <PopoverButton
                class="cursor-pointer text-xs font-bold text-white bg-gray-600/80 hover:bg-gray-800/80 rounded-lg px-1">
                ALT
            </PopoverButton>
            <transition enter-active-class="transition duration-200 ease-out" enter-from-class="translate-y-1 opacity-0"
                enter-to-class="translate-y-0 opacity-100" leave-active-class="transition duration-150 ease-in"
                leave-from-class="translate-y-0 opacity-100" leave-to-class="translate-y-1 opacity-0">
                <PopoverPanel class="absolute z-10">
                    <div class="overflow-hidden rounded-lg shadow-lg ring-1 ring-black/5 bg-white m-4">
                        <p class="text-sm font-bold text-gray-800 m-4">{{ t("status.altTitle") }}</p>
                        <p class="relative text-xs m-4 text-gray-700 whitespace-pre-wrap">
                            {{ attachment.name }}
                        </p>
                    </div>
                </PopoverPanel>
            </transition>
        </Popover>
    </div>
</template>

<script setup lang="ts">
    import { Popover, PopoverButton, PopoverPanel } from "@headlessui/vue"
    const { t } = useI18n()
    const props = defineProps<{
        attachment: {
            [key: string]: any | any[]
        }
    }>()
</script>