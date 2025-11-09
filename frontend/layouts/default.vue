<template>
    <Html :lang="htmlAttrs.lang" :dir="htmlAttrs.dir" class="h-full bg-white">

    <Body class="h-full max-w-7xl mx-auto">
        <div class="flex min-h-full flex-col">
            <header class="fixed top-0 shrink-0 bg-white/95 w-full inset-x-0">
                <div class="sticky top-0 flex h-16 shrink-0 items-center">
                    <slot name="mobile">
                        <LayoutsDefaultNavigationMobile />
                    </slot>
                    <div class="fixed top-0 w-full hidden md:flex md:max-w-md mx-auto inset-x-0">
                        <slot name="search">
                            <LayoutsDefaultNavigationSearch />
                        </slot>
                    </div>
                </div>
            </header>
            <div class="mx-auto flex w-full max-w-7xl items-start gap-x-4 px-4 py-10 sm:px-6 lg:px-8">
                <aside class="sticky top-8 hidden md:w-20 lg:w-60 shrink-0 md:block">
                    <!-- Left column area -->
                    <slot name="sidebar">
                        <LayoutsDefaultNavigationSidebar />
                    </slot>
                </aside>
                <main class="flex-1">
                    <!-- Main area -->
                    <slot />
                </main>
                <aside class="sticky hidden w-60 overflow-y-auto py-6 lg:px-8 lg:block">
                    <!-- Right column area -->
                    <slot name="asidebar">
                        <LayoutsDefaultNavigationSidebarFooter />
                    </slot>
                </aside>
            </div>
        </div>
    </Body>

    </Html>
</template>

<script setup lang="ts">
    const head = useLocaleHead({
        dir: true,
        seo: true,
    })
    const htmlAttrs = computed(() => head.value.htmlAttrs!)
</script>