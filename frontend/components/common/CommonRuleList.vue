<template>
    <div class="flow-root">
        <h2 class="text-center text-2xl/9 font-bold tracking-tight text-gray-900">
            {{ t("rules.title") }}
        </h2>
        <p class="text-sm text-center font-medium text-hops-500 hover:text-hops-600 my-6">
            {{ t("rules.prompt") }}
        </p>
        <ul role="list" class="-mb-8">
            <li v-for="rule in ruleSet" :key="`rule-${rule.order}`">
                <div class="relative pb-4">
                    <span v-if="rule.order !== ruleSet.length - 1"
                        class="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />
                    <div class="relative flex space-x-3">
                        <div>
                            <span
                                class="bg-hops-500 flex size-8 items-center justify-center rounded-full ring-8 ring-white text-white">
                                {{ rule.order + 1 }}
                            </span>
                        </div>
                        <div>
                            <p class="text-sm text-gray-500">
                                {{ rule.text }}
                            </p>
                        </div>
                    </div>
                </div>
            </li>
        </ul>
    </div>
</template>

<script setup lang="ts">
    import type { IRule } from "@/interfaces"
    import { apiInstance } from "@/api"

    const { locale, t } = useI18n()
    const ruleSet = ref<IRule[]>([])

    onMounted(async () => {
        // Get the Rules
        try {
            const { data: response } = await apiInstance.getRules(locale.value)
            if (response.value) ruleSet.value = response.value
        } catch (error) { console.log(error) }
    })
</script>