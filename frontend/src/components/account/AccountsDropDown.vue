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
    <div class="menu-item ">
      <div class="menu-content px-3 justify-content-between d-flex align-items-center">
        <el-select
            v-if="categoryStore.categories.data.length"
            style="width: 220px"
            v-model="store.accounts.category_id" placeholder="Select Category">
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
import {defineComponent, onMounted, ref} from "vue";
import {useAccountStore} from "@/stores/Account";
import {useCategoryStore} from "@/stores/Category";
import {showModal} from "@/core/helpers/modal";
import ApiService from "@/core/services/ApiService";

export default defineComponent({
  name: "accounts-drop-down",
  methods: {showModal},
  components: {},
  setup() {
    const categoryStore = useCategoryStore()

    onMounted(categoryStore.getCategories)

    return {
      store: useAccountStore(),
      categoryStore,
    }

  }
});
</script>

<style>
.fill-flex a {
  flex: 1 !important;
}
</style>
