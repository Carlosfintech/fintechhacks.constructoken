<template>
    <main class="max-w-none mx-auto sm:w-3/5 prose prose-reader-light prose-reader-base prose-reader-compact px-4 pt-10 pb-20 sm:px-6">
      <ContentRenderer v-if="page" :value="page" />
    </main>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: ["refresh"],
});

const route = useRoute()
const { locale } = useI18n()

const { data: page } = await useAsyncData(route.path, () => {
  return queryCollection("blog").path(route.path).first()
})
if (!page.value) {
  // https://stackblitz.com/edit/nuxt-starter-jnysug?file=pages%2F[...slug].vue
  const pathWithoutLocale = route.path.replace(
    new RegExp(`^/${locale.value}(\/|$)`),
    "/"
  )
  const { data: page } = await useAsyncData(route.path, () => {
    return queryCollection("blog").path(pathWithoutLocale).first()
  })
  if (!page.value)
    throw createError({ statusCode: 404, statusMessage: "Page not found" })
}
</script>
  