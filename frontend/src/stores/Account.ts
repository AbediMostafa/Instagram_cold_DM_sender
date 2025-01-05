import {defineStore} from "pinia";
import ApiService from "@/core/services/ApiService";
import {ref} from "vue";
import {hideModal} from "@/core/helpers/modal";
import Swal from "sweetalert2/dist/sweetalert2.js";
import {ElMessage} from "element-plus";
import {copyToClipboard} from "@/core/helpers/helper";
import {warningPromise} from "@/core/helpers/helper";

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
                sortBy: 'total_cold_dms',
                sortDesc: true,
                category_id: '',
                type:'',
                tags: [],
            },
            accountsData: [],
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
            warningPromise("Are you sure you want to delete selected account(s)?")
                .then(() => ApiService.post("account/delete", {ids}).then(this.getAccounts))
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
                type: this.accounts.type,
                dateRange: this.accounts.dateRange,
                sortBy: this.accounts.sortBy,
                sortDesc: this.accounts.sortDesc,
                tags: this.accounts.tags,
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
        setCategory() {
            const data = {
                categoryId: this.accounts.category_id,
                accountIds: this.checkedAccountRows
            }

            this.warnIfdosntSelected(this.checkedAccountRows) &&
            ApiService.post('account/set-category', data)
                .then(this.getAccounts);

        },
        deleteWarning(ids) {
            ApiService.post('account/delete-warning', {ids})
                .then(this.getAccounts);

        },
        makeActive(ids) {
            ApiService.post('account/make-active', {ids})
                .then(this.getAccounts);

        },
        clearNextLogin(ids) {
            ApiService.post('account/clear-next-login', {ids})
                .then(this.getAccounts);

        },
        clearProfile(ids) {
            ApiService.post('account/clear-profile', {ids})
                .then(this.getAccounts);

        },
        fetchAccounts(q) {
            ApiService.post("accounts/fetch-accounts", {q})
                .then(response => this.accountsData = response.data)
        },
        fetchOtpAndCopy(secretKey) {

            ApiService.post("accounts/get-2fa-code", {secretKey})
                .then(response => {
                    copyToClipboard(response.data)
                })
                .catch(error => {
                    ElMessage.error('Failed to fetch OTP:', error);
                })
        },

        changeProfileProxy(ids){
            const accountType = ids.length ? 'selected accounts':'challenging accounts'
            warningPromise(`Are you sure you want to change ${accountType} profile proxy?`)
                .then(() => ApiService.post("account/change-profile-proxy-to-custom", {ids}))

        }
    },
});
