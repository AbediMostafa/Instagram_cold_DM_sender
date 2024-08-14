import {defineStore} from "pinia";
import ApiService from "@/core/services/ApiService";
import Swal from "sweetalert2/dist/sweetalert2.js";
import {hideModal, showModal} from "@/core/helpers/modal";

export const useSpintaxStore = defineStore("SpintaxStore", {
    state() {
        return {
            checkedProxyRows: [],
            spintaxes: {
                data: [],
                current_page: 1,
                total: 0,
            },
            is: {
                loading: false,
                deleting: false,
                creating: false,
                updating: false,
                loadingSpintax: false
            },
            spintax: {},
            createSpintaxData: {
                name: '',
                type: '',
                text: '',
            }
        };
    },

    actions: {
        deleteSelected(ids) {
            Swal.fire({
                title: "Are you sure you want to delete selected spintax(s)?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, delete it!",
            }).then((result) => {
                // Read more about isConfirmed, isDenied below
                if (result.isConfirmed) {
                    ApiService.post("spintax/delete", {ids}).then(this.getSpintaxes);
                }
            });
        },

        getSpintaxes(page = 1, withLoading = true) {
            if (withLoading) this.is.loading = true;

            ApiService.post("spintaxes", {page})
                .then((response) => {
                    this.spintaxes.data = response.data.data;
                    this.spintaxes.total = response.data.total;
                    this.spintaxes.current_page = response.data.current_page;
                })
                .finally(() => {
                    this.is.loading = false;
                });
        },

        viewSpintax(id) {
            this.is.loadingSpintax = true;
            showModal("view_spintax_modal")

            ApiService.post('spintaxe/view', {id})
                .then((response) => (this.spintax = response.data))
                .finally(() => this.is.loadingSpintax = false)
        },

        createSpintax() {
            this.is.creating = true;

            ApiService.post('spintaxe/create', {data: this.createSpintaxData})
                .then(this.getSpintaxes)
                .finally(() => {
                    this.is.creating = false;
                    hideModal("create_spintax_modal")
                })
        },

        updateSpintax() {
            this.is.updating = true;

            ApiService.post('spintaxe/update', {data: this.createSpintaxData})
                .then(this.getSpintaxes)
                .finally(() => {
                    this.is.updating = false;
                    hideModal("create_spintax_modal")
                })
        }
    },
});
