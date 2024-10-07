import {defineStore} from "pinia";
import ApiService from "@/core/services/ApiService";
import {ref} from "vue";
import {hideModal} from "@/core/helpers/modal";
import Swal from "sweetalert2/dist/sweetalert2.js";

export const useAccountStore = defineStore("AccountStore", {
    state() {
        return {
            checkedAccountRows: [],
            accounts: {
                data: [],
                current_page: 1,
                total: 0,
                filters: [],
                search: '',
                dateRange: '',
                sortBy:  'total_cold_dms',
                sortDesc: true,
                category_id:'',
            },
            accountStates: [
                {value: "Active", label: "active"},
                {value: "Suspended", label: "suspended"},
                {value: "Challenging", label: "challenging"},
            ],
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
                title: "Are you sure you want to delete selected account(s)?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, delete it!",
            }).then((result) => {
                /* Read more about isConfirmed, isDenied below */
                if (result.isConfirmed) {
                    ApiService.post("account/delete", {ids}).then(this.getAccounts);
                }
            });
        },

        changeProperty(ids, key, value, msg, handler) {
            this.warnIfdosntSelected(ids) &&
            ApiService.post("account/change-property", {
                ids,
                key,
                value,
                msg,
            }).then(handler);
        },
        warnIfdosntSelected(selected) {
            if (selected.length) return true;

            Swal.fire({
                icon: "error",
                text: "Please select one account to proceed",
            });

            return false;
        },

        getAccounts(page = 1, withLoading = true) {

            if (withLoading) this.is.loading = true;

            this.accounts.current_page = page;

            const data = {
                page,
                filter: this.accounts.filters,
                search: this.accounts.search,
                dateRange: this.accounts.dateRange,
                sortBy: this.accounts.sortBy,
                sortDesc: this.accounts.sortDesc,
            }

            ApiService.post("accounts", data)
                .then((response) => {
                    this.accounts.data = response.data.data;
                    this.accounts.total = response.data.total;
                })
                .finally(() => {
                    this.is.loading = false;
                });
        },

        checkRows(e) {
            this.checkedAccountRows = e.target.checked
                ? this.accounts.data.map((account) => account.id)
                : [];
        },
        sortBy(field) {
            if (this.accounts.sortBy === field) {
                this.accounts.sortDesc = !this.accounts.sortDesc;
            } else {
                this.accounts.sortBy = field;
                this.accounts.sortDesc = false;
            }
            this.getAccounts(this.accounts.current_page);
        },

        clearSort() {
            this.accounts.sortBy = 'total_cold_dms';
            this.accounts.sortDesc = true;
            this.getAccounts(this.accounts.current_page);
        },

        setCategory(){
            const data = {
                categoryId:this.accounts.category_id,
                accountIds :this.checkedAccountRows
            }

            this.warnIfdosntSelected(this.checkedAccountRows) &&
            ApiService.post('account/set-category', data)
                .then(this.getAccounts);

        }
    },
});
