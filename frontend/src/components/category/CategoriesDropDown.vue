<template>
  <!--begin::Menu-->
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
    <div class="menu-item">
      <div class="menu-content px-3 fill-flex d-flex align-items-center">
        <a class="btn btn-sm btn-success me-2" @click="showModal('create_category_modal')">Add Category</a>
        <a class="btn btn-sm btn-primary" @click="store.getCategories(store.categories.current_page)">Refresh</a>
      </div>
    </div>

    <div class="menu-item">
      <div class="menu-content px-3 fill-flex d-flex align-items-center">
        <a class="btn btn-light-danger btn-sm px-4" @click="store.deleteSelected(store.checkedCategoryRows)">
          Delete Selected
        </a>
      </div>
    </div>
  </div>
  <!--end::Menu-->
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { useCategoryStore } from "@/stores/Category";
import { showModal } from "@/core/helpers/modal";

export default defineComponent({
  name: "CategoriesDropDown",
  setup() {
    return {
      store: useCategoryStore(),
      showModal,
    };
  },
});
</script>

<style>
.fill-flex a {
  flex: 1 !important;
}
</style>
