// https://v3.nuxtjs.org/api/configuration/nuxt.config
import tailwindcss from "@tailwindcss/vite"

export default defineNuxtConfig({
  app: {
    head: {
      meta: [
        { charset: "utf-8" },
        // <meta name="viewport" content="width=device-width, initial-scale=1">
        { name: "viewport", content: "width=device-width, initial-scale=1" },
      ],
      script: [
        // <script src="https://myawesome-lib.js"></script>
        // { src: "@/assets/css/main.css" }
      ],
      noscript: [
        // <noscript>Javascript is required</noscript>
        { children: "Javascript is required" },
      ],
    },
    // pageTransition: { name: "page", mode: "out-in" }
  },

  runtimeConfig: {
    // https://nuxt.com/docs/api/composables/use-runtime-config#using-the-env-file
    // Private keys are only available on the server
    apiSecret: process.env.VUE_PRIVATE_TERM,
    // Public keys that are exposed to the client
    public: {
      appName: process.env.VUE_APP_NAME,
      appDomain: process.env.VUE_APP_DOMAIN,
      appEnv: process.env.VUE_APP_ENV,
      apiWS: process.env.VUE_APP_DOMAIN_WS,
      apiUrl: process.env.VUE_APP_DOMAIN_API,
      apiRootUrl: process.env.VUE_APP_DOMAIN_ROOT,
      minNameLength: process.env.MINIMUM_NAME_LENGTH,
      maxNameLength: process.env.MAXIMUM_NAME_LENGTH,
      // idbName: process.env.VUE_IDB_NAME,
      // idbVersion: process.env.VUE_IDB_VERSION,
    },
  },

  modules: [
    // "@nuxt/ui",
    "@vite-pwa/nuxt",
    "@pinia/nuxt",
    "pinia-plugin-persistedstate/nuxt",
    "@nuxtjs/i18n",
    "@nuxtjs/robots",
    "@nuxt/content",
  ],

  // pinia: {
  //   autoImports: [
  //     "definePiniaStore",
  //     "defineStore",
  //   ],
  // },
  piniaPluginPersistedstate: {
    cookieOptions: {
      path: "/",
      // maxAge: 60 * 60 * 24 * 30,
      secure: true,
    },
  },

  content: {
    // https://content.nuxtjs.org/api/configuration
  },

  i18n: {
    // https://phrase.com/blog/posts/nuxt-js-tutorial-i18n/
    // https://v8.i18n.nuxtjs.org/
    // https://stackblitz.com/edit/nuxt-starter-jnysug
    locales: [
      {
        code: "en",
        name: "English",
        language: "en-GB",
        dir: "ltr",
        file: "en-GB.ts",
      },
      {
        code: "fr",
        name: "Français",
        language: "fr-FR",
        dir: "ltr",
        file: "fr-FR.ts",
      },
    ],
    defaultLocale: "en",
    detectBrowserLanguage: false,
    lazy: true,
    strategy: "prefix_and_default",
    vueI18n: "./i18n.config.ts",
    baseUrl: process.env.BASE_URL,
  },

  robots: {
    // https://nuxtseo.com/docs/robots/guides/disable-page-indexing]
  },

  pwa: {
    // https://vite-pwa-org.netlify.app/frameworks/nuxt.html
    // https://github.com/vite-pwa/nuxt/blob/main/playground
    // Generate icons with:
    //   node node_modules/@vite-pwa/assets-generator/bin/pwa-assets-generator.mjs --preset minimal public/images/logo.svg
    registerType: "autoUpdate",
    manifest: {
      name: "Hop Sauna",
      short_name: "Hop Sauna",
      theme_color: "#f43f5e",
      icons: [
        {
          src: "images/pwa-64x64.png",
          sizes: "64x64",
          type: "image/png",
        },
        {
          src: "images/pwa-192x192.png",
          sizes: "192x192",
          type: "image/png",
        },
        {
          src: "images/pwa-512x512.png",
          sizes: "512x512",
          type: "image/png",
          purpose: "any",
        },
        {
          src: "images/maskable-icon-512x512.png",
          sizes: "512x512",
          type: "image/png",
          purpose: "maskable",
        },
      ],
    },
    workbox: {
      navigateFallback: "/",
      globPatterns: [
        "**/*.{js,json,css,html,txt,svg,png,icon,ebpt,woff,woff2,ttf,eot,otf,wasm}",
      ],
    },
    client: {
      installPrompt: true,
    },
    devOptions: {
      enabled: true,
      suppressWarnings: true,
      navigateFallbackAllowlist: [/^\/$/],
      type: "module",
    },
  },

  css: ["~/assets/css/main.css"],

  vite: {
    plugins: [tailwindcss()],
  },

  build: {
    transpile: ["@heroicons/vue"],
  },

  compatibilityDate: "2025-02-24",

  future: {
    compatibilityVersion: 4,
  },

  // devtools: {
  //   enabled: true,
  // },
})
