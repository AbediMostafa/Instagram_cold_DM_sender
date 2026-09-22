import {defineStore} from "pinia";
import ApiService from "@/core/services/ApiService";
import Swal from "sweetalert2/dist/sweetalert2.js";

export const useModuleStore = defineStore("ModuleStore", {
    state() {
        return {
            checkedModuleRows: [] as number[],

            modules: {
                data: [] as any[],
                current_page: 1,
                total: 0,
            },

            queryParams: {},

            is: {
                loading: false,
                deleting: false,
                searching: false
            },
        };
    },

    actions: {
        deleteSelected(ids: number[]) {
            this.warnIfdosntSelected(ids) &&
            Swal.fire({
                title: "Are you sure you want to delete selected module(s)?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, delete it!",
            }).then((result) => {
                if (result.isConfirmed) {
                    ApiService.post("modules/delete", {ids}).then(() =>
                        this.getModules()
                    );
                }
            });
        },

        warnIfdosntSelected(selected: number[]) {
            if (selected.length) return true;

            Swal.fire({
                icon: "error",
                text: "Please select at least one module to proceed",
            });

            return false;
        },

        getModules(page = 1, withLoading = true) {
            if (withLoading) this.is.loading = true;

            this.modules.current_page = page;

            const data = {
                page,
                queryParams: this.queryParams,
            };

            return ApiService.post("modules", data)
                .then((response) => {
                    this.modules.data = response.data.data;
                    this.modules.total = response.data.total;
                })
                .finally(() => {
                    this.is.loading = false;
                });
        },
        fetchModules(q) {
            if (q) {
                this.is.searching = true;
                ApiService.post(`modules/search`, {q})
                    .then(response => this.modules.data = response.data)
                    .catch(error => console.error('Error fetching tags:', error))
                    .finally(() => this.is.searching = false);
            }
        },

        checkRows(e: Event) {
            const target = e.target as HTMLInputElement;

            this.checkedModuleRows = target.checked
                ? this.modules.data.map((module: any) => module.id)
                : [];
        },
    },
});
