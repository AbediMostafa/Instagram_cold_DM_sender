import { defineStore } from 'pinia';
import ApiService from '../core/services/ApiService';
import Swal from 'sweetalert2/dist/sweetalert2.js';
import { hideModal } from "@/core/helpers/modal";

export const useHashtagStore = defineStore('hashtag', {
    state: () => ({
        hashtags: {
            data: [],
            total: 0,
            current_page: 1,
            key: '',
        },
        hashtagsForDropDown: [],
        is: {
            loading: false,
            creating: false,
            editing: false,
            creatingHashtag: false,
            updatingHashtag: false,
        },

        checkedHashtagRows: [],
        hashtagData: {
            title: '',
            category: '',
        }
    }),
    actions: {
        getHashtags(page = 1) {
            this.is.loading = true;
            ApiService.post(`hashtags`, { page })
                .then(response => {
                    this.hashtags.data = response.data.data;
                    this.hashtags.total = response.data.total;
                })
                .finally(() => this.is.loading = false);
        },

        getHashtagsForDropDown() {
            ApiService.post(`hashtags/get-hashtags`, {})
                .then(response => this.hashtagsForDropDown = response.data);
        },

        createHashtag() {
            this.is.creating = true;
            ApiService.post('hashtags/create', this.hashtagData)
                .then(this.getHashtags)
                .finally(() => this.is.creating = false);
        },

        updateHashtag(id) {
            ApiService.post(`hashtags/edit/${id}`, this.hashtagData)
                .then(() => {
                    this.is.editing = false;
                    this.cancelEditing(hashtag)
                });
        },

        editHashtag(hashtag) {
            hashtag.editing = true;
            this.hashtagData = hashtag;
        },

        cancelEditing(hashtag) {
            hashtag.editing = false;
            this.hashtagData = {
                title: '',
                description: '',
            };
        },

        cancelCreating() {
            this.is.creatingHashtag = false;
            this.hashtagData = {
                title: '',
                description: '',
            };
        },

        resetSearch() {
            this.hashtags.key = '';
            this.getHashtags();
        },

        deleteSelected(id) {
            const ids = [id];

            Swal.fire({
                title: 'Are you sure you want to delete the hashtag?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, delete it!',
            }).then(async (result) => {
                if (result.isConfirmed) {
                    try {
                        ApiService.post('hashtags/delete', { ids })
                            .then(this.getHashtags);
                    } catch (error) {
                        console.error('Error deleting hashtags:', error);
                    }
                }
            });
        },

        checkRows(e) {
            this.checkedHashtagRows = e.target.checked
                ? this.hashtags.data.map((hashtag) => hashtag.id)
                : [];
        },

        warnIfNotSelected(selected) {
            if (selected.length) return true;

            Swal.fire({
                icon: 'error',
                text: 'Please select at least one hashtag to proceed.',
            });

            return false;
        },
    },
});
