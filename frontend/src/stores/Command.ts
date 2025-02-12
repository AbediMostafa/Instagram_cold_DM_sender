import {defineStore} from 'pinia';
import ApiService from '../core/services/ApiService';
import Swal from 'sweetalert2/dist/sweetalert2.js';
import {hideModal} from "@/core/helpers/modal";

export const useCommandStore = defineStore('command', {
    state: () => ({
        commands: {
            data: [],
            current_page: 1,
            total: 0,
        },
        queryParams:{
            account:'',
            lead:'',
            type:'',
            status:'',
            category_id:'',
        },
        is: {
            loading: false,
        },

        commandTypes:[],
        commandStatuses:[],

        checkedCategoryRows: [],
    }),
    actions: {
        getCommands(page = 1) {
            const data = {
                page,
                queryParams: this.queryParams
            }

            this.is.loading = true;

            ApiService.post(`commands`, data)
                .then(response => {
                    this.commands.data = response.data.data
                    this.commands.total = response.data.total
                })
                .finally(() => this.is.loading = false)
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

        getCommandTypes(){
            ApiService.post('command/get-types',{})
                .then(response=> this.commandTypes = response.data)
        },
        getCommandStatuses(){
            ApiService.post('command/get-statuses',{})
                .then(response=> this.commandStatuses = response.data)
        }
    },
});
