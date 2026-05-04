<template>
  <div
      class="modal fade"
      id="assign_accounts_modal"
      tabindex="-1"
      aria-hidden="true"
  >
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">

        <div class="modal-header">
          <h2 class="fw-bold">Assign template to accounts</h2>
          <div
              class="btn btn-icon btn-sm btn-active-icon-primary"
              data-bs-dismiss="modal"
              aria-label="Close"
          >
            <KTIcon icon-name="cross" icon-class="fs-1"/>
          </div>
        </div>

        <div class="modal-body py-8 px-lg-12">

          <!-- Add accounts section -->
          <div class="mb-8">
            <h4 class="fw-semibold mb-4">Add accounts</h4>

            <div class="d-flex align-items-center gap-3 mb-4 p-4 bg-light rounded">
              <label class="form-check form-switch form-check-custom form-check-solid m-0">
                <input
                    class="form-check-input"
                    type="checkbox"
                    v-model="allActive"
                />
              </label>
              <div>
                <div class="fw-semibold text-gray-800">All active accounts</div>
                <div class="text-muted fs-7">
                  Assign this template to every account with state = active
                </div>
              </div>
            </div>

            <div v-if="!allActive">
              <label class="form-label fw-semibold">Search accounts</label>

              <el-select
                  v-model="selectedAccountIds"
                  multiple
                  filterable
                  remote
                  reserve-keyword
                  placeholder="Type a username to search ..."
                  :remote-method="onSearch"
                  :loading="store.is.searchingAccounts"
                  style="width: 100%"
              >
                <el-option
                    v-for="account in store.activeAccountResults"
                    :key="account.id"
                    :label="account.username"
                    :value="account.id"
                />
              </el-select>

              <div class="text-muted fs-7 mt-2">
                Showing up to 50 results. Refine your search to narrow down.
              </div>

              <div v-if="selectedAccountIds.length" class="mt-3">
                <span class="badge badge-light-primary">
                  {{ selectedAccountIds.length }} selected to add
                </span>
              </div>
            </div>
          </div>

          <!-- Currently assigned section -->
          <div class="border-top pt-6">
            <div class="d-flex align-items-center justify-content-between mb-4">
              <h4 class="fw-semibold m-0">
                Currently assigned (pending)
                <span class="badge badge-light-info ms-2">
                  {{ headerCount }}
                </span>
              </h4>

              <a
                  v-if="store.assignedTotal > 0 && !unassignAllFlag"
                  class="btn btn-sm btn-light-danger"
                  @click="onClickUnassignAll"
              >
                Unassign all
              </a>
            </div>

            <!-- Search box. Backend-side filter, debounced.
                 Updates the visible page; "Unassign all" still acts
                 on the full pending set, ignoring the search filter. -->
            <div class="mb-3">
              <input
                  type="text"
                  class="form-control form-control-sm"
                  placeholder="Search assigned accounts ..."
                  :value="searchInput"
                  @input="onSearchInput"
              />
            </div>

            <div v-if="store.is.loadingAssigned" class="text-muted fs-7">
              Loading ...
            </div>

            <div
                v-else-if="!store.assignedAccounts.length && !unassignAllFlag"
                class="text-muted fs-7"
            >
              <span v-if="store.assignedSearch">No matches.</span>
              <span v-else>No pending assignments.</span>
            </div>

            <div
                v-else-if="unassignAllFlag"
                class="p-4 bg-light-danger rounded text-center"
            >
              <div class="fw-semibold text-danger mb-2">
                All {{ store.assignedTotal }} pending assignments will be unassigned
              </div>
              <a class="btn btn-sm btn-light" @click="cancelUnassignAll">
                Cancel
              </a>
            </div>

            <div v-else>
              <div
                  ref="listRef"
                  class="assigned-list"
                  @scroll="onListScroll"
              >
                <div
                    v-for="row in store.assignedAccounts"
                    :key="row.id"
                    class="d-flex align-items-center justify-content-between p-2 px-3 mb-2 rounded"
                    :class="isMarkedForRemoval(row.account_id) ? 'bg-light-danger' : 'bg-light'"
                >
                  <div class="d-flex align-items-center gap-3">
                    <span class="fw-semibold text-gray-800">
                      {{ row.account?.username ?? `#${row.account_id}` }}
                    </span>
                    <span
                        v-if="isMarkedForRemoval(row.account_id)"
                        class="badge badge-light-danger"
                    >
                      Will be unassigned
                    </span>
                  </div>

                  <a
                      v-if="!isMarkedForRemoval(row.account_id)"
                      class="btn btn-icon btn-sm btn-light-danger"
                      @click="markForRemoval(row.account_id)"
                  >
                    <KTIcon icon-name="cross" icon-class="fs-4"/>
                  </a>

                  <a
                      v-else
                      class="btn btn-sm btn-light"
                      @click="undoRemoval(row.account_id)"
                  >
                    Undo
                  </a>
                </div>

                <div
                    v-if="store.is.loadingMoreAssigned"
                    class="text-center text-muted fs-7 py-2"
                >
                  Loading more ...
                </div>
              </div>
            </div>

            <!-- Inline counter for posts that have moved past the
                 pending stage. Processing rows are short-lived (worker
                 in flight); completed rows are final. The View stats
                 shortcut closes this modal and opens the stats modal
                 to show the full per-account breakdown. -->
            <div
                v-if="postedCount > 0 || processingCount > 0"
                class="d-flex align-items-center justify-content-between mt-4 p-3 bg-light-info rounded"
            >
              <div class="text-gray-700 fs-7">
                <KTIcon icon-name="information-2" icon-class="fs-4 me-2"/>
                <strong>{{ postedCount }}</strong> posted,
                <strong>{{ processingCount }}</strong> in progress
              </div>

              <a
                  class="btn btn-sm btn-light-info"
                  @click="openStats"
              >
                View stats
              </a>
            </div>

          </div>

        </div>

        <div class="modal-footer flex-center">
          <button
              type="button"
              class="btn btn-light me-3"
              data-bs-dismiss="modal"
          >
            Cancel
          </button>
          <button
              type="button"
              class="btn btn-primary"
              :disabled="!canSubmit || store.is.saving"
              @click="submit"
          >
            <span v-if="!store.is.saving">Save</span>
            <span v-else>
              Saving ...
              <span class="spinner-border spinner-border-sm align-middle ms-2"/>
            </span>
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {computed, ref, watch} from "vue";
import {useTemplateStore} from "@/stores/Template";
import {hideModal, showModal} from "@/core/helpers/modal";
import Swal from "sweetalert2/dist/sweetalert2.js";

const store = useTemplateStore();

const allActive = ref(false);
const selectedAccountIds = ref<number[]>([]);
// Account IDs the user has clicked the X on. They will be removed
// only when the user clicks Save; this lets them undo before submit.
const removalSet = ref<Set<number>>(new Set());
// Flag for "Unassign all". When true, every currently-pending row
// will be deleted on Save regardless of removalSet contents.
const unassignAllFlag = ref(false);

// Local mirror of the search input so we can debounce updates to
// the store without typing every keystroke into a request.
const searchInput = ref('');
let searchDebounce: ReturnType<typeof setTimeout> | null = null;

// Ref to the scroll container so we can detect when the user has
// scrolled near the bottom and trigger the next page.
const listRef = ref<HTMLElement | null>(null);

// Counters for the inline info strip below the pending list.
// Both come from the stats endpoint that openAssignModal also fetches.
const postedCount = computed(() =>
    Number(store.stats.totals?.total_posts ?? 0)
);
const processingCount = computed(() =>
    Number(store.stats.processing_count ?? 0)
);

// Header count tracks the full pending set, not the visible page.
// When the user has marked rows for removal, subtract them so the
// number reflects what will exist after Save.
const headerCount = computed(() => {
  if (unassignAllFlag.value) return 0;
  return Math.max(0, store.assignedTotal - removalSet.value.size);
});

// Reset modal state every time the modal is opened, even when the
// same template is opened twice in a row (which would not change
// assignTarget.id and so a watcher on it would not fire).
watch(
    () => store.assignModalOpenedAt,
    () => {
      allActive.value = false;
      selectedAccountIds.value = [];
      removalSet.value = new Set();
      unassignAllFlag.value = false;
      searchInput.value = '';
    }
);

// Keep the two add modes mutually exclusive in the payload.
watch(allActive, (val) => {
  if (val) {
    selectedAccountIds.value = [];
  }
});

const isMarkedForRemoval = (accountId: number) =>
    unassignAllFlag.value || removalSet.value.has(accountId);

const markForRemoval = (accountId: number) => {
  const next = new Set(removalSet.value);
  next.add(accountId);
  removalSet.value = next;
};

const undoRemoval = (accountId: number) => {
  const next = new Set(removalSet.value);
  next.delete(accountId);
  removalSet.value = next;
};

const onClickUnassignAll = async () => {
  // Confirm when a search filter is active because the action
  // ignores the filter and removes every pending row.
  if (store.assignedSearch) {
    const result = await Swal.fire({
      title: 'Unassign all pending?',
      html:
          `This removes <strong>all ${store.assignedTotal}</strong> pending ` +
          `assignments for this template, not only the rows matching ` +
          `your search "<em>${store.assignedSearch}</em>".`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Yes, unassign all',
      cancelButtonText: 'Cancel',
      confirmButtonColor: '#d33',
    });

    if (!result.isConfirmed) return;
  }

  unassignAllFlag.value = true;
  removalSet.value = new Set();
};

const cancelUnassignAll = () => {
  unassignAllFlag.value = false;
};

// Debounce search input; cancel the pending request and start a
// fresh one once the user pauses typing.
const onSearchInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  searchInput.value = target.value;

  if (searchDebounce) {
    clearTimeout(searchDebounce);
  }

  searchDebounce = setTimeout(() => {
    store.getAssignedAccounts(searchInput.value.trim());
  }, 300);
};

// Trigger the next page once the user scrolls near the bottom.
// 80px headroom keeps the load smooth instead of stuttering at the
// last visible item.
const onListScroll = (event: Event) => {
  const el = event.target as HTMLElement;
  const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;

  if (distanceFromBottom < 80) {
    store.loadMoreAssignedAccounts();
  }
};

// Save is enabled when there is something to apply: either accounts
// to add (manual or all_active) or rows marked for removal.
const canSubmit = computed(() => {
  const hasAssignWork =
      allActive.value || selectedAccountIds.value.length > 0;
  const hasUnassignWork =
      unassignAllFlag.value || removalSet.value.size > 0;
  return hasAssignWork || hasUnassignWork;
});

const onSearch = (query: string) => {
  store.searchActiveAccounts(query);
};

const submit = () => {
  store.saveAssignments({
    assignAccountIds: selectedAccountIds.value,
    allActive: allActive.value,
    unassignAccountIds: Array.from(removalSet.value),
    unassignAll: unassignAllFlag.value,
  }).then(() => {
    // Refresh the templates list so any indicator that depends on
    // assignment state stays in sync.
    store.getTemplates(store.templates.current_page);
  });
};

// Switch from the assign modal to the stats modal. Stats data is
// already loaded by openAssignModal so the target modal renders
// immediately without an extra fetch.
const openStats = () => {
  hideModal('assign_accounts_modal');
  showModal('template_stats_modal');
};
</script>

<style scoped>
.assigned-list {
  max-height: 320px;
  overflow-y: auto;
}
</style>