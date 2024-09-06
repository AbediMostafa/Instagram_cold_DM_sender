<template>
  <!--begin::Menu 2-->
  <div
      class="menu menu-sub menu-sub-dropdown menu-column menu-rounded menu-gray-600 menu-state-bg-light-primary fw-semibold w-350px"
      data-kt-menu="true"
  >
    <!--begin::Menu item-->
    <div class="menu-item px-3">
      <div class="menu-content fs-6 text-gray-900 fw-bold px-3 py-4">
        Quick Actions
      </div>
    </div>
    <!--end::Menu item-->

    <!--begin::Menu separator-->
    <div class="separator mb-3 opacity-75"></div>

    <!--begin::Menu item-->
    <div class="menu-item ">
      <div class="menu-content px-3 fill-flex d-flex align-items-center">

      </div>
    </div>
    <div class="menu-item ">
      <div class="menu-content px-3 fill-flex d-flex align-items-center">
        <a
            class="btn btn-sm btn-success me-2"
            @click="showModal('create_account_modal')"
        >Add Account</a>

        <a
            class="btn btn-sm btn-primary"
            @click="store.getAccounts(store.accounts.current_page)"
        >Refresh</a>
      </div>
    </div>
    <div class="menu-item ">
      <div class="menu-content px-3 fill-flex d-flex align-items-center">
        <a
            class="btn btn-light-danger btn-sm px-4"
            @click="store.deleteSelected(store.checkedAccountRows)"> Delete Selected </a>
      </div>
    </div>
    <div class="menu-item ">
      <div class="menu-content px-3 fill-flex d-flex align-items-center">
        <a
            class="btn btn-light-success btn-sm px-4 me-2"
            @click="store.changeProperty(store.checkedAccountRows, 'is_active', 1, `Selected Accounts activated successfully`,store.getAccounts)">
          Activate Selected
        </a>
        <a
            class="btn btn-light-danger btn-sm px-4"
            @click="store.changeProperty(store.checkedAccountRows, 'is_active', 0, `Selected Accounts deactivated successfully`,store.getAccounts)"
        > Deactivate Selected </a>
      </div>
    </div>
  </div>
  <!--end::Menu 2-->
</template>

<script lang="ts">
import {defineComponent, ref} from "vue";
import {useAccountStore} from "@/stores/Account";
import {showModal} from "@/core/helpers/modal";

export default defineComponent({
  name: "accounts-drop-down",
  methods: {showModal},
  components: {},
  setup() {

    return {
      store: useAccountStore()
    }

  }
});
</script>

<style>
.fill-flex a {
  flex: 1 !important;
}
</style>
