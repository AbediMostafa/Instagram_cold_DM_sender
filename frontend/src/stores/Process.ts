import { defineStore } from "pinia";
import ApiService from "@/core/services/ApiService";
import Swal from "sweetalert2/dist/sweetalert2.js";

export const useProcessStore = defineStore("ProcessStore", {
    state() {
        return {
            checkedProcessRows: [] as number[],
            selectedServers: [] as string[],

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
        clearCheckedRows() {
            this.checkedProcessRows = [];
        },

        deleteSelected(ids: number[]) {
            // If no rows selected but servers are selected, delete by servers
            if (ids.length === 0 && this.selectedServers.length > 0) {
                this.deleteByServers();
                return;
            }

            if (!this.warnIfdosntSelected(ids)) return;

            Swal.fire({
                title: "Are you sure you want to delete selected process(es)?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, delete it!",
            }).then((result) => {
                if (result.isConfirmed) {
                    ApiService.post("processes/delete", { ids }).then(() => {
                        this.clearCheckedRows();
                        this.getProcesses();
                    });
                }
            });
        },

        deleteByServers() {
            Swal.fire({
                title: `Delete ALL processes on ${this.selectedServers.length} server(s)?`,
                text: "This action cannot be undone!",
                icon: "error",
                showCancelButton: true,
                confirmButtonColor: "#d33",
                confirmButtonText: "Yes, delete all",
            }).then((result) => {
                if (result.isConfirmed) {
                    ApiService.post("processes/delete-by-servers", {
                        server_ips: this.selectedServers,
                    }).then(() => {
                        this.clearCheckedRows();
                        this.getProcesses();
                    });
                }
            });
        },

        warnIfdosntSelected(selected: number[]) {
            if (selected.length) return true;

            Swal.fire({
                icon: "error",
                text: "Please select at least one process or server to proceed",
            });

            return false;
        },

        getProcesses(page = 1, filters = {}, withLoading = true) {
            if (withLoading) this.is.loading = true;

            this.processes.current_page = page;

            const params = {
                page,
                ...filters,
            };

            ApiService.query("processes", { params })
                .then((response) => {
                    this.processes.data = response.data.data;
                    this.processes.total = response.data.total;
                })
                .finally(() => {
                    this.is.loading = false;
                });
        },

        setWorkflow(workflow_id, ids: number[]) {
            // If no rows selected but servers are selected, set workflow by servers
            if (ids.length === 0 && this.selectedServers.length > 0) {
                this.setWorkflowByServers(workflow_id);
                return;
            }

            if (!this.warnIfdosntSelected(ids)) return;

            this.is.loading = true;
            ApiService.post("processes/set-workflow", { workflow_id, ids })
                .then(() => {
                    this.clearCheckedRows();
                    this.getProcesses();
                })
                .finally(() => {
                    this.is.loading = false;
                });
        },

        setWorkflowByServers(workflow_id) {
            this.is.loading = true;
            ApiService.post("processes/set-workflow-by-servers", {
                server_ips: this.selectedServers,
                workflow_id,
            })
                .then(() => {
                    this.clearCheckedRows();
                    this.getProcesses();
                })
                .finally(() => {
                    this.is.loading = false;
                });
        },

        setStatusTo(status: string, ids: number[]) {
            // If no rows selected but servers are selected, set status by servers
            if (ids.length === 0 && this.selectedServers.length > 0) {
                this.setStatusByServers(status);
                return;
            }

            if (!this.warnIfdosntSelected(ids)) return;

            this.is.loading = true;
            ApiService.post("processes/set-status", { status, ids })
                .then(() => {
                    this.clearCheckedRows();
                    this.getProcesses();
                })
                .finally(() => {
                    this.is.loading = false;
                });
        },

        setStatusByServers(status: string) {
            const action = status === 'running' ? 'Start' : 'Stop';

            Swal.fire({
                title: `${action} all processes on ${this.selectedServers.length} server(s)?`,
                icon: status === 'running' ? "question" : "warning",
                showCancelButton: true,
                confirmButtonText: `Yes, ${action.toLowerCase()} all`,
            }).then((result) => {
                if (result.isConfirmed) {
                    this.is.loading = true;
                    ApiService.post("processes/set-status-by-servers", {
                        server_ips: this.selectedServers,
                        status,
                    })
                        .then(() => {
                            this.clearCheckedRows();
                            this.getProcesses();
                        })
                        .finally(() => {
                            this.is.loading = false;
                        });
                }
            });
        },

        checkRows(e: Event) {
            const target = e.target as HTMLInputElement;

            this.checkedProcessRows = target.checked
                ? this.processes.data.map((process: any) => process.id)
                : [];
        },

        setSelectedServers(servers: string[]) {
            this.selectedServers = servers;
        },
    },
});