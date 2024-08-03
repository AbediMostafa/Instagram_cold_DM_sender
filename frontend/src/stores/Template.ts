import {defineStore} from "pinia";
import ApiService from "@/core/services/ApiService";
import {ref} from "vue";
import {hideModal} from "@/core/helpers/modal";
import Swal from "sweetalert2/dist/sweetalert2.js";


export const useTemplateStore = defineStore('TemplateStore', {
    state() {
        return {
            checkedTemplateRows: [],
            templates: {
                data: [],
                current_page: 1,
                total: 0
            },
            is: {
                loading: false,
                deleting: false,
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
                    ApiService.post('template/delete', {ids})
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

            ApiService.post('templates', {page})
                .then(response => {
                    this.templates.data = response.data.data
                    this.templates.total = response.data.total
                    this.templates.current_page = response.data.current_page
                })
                .finally(() => {
                    this.checkedTemplateRows = [];
                    this.is.loading = false
                })
        },

        checkRows(e) {
            this.checkedTemplateRows = e.target.checked ?
                this.templates.data.map(template => template.id) : []
        }
    }
})