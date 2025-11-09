<template>
  <main>
    <!-- Product grid -->
    <section aria-labelledby="works-heading"
      class="mx-auto max-w-2xl px-4 pt-12 pb-16 sm:px-6 sm:pt-16 sm:pb-24 lg:max-w-7xl lg:px-8">
      <h2 id="works-heading" class="sr-only">Actors</h2>
      <div
        class="mx-auto mt-20 grid max-w-2xl grid-cols-1 gap-x-6 gap-y-20 sm:grid-cols-2 lg:max-w-4xl lg:gap-x-8 xl:max-w-none">
        <ActorSnapshot v-for="(actor, i) in workingActors" :key="`actor-${i}`" :source="actor"
          class="flex flex-col gap-6 xl:flex-row" />
      </div>
      <!-- <h2 id="works-heading" class="sr-only">Products</h2>
      <div class="mt-20 grid grid-cols-1 gap-x-6 gap-y-10 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 xl:gap-x-8">
        <WorkSnapshot v-for="(work, i) in works" :key="`work-${i}`" :work="work" />
      </div> -->
    </section>
  </main>
</template>

<script setup lang="ts">
  import type { APActor } from "activitypub-types"
  import { tokenIsTOTP } from "@/utilities"
  import { useAuthStore } from "@/stores/auth"
  import { useTokenStore } from "@/stores/tokens"
  import { useCreatorStore } from "@/stores/creator"
  import { apiActivity, apiAuth } from "@/api"
  import type { IWellKnownActor, IActorProfile } from "@/interfaces"

  definePageMeta({
    layout: "home",
  });

  const { locale, t } = useI18n()
  const authStore = useAuthStore()
  const tokenStore = useTokenStore()
  const creatorStore = useCreatorStore()
  const route = useRoute()
  const redirectTOTP = "/totp"
  const redirectAfterLogin = "/"
  const workingActors = ref<IActorProfile[]>([])

  onMounted(async () => {
    // Check if email is being validated
    if (route.query && route.query.magic) {
      // No idea: https://stackoverflow.com/q/74759799/295606
      await new Promise((resolve) => {
        setTimeout(() => {
          resolve(true)
        }, 100)
      })
      await tokenStore.validateMagicTokens(route.query.magic as string)
      if (!authStore.loggedIn) await authStore.magicLogin(route.query.magic as string)
      if (authStore.loggedIn) {
        await creatorStore.getActors(locale.value)
      }
      if (tokenIsTOTP(tokenStore.token)) await navigateTo(redirectTOTP)
      else await navigateTo(redirectAfterLogin)
    }
    // Get any working actors
    try {
      const { data: response } = await apiAuth.getTestText()
      console.log("response", response.value)
    } catch { }
    // try {
    //   const { data: response } = await apiActivity.getPublicActors()
    //   if (response.value && response.value.length) workingActors.value = response.value
    //   console.log(response.value)
    // } catch (error) { console.log(error) }
  })

  const works = <APActor[]>[
    {
      type: "Service",
      name: 'Hops on the Vine',
      inbox: "#",
      outbox: "#",
      url: '#',
      image: {
        type: "Image",
        name: "So fresh they haven't even been harvested yet. We ensure quality by requiring you to harvest them.",
        url: '/images/hops/josh-olalde-C5ZE4kNGEjU-unsplash.jpg'
      },
      attachment: [
        {
          type: "Product",
          name: 'Hops on the Vine',
          description: "So fresh they haven't even been harvested yet. We ensure quality by requiring you to harvest them.",
          image: ['/images/hops/josh-olalde-C5ZE4kNGEjU-unsplash.jpg'],
          offers: {
            type: "Offer",
            priceCurrency: "USD",
            price: 90.00
          }
        }
      ]
    },
    {
      type: "Service",
      name: 'Harvested Hops',
      inbox: "#",
      outbox: "#",
      url: '#',
      image: {
        type: "Image",
        name: "Hops stored in the barrels we harvest them in. Fill your own containers directly from the farm.",
        url: '/images/hops/markus-spiske-qn5iDwvOZgo-unsplash.jpg'
      },
      attachment: [
        {
          type: "Product",
          name: 'Harvested Hops',
          description: "Hops stored in the barrels we harvest them in. Fill your own containers directly from the farm.",
          image: ['/images/hops/markus-spiske-qn5iDwvOZgo-unsplash.jpg'],
          offers: {
            type: "Offer",
            priceCurrency: "USD",
            price: 47.00
          }
        }
      ]
    },
    {
      type: "Service",
      name: 'Bottled Hops',
      inbox: "#",
      outbox: "#",
      url: '#',
      image: {
        type: "Image",
        name: 'Bottled for freshness and delivered to your door. The best a hop can get.',
        url: '/images/hops/markus-spiske-R0PHtuR1ofs-unsplash.jpg'
      },
      attachment: [
        {
          type: "Product",
          name: 'Bottled Hops',
          description: 'Bottled for freshness and delivered to your door. The best a hop can get.',
          image: ['/images/hops/markus-spiske-R0PHtuR1ofs-unsplash.jpg'],
          offers: {
            type: "Offer",
            priceCurrency: "USD",
            price: 23.00
          }
        }
      ]
    },
    {
      type: "Service",
      name: 'Hops for the Future',
      inbox: "#",
      outbox: "#",
      url: '#',
      image: {
        type: "Image",
        name: "These are next year's hops. Order now to ensure your supply.",
        url: '/images/hops/meg-macdonald-ulvpSj-LPMg-unsplash.jpg'
      },
      attachment: [
        {
          type: "Product",
          name: 'Hops for the Future',
          description: "These are next year's hops. Order now to ensure your supply.",
          image: ['/images/hops/meg-macdonald-ulvpSj-LPMg-unsplash.jpg'],
          offers: {
            type: "Offer",
            priceCurrency: "USD",
            price: 23.00
          }
        }
      ]
    },
  ]
</script>