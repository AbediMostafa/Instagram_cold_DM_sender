import { defineStore } from 'pinia';
import ApiService from '../core/services/ApiService';
import Swal from 'sweetalert2/dist/sweetalert2.js';
import { hideModal } from "@/core/helpers/modal";

export const useLeadSourceStore = defineStore('leadSource', {
    state: () => ({
        leadSources: {
            data: [],
            total: 0,
            current_page: 1,
            key: '',
        },
        leadSourcesForDropDown: [],
        is: {
            loading: false,
            creating: false,
            editing: false,
            creatingLeadSource: false,
            updatingLeadSource: false,
        },

        checkedLeadSourceRows: [],
        leadSourceData: {
            title: '',
            category: '',
        }
    }),
    actions: {
        getLeadSources(page = 1) {
            this.is.loading = true;
            ApiService.post(`lead-sources`, { page })
                .then(response => {
                    this.leadSources.data = response.data.data;
                    this.leadSources.total = response.data.total;
                })
                .finally(() => this.is.loading = false);
        },

        getLeadSourcesForDropDown() {
            ApiService.post(`lead-sources/get-lead-sources`, {})
                .then(response => this.leadSourcesForDropDown = response.data);
        },

        createLeadSource() {
            this.is.creating = true;
            ApiService.post('lead-sources/create', this.leadSourceData)
                .then(this.getLeadSources)
                .finally(() => this.is.creating = false);
        },

        updateLeadSource(id) {
            ApiService.post(`lead-sources/edit/${id}`, this.leadSourceData)
                .then(() => {
                    this.is.editing = false;
                    this.cancelEditing(this.leadSourceData); // Pass the current data
                });
        },

        editLeadSource(leadSource) {
            leadSource.editing = true;
            this.leadSourceData = leadSource;
        },

        cancelEditing(leadSource) {
            leadSource.editing = false;
            this.leadSourceData = {
                title: '',
                category: '',
            };
        },

        cancelCreating() {
            this.is.creatingLeadSource = false;
            this.leadSourceData = {
                title: '',
                category: '',
            };
        },

        resetSearch() {
            this.leadSources.key = '';
            this.getLeadSources();
        },

        deleteSelected(id) {
            const ids = [id];

            Swal.fire({
                title: 'Are you sure you want to delete the lead source?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, delete it!',
            }).then(async (result) => {
                if (result.isConfirmed) {
                    try {
                        ApiService.post('lead-sources/delete', { ids })
                            .then(this.getLeadSources);
                    } catch (error) {
                        console.error('Error deleting lead sources:', error);
                    }
                }
            });
        },

        checkRows(e) {
            this.checkedLeadSourceRows = e.target.checked
                ? this.leadSources.data.map((leadSource) => leadSource.id)
                : [];
        },

        warnIfNotSelected(selected) {
            if (selected.length) return true;

            Swal.fire({
                icon: 'error',
                text: 'Please select at least one lead source to proceed.',
            });

            return false;
        },
    },
});
