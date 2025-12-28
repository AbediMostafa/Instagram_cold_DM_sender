import { defineStore } from "pinia";
import ApiService from "@/core/services/ApiService";
import Swal from "sweetalert2/dist/sweetalert2.js";

export const useProcessStore = defineStore("ProcessStore", {
    state() {
        return {
            checkedProcessRows: [] as number[],

            processes: {
                data: [] as any[],
                current_page: 1,
                total: 0,
            },

            queryParams: {},

            is: {
                loading: false,
                deleting: false,
            },
        };
    },

    actions: {
        deleteSelected(ids) {
            Swal.fire({
                title: "Are you sure you want to delete selected process(es)?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, delete it!",
            }).then((result) => {
                if (result.isConfirmed) {
                    ApiService.post("processes/delete", { ids }).then(() =>
                        this.getProcesses()
                    );
                }
            });
        },

        warnIfdosntSelected(selected: number[]) {
            if (selected.length) return true;

            Swal.fire({
                icon: "error",
                text: "Please select at least one process to proceed",
            });

            return false;
        },

        getProcesses(page = 1, withLoading = true) {
            if (withLoading) this.is.loading = true;

            this.processes.current_page = page;

            const data = {
                page,
                queryParams: this.queryParams,
            };

            ApiService.post("processes", data)
                .then((response) => {
                    this.processes.data = response.data.data;
                    this.processes.total = response.data.total;
                })
                .finally(() => {
                    this.is.loading = false;
                });
        },
        setWorkflow(workflow_id, ids){
            this.is.loading = true;
            ApiService.post("processes/set-workflow", {workflow_id,ids})
                .then(this.getProcesses)
                .finally(() => {
                    this.is.loading = false;
                });

        },
        setStatusTo(status, ids){
            this.is.loading = true;
            ApiService.post("processes/set-status", {status,ids})
                .then(this.getProcesses)
                .finally(() => {
                    this.is.loading = false;
                });

        },

        checkRows(e: Event) {
            const target = e.target as HTMLInputElement;

            this.checkedProcessRows = target.checked
                ? this.processes.data.map((process: any) => process.id)
                : [];
        },
    },
});
