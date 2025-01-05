<template>
  <div class="modal fade" id="create_profile_modal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered mw-650px">
      <div class="modal-content rounded">
        <div class="modal-header pb-0 border-0 justify-content-end">
          <button class="btn btn-sm btn-icon btn-active-color-primary" @click="hideModal('create_profile_modal')">
            <i class="bi bi-x fs-1"></i>
          </button>
        </div>

        <div class="modal-body scroll-y px-10 px-lg-15 pt-0 pb-15">
          <form @submit.prevent="profileStore.createProfile">
            <h3 class="text-center mb-10">Create New Profile</h3>

            <!-- Title Field -->
            <div class="mb-6">
              <label class="form-label required">Title</label>
              <input type="text" v-model="profileStore.profile.title" class="form-control" required/>
            </div>

            <!-- Profile ID Field -->
            <div class="mb-6">
              <label class="form-label required">Profile Id</label>
              <input type="text" v-model="profileStore.profile.profile_id" class="form-control" required/>
            </div>

            <!-- Folder Field -->
            <div class="mb-6">
              <label class="form-label required">Folder</label>
              <input type="text" v-model="profileStore.profile.folder" class="form-control" required/>
            </div>

            <!-- Select Accounts with Search and Tags -->
            <div class="mb-6">
              <label class="form-label">Select Accounts</label>
              <el-select
                  v-model="profileStore.profile.accounts"
                  multiple
                  filterable
                  remote
                  clearable
                  placeholder="Select Accounts"
                  :remote-method="fetchAccounts"
                  :loading="accountLoading"
                  on-change="fetchAccounts"
              >
                <el-option
                    v-for="account in accountStore.accountsData"
                    :key="account.id"
                    :label="account.username"
                    :value="account.id"
                >
                  {{account.id}} - {{account.username}}
                </el-option>
              </el-select>
            </div>

            <!-- Select Proxy from Dropdown -->
            <div class="mb-6">
              <label class="form-label">Select Proxy</label>
              <el-select
                  v-model="profileStore.profile.proxy_id"
                  filterable
                  clearable
                  placeholder="Select Proxy"
              >
                <el-option
                    v-for="proxy in proxyStore.proxiesData"
                    :key="proxy.id"
                    :label="proxy.ip"
                    :value="proxy.id"
                />
              </el-select>
            </div>

            <div class="text-center">
              <!-- Submit Button with Loading Indicator -->
              <button
                  :data-kt-indicator="profileStore.is.creating ? 'on' : null"
                  class="btn btn-primary"
                  type="submit"
                  :disabled="profileStore.is.creating"
              >
                <span v-if="!profileStore.is.creating" class="indicator-label">
                  Submit
                  <i class="bi bi-arrow-right fs-3 ms-2 me-0"></i>
                </span>
                <span v-if="profileStore.is.creating" class="indicator-progress">
                  Please wait...
                  <span class="spinner-border spinner-border-sm align-middle ms-2"></span>
                </span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted} from "vue";
import {useProfileStore} from "@/stores/Profile";
import {useAccountStore} from "@/stores/Account";
import {useProxyStore} from "@/stores/Proxy";
import {hideModal} from "@/core/helpers/modal";

const profileStore = useProfileStore();
const accountStore = useAccountStore();
const proxyStore = useProxyStore();

const accountLoading = ref(false);

const fetchAccounts = async (query) => {
  accountLoading.value = true;
  await accountStore.fetchAccounts(query); // Assume `searchAccounts` is a method in the Account store to fetch accounts by query
  accountLoading.value = false;
};

onMounted(() => {
  proxyStore.fetchProxies();
})
</script>

<style lang="scss">
.el-select {
  width: 100%;
}
</style>
