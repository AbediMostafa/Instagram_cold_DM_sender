import {defineStore} from "pinia";
import ApiService from "@/core/services/ApiService";
import Swal from "sweetalert2/dist/sweetalert2.js";
import {ElMessage} from "element-plus";
import {copyToClipboard, warningPromise} from "@/core/helpers/helper";

export const useAccountStore = defineStore("AccountStore", {
    state() {
        return {
            checkedAccountRows: [],
            currentStartingAccount: '',
            accounts: {
                data: [],
                current_page: 1,
                total: 0,
                filters: [],
                uploadPostFilter: [],
                search: '',
                dateRange: '',
                sortBy: 'id',
                sortDesc: false,
                category_id: '',
                type: '',
                tags: [],
                services: [],
            },
            accountsData: [],
            accountStates: [
                {value: "active", label: "active"},
                {value: "suspended", label: "suspended"},
                {value: "challenging", label: "challenging"},
            ],
            // Upload-Post status options for the filter checkbox group
            uploadPostStates: [
                {value: "none", label: "None"},
                {value: "pending", label: "Pending"},
                {value: "connecting", label: "Connecting"},
                {value: "connected", label: "Connected"},
                {value: "failed", label: "Failed"},
                {value: "disconnecting", label: "Disconnecting"},
            ],
            is: {
                loading: false,
                deleting: false,
                profileStarting: false,
                uploadPostStarting: false,
            },
        };
    },

    actions: {
        deleteSelected(ids) {
            this.warnIfdosntSelected(ids) &&
            warningPromise("Are you sure you want to delete selected account(s)?")
                .then(() => ApiService.post("account/delete", {ids}).then(this.getAccounts))
        },
        startSingleProfile(id) {
            this.currentStartingAccount = id;
            this.startProfile([id]);
        },
        startProfile(ids) {
            this.is.profileStarting = true;
            ApiService.post("account/start-profile", {ids})
                .finally(() => {
                    this.is.profileStarting = false;
                })
        },

        // ---- Upload-Post actions ----

        /**
         * Set upload_post_status to 'pending' for selected accounts (bulk).
         * The Python worker will pick these up and run the connect flow.
         */
        connectUploadPost(ids) {
            this.warnIfdosntSelected(ids) &&
            warningPromise("Mark selected account(s) for Upload-Post connection?")
                .then(() => {
                    ApiService.post("account/upload-post-connect", {ids})
                        .then(() => {
                            ElMessage.success('Account(s) marked for connection');
                            this.getAccounts(this.accounts.current_page);
                        })
                })
        },

        /**
         * Set upload_post_status to 'disconnecting' for selected accounts (bulk).
         * The Python worker will pick these up and run the disconnect flow.
         */
        disconnectUploadPost(ids) {
            this.warnIfdosntSelected(ids) &&
            warningPromise("Mark selected account(s) for Upload-Post disconnection?")
                .then(() => {
                    ApiService.post("account/upload-post-disconnect", {ids})
                        .then(() => {
                            ElMessage.success('Account(s) marked for disconnection');
                            this.getAccounts(this.accounts.current_page);
                        })
                })
        },

        /**
         * Toggle Upload-Post for a single account.
         * If not connected -> runs connect script (opens browser).
         * If connected -> disconnects via API.
         */
        toggleUploadPost(id) {
            ApiService.post("account/toggle-upload-post", {id})
                .then((response) => {
                    ElMessage.success(response.data.msg);
                    this.getAccounts(this.accounts.current_page);
                })
        },

        /**
         * Reset upload_post_status to 'none' for selected accounts.
         * Keeps upload_post_username so the profile number can be reused on reconnect.
         */
        resetUploadPostStatus(ids) {
            this.warnIfdosntSelected(ids) &&
            warningPromise("Reset Upload-Post status to 'none' for selected account(s)?")
                .then(() => {
                    ApiService.post("account/reset-upload-post-status", {ids})
                        .then(() => {
                            ElMessage.success('Upload-Post status reset');
                            this.getAccounts(this.accounts.current_page);
                        })
                })
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
                uploadPostFilter: this.accounts.uploadPostFilter,
                search: this.accounts.search,
                type: this.accounts.type,
                dateRange: this.accounts.dateRange,
                sortBy: this.accounts.sortBy,
                sortDesc: this.accounts.sortDesc,
                tags: this.accounts.tags,
                services: this.accounts.services,
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

        attachTag() {
            this.is.loading = true;

            const data = {
                accountIds: this.checkedAccountRows,
                tagIds: this.accounts.tags,
            }

            ApiService.post("account/attach-tag", data)
                .finally(() => this.is.loading = false);

        },
        attachService() {
            this.is.loading = true;

            const data = {
                accountIds: this.checkedAccountRows,
                serviceIds: this.accounts.services,
            }

            ApiService.post("account/attach-service", data)
                .finally(() => this.is.loading = false);

        },
        resetIsUsed(){
            warningPromise("Are you sure you want to reset is used?")
                .then(() => {
                    this.is.loading = true;
                    ApiService.post("account/reset-is-used", {})
                        .finally(() => this.is.loading = false);

                })
        },
        detachService() {
            this.warnIfdosntSelected(this.checkedAccountRows) &&
            warningPromise("Are you sure you want to detach service from selected account(s)?")
                .then(() => {
                    this.is.loading = true;

                    const data = {
                        accountIds: this.checkedAccountRows,
                    }

                    ApiService.post("account/detach-service", data)
                        .then(this.getAccounts)
                        .finally(() => this.is.loading = false);

                })

        },
        detachTag() {
            this.is.loading = true;

            const data = {
                accountIds: this.checkedAccountRows,
                tagIds: this.accounts.tags,
            }

            ApiService.post("account/detach-tag", data)
                .finally(() => this.is.loading = false);

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
                    return response.data
                })
                .catch(error => {
                    ElMessage.error('Failed to fetch OTP:', error);
                })
        },
    },
});