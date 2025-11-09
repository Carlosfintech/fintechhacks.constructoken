<template>
  <div>

    <Head>
      <Link rel="icon" href="/images/favicon.ico" sizes="any" />
      <Link rel="icon" href="/images/favicon.svg" type="image/svg+xml" />
      <Link rel="apple-touch-icon" href="/images/apple-touch-icon-180x180.png" />
    </Head>
    <div class="h-full">
      <VitePwaManifest />
      <NuxtLoadingIndicator />
      <NuxtLayout>
        <NuxtPage />
      </NuxtLayout>
    </div>
  </div>
</template>
