import {defineStore} from "pinia";
import ApiService from "@/core/services/ApiService";
import {ref} from "vue";
import {hideModal} from "@/core/helpers/modal";
import Swal from "sweetalert2/dist/sweetalert2.js";


export const useTemplateStore = defineStore('TemplateStore', {
    state() {
        return {
            checkedTemplateRows: [],
            selectedTemplate: {
                category_id: '',
                caption: '',
                id: ''
            },
            templates: {
                data: {},
                current_page: 1,
                total: 0,
                queryParams: {
                    tags: [],
                    category_id: '',
                    type: 'name-username',
                    color: 1,
                },
                receivedType: 'username',
            },
            types: [],
            colors: [],
            is: {
                loading: false,
                deleting: false,
                gettingTemplate: false
            },

        }
    },

    actions: {
        deleteSelected(ids) {
            this.warnIfdosntSelected(ids) &&
            Swal.fire({
                title: "Are you sure you want to delete selected templates?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, delete it!"
            }).then((result) => {
                if (result.isConfirmed) {
                    ApiService.post('template/delete', {ids, receivedType: this.templates.receivedType})
                        .then(this.getTemplates)
                }
            });
        },

        warnIfdosntSelected(selected) {
            if (selected.length)
                return true;

            Swal.fire({
                icon: "error",
                text: "Please select one template to proceed",
            });

            return false;
        },

        getTemplates(page = 1) {
            this.is.loading = true;

            ApiService.post('templates', {page, ...this.templates.queryParams})
                .then(response => {
                    this.templates.data = response.data.data
                    this.templates.total = response.data.meta.total;
                    this.templates.current_page = response.data.meta.current_page;
                    this.templates.receivedType = response.data.type
                })
                .finally(() => {
                    this.checkedTemplateRows = [];
                    this.is.loading = false
                })
        },

        getTemplate() {
            this.is.gettingTemplate = true;

            ApiService.post('template/view', {id: this.selectedTemplate.id})
                .then(response => {
                    this.selectedTemplate = {...response.data};
                })
                .finally(() => this.is.gettingTemplate = false)
        },

        checkRows(e) {
            this.checkedTemplateRows = e.target.checked ?
                this.templates.data.map(template => template.id) : []
        },

        fetchTypes() {
            return ApiService.post('template/fetch-types', {})
                .then(response => this.types = response.data)
        },
        fetchColors() {
            return ApiService.post('template/fetch-colors', {})
                .then(response => this.colors = response.data)
        },

        updateTemplate() {
            ApiService.post('template/update', this.selectedTemplate)
                .then(this.getTemplates)
                .then(() => hideModal("edit_media_modal"))

        },

        attachTag() {

            const data = {
                templateIds: this.checkedTemplateRows,
                tagIds: this.templates.queryParams.tags
            }

            return ApiService.post('template/attach-tag', data)
        }
    }
})