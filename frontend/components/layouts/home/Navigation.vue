<template>
  <div class="bg-white">
    <!-- Mobile menu -->
    <TransitionRoot as="template" :show="mobileMenuOpen">
      <Dialog class="relative z-40 lg:hidden" @close="mobileMenuOpen = false">
        <TransitionChild as="template" enter="transition-opacity ease-linear duration-300" enter-from="opacity-0"
          enter-to="opacity-100" leave="transition-opacity ease-linear duration-300" leave-from="opacity-100"
          leave-to="opacity-0">
          <div class="fixed inset-0 bg-black/25" />
        </TransitionChild>

        <div class="fixed inset-0 z-40 flex">
          <TransitionChild as="template" enter="transition ease-in-out duration-300 transform"
            enter-from="-translate-x-full" enter-to="translate-x-0"
            leave="transition ease-in-out duration-300 transform" leave-from="translate-x-0"
            leave-to="-translate-x-full">
            <DialogPanel class="relative flex w-full max-w-xs flex-col overflow-y-auto bg-white pb-12 shadow-xl">
              <div class="flex px-4 pt-5 pb-2">
                <button type="button" class="-m-2 inline-flex items-center justify-center rounded-md p-2 text-gray-400"
                  @click="mobileMenuOpen = false">
                  <span class="sr-only">{{ t("nav.close") }}</span>
                  <XMarkIcon class="size-6" aria-hidden="true" />
                </button>
              </div>

              <!-- Links -->
              <div class="space-y-6 border-t border-gray-200 px-4 py-6">
                <div v-for="(nav, i) in navigation" :key="`nav-${i}`" class="flow-root">
                  <NuxtLinkLocale :to="nav.to" class="-m-2 block p-2 font-medium text-gray-900">{{ t(nav.name) }}
                  </NuxtLinkLocale>
                </div>
              </div>

              <div class="space-y-6 border-t border-gray-200 px-4 py-6">
                <!-- Currency selector -->
                <form>
                  <div class="-ml-2 inline-grid grid-cols-1">
                    <select id="mobile-currency" name="currency" aria-label="Currency"
                      class="col-start-1 row-start-1 w-full appearance-none rounded-md bg-white py-0.5 pr-7 pl-2 text-base font-medium text-gray-700 group-hover:text-gray-800 focus:outline-2 sm:text-sm/6">
                      <option v-for="currency in currencies" :key="currency">{{ currency }}</option>
                    </select>
                    <ChevronDownIcon
                      class="pointer-events-none col-start-1 row-start-1 mr-1 size-5 self-center justify-self-end fill-gray-500"
                      aria-hidden="true" />
                  </div>
                </form>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </Dialog>
    </TransitionRoot>
    <!-- Hero section -->
    <div class="relative bg-gray-900">
      <!-- Decorative image and overlay -->
      <div aria-hidden="true" class="absolute inset-0 overflow-hidden">
        <img src="/images/hops/meg-macdonald-OCp00Tg3iGU-unsplash.jpg" alt="" class="size-full object-cover" />
      </div>
      <div aria-hidden="true" class="absolute inset-0 bg-gray-700 opacity-40" />
      <!-- Navigation -->
      <header class="relative z-10">
        <nav aria-label="Top">
          <!-- Top navigation -->
          <div class="bg-gray-900">
            <div class="mx-auto flex h-10 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
              <!-- Currency selector -->
              <form>
                <div class="-ml-2 inline-grid grid-cols-1">
                  <select id="desktop-currency" name="currency" aria-label="Currency"
                    class="col-start-1 row-start-1 w-full appearance-none rounded-md bg-gray-900 py-0.5 pr-7 pl-2 text-left text-base font-medium text-white focus:outline-2 focus:-outline-offset-1 focus:outline-white sm:text-sm/6">
                    <option v-for="currency in currencies" :key="currency">{{ currency }}</option>
                  </select>
                  <ChevronDownIcon
                    class="pointer-events-none col-start-1 row-start-1 mr-1 size-5 self-center justify-self-end fill-gray-300"
                    aria-hidden="true" />
                </div>
              </form>

              <div class="flex items-center space-x-6">
                <PwaBadge />
                <PwaInstallPrompt />
                <AlertsButton />
                <AuthenticationNavigation />
              </div>
            </div>
          </div>

          <!-- Secondary navigation -->
          <div class="bg-white/10 backdrop-blur-md backdrop-filter">
            <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <div>
                <div class="flex h-16 items-center justify-between">
                  <!-- Logo (lg+) -->
                  <div class="hidden lg:flex lg:flex-1 lg:items-center">
                    <NuxtLinkLocale to="/">
                      <span class="sr-only">{{ t("common.title") }}</span>
                      <img class="h-8 w-auto" src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=white"
                        alt="" />
                    </NuxtLinkLocale>
                  </div>

                  <div class="hidden h-full lg:flex">
                    <!-- Flyout menus -->
                    <PopoverGroup class="inset-x-0 bottom-0 px-4">
                      <div class="flex h-full justify-center space-x-8">
                        <NuxtLinkLocale v-for="(nav, i) in navigation" :key="`nav-mobile-${i}`" :to="nav.to"
                          class="flex items-center text-sm font-medium text-white">
                          {{ t(nav.name) }}
                        </NuxtLinkLocale>
                      </div>
                    </PopoverGroup>
                  </div>

                  <!-- Mobile menu and search (lg-) -->
                  <div class="flex flex-1 items-center lg:hidden">
                    <button type="button" class="-ml-2 p-2 text-white" @click="mobileMenuOpen = true">
                      <span class="sr-only">{{ t("nav.open") }}</span>
                      <Bars3Icon class="size-6" aria-hidden="true" />
                    </button>

                    <!-- Search -->
                    <a href="#" class="ml-2 p-2 text-white">
                      <span class="sr-only">{{ t("nav.search") }}</span>
                      <MagnifyingGlassIcon class="size-6" aria-hidden="true" />
                    </a>
                  </div>

                  <!-- Logo (lg-) -->
                  <NuxtLinkLocale to="/" class="lg:hidden">
                    <span class="sr-only">{{ t("common.title") }}</span>
                    <img src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=white" alt=""
                      class="h-8 w-auto" />
                  </NuxtLinkLocale>

                  <div class="flex flex-1 items-center justify-end">
                    <a href="#" class="hidden text-sm font-medium text-white lg:block">{{ t("nav.search") }}</a>

                    <div class="flex items-center lg:ml-8">
                      <!-- Cart -->
                      <div class="ml-4 flow-root lg:ml-8">
                        <a href="#" class="group -m-2 flex items-center p-2">
                          <ShoppingBagIcon class="size-6 shrink-0 text-white" aria-hidden="true" />
                          <span class="ml-2 text-sm font-medium text-white">0</span>
                          <span class="sr-only">{{ t("shop.accessibility.onicon") }}</span>
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </nav>
      </header>

      <div class="relative mx-auto flex max-w-3xl flex-col items-center px-6 py-32 text-center sm:py-64 lg:px-0">
        <h1 class="text-4xl font-bold tracking-tight text-white lg:text-6xl">{{ t("shop.homehero.header") }}</h1>
        <p class="mt-4 text-xl text-white">{{ t("shop.homehero.description") }}</p>
        <a href="#"
          class="mt-8 inline-block rounded-md border border-transparent bg-white px-8 py-3 text-base font-medium text-gray-900 hover:bg-gray-100">{{
            t("shop.homehero.call") }}</a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import {
    TransitionChild,
    TransitionRoot,
    Dialog,
    DialogPanel,
    PopoverGroup,
  } from "@headlessui/vue"
  import { Bars3Icon, MagnifyingGlassIcon, ShoppingBagIcon, XMarkIcon, ChevronDownIcon } from "@heroicons/vue/24/outline"

  const { t } = useI18n()
  const mobileMenuOpen = ref(false)
  const navigation = [
    { name: "nav.about", to: "/about" },
    { name: "nav.blog", to: "/blog" },
  ]
  const currencies = ['CAD', 'USD', 'AUD', 'EUR', 'GBP']
</script>