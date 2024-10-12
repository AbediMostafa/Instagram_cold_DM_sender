import { defineStore } from 'pinia';
import ApiService from '../core/services/ApiService';
import Swal from 'sweetalert2/dist/sweetalert2.js';
import { hideModal } from "@/core/helpers/modal";

export const useTagStore = defineStore('tag', {
    state: () => ({
        tags: {
            data: [],
            total: 0,
            current_page: 1,
            key: '',
        },
        is: {
            loading: false,
            creating: false,
            editing: false,
            creatingTag: false,
            updatingTag: false,
        },

        checkedTagRows: [],
        tagData: {
            title: '',
        }
    }),
    actions: {
        getTags(page = 1) {
            this.is.loading = true;
            ApiService.post(`tags`, { page })
                .then(response => {
                    this.tags.data = response.data.data;
                    this.tags.total = response.data.total;
                })
                .finally(() => this.is.loading = false);
        },

        createTag() {
            this.is.creating = true;
            ApiService.post('tags/create', this.tagData)
                .then(this.getTags)
                .finally(() => this.is.creating = false);
        },

        updateTag(tag) {
            this.is.editing = true
            ApiService.post(`tags/edit/${tag.id}`, this.tagData)
                .then(()=> {
                    this.is.editing = false;
                    this.cancelEditing(tag)
                });
        },

        editTag(tag) {
            tag.editing = true;
            this.tagData = tag;
        },

        cancelEditing(tag) {
            tag.editing = false;
            this.tagData = {
                title: '',
            };
        },

        cancelCreating() {
            this.is.creatingTag = false;
            this.tagData = {
                title: '',
            };
        },

        deleteSelected(id) {
            const ids = [id];

            Swal.fire({
                title: 'Are you sure you want to delete the tag?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, delete it!',
            }).then(async (result) => {
                if (result.isConfirmed) {
                    try {
                        ApiService.post('tags/delete', { ids })
                            .then(this.getTags);

                    } catch (error) {
                        console.error('Error deleting tags:', error);
                    }
                }
            });
        },
    },
});
