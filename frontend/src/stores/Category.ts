import {defineStore} from 'pinia';
import ApiService from '../core/services/ApiService';
import Swal from 'sweetalert2/dist/sweetalert2.js';

export const useCategoryStore = defineStore('category', {
    state: () => ({
        categories: {
            data: [],
            total: 0,
            current_page: 1,
        },
        is: {
            loading: false,
        },
        checkedCategoryRows: [],
    }),
    actions: {
        getCategories(page = 1) {
            this.is.loading = true;
            ApiService.post(`categories`, {page})
                .then(response => this.categories.data = response.data)
                .finally(() => this.is.loading = false)
        },


        async deleteSelected(ids) {
            if (!this.warnIfNotSelected(ids)) return;

            Swal.fire({
                title: 'Are you sure you want to delete selected category(ies)?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, delete it!',
            }).then(async (result) => {
                if (result.isConfirmed) {
                    try {
                        await ApiService.post('categories/delete', {ids});
                        this.getCategories(this.categories.current_page);
                        Swal.fire('Deleted!', 'Your categories have been deleted.', 'success');
                    } catch (error) {
                        console.error('Error deleting categories:', error);
                    }
                }
            });
        },

        checkRows(e) {
            this.checkedCategoryRows = e.target.checked
                ? this.categories.data.map((account) => account.id)
                : [];
        },

        warnIfNotSelected(selected) {
            if (selected.length) return true;

            Swal.fire({
                icon: 'error',
                text: 'Please select at least one category to proceed.',
            });

            return false;
        },
    },
});
