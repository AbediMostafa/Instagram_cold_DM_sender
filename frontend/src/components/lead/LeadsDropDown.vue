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
        <a
            class="btn btn-light-danger btn-sm px-4"
            @click="store.deleteSelected(store.checkedLeadRows)"> Delete Selected </a>
      </div>
    </div>
  </div>
  <!--end::Menu 2-->
</template>

<script lang="ts">
import {defineComponent} from "vue";
import {useLeadStore} from "@/stores/Lead";

export default defineComponent({
  name: "accounts-drop-down",
  components: {},
  setup() {

    return {
      store: useLeadStore()
    }

  }
});
</script>

<style>
.fill-flex a {
  flex: 1 !important;
}
</style>
