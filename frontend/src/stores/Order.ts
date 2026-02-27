import {defineStore} from "pinia";
import ApiService from "@/core/services/ApiService";
import Swal from "sweetalert2/dist/sweetalert2.js";

export const useOrderStore = defineStore("OrderStore", {
    state() {
        return {
            checkedOrderRows: [],
            orders: {
                data: [],
                current_page: 1,
                total: 0,
                category_id: ''
            },
            statuses: [],
            filters: {
                order_id: '',
                link: '',
                status: '',
                service_type: '',
                date_from: '',
                date_to: ''
            },
            is: {
                loading: false,
                deleting: false,
            },
        };
    },

    actions: {
        deleteSelected(ids) {
            this.warnIfdosntSelected(ids) &&
            Swal.fire({
                title: "Are you sure you want to delete selected orders(s)?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, delete it!",
            }).then((result) => {
                if (result.isConfirmed) {
                    ApiService.post("order/delete", {ids}).then(() => this.getOrders());
                }
            });
        },

        warnIfdosntSelected(selected) {
            if (selected.length) return true;

            Swal.fire({
                icon: "error",
                text: "Please select one order to proceed",
            });

            return false;
        },

        getOrders(page = 1, withLoading = true, filters = null) {
            if (withLoading) this.is.loading = true;

            this.orders.current_page = page;

            // Use passed filters or current store filters
            const activeFilters = filters || this.filters;

            const data = {
                page,
                order_id: activeFilters.order_id || '',
                link: activeFilters.link || '',
                status: activeFilters.status || '',
                service_type: activeFilters.service_type || '',
                date_from: '',
                date_to: ''
            };

            // Handle date range
            if (activeFilters.date_range && activeFilters.date_range.length === 2) {
                data.date_from = activeFilters.date_range[0];
                data.date_to = activeFilters.date_range[1];
            }

            // Update store filters if passed
            if (filters) {
                this.filters = {...activeFilters};
            }

            ApiService.post("orders", data)
                .then((response) => {
                    this.orders.data = response.data.data;
                    this.orders.total = response.data.total;
                })
                .finally(() => {
                    this.is.loading = false;
                });
        },

        resetFilters() {
            this.filters = {
                order_id: '',
                link: '',
                status: '',
                service_type: '',
                date_from: '',
                date_to: ''
            };
            this.getOrders(1, true);
        },

        checkRows(e) {
            this.checkedOrderRows = e.target.checked
                ? this.orders.data.map((order) => order.id)
                : [];
        },

        finish(id) {
            Swal.fire({
                title: "Are you sure you want to finish the order?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, finish it!",
            }).then((result) => {
                if (result.isConfirmed) {
                    ApiService.post("order/finish", {id})
                        .then(() => this.getOrders(this.orders.current_page, false))
                        .finally(() => {
                            this.is.loading = false;
                        });
                }
            });
        },

        fail(id) {
            Swal.fire({
                title: "Are you sure you want to fail the order?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, fail it!",
            }).then((result) => {
                if (result.isConfirmed) {
                    ApiService.post("order/fail", {id})
                        .then(() => this.getOrders(this.orders.current_page, false))
                        .finally(() => {
                            this.is.loading = false;
                        });
                }
            });
        },

        reset(id) {
            Swal.fire({
                title: "Are you sure you want to reset the order?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, reset it!",
            }).then((result) => {
                if (result.isConfirmed) {
                    ApiService.post("order/reset", {id})
                        .then(() => this.getOrders(this.orders.current_page, false))
                        .finally(() => {
                            this.is.loading = false;
                        });
                }
            });
        },

        changProcessingCommentsToFree(id) {
            Swal.fire({
                title: "Are you sure you want to reset the order?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, reset it!",
            }).then((result) => {
                if (result.isConfirmed) {
                    ApiService.post("order/change-processing-to-free", {id})
                        .then(() => this.getOrders(this.orders.current_page, false))
                        .finally(() => {
                            this.is.loading = false;
                        });
                }
            });
        }
    },
});