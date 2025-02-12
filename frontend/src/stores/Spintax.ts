import {defineStore} from "pinia";
import ApiService from "@/core/services/ApiService";
import Swal from "sweetalert2/dist/sweetalert2.js";
import {hideModal, showModal} from "@/core/helpers/modal";

export const useSpintaxStore = defineStore("SpintaxStore", {
    state() {
        return {
            checkedProxyRows: [],
            selectedId: '',
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
            spintax: {
                name:'',
                times:'',
                text:'',
                category_id: '',
            },
            createSpintaxData: {
                name: '',
                times: '',
                text: '',
                category_id: '',
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
            this.getSpintax(id)
        },

        getSpintax(id) {
            ApiService.post('spintaxe/view', {id})
                .then((response) => (this.spintax = response.data))
                .finally(() => this.is.loadingSpintax = false)
        },

        editSpintax(id) {
            this.selectedId = id;
            showModal("edit_spintax_modal");
        },

        createSpintax() {
            this.is.creating = true;

            ApiService.post('spintaxe/create', this.createSpintaxData)
                .then(this.getSpintaxes)
                .finally(() => {
                    this.is.creating = false;
                    hideModal("create_spintax_modal")
                })
        },

        updateSpintax() {
            this.is.updating = true;

            ApiService.post('spintaxe/update', {data: this.spintax})
                .then(this.getSpintaxes)
                .finally(() => {
                    this.is.updating = false;
                    hideModal("create_spintax_modal")
                })
        },

        spintaxTimeMap(time) {
            if (time < 11)
                return {
                    0: 'Cold Dm',
                    1: 'First Follow up',
                    2: 'Second Follow up',
                    3: 'Third Follow up',
                    4: 'fourth Follow up',
                    5: 'fifth Follow up',
                    6: 'sixth Follow up',
                    7: 'seventh Follow up',
                    8: 'eighth Follow up',
                    9: 'ninth Follow up',
                    10: 'tenth Follow up',
                }[time]

            return `${time}th Follow up`
        }

    },
});
