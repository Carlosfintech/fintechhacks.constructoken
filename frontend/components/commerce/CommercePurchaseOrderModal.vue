<template>
    <div class="self-center justify-self-end ml-0.5">
        <button type="button" @click="openModal" :title="t('commerce.buy')" :disabled="product_id === ''"
            class="cursor-pointer inline-flex items-center rounded-md bg-hops-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-hops-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-hops-600 dark:bg-hops-500 dark:shadow-none dark:hover:bg-hops-400 dark:focus-visible:outline-hops-500">
            {{ t("commerce.buy") }}
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
                                        <div class="space-y-2">
                                            <div class="space-y-1">
                                                <label for="email" class="block text-sm font-medium text-gray-700">
                                                    {{ t("login.email_address") }}
                                                </label>
                                                <div class="mt-1 group relative inline-block w-full">
                                                    <Field id="email" name="email" type="email" autocomplete="email"
                                                        v-model="postEmail"
                                                        class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-hops-600 focus:outline-none focus:ring-hops-600 sm:text-sm" />
                                                    <ErrorMessage name="email"
                                                        class="absolute left-5 top-5 translate-y-full w-48 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700" />
                                                </div>
                                            </div>
                                            <div class="space-y-1">
                                                <label for="wallet" class="block text-sm font-medium text-gray-700">
                                                    {{ t("commerce.wallet_address") }}
                                                </label>
                                                <div class="mt-1 group relative inline-block w-full">
                                                    <Field id="wallet" name="wallet" type="text" v-slot="{ field }">
                                                        <div :class="[
                                                            errorState ?
                                                                'border-thunderbird-500 bg-thunderbird-100' :
                                                                'border-gray-300 placeholder-gray-400 focus-within:border-hops-600 focus-within:outline-none focus-within:ring-hops-600 sm:text-sm',
                                                            'flex items-center rounded-md border']">
                                                            <input v-bind="field"
                                                                @click.prevent="toggleErrorState(false)"
                                                                class="block min-w-0 grow py-2 px-3 border-transparent rounded-md focus:border-transparent focus:outline-none focus:ring-transparent sm:text-sm/6 shadow-sm" />
                                                        </div>
                                                    </Field>
                                                    <div v-if="errorState"
                                                        class="absolute left-5 top-6 translate-y-full w-60 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700">
                                                        {{ t("commerce.orderError") }}
                                                    </div>
                                                    <ErrorMessage name="required"
                                                        class="absolute left-5 top-6 translate-y-full w-60 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700" />
                                                    <Field id="required" name="required" type="hidden" :value="true" />
                                                </div>
                                            </div>
                                            <!-- Order -->
                                            <section aria-labelledby="order-heading" class="mt-2">
                                                <h2 id="order-heading" class="sr-only">Product order</h2>
                                                <div
                                                    class="cursor-pointer rounded-lg p-1 border border-gray-200 bg-gray-50 hover:bg-gray-100 hover:border-gray-500">
                                                    <div class="flex items-center justify-between">
                                                        <div>
                                                            <span class="text-sm font-medium text-gray-900">{{
                                                                order.name }} - </span>
                                                            <span class="text-sm text-gray-500">{{ order.description
                                                                }}</span>
                                                        </div>
                                                        <span class="text-sm font-medium text-gray-900 shrink">
                                                            {{ order.currency }}{{ price }}
                                                        </span>
                                                    </div>
                                                </div>
                                            </section>
                                            <div class="flex items-center justify-between pt-2">
                                                <button type="submit" @click.prevent="closeModal"
                                                    :title="t('forms.cancel')"
                                                    class="rounded-md bg-thunderbird-300 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-thunderbird-400">
                                                    {{ t("forms.cancel") }}
                                                </button>
                                                <button type="submit" :title="t('commerce.buy')"
                                                    class="rounded-md bg-hops-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-hops-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-hops-600 dark:bg-hops-500 dark:shadow-none dark:hover:bg-hops-400 dark:focus-visible:outline-hops-500">
                                                    {{ t("commerce.buy") }}
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
    import { apiOpenPayments } from "@/api"
    import type { IKeyable } from "@/interfaces"

    const { t } = useI18n()
    const authStore = useAuthStore()
    const tokenStore = useTokenStore()
    const props = defineProps<{ product_id?: string, volume: number }>()
    const order = ref<IKeyable>({})
    const price = ref<number>(0)
    const errorState = ref<boolean>(false)
    const postEmail = ref<string>("")
    const schema = {
        email: { email: true, required: true },
        wallet: { required: true },
    }

    const products: IKeyable[] = [
        { id: "01K24SCPT4JG59FYRVE5RXPX7J", name: "Standard", description: "1 kg, vaccuum-sealed for freshness.", price: 15, currency: "€" },
        { id: "01K66D4JD67CRDXV750450V6P4", name: "Bulk", description: "5 kg, vaccuum-sealed for freshness.", price: 25, currency: "€" },
    ]

    function toggleErrorState(newState: boolean) {
        errorState.value = newState
    }
    function setOrder() {
        order.value = {} as IKeyable
        if (props.product_id) {
            order.value = products.find((item) => item.id === props.product_id) as IKeyable
            price.value = order.value.price * props.volume
        }
    }

    watch(() => [props.product_id, props.volume], () => {
        setOrder()
    },
        { immediate: true }
    )

    onMounted(async () => {
        if (authStore.loggedIn) postEmail.value = authStore.profile.email
        setOrder()
    })

    async function submit(values: any) {
        if (authStore.loggedIn) await tokenStore.refreshTokens()
        try {
            const { data: response } = await apiOpenPayments.orderProduct(props.product_id as string, values.wallet, props.volume, tokenStore.token)
            // toggleModal(false)
            if (response.value) {
                console.log("order response", response.value.msg)
                return await navigateTo(response.value.msg, {
                    external: true,
                })
            }
        } catch (error) {
            toggleErrorState(true)
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