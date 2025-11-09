<template>
    <div class="relative text-center">
        <div class="relative text-center flex items-center">
            <img v-if="iconURL" class="size-24 rounded-full" :src="iconURL as string" :alt="actorRoute" />
            <UserCircleIcon v-else class="size-12 text-gray-300 dark:text-gray-500" aria-hidden="true" />
            <div class="w-full absolute top-0 left-0 text-center mt-10 opacity-0 hover:opacity-100 duration-300">
                <button type="button"
                    class="rounded-full bg-white p-1 mr-2 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:shadow-none dark:inset-ring-white/5 dark:hover:bg-white/20">
                    <TrashIcon class="size-5" aria-hidden="true" />
                </button>
                <button type="button"
                    class="rounded-full  bg-white p-1 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-50 dark:bg-white/10 dark:text-white dark:shadow-none dark:inset-ring-white/5 dark:hover:bg-white/20">
                    <ArrowUpOnSquareIcon class="size-5" aria-hidden="true" />
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { UserCircleIcon } from "@heroicons/vue/24/solid"
    import { TrashIcon, ArrowUpOnSquareIcon } from "@heroicons/vue/24/outline"

    const props = defineProps<{ iconURL?: string, actorRoute: string }>()


</script>