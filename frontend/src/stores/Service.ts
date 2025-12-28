import { defineStore } from "pinia";
import ApiService from "@/core/services/ApiService";
import Swal from "sweetalert2/dist/sweetalert2.js";

export const useServiceStore = defineStore("ServiceStore", {
    state() {
        return {
            checkedServiceRows: [] as number[],

            services: {
                data: [] as any[],
                current_page: 1,
                total: 0,
            },

            queryParams: {},

            is: {
                loading: false,
                deleting: false,
                searching: false,
            },
        };
    },

    actions: {
        deleteSelected(ids: number[]) {
            this.warnIfdosntSelected(ids) &&
            Swal.fire({
                title: "Are you sure you want to delete selected service(s)?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, delete it!",
            }).then((result) => {
                if (result.isConfirmed) {
                    ApiService.post("service/delete", { ids }).then(() =>
                        this.getServices()
                    );
                }
            });
        },

        warnIfdosntSelected(selected: number[]) {
            if (selected.length) return true;

            Swal.fire({
                icon: "error",
                text: "Please select at least one service to proceed",
            });

            return false;
        },

        getServices(page = 1, withLoading = true) {
            if (withLoading) this.is.loading = true;

            this.services.current_page = page;

            const data = {
                page,
                queryParams: this.queryParams,
            };

            ApiService.post("services", data)
                .then((response) => {
                    this.services.data = response.data.data;
                    this.services.total = response.data.total;
                })
                .finally(() => {
                    this.is.loading = false;
                });
        },
        fetchService(q) {
            if (q) {
                this.is.searching = true;
                ApiService.post(`services/search`, {q})
                    .then(response => this.services.data = response.data)
                    .catch(error => console.error('Error fetching tags:', error))
                    .finally(() => this.is.searching = false);
            }
        },

        checkRows(e: Event) {
            const target = e.target as HTMLInputElement;

            this.checkedServiceRows = target.checked
                ? this.services.data.map((service: any) => service.id)
                : [];
        },
    },
});
