FROM node:22.15 AS build
ENV NODE_ENV=development APP_ENV=development NITRO_HOST=${NUXT_HOST:-0.0.0.0} NITRO_PORT=${NUXT_PORT:-3000} NUXT_TELEMETRY_DISABLED=1
# ENV PATH /frontend/node_modules/.bin:$PATH
COPY . /frontend
WORKDIR /frontend
RUN yarn install --frozen-lockfile --network-timeout 100000 --non-interactive
RUN yarn build --standalone
EXPOSE ${NUXT_PORT}

FROM build AS run-dev
# ENTRYPOINT ["yarn"]
CMD ["yarn", "dev"]

FROM build AS run-start
ENV NODE_ENV=production APP_ENV=production
ENTRYPOINT ["yarn"]
CMD ["start"]

FROM node:22.15-alpine AS run-minimal
ARG NUXT_VERSION=^3.15.4
ARG PINIA_VERSION=^3.0.1
ARG PINIA_NUXT_VERSION=^0.10.1
ARG PINIA_PERSISTED_VERSION=^4.2.0
ARG NUXT_CONTENT_VERSION=^3.2.2
ARG I18N_VERSION=^9.2.1
ARG VEE_VERSION=^4.15.0
ARG VEE_INT_VERSION=^4.15.0
ARG VEE_RULES_VERSION=^4.15.0
ARG TAILWINDCSS_VERSION=^4.0.8
ARG TAILWINDCSS_VITE_VERSION=^4.0.8
ARG POSTCSS_VERSION=^8.5.3
ARG ASPECT_RATIO_VERSION=^0.4.2
ARG FORMS_VERSION=^0.5.10
ARG TYPOGRAPHY_VERSION=^0.5.16
ARG VITE_PWA_NUXT_VERSION=^0.10.6
ARG HEADLESSUI_VERSION=^1.7.23
ARG HEROICONS_VERSION=^2.2.0
ARG NUXT_ROBOTS_VERSION=^5.2.4
ARG QR_CODE_VERSION=^3.6.0
ARG ACTIVITYPUB_TYPES=^1.1.0
ARG INFINITE_LOADING_VERSION=^2.4.5
ARG NUXT_UI_VERSION=^3.3.2
ARG BROWSER_FS_ACCESS_VERSION=^0.38.0
ENV NODE_ENV=production APP_ENV=production NITRO_HOST=${NUXT_HOST:-0.0.0.0} NITRO_PORT=${NUXT_PORT:-3000} NUXT_TELEMETRY_DISABLED=1
WORKDIR /frontend
RUN yarn add nuxt@${NUXT_VERSION} pinia@${PINIA_VERSION} @pinia/nuxt@${PINIA_NUXT_VERSION} pinia-plugin-persistedstate@${PINIA_PERSISTED_VERSION} @nuxt/content@${NUXT_CONTENT_VERSION} @nuxtjs/i18n@${I18N_VERSION} vee-validate@${VEE_VERSION} @vee-validate/i18n@${VEE_INT_VERSION} @vee-validate/rules@${VEE_RULES_VERSION} tailwindcss@${TAILWINDCSS_VERSION} @tailwindcss/vite@${TAILWINDCSS_VITE_VERSION} postcss@${POSTCSS_VERSION} @tailwindcss/aspect-ratio@${ASPECT_RATIO_VERSION} @tailwindcss/forms@${FORMS_VERSION} @tailwindcss/typography@${TYPOGRAPHY_VERSION} @vite-pwa/nuxt@${VITE_PWA_NUXT_VERSION} @headlessui/vue@${HEADLESSUI_VERSION} @heroicons/vue@${HEROICONS_VERSION} @nuxtjs/robots@${NUXT_ROBOTS_VERSION} qrcode.vue@${QR_CODE_VERSION} activitypub-types@{ACTIVITYPUB_TYPES} vue-infinite-loading@{INFINITE_LOADING_VERSION} @nuxt/ui@{NUXT_UI_VERSION} browser-fs-access@${BROWSER_FS_ACCESS_VERSION}
COPY --from=build /frontend/.nuxt ./.nuxt
COPY --from=build /frontend/.output ./.output
COPY --from=build /frontend/api ./api
COPY --from=build /frontend/assets ./assets
COPY --from=build /frontend/components ./components
COPY --from=build /frontend/composables ./composables
COPY --from=build /frontend/content ./content
COPY --from=build /frontend/interfaces ./interfaces
COPY --from=build /frontend/layouts ./layouts
COPY --from=build /frontend/middleware ./middleware
COPY --from=build /frontend/pages ./pages
COPY --from=build /frontend/plugins ./plugins
COPY --from=build /frontend/public ./public
COPY --from=build /frontend/stores ./stores
COPY --from=build /frontend/utilities ./utilities
COPY --from=build /frontend/.env ./
COPY --from=build /frontend/app.vue ./
COPY --from=build /frontend/nuxt.config* ./
COPY --from=build /frontend/tailwind.config* ./
COPY --from=build /frontend/content.config* ./
COPY --from=build /frontend/robots.txt ./
COPY --from=build /frontend/tsconfig.json ./
COPY --from=build /frontend/package.json ./
ENTRYPOINT [ "yarn" ]
CMD [ "start" ]
