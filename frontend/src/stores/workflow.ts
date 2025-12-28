import { defineStore } from "pinia";
import ApiService from "@/core/services/ApiService";
import Swal from "sweetalert2/dist/sweetalert2.js";

export const useWorkflowStore = defineStore("WorkflowStore", {
    state: () => ({
        checkedWorkflowRows: [] as number[],

        workflows: {
            data: [] as any[],
            current_page: 1,
            total: 0,
        },

        queryParams: {},

        is: {
            loading: false,
            deleting: false,
        },
    }),

    actions: {
        getWorkflows(page = 1, withLoading = true) {
            if (withLoading) this.is.loading = true;
            this.workflows.current_page = page;

            const data = {
                page,
                queryParams: this.queryParams,
            };

            ApiService.post("workflows", data)
                .then((response) => {
                    this.workflows.data = response.data.data;
                    this.workflows.total = response.data.total;
                })
                .finally(() => {
                    this.is.loading = false;
                });
        },

        deleteSelected(ids: number[]) {
            if (!this.warnIfNotSelected(ids)) return;

            Swal.fire({
                title: "Are you sure you want to delete selected workflow(s)?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, delete it!",
            }).then((result) => {
                if (result.isConfirmed) {
                    ApiService.post("workflow/delete", { ids }).then(() => this.getWorkflows());
                }
            });
        },

        warnIfNotSelected(selected: number[]) {
            if (selected.length) return true;
            Swal.fire({ icon: "error", text: "Please select at least one workflow to proceed" });
            return false;
        },

        checkRows(e: Event) {
            const target = e.target as HTMLInputElement;
            this.checkedWorkflowRows = target.checked
                ? this.workflows.data.map((workflow: any) => workflow.id)
                : [];
        },
    },
});
