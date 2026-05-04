import {defineStore} from "pinia";
import ApiService from "@/core/services/ApiService";
import {hideModal} from "@/core/helpers/modal";
import Swal from "sweetalert2/dist/sweetalert2.js";


export const useTemplateStore = defineStore('TemplateStore', {
    state() {
        return {
            checkedTemplateRows: [],
            selectedTemplate: {
                category_id: '',
                caption: '',
                id: ''
            },
            // Template currently targeted for the assign-accounts modal.
            // Holds the minimal fields needed by the modal (id, type).
            assignTarget: {
                id: null,
                type: null,
            },
            // Search results for the active-accounts dropdown.
            activeAccountResults: [],
            // Accounts currently assigned (status='pending') to the
            // target template. Loaded in pages so very large pending
            // sets don't freeze the UI.
            assignedAccounts: [],
            assignedTotal: 0,
            assignedHasMore: false,
            assignedNextBefore: null,
            assignedSearch: '',
            // Counter that ticks every time openAssignModal runs so
            // the modal can reset its local state even when the same
            // template is opened twice in a row.
            assignModalOpenedAt: 0,
            // Aggregated stats and per-account breakdown for the
            // template currently shown in the stats modal.
            stats: {
                template_id: null,
                totals: null,
                processing_count: 0,
                breakdown: [],
            },
            templates: {
                data: {},
                current_page: 1,
                total: 0,
                queryParams: {
                    tags: [],
                    category_id: '',
                    type: 'name-username',
                    color: 1,
                    custom_only: false,
                },
                receivedType: 'username',
            },
            types: [],
            colors: [],
            is: {
                loading: false,
                deleting: false,
                gettingTemplate: false,
                searchingAccounts: false,
                loadingAssigned: false,
                loadingMoreAssigned: false,
                loadingStats: false,
                saving: false,
            },

        }
    },

    actions: {
        deleteSelected(ids) {
            this.warnIfdosntSelected(ids) &&
            Swal.fire({
                title: "Are you sure you want to delete selected templates?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, delete it!"
            }).then((result) => {
                if (result.isConfirmed) {
                    ApiService.post('template/delete', {ids, receivedType: this.templates.receivedType})
                        .then(this.getTemplates)
                }
            });
        },

        warnIfdosntSelected(selected) {
            if (selected.length)
                return true;

            Swal.fire({
                icon: "error",
                text: "Please select one template to proceed",
            });

            return false;
        },

        getTemplates(page = 1) {
            this.is.loading = true;

            ApiService.post('templates', {page, ...this.templates.queryParams})
                .then(response => {
                    this.templates.data = response.data.data
                    this.templates.total = response.data.meta.total;
                    this.templates.current_page = response.data.current_page;
                    this.templates.receivedType = response.data.type
                })
                .finally(() => {
                    this.checkedTemplateRows = [];
                    this.is.loading = false
                })
        },

        getTemplate() {
            this.is.gettingTemplate = true;

            ApiService.post('template/view', {id: this.selectedTemplate.id})
                .then(response => {
                    this.selectedTemplate = {...response.data};
                })
                .finally(() => this.is.gettingTemplate = false)
        },

        checkRows(e) {
            this.checkedTemplateRows = e.target.checked ?
                this.templates.data.map(template => template.id) : []
        },

        fetchTypes() {
            return ApiService.post('template/fetch-types', {})
                .then(response => this.types = response.data)
        },
        fetchColors() {
            return ApiService.post('template/fetch-colors', {})
                .then(response => this.colors = response.data)
        },

        updateTemplate(tagIds: number[] = []) {
            const payload = {
                ...this.selectedTemplate,
                tags: tagIds,
            };

            ApiService.post('template/update', payload)
                .then(this.getTemplates)
                .then(() => hideModal("edit_media_modal"))
        },

        attachTag() {

            const data = {
                templateIds: this.checkedTemplateRows,
                tagIds: this.templates.queryParams.tags
            }

            return ApiService.post('template/attach-tag', data)
        },

        // Open the assign modal for a specific template and load both
        // its first page of pending assignments and its stats (for the
        // inline "X posted, Y in progress" counter that links to the
        // full stats modal). The opened-at counter is bumped so the
        // modal resets its local state even when the same template is
        // opened twice in a row.
        openAssignModal(template) {
            this.assignTarget = {
                id: template.id,
                type: template.type,
            };
            this.activeAccountResults = [];
            this.assignedAccounts = [];
            this.assignedTotal = 0;
            this.assignedHasMore = false;
            this.assignedNextBefore = null;
            this.assignedSearch = '';
            this.assignModalOpenedAt = Date.now();
            this.getAssignedAccounts();
            this.fetchStats(template.id);
        },

        // Load the first page of pending assignments. Replaces any
        // previously loaded list. The search argument, when given,
        // also updates the stored search term so subsequent loadMore
        // calls keep the same filter.
        getAssignedAccounts(search: string | null = null) {
            if (!this.assignTarget.id) return;

            if (search !== null) {
                this.assignedSearch = search;
            }

            this.is.loadingAssigned = true;

            const payload: any = {
                template_id: this.assignTarget.id,
                per_page: 100,
            };

            if (this.assignedSearch) {
                payload.search = this.assignedSearch;
            }

            return ApiService.post('template/assigned-accounts', payload)
                .then(response => {
                    const data = response.data;
                    this.assignedAccounts = data.data ?? [];
                    this.assignedHasMore = !!data.has_more;
                    this.assignedNextBefore = data.next_before ?? null;
                    this.assignedTotal = data.total ?? 0;
                    return data;
                })
                .finally(() => this.is.loadingAssigned = false);
        },

        // Append the next page to the existing list. Used by the
        // infinite-scroll trigger in the modal. Safe to call even
        // when there is nothing more to load.
        loadMoreAssignedAccounts() {
            if (!this.assignTarget.id) return;
            if (!this.assignedHasMore) return;
            if (this.is.loadingMoreAssigned) return;

            this.is.loadingMoreAssigned = true;

            const payload: any = {
                template_id: this.assignTarget.id,
                per_page: 100,
                before_id: this.assignedNextBefore,
            };

            if (this.assignedSearch) {
                payload.search = this.assignedSearch;
            }

            return ApiService.post('template/assigned-accounts', payload)
                .then(response => {
                    const data = response.data;
                    this.assignedAccounts = [
                        ...this.assignedAccounts,
                        ...(data.data ?? []),
                    ];
                    this.assignedHasMore = !!data.has_more;
                    this.assignedNextBefore = data.next_before ?? null;
                    return data;
                })
                .finally(() => this.is.loadingMoreAssigned = false);
        },

        // Search active accounts by username for the dropdown.
        // The backend returns at most 50 rows, ordered by username.
        searchActiveAccounts(query = '') {
            this.is.searchingAccounts = true;

            return ApiService.post('accounts/search-active', {query})
                .then(response => {
                    this.activeAccountResults = response.data;
                    return response.data;
                })
                .finally(() => this.is.searchingAccounts = false);
        },

        // Persist the modal changes in a single round trip:
        //   1. Optionally unassign — either a list of account_ids or all pending
        //   2. Optionally assign — either a list of account_ids or all_active
        // Both operations are independent on the backend, so we run them
        // sequentially and aggregate the result counts for the user.
        saveAssignments({
                            assignAccountIds = [],
                            allActive = false,
                            unassignAccountIds = [],
                            unassignAll = false,
                        }) {
            if (!this.assignTarget.id) return Promise.resolve();

            this.is.saving = true;

            const counts = {assigned: 0, skipped: 0, unassigned: 0};

            const unassignStep = () => {
                const hasUnassignWork = unassignAll || unassignAccountIds.length > 0;
                if (!hasUnassignWork) return Promise.resolve();

                const payload = {
                    template_id: this.assignTarget.id,
                    unassign_all: unassignAll,
                };

                if (!unassignAll) {
                    payload.account_ids = unassignAccountIds;
                }

                return ApiService.post('template/unassign-accounts', payload)
                    .then(response => {
                        counts.unassigned = response.data?.unassigned ?? 0;
                    });
            };

            const assignStep = () => {
                const hasAssignWork = allActive || assignAccountIds.length > 0;
                if (!hasAssignWork) return Promise.resolve();

                const payload = {
                    template_id: this.assignTarget.id,
                    all_active: allActive,
                };

                if (!allActive) {
                    payload.account_ids = assignAccountIds;
                }

                return ApiService.post('template/assign-accounts', payload)
                    .then(response => {
                        counts.assigned = response.data?.assigned ?? 0;
                        counts.skipped = response.data?.skipped ?? 0;
                    });
            };

            return unassignStep()
                .then(assignStep)
                .then(() => {
                    Swal.fire({
                        icon: 'success',
                        title: 'Saved',
                        text:
                            `Assigned: ${counts.assigned} | ` +
                            `Skipped: ${counts.skipped} | ` +
                            `Unassigned: ${counts.unassigned}`,
                    });

                    hideModal('assign_accounts_modal');
                    return counts;
                })
                .catch(err => {
                    Swal.fire({
                        icon: 'error',
                        text: err?.response?.data?.message ?? 'Failed to save assignments',
                    });
                    throw err;
                })
                .finally(() => this.is.saving = false);
        },
        // Load aggregated stats and per-account breakdown for a template.
        // The backend already filters to status='completed' so the
        // breakdown reflects only successfully posted records.
        fetchStats(templateId: number) {
            this.is.loadingStats = true;
            this.stats = {
                template_id: templateId,
                totals: null,
                processing_count: 0,
                breakdown: [],
            };

            return ApiService.post('template/stats', {id: templateId})
                .then(response => {
                    this.stats = response.data;
                    return response.data;
                })
                .finally(() => this.is.loadingStats = false);
        },
    }
})