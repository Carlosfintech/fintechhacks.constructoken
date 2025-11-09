<template>
    <div @click.prevent="fileClickHandler" @dragover="handleDragOver" @drop="handleDrop"
        class="flex relative text-center justify-center rounded-lg border border-dashed border-gray-900/25 p-1">
        <div class="relative flex items-center panel">
            <!-- @vue-ignore -->
            <img v-if="fileSrc" class="aspect-auto w-full rounded-lg object-cover" :src="fileSrc as string" />
            <component v-else :is="importer[props.mediaUse].icon" class="size-24 text-gray-300" aria-hidden="true" />
            <div class="w-full absolute bottom-0 left-0 mb-10 inputs">
                <div class="grid grid-cols-2 gap-1">
                    <div class="col-span-2 grid grid-cols-subgrid gap-1">
                        <div class="col-start-2">
                            <CommonAltTextModal :text="actorID" language="fr" @set-alt-text="setAltText" />
                            <button type="button" @click="openModal"
                                class="cursor-pointer rounded-full bg-white p-1 text-sm font-semibold text-gray-900 shadow-xs inset-ring inset-ring-gray-300 hover:bg-gray-100">
                                <PencilIcon class="size-5" aria-hidden="true" />
                            </button>
                        </div>
                        <TransitionRoot appear :show="isOpen" as="template">
                            <Dialog as="div" :open="isOpen" @close="toggleModal" class="relative z-10">
                                <TransitionChild as="template" enter="duration-300 ease-out" enter-from="opacity-0"
                                    enter-to="opacity-100" leave="duration-200 ease-in" leave-from="opacity-100"
                                    leave-to="opacity-0">
                                    <div class="fixed inset-0 bg-black/25" />
                                </TransitionChild>
                                <div class="fixed inset-0 overflow-y-auto">
                                    <div class="flex min-h-full items-center justify-center p-4 text-center">
                                        <TransitionChild as="template" enter="duration-300 ease-out"
                                            enter-from="opacity-0 scale-95" enter-to="opacity-100 scale-100"
                                            leave="duration-200 ease-in" leave-from="opacity-100 scale-100"
                                            leave-to="opacity-0 scale-95">
                                            <DialogPanel
                                                class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                                                <DialogTitle as="h3"
                                                    class="text-lg font-medium leading-6 text-gray-900">
                                                    Payment successful
                                                </DialogTitle>
                                                <div class="mt-2">
                                                    <p class="text-sm text-gray-500">
                                                        Your payment has been successfully submitted. We’ve sent you
                                                        an email with all of the details of your order.
                                                    </p>
                                                </div>
                                                <div class="mt-4">
                                                    <button type="button"
                                                        class="inline-flex justify-center rounded-md border border-transparent bg-blue-100 px-4 py-2 text-sm font-medium text-blue-900 hover:bg-blue-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
                                                        @click="isOpen = false">
                                                        Got it, thanks!
                                                    </button>
                                                </div>
                                            </DialogPanel>
                                        </TransitionChild>
                                    </div>
                                </div>
                            </Dialog>
                        </TransitionRoot>
                    </div>
                    <div>
                        <button type="button" @click.prevent="fileDeleteHandler"
                            class="cursor-pointer rounded-full bg-thunderbird-50 p-1 text-sm font-semibold text-thunderbird-600 shadow-xs inset-ring inset-ring-thunderbird-200 hover:bg-thunderbird-100">
                            <TrashIcon class="size-5" aria-hidden="true" />
                        </button>
                    </div>
                    <div>
                        <button type="button"
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
    import {
        TransitionRoot,
        TransitionChild,
        Dialog,
        DialogPanel,
        DialogTitle
    } from "@headlessui/vue"
    import { fileOpen, type FileWithHandle } from "browser-fs-access"
    import { UserCircleIcon, PhotoIcon } from "@heroicons/vue/24/solid"
    import { TrashIcon, ArrowUpOnSquareIcon, PencilIcon } from "@heroicons/vue/24/outline"
    import { useToastStore } from "@/stores/toasts"
    import type { IKeyable } from "@/interfaces"

    const toast = useToastStore()
    const importer: IKeyable = {
        ICON: {
            icon: UserCircleIcon,
            mimeTypes: [
                "image/gif", "image/jpeg", "image/png"
            ],
            extensions: [".gif", ".jpg", ".jpeg", ".png"],
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
    const props = defineProps<{ mediaUse: string, actorID: string }>()
    const emit = defineEmits<{ setImport: [response: any] }>()
    const fileSrc = ref("")
    const fileImport = ref<File>({} as File)

    onMounted(async () => {
        dragndrop.value = determineDragAndDropCapable()
    })

    // MODAL
    const isOpen = ref(false)

    function toggleModal(value: boolean) {
        isOpen.value = value
    }
    function openModal(event: MouseEvent) {
        event.stopPropagation()
        isOpen.value = true
    }

    function setAltText(text: string) {
        console.log(text)
    }

    // UTILITIES
    async function fileDeleteHandler(event: MouseEvent) {
        event.stopPropagation()
        fileSrc.value = ""
        fileImport.value = {} as File
    }

    async function fileClickHandler() {
        try {
            let response: any[] | any = await fileOpen({
                mimeTypes: importer[props.mediaUse].mimeTypes,
                extensions: importer[props.mediaUse].extensions,
                multiple: importer[props.mediaUse].multiple,
            })
            // if (props.mediaUse !== "DATA") response = await getJSONfromBlob(response)
            console.log(response)
            fileImport.value = await response.handle.getFile()
            fileSrc.value = URL.createObjectURL(fileImport.value)
            console.log(fileSrc.value)
            emit("setImport", response)
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
                let response: any[] = []
                for (const blob of Array.from(event.dataTransfer.files)) {
                    if (!importer[props.mediaUse].mimeTypes.includes(blob.type))
                        throw new Error("Not an allowed mimetype.")
                    // if (props.mediaUse !== "DATA") {
                    //     const altblob = await getJSONfromBlob(blob)
                    //     response.push(altblob)
                    // }
                }
                // if (props.mediaUse !== "DATA") emit("setImport", response)
                emit("setImport", event.dataTransfer.files)
                fileImport.value = await event.dataTransfer.files[0] as File
                fileSrc.value = URL.createObjectURL(fileImport.value)
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