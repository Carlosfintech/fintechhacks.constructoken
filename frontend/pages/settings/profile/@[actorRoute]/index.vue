<template>
    <form class="mx-auto py-10 lg:pb-3">
        <h2 class="text-base/7 font-semibold text-gray-900 dark:text-white">{{ t("actor.informationSR") }}</h2>
        <div class="flex items-center justify-between my-2">
            <div class="flex items-center">
                <Switch v-model="actorUpdate.locked"
                    class="group relative inline-flex h-5 w-10 flex-shrink-0 cursor-pointer items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-hops-600 focus:ring-offset-2">
                    <span class="sr-only">{{ t("actor.locked") }}</span>
                    <span aria-hidden="true" class="pointer-events-none absolute h-full w-full rounded-md bg-white" />
                    <span aria-hidden="true"
                        :class="[actorUpdate.locked ? 'bg-hops-500' : 'bg-gray-200', 'pointer-events-none absolute mx-auto h-4 w-9 rounded-full transition-colors duration-200 ease-in-out']" />
                    <span aria-hidden="true"
                        :class="[actorUpdate.locked ? 'translate-x-5' : 'translate-x-0', 'pointer-events-none absolute left-0 inline-block h-5 w-5 transform rounded-full border border-gray-200 bg-white shadow ring-0 transition-transform duration-200 ease-in-out']" />
                </Switch>
                <span class="flex items-center text-sm ml-1 mr-5 font-bold">{{ t("actor.locked") }}</span>
                <Switch v-model="actorUpdate.discoverable"
                    class="group relative inline-flex h-5 w-10 flex-shrink-0 cursor-pointer items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-hops-600 focus:ring-offset-2">
                    <span class="sr-only">{{ t("actor.discoverable") }}</span>
                    <span aria-hidden="true" class="pointer-events-none absolute h-full w-full rounded-md bg-white" />
                    <span aria-hidden="true"
                        :class="[actorUpdate.discoverable ? 'bg-hops-500' : 'bg-gray-200', 'pointer-events-none absolute mx-auto h-4 w-9 rounded-full transition-colors duration-200 ease-in-out']" />
                    <span aria-hidden="true"
                        :class="[actorUpdate.discoverable ? 'translate-x-5' : 'translate-x-0', 'pointer-events-none absolute left-0 inline-block h-5 w-5 transform rounded-full border border-gray-200 bg-white shadow ring-0 transition-transform duration-200 ease-in-out']" />
                </Switch>
                <span class="flex items-center text-sm ml-1 font-bold">{{ t("actor.discoverable") }}</span>
            </div>
            <CommonLocaleDropdown :language="actorStore.editingLocale as string"
                @set-locale-select="watchLocaleSelect" />
        </div>
        <div class="lg:grid lg:grid-cols-3 lg:gap-x-4">
            <!-- Actor details -->
            <div class="col-span-2">
                <div class="flex items-center gap-x-4">
                    <div class="shrink-0">
                        <SettingsProfileImageImportCard media-use="ICON" @set-import="watchSetIconImport"
                            @set-metadata="watchSetIconMetadata" @remove-media="watchRemoveIcon" />
                    </div>
                    <div class="w-full">
                        <p class="text-sm text-gray-600 line-clamp-1">@{{ actorRoute }}</p>
                        <div class="mt-2 max-w-full">
                            <input id="name" name="name" type="text" v-model="actorUpdate.name"
                                class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-hops-600 focus:outline-none focus:ring-hops-600 sm:text-sm" />
                        </div>
                    </div>
                </div>
                <div>
                    <div class="mt-1 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
                        <div class="col-span-full">
                            <label for="summary_raw" class="block text-sm/6 font-medium text-gray-900 dark:text-white">
                                {{ t("actor.summary") }}
                            </label>
                            <div class="mt-2">
                                <textarea name="summary_raw" id="summary_raw" rows="5" v-model="actorUpdate.summary_raw"
                                    class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-hops-600 focus:outline-none focus:ring-hops-600 sm:text-sm" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <!-- Standout image -->
            <SettingsProfileImageImportCard media-use="STANDOUT" @set-import="watchSetStandoutImport"
                @set-metadata="watchSetStandoutMetadata" @remove-media="watchRemoveStandout" />
        </div>
        <div>
            <div class="table w-full border-collapse border-0 mt-2 text-sm font-medium text-gray-900">
                <div class="table-header-group">
                    <div class="table-row border-transparent">
                        <div class="table-cell border-0">
                            <span v-if="attachments && attachments.length">
                                {{ t("actor.attachmentTerm") }}
                            </span>
                            <span v-else>{{ t("actor.attachmentAdd") }}</span>
                        </div>
                        <div v-if="attachments && attachments.length" class="table-cell border-0">
                            {{ t("actor.attachmentValue") }}
                        </div>
                        <div class="table-cell border-0 text-right align-middle">
                            <button @click.prevent="addAttachment" :title="t('forms.add')" class="hover:text-hops-600">
                                <PlusCircleIcon class="h-5 w-5" />
                            </button>
                        </div>
                    </div>
                </div>
                <div v-if="attachments && attachments.length" class="table-row-group">
                    <div v-for="(term, aIdx) in attachments" :key="`attachment-${aIdx}`"
                        class="table-row border-transparent">
                        <div v-if="attachments[aIdx]" class="table-cell border-0 p-1">
                            <label :for="`attachment-name-${aIdx}`" class="sr-only">{{ t("actor.attachmentTerm")
                                }}</label>
                            <input :id="`attachment-name-${aIdx}`" v-model="attachments[aIdx].name"
                                :name="`attachment-name-${aIdx}`" type="text" :placeholder="t('actor.attachmentTerm')"
                                required
                                class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-hops-600 focus:outline-none focus:ring-hops-600 sm:text-sm" />
                        </div>
                        <div v-if="attachments[aIdx]" class="table-cell border-0">
                            <label for="attachment-value" class="sr-only">{{ t("actor.attachmentValue") }}</label>
                            <input :id="`attachment-value-${aIdx}`" v-model="attachments[aIdx].value" type="text"
                                :placeholder="t('actor.attachmentValue')"
                                class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-hops-600 focus:outline-none focus:ring-hops-600 sm:text-sm" />
                        </div>
                        <div v-if="attachments[aIdx]" class="table-cell border-0 text-right align-middle">
                            <button v-show="attachments.length > 0" @click.prevent="removeAttachment(aIdx)"
                                :title="t('forms.remove')" class="hover:text-thunderbird-600">
                                <MinusCircleIcon class="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="mt-10 flex items-center justify-end gap-x-6">
            <button type="submit" @click.prevent="submit" :title="t('forms.submit')"
                class="inline-flex items-center rounded-md bg-hops-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-hops-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-hops-600 dark:bg-hops-500 dark:shadow-none dark:hover:bg-hops-400 dark:focus-visible:outline-hops-500">
                {{ t("forms.submit") }}
            </button>
        </div>
    </form>
</template>

<script setup lang="ts">
    import { Switch } from "@headlessui/vue"
    import { PlusCircleIcon, MinusCircleIcon } from "@heroicons/vue/16/solid"
    import type { IKeyable, IActorUpdate, IMediaImport } from "@/interfaces"
    import { useActorStore } from "@/stores/actor"
    import { useToastStore } from "@/stores/toasts"
    import { useTokenStore } from "@/stores/tokens"
    import { apiActivity } from "@/api"

    definePageMeta({
        middleware: ["refresh"],
    });

    const { t, locale } = useI18n()
    const route = useRoute()

    const actorStore = useActorStore()
    const toastStore = useToastStore()
    const tokenStore = useTokenStore()
    const actorUpdate = ref<IActorUpdate>({} as IActorUpdate)
    const handle = ref("")
    const actorRoute = ref("")
    const iconMetadata = ref<IMediaImport>({})
    const iconFile = ref<File>({} as File)
    const iconEditState = ref<string>("None")
    const standoutMetadata = ref<IMediaImport>({})
    const standoutFile = ref<File>({} as File)
    const standoutEditState = ref<string>("None")
    const attachments = ref<IKeyable[]>([])

    // SAVE / UPDATE
    async function processMedia(isIcon: boolean, mediaMetadata: IMediaImport, mediaFile: File, existingMedia: IKeyable, editState: string) {
        switch (editState) {
            case "Update":
                // Update media
                if (existingMedia && Object.hasOwn(existingMedia, "id") && existingMedia.id) {
                    try {
                        await apiActivity.updateMediaForActor(tokenStore.token, actorUpdate.value.id, mediaMetadata)
                    } catch (error) {
                        toastStore.addNotice({
                            title: "Update error",
                            content: error as string,
                            icon: "error"
                        })
                    }
                }
                break
            case "Create":
                // Create media 
                if (mediaMetadata && Object.hasOwn(mediaMetadata, "type") && mediaMetadata.type == "Image") {
                    if (isIcon) {
                        mediaMetadata.actor_avatar_id = actorUpdate.value.id
                        mediaMetadata.as_avatar = true
                    } else {
                        mediaMetadata.actor_standout_id = actorUpdate.value.id
                        mediaMetadata.as_standout = true
                    }
                    mediaMetadata.language = actorStore.editingLocale
                    let formData: FormData = new FormData()
                    formData.append("data", JSON.stringify(mediaMetadata))
                    formData.append("file", mediaFile, mediaFile.name)
                    try {
                        await apiActivity.postMediaForActor(tokenStore.token, formData)
                    } catch (error) {
                        toastStore.addNotice({
                            title: "Upload error",
                            content: error as string,
                            icon: "error"
                        })
                    }
                }
                break
            case "Delete":
                // Media must be removed
                if (existingMedia && Object.hasOwn(existingMedia, "id") && existingMedia.id) {
                    try {
                        await apiActivity.deleteMediaForActor(tokenStore.token, actorUpdate.value.id, existingMedia.id as string)
                    } catch (error) {
                        toastStore.addNotice({
                            title: "Deletion error",
                            content: error as string,
                            icon: "error"
                        })
                    }
                }
                break
        }
    }

    async function submit() {
        actorUpdate.value.attachment = JSON.parse(JSON.stringify(attachments.value)) as IKeyable[]
        actorUpdate.value.language = actorStore.editingLocale
        await tokenStore.refreshTokens()
        // Step 1 - Update avatar image
        await processMedia(true, iconMetadata.value, iconFile.value, actorUpdate.value.icon as IKeyable, iconEditState.value)
        // Step 2 - Update standout image
        await processMedia(false, standoutMetadata.value, standoutFile.value, actorUpdate.value.standout as IKeyable, standoutEditState.value)
        // Step 3 - Update the actor profile
        await actorStore.updateActor(actorUpdate.value)
    }

    // WATCHERS
    async function watchLocaleSelect(select: string) {
        actorStore.setLanguageActorUpdate(select)
    }

    // ATTACHMENTS
    function addAttachment(): void {
        if (!attachments.value) attachments.value = [] as IKeyable[]
        const newAttachment: IKeyable = {
            name: "",
            type: "PropertyValue",
            value: "",
        }
        attachments.value.splice(attachments.value.length, 1, newAttachment)
    }

    function removeAttachment(term: number): void {
        if (attachments.value && attachments.value.length) attachments.value.splice(term, 1)
    }

    // IMAGE IMPORTERS - START
    async function watchSetIconMetadata(data: IMediaImport) {
        if (iconEditState.value != "Create") iconEditState.value = "Update"
        iconMetadata.value = data
    }

    async function watchSetStandoutMetadata(data: IMediaImport) {
        if (standoutEditState.value != "Create") standoutEditState.value = "Update"
        standoutMetadata.value = data
    }

    async function watchSetIconImport(data: File) {
        iconEditState.value = "Create"
        iconFile.value = data
    }

    async function watchSetStandoutImport(data: File) {
        standoutEditState.value = "Create"
        standoutFile.value = data
    }

    async function watchRemoveIcon() {
        iconEditState.value = "Delete"
        iconMetadata.value = {} as IMediaImport
        iconFile.value = {} as File
    }

    async function watchRemoveStandout() {
        standoutEditState.value = "Delete"
        standoutMetadata.value = {} as IMediaImport
        standoutFile.value = {} as File
    }
    // IMAGE IMPORTERS - END

    onMounted(async () => {
        // lookup the actor
        handle.value = route.params.actorRoute as string
        await actorStore.getActorForUpdate(handle.value, locale.value)
        if (!Object.hasOwn(actorStore.editing, "id")) {
            throw createError({
                statusCode: 404,
                message: t("notfound.actor"),
            })
        }
        actorUpdate.value = {
            id: actorStore.editing.id,
            language: actorStore.editing.language,
            name: actorStore.editing.name,
            summary_raw: actorStore.editing.summary_raw,
            locked: actorStore.editing.locked,
            discoverable: actorStore.editing.discoverable,
            attachment: actorStore.editing.attachment,
            default_persona: actorStore.editing.default_persona
        }
        if (actorStore.editing.attachment && actorStore.editing.attachment.length)
            attachments.value = JSON.parse(JSON.stringify(actorStore.editing.attachment)) as IKeyable[]
        actorRoute.value = handle.value.split("@")[0] as string
    })
</script>
