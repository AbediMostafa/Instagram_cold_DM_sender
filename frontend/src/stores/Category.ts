import {defineStore} from 'pinia';
import ApiService from '../core/services/ApiService';
import Swal from 'sweetalert2/dist/sweetalert2.js';
import {hideModal} from "@/core/helpers/modal";

export const useCategoryStore = defineStore('category', {
    state: () => ({
        categories: {
            data: [],
            total: 0,
            current_page: 1,
            key: '',
        },
        is: {
            loading: false,
            creating: false,
            editing: false,
            creatingCategory: false,
            updatingCategory: false,
        },

        checkedCategoryRows: [],
        categoryData: {
            title: '',
            description: '',
        }
    }),
    actions: {
        getCategories(page = 1) {
            this.is.loading = true;
            ApiService.post(`categories`, {page})
                .then(response => {
                    this.categories.data = response.data.data
                    this.categories.total = response.data.total
                })
                .finally(() => this.is.loading = false)
        },

        createCategory() {
            this.is.creating = true
            ApiService.post('categories/create', this.categoryData)
                .then(this.getCategories)
                .then(() => hideModal("create_category_modal"))
                .finally(() => this.is.creating = false);
        },

        updateCategory(id) {
            ApiService.post(`categories/edit/${id}`, this.categoryData);
        },

        editCategory(category) {
            category.editing = true;
            this.categoryData = category
        },

        cancelEditing(category) {
            category.editing = false;
            this.categoryData = {
                title: '',
                description: '',
            }
        },

        cancelCreating() {
            this.is.creatingCategory = false;
            this.categoryData = {
                title: '',
                description: '',
            }
        },
        resetSearch() {
            this.categories.key = ''
            this.getCategories();
        },

        deleteSelected(id) {
            const ids = [id]

            Swal.fire({
                title: 'Are you sure you want to delete the category?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, delete it!',
            }).then(async (result) => {
                if (result.isConfirmed) {
                    try {
                        ApiService.post('categories/delete', {ids})
                            .then(this.getCategories)
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
