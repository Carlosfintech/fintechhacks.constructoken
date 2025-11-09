<template>
    <div @click.prevent="fileClickHandler" @dragover="handleDragOver" @drop="handleDrop"
        :class="[mediaUse === 'ICON' ? 'rounded-full' : 'rounded-lg', 'flex relative text-center justify-center border border-dashed border-gray-900/25 p-1']">
        <div class="relative flex items-center panel">
            <!-- @vue-ignore -->
            <img v-if="fileSrc"
                :class="[mediaUse === 'ICON' ? 'size-24 rounded-full' : 'w-full rounded-lg', 'aspect-auto object-cover']"
                :src="fileSrc as string" />
            <component v-else :is="importer[props.mediaUse].icon" class="size-24 text-gray-300" aria-hidden="true" />
            <div :class="[mediaUse === 'ICON' ? 'mb-2 px-2' : 'mb-10', 'w-full absolute bottom-0 left-0 inputs']">
                <div class="grid grid-cols-2 gap-1">
                    <div class="col-span-2 grid grid-cols-subgrid gap-1">
                        <div class="col-start-2">
                            <SettingsProfileAltTextModal :text="media.text as string" @set-alt-text="setAltText"
                                :id="mediaUse" />
                        </div>
                    </div>
                    <div>
                        <button type="button" @click.prevent="fileDeleteHandler" :title="t('forms.remove')"
                            class="cursor-pointer rounded-full bg-thunderbird-50 p-1 text-sm font-semibold text-thunderbird-600 shadow-xs inset-ring inset-ring-thunderbird-200 hover:bg-thunderbird-100">
                            <TrashIcon class="size-5" aria-hidden="true" />
                        </button>
                    </div>
                    <div>
                        <button type="button" :title="t('forms.upload')"
                            class="cursor-pointer rounded-full bg-white p-1 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-100">
                            <ArrowUpOnSquareIcon class="size-5" aria-hidden="true" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { fileOpen } from "browser-fs-access"
    import { UserCircleIcon, PhotoIcon } from "@heroicons/vue/24/solid"
    import { TrashIcon, ArrowUpOnSquareIcon, PencilIcon } from "@heroicons/vue/24/outline"
    import { useToastStore } from "@/stores/toasts"
    import { useActorStore } from "@/stores/actor"
    import type { IKeyable, IMediaImport } from "@/interfaces"

    const { t } = useI18n()
    const toast = useToastStore()
    const actorStore = useActorStore()
    const importer: IKeyable = {
        ICON: {
            icon: UserCircleIcon,
            mimeTypes: [
                "text/csv", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "image/gif", "image/jpeg", "image/png"
            ],
            extensions: [".csv", ".xls", ".xlsx", ".gif", ".jpg", ".jpeg", ".png"],
            multiple: false
        },
        STANDOUT: {
            icon: PhotoIcon,
            mimeTypes: [
                "image/gif", "image/jpeg", "image/png"
            ],
            extensions: [".gif", ".jpg", ".jpeg", ".png"],
            multiple: false
        },
    }
    const dragndrop = ref(false)
    const props = defineProps<{ mediaUse: string }>()
    const emit = defineEmits<{ setImport: [response: any], setMetadata: [response: IMediaImport], removeMedia: [] }>()
    const fileSrc = ref("")
    const fileImport = ref<File>({} as File)
    const media = ref<IMediaImport>({})

    onMounted(async () => {
        setMediaDefault()
        dragndrop.value = determineDragAndDropCapable()
    })

    // WATCHERS
    function setMediaDefault() {
        if (props.mediaUse === "ICON" && actorStore.editing.icon != null) media.value = JSON.parse(JSON.stringify(actorStore.editing.icon))
        if (props.mediaUse === "STANDOUT" && actorStore.editing.standout != null) media.value = JSON.parse(JSON.stringify(actorStore.editing.standout))
        if (media.value == null) media.value = {} as IMediaImport
        if (Object.hasOwn(media.value, "URL") && media.value.URL) fileSrc.value = media.value.URL
    }

    function setAltText(text: string) {
        media.value.language = actorStore.editingLocale
        media.value.text = text
        emit("setMetadata", media.value)
    }

    function setMediaMetadata(data: File) {
        media.value.content_type = data.type
        media.value.file_size = data.size
        media.value.type = "Image"
        if (props.mediaUse === "ICON") media.value.as_avatar = true
        else media.value.as_standout = true
        emit("setMetadata", media.value)
    }

    watch(() => actorStore.editing.id, async () => {
        setMediaDefault()
    })

    // UTILITIES
    async function fileDeleteHandler(event: MouseEvent) {
        event.stopPropagation()
        fileSrc.value = ""
        fileImport.value = {} as File
        media.value = {} as IMediaImport
        emit("removeMedia")
    }

    async function fileClickHandler() {
        try {
            let response: any[] | any = await fileOpen({
                mimeTypes: importer[props.mediaUse].mimeTypes,
                extensions: importer[props.mediaUse].extensions,
                multiple: importer[props.mediaUse].multiple,
            })
            // if (props.mediaUse !== "DATA") response = await getJSONfromBlob(response)
            emit("setImport", response)
            setMediaMetadata(response)
            fileImport.value = await response.handle.getFile()
            fileSrc.value = URL.createObjectURL(fileImport.value)
        } catch (error: any) {
            if (error.name !== "AbortError") {
                toast.addNotice({
                    title: "Import error",
                    content: `Error: ${error}`,
                    icon: "error"
                })
            }
        }
    }

    async function handleDrop(event: DragEvent) {
        event.stopPropagation()
        event.preventDefault()
        try {
            if (event.dataTransfer && event.dataTransfer.files.length) {
                for (const blob of Array.from(event.dataTransfer.files)) {
                    if (!importer[props.mediaUse].mimeTypes.includes(blob.type))
                        throw new Error("Not an allowed mimetype.")
                }
                fileImport.value = await event.dataTransfer.files[0] as File
                fileSrc.value = URL.createObjectURL(fileImport.value)
                emit("setImport", event.dataTransfer.files[0])
                setMediaMetadata(event.dataTransfer.files[0] as File)
            }
        } catch (error: any) {
            if (error.name !== "AbortError") {
                toast.addNotice({
                    title: "Import error",
                    content: `Error: ${error}`,
                    icon: "error"
                })
            }
        }
    }

    function handleDragOver(event: DragEvent) {
        event.preventDefault()
    }

    function determineDragAndDropCapable() {
        // Complete guide to drag and drop files
        // https://serversideup.net/drag-and-drop-file-uploads-with-vuejs-and-axios/
        const div = document.createElement("div")
        return (
            ("draggable" in div || ("ondragstart" in div && "ondrop" in div)) &&
            "FormData" in window &&
            "FileReader" in window
        )
    }
</script>

<style lang="css">
    .inputs {
        opacity: 0.0;
        -webkit-transition: all 300ms ease-in-out;
        -moz-transition: all 300ms ease-in-out;
        -ms-transition: all 300ms ease-in-out;
        -o-transition: all 300ms ease-in-out;
        transition: all 300ms ease-in-out;
    }

    .panel:hover .inputs {
        opacity: 1.0;
    }
</style>