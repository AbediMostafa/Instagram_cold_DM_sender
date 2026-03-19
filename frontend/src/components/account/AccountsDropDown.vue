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
      <div class="px-3 fill-flex d-flex align-items-center">
        <a
            class="btn btn-light-success btn-sm px-4"
            @click="store.startProfile(store.checkedAccountRows)">Start Profile</a>
      </div>
    </div>
    <div class="menu-item ">
      <div class="px-3 fill-flex d-flex align-items-center">
        <a
            class="btn btn-light-success btn-sm px-4"
            @click="showModal('account_update_phone')">Update Phone</a>
      </div>
    </div>
    <div class="menu-item ">
      <div class="px-3 fill-flex d-flex align-items-center">
        <a
            class="btn btn-light-danger btn-sm px-4"
            @click="store.deleteSelected(store.checkedAccountRows)"> Delete Selected </a>
      </div>
    </div>

    <!-- Upload-Post bulk actions -->
    <div class="separator my-3 opacity-75"></div>
    <div class="menu-item px-3">
      <div class="menu-content fs-6 text-gray-900 fw-bold px-3 pb-2">
        Upload-Post
      </div>
    </div>
    <div class="menu-item ">
      <div class="px-3 fill-flex d-flex align-items-center">
        <a
            class="btn btn-light-success btn-sm px-4 me-2"
            @click="store.connectUploadPost(store.checkedAccountRows)">Connect Upload-Post</a>
        <a
            class="btn btn-light-danger btn-sm px-4 me-2"
            @click="store.disconnectUploadPost(store.checkedAccountRows)">Disconnect Upload-Post</a>
        <a
            class="btn btn-light-warning btn-sm px-4"
            @click="store.resetUploadPostStatus(store.checkedAccountRows)">Reset Status</a>
      </div>
    </div>

    <div class="menu-item">
      <div class="menu-content fs-6 text-gray-900 fw-bold px-3 pt-4">
        Filter
      </div>
      <div class="menu-content px-3 ">
        <!-- Filter by Tags -->
        <el-select
            v-model="store.accounts.tags"
            multiple
            filterable
            remote
            clearable
            placeholder="Filter by Tags"
            :remote-method="tagStore.fetchTags"
            :loading="tagLoading"
        >
          <el-option
              v-for="tag in tagStore.searchedTags"
              :key="tag.id"
              :label="tag.title"
              :value="tag.id"
          />
        </el-select>

        <div class="fill-flex d-flex align-items-center mt-4">
          <a class="btn btn-sm btn-light-danger" @click="store.detachTag()">Detach Tag</a>
          <a class="btn btn-sm btn-light-success ms-2" @click="store.attachTag()">Attach Tag</a>
        </div>

      </div>
      <div class="menu-content px-3 ">
        <!-- Filter by Service -->
        <el-select
            v-model="store.accounts.services"
            multiple
            filterable
            remote
            clearable
            placeholder="Filter by Service"
            :remote-method="serviceStore.fetchService"
            :loading="serviceStore.is.searching"
        >
          <el-option
              v-for="service in serviceStore.services.data"
              :key="service.id"
              :label="service.title"
              :value="service.id"
          />
        </el-select>

        <div class="fill-flex d-flex align-items-center mt-4">
          <a class="btn btn-sm btn-light-danger" @click="store.detachService()">Detach Service</a>
          <a class="btn btn-sm btn-light-success ms-2" @click="store.attachService()">Attach Service</a>
        </div>

        <div class="mt-2 fill-flex d-flex align-items-center">
          <a
              class="btn btn-light-success btn-sm"
              @click="store.getAccounts()">Filter</a>
        </div>

      </div>

      <!-- Upload-Post status filter -->
      <div class="menu-content px-3 mt-3">
        <span class="text-muted fw-semibold fs-8 d-block mb-2">Upload-Post Status</span>
        <el-checkbox-group
            v-model="store.accounts.uploadPostFilter"
            size="small"
        >
          <el-checkbox-button
              v-for="state in store.uploadPostStates"
              :key="state.value"
              :value="state.value"
              :label="state.label"
              @click="actionClicked"
          >
            {{ state.label }}
          </el-checkbox-button>
        </el-checkbox-group>
      </div>
    </div>

  </div>
  <!--end::Menu 2-->
</template>

<script lang="ts">
import {defineComponent, ref} from "vue";
import {useAccountStore} from "@/stores/Account";
import {useTagStore} from "@/stores/Tag";
import {showModal} from "@/core/helpers/modal";
import {useProfileStore} from "@/stores/Profile";
import {useServiceStore} from "@/stores/Service";
import {useDebounceFn} from "@vueuse/core";

export default defineComponent({
  name: "accounts-drop-down",
  methods: {showModal},
  components: {},
  setup() {
    const tagStore = useTagStore();
    const serviceStore = useServiceStore();
    const tagLoading = ref(false)
    const store = useAccountStore();

    const actionClicked = useDebounceFn(() => store.getAccounts(store.accounts.current_page), 300);

    return {
      store,
      profileStore: useProfileStore(),
      tagStore,
      tagLoading,
      serviceStore,
      actionClicked,
    }

  }
});
</script>

<style>
.fill-flex a {
  flex: 1 !important;
}
</style>