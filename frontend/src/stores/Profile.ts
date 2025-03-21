import {defineStore} from "pinia";
import ApiService from "@/core/services/ApiService";
import {ref} from "vue";
import Swal from "sweetalert2/dist/sweetalert2.js";
import {hideModal} from "@/core/helpers/modal";

export const useProfileStore = defineStore('ProfileStore', {
    state() {
        return {
            checkedProfileRows: [],
            profiles: {
                data: [],
                current_page: 1,
                total: 0,
                search: {
                    text: "",
                    type: "",
                },
            },
            profile: {
                title: "",
                folder: "",
                profile_id: "",
                accounts: [],
                proxy_id: "",
            },
            is: {
                loading: false,
                deleting: false,
                creating: false,
                assigning: false,
            },
        }
    },

    actions: {
        checkRows(e) {
            this.checkedProfileRows = e.target.checked
                ? this.profiles.data.map((profile) => profile.id)
                : [];
        },

        deleteSelected(ids) {
            const selectedIds = ids.length ? ids : this.checkedProfileRows;
            
            if (!selectedIds.length) {
                Swal.fire({
                    icon: "error",
                    text: "Please select one profile to proceed",
                });
                return;
            }

            Swal.fire({
                title: "Are you sure you want to delete selected profile(s)?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, delete it!"
            }).then((result) => {
                if (result.isConfirmed) {
                    ApiService.post('profiles/delete', {ids: selectedIds})
                        .then(() => {
                            this.checkedProfileRows = [];
                            this.getProfiles();
                        });
                }
            });
        },

        getProfiles(page = 1, withLoading = true) {
            if (withLoading)
                this.is.loading = true;

            ApiService.post('profiles', {page, ...this.profiles.search})
                .then(response => {
                    this.profiles.data = response.data.data;
                    this.profiles.total = response.data.total;
                    this.profiles.current_page = response.data.current_page;
                })
                .finally(() => {
                    this.is.loading = false;
                });
        },

        createProfile() {
            this.is.creating = true
            ApiService.post("profiles/create", this.profile)
                .then(() => {
                    hideModal("create_profile_modal");
                    this.getProfiles();
                })
                .finally(() => {
                    this.is.creating = false;
                });
        },

        assignProfiles(ids = []) {
            this.is.assigning = true
            ApiService.post("profiles/make-and-assign-profiles", {ids})
                .finally(() => {
                    this.is.assigning = false;
                });
        },
        changeProxyToResidential(ids = []) {
            this.is.assigning = true
            ApiService.post("account/change-profile-proxy-to-residential", {ids})
                .finally(() => {
                    this.is.assigning = false;
                });
        },
        changeProxyToCustom(ids = []) {
            this.is.assigning = true
            ApiService.post("account/change-profile-proxy-to-custom", {ids})
                .finally(() => {
                    this.is.assigning = false;
                });
        }
    }
});
