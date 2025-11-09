<template>
    <div class="flex items-center">
        <p class="text-sm text-gray-600 sm:text-base line-clamp-1">@{{ actorURI }}</p>
        <div class="group relative">
            <button @click="copyActorRoute">
                <component :is="isCopied ? CheckIcon : DocumentDuplicateIcon"
                    :class="[isCopied ? 'text-hops-500' : 'text-hops-600 group-hover:text-hops-400', 'ml-1 size-5 shrink-0 cursor-pointer']"
                    aria-hidden="true" />
            </button>
            <div v-if="!isCopied" id="tooltip-default" role="tooltip"
                class="pointer-events-none absolute -left-20 top-0 translate-y-full w-48 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700 opacity-0 transition-opacity group-hover:opacity-100">
                {{ t('actor.copyActorRoute') }}
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { DocumentDuplicateIcon, CheckIcon } from "@heroicons/vue/24/outline"

    const props = defineProps<{ actorURI: string }>()
    const { t } = useI18n()
    const isCopied = ref<boolean>(false)

    async function copyActorRoute() {
        // https://github.com/elk-zone/elk/blob/4f5648f1512484b84967fcf81186cde1ee2fb9cc/app/components/account/AccountHeader.vue#L199
        try {
            await navigator.clipboard.writeText(props.actorURI)
        }
        catch (error) {
            console.error('Failed to copy account name:', error)
        }

        isCopied.value = true
        setTimeout(() => {
            isCopied.value = false
        }, 2000)
    }

</script>
