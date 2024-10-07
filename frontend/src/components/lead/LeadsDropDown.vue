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
    <!--begin::Menu separator-->
    <div class="separator mb-3 opacity-75"></div>

    <div class="menu-item ">
      <div class="menu-content px-3 fill-flex d-flex align-items-center">
        <a
            class="btn btn-light-danger btn-sm px-4"
            @click="store.deleteSelected(store.checkedLeadRows)"> Delete Selected </a>
      </div>
    </div>
    <div class="menu-item">
      <div class="menu-content px-3 justify-content-between d-flex align-items-center">
        <!--end::Label-->
        <el-select
            style="width: 220px"
            v-model="store.leads.category_id" placeholder="Select Category">
          <el-option
              v-for="item in categoryStore.categories.data"
              :key="item.id"
              :label="item.title"
              :value="item.id"
          />

          <el-option
              label="Clear Category"
              :value="null"
          />
        </el-select>

        <a class="btn btn-sm btn-light-success ms-1" @click="store.setCategory()"> Set Category</a>
      </div>
    </div>

  </div>
  <!--end::Menu 2-->
</template>

<script lang="ts">
import {defineComponent, onMounted} from "vue";
import {useLeadStore} from "@/stores/Lead";
import {useCategoryStore} from "@/stores/Category";

export default defineComponent({
  name: "accounts-drop-down",
  components: {},
  setup() {
    const categoryStore = useCategoryStore()
    onMounted(categoryStore.getCategories)

    return {
      store: useLeadStore(),
      categoryStore
    }

  }
});
</script>

<style>
.fill-flex a {
  flex: 1 !important;
}
</style>
