<template>
    <main class="py-12">
        <div
            class="mx-auto w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
            <div class="min-w-0 flex-1">
                Processing
            </div>
        </div>
    </main>
</template>

<script setup lang="ts">
    /*
        Strictly a processing page. Performs the following steps:
         - Extracts the transaction reference from `key`, and additional parameters `hash` and `interact_ref`.
         - Sends these to the backend for confirmation and processing.
         - Redirects buyer to the order page (logged in) or to the login page.
    */
    import { apiOpenPayments } from "@/api"

    const route = useRoute()
    const authStore = useAuthStore()
    const tokenStore = useTokenStore()

    onMounted(async () => {
        // Check if password requested
        console.log("key", route.params.key as string)
        if (route.query && route.query.hash) console.log("hash", route.query.hash)
        if (route.query && route.query.interact_ref) console.log("interact_ref", route.query.interact_ref)
        if (route.params.key && route.query && route.query.hash && route.query.interact_ref) {
            // Process the references ... assuming no error, redirect to purchase
            if (authStore.loggedIn) await tokenStore.refreshTokens()
            try {
                const { data: response } = await apiOpenPayments.fulfilProduct(route.params.key as string, route.query.hash as string, route.query.interact_ref as string, tokenStore.token)
                // Response will be the order number, which can be used to retrieve the product purchase
                if (authStore.loggedIn) {
                    // Redirect to orders page
                    return await navigateTo(`/settings/orders/${route.params.key as string}`)
                } else {
                    // Redirect to login page
                    return await navigateTo("/login")
                }

            } catch (error) {
                console.log("Deal with it.")
            }

        }
    })
</script>