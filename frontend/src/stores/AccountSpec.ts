import { defineStore } from 'pinia';
import { ref } from 'vue';
import ApiService from '@/core/services/ApiService';
import { ElMessage } from 'element-plus';
import { useDebounceFn } from '@vueuse/core';

export const useAccountSpecStore = defineStore('AccountSpecStore', {
    state() {
        return {
            accountSpecs: {
                data: [] as any[],             // List of AccountSpec objects
                total: 0,                      // Total number of specs
                current_page: 1,               // Current page for pagination
                search: '',                    // Search string
                sortBy: 'last_reels_scan_at',  // Default sort field
                sortDesc: true,                // Default descending
            },
            is: {
                loading: false,
            },
        };
    },

    actions: {
        /**
         * Fetch paginated account specs from the backend
         */
        getAccountSpecs(page: number = 1, withLoading: boolean = true) {
            if (withLoading) this.is.loading = true;

            this.accountSpecs.current_page = page;

            const payload = {
                page,
                search: this.accountSpecs.search,
                sortBy: this.accountSpecs.sortBy,
                sortDesc: this.accountSpecs.sortDesc,
            };

            return ApiService.post('account-specs', payload)
                .then((response) => {
                    this.accountSpecs.data = response.data.data;
                    this.accountSpecs.total = response.data.total;
                })
                .catch((err) => {
                    ElMessage.error('Failed to fetch account specs');
                    console.error(err);
                })
                .finally(() => {
                    this.is.loading = false;
                });
        },

        /**
         * Sort the account specs table by a given field
         */
        sortAccountSpecsBy(field: string) {
            if (this.accountSpecs.sortBy === field) {
                this.accountSpecs.sortDesc = !this.accountSpecs.sortDesc;
            } else {
                this.accountSpecs.sortBy = field;
                this.accountSpecs.sortDesc = false;
            }
            this.getAccountSpecs(this.accountSpecs.current_page);
        },

        /**
         * Update a single account spec
         * Example: after rescanning reels
         */
        updateAccountSpec(specId: number, payload: any) {
            this.is.loading = true;

            return ApiService.post(`account-specs/${specId}/update`, payload)
                .then(() => {
                    // Optionally refresh the current page
                    return this.getAccountSpecs(this.accountSpecs.current_page, false);
                })
                .catch((err) => {
                    ElMessage.error('Failed to update account spec');
                    console.error(err);
                })
                .finally(() => {
                    this.is.loading = false;
                });
        },

        /**
         * Refresh all account specs (optional bulk action)
         */
        refreshAllSpecs() {
            this.is.loading = true;
            return ApiService.post('account-specs/refresh-all')
                .then(() => this.getAccountSpecs(this.accountSpecs.current_page))
                .catch((err) => {
                    ElMessage.error('Failed to refresh account specs');
                    console.error(err);
                })
                .finally(() => (this.is.loading = false));
        },
    },
});
