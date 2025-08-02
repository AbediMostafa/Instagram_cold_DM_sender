import { defineStore } from 'pinia';
import ApiService from '../core/services/ApiService';
import Swal from 'sweetalert2/dist/sweetalert2.js';
import { hideModal } from "@/core/helpers/modal";

export const useDmPostStore = defineStore('dmPost', {
    state: () => ({
        dmPosts: {
            data: [],
            total: 0,
            current_page: 1,
            key: '',
        },
        dmPostsForDropDown: [],
        is: {
            loading: false,
            creating: false,
            editing: false,
            creatingDmPost: false,
            updatingDmPost: false,
        },

        checkedDmPostRows: [],
        dmPostData: {
            title: '',
            priority: '',
            category: '',
        }
    }),
    actions: {
        getDmPosts(page = 1) {
            this.is.loading = true;
            ApiService.post(`dm-posts`, { page })
                .then(response => {
                    this.dmPosts.data = response.data.data;
                    this.dmPosts.total = response.data.total;
                })
                .finally(() => this.is.loading = false);
        },

        getDmPostsForDropDown() {
            ApiService.post(`dm-posts/get-dm-posts`, {})
                .then(response => this.dmPostsForDropDown = response.data);
        },

        createDmPost() {
            this.is.creating = true;
            ApiService.post('dm-posts/create', this.dmPostData)
                .then(this.getDmPosts)
                .finally(() => this.is.creating = false);
        },

        updateDmPost(id) {
            ApiService.post(`dm-posts/edit/${id}`, this.dmPostData)
                .then(() => {
                    this.is.editing = false;
                    this.cancelEditing(this.dmPostData); // Reset the form
                });
        },

        editDmPost(dmPost) {
            dmPost.editing = true;
            this.dmPostData = dmPost;
        },

        cancelEditing(dmPost) {
            dmPost.editing = false;
            this.dmPostData = {
                title: '',
                category: '',
                priority: '',
            };
        },

        cancelCreating() {
            this.is.creatingDmPost = false;
            this.dmPostData = {
                title: '',
                priority: '',
                category: '',
            };
        },

        resetSearch() {
            this.dmPosts.key = '';
            this.getDmPosts();
        },

        deleteSelected(id) {
            const ids = [id];

            Swal.fire({
                title: 'Are you sure you want to delete the DM Post?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Yes, delete it!',
            }).then(async (result) => {
                if (result.isConfirmed) {
                    try {
                        ApiService.post('dm-posts/delete', { ids })
                            .then(this.getDmPosts);
                    } catch (error) {
                        console.error('Error deleting DM posts:', error);
                    }
                }
            });
        },

        checkRows(e) {
            this.checkedDmPostRows = e.target.checked
                ? this.dmPosts.data.map((dmPost) => dmPost.id)
                : [];
        },

        warnIfNotSelected(selected) {
            if (selected.length) return true;

            Swal.fire({
                icon: 'error',
                text: 'Please select at least one DM Post to proceed.',
            });

            return false;
        },
    },
});
