
import { defineStore } from "pinia";
import ApiService from "@/core/services/ApiService";
import { ref } from "vue";
import { hideModal } from "@/core/helpers/modal";
import Swal from "sweetalert2/dist/sweetalert2.js";

export const useProxyStore = defineStore('ProxyStore', {
    state() {
        return {
            checkedProxyRows: [],
            proxies: {
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
            this.warnIfNotSelected(ids) &&
            Swal.fire({
                title: "Are you sure you want to delete selected proxy(s)?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, delete it!"
            }).then((result) => {
// Read more about isConfirmed, isDenied below
                if (result.isConfirmed) {
                    ApiService.post('proxy/delete', { ids })
                        .then(this.getProxies)
                }
            });
        },

        warnIfNotSelected(selected) {
            if (selected.length)
                return true;

            Swal.fire({
                icon: "error",
                text: "Please select at least one proxy to proceed",
            });

            return false;
        },

        getProxies(page = 1, withLoading = true) {
            if (withLoading)
                this.is.loading = true;

            ApiService.post('proxies', { page })
                .then(response => {
                    this.proxies.data = response.data.data
                    this.proxies.total = response.data.total
                    this.proxies.current_page = response.data.current_page
                })
                .finally(() => {
                    this.is.loading = false
                })
        },

        checkRows(e) {
            this.checkedProxyRows = e.target.checked ?
                this.proxies.data.map(proxy => proxy.id) : []
        },
    }
})