<template>
  <div class="modal fade" tabindex="-1" aria-hidden="true" id="edit_profile_modal">
    <div class="modal-dialog modal-dialog-centered mw-650px">
      <div class="modal-content rounded">
        <div class="modal-header pb-0 border-0 justify-content-end">
          <button type="button" class="btn btn-sm btn-icon btn-active-color-primary" @click="$emit('close')">
            <KTIcon icon-name="cross" icon-class="fs-1"/>
          </button>
        </div>
        <div class="modal-body scroll-y px-10 px-lg-15 pt-0 pb-15">
          <el-form @submit.prevent="submit" :model="profile" ref="formRef">
            <h1 class="mb-3">Edit Profile</h1>

            <el-form-item label="Title" prop="title">
              <el-input v-model="profile.title" placeholder="Enter Profile Title"></el-input>
            </el-form-item>

            <el-form-item label="Folder" prop="folder">
              <el-input v-model="profile.folder" placeholder="Enter Folder Name"></el-input>
            </el-form-item>

            <el-form-item label="Profile ID" prop="profile_id">
              <el-input v-model="profile.profile_id" placeholder="Enter Profile ID"></el-input>
            </el-form-item>

            <el-form-item label="Select Accounts">
              <el-select
                v-model="selectedAccounts"
                multiple
                filterable
                remote
                clearable
                placeholder="Select Accounts"
                :remote-method="fetchAccounts"
                :loading="accountLoading"
              >
                <el-option
                  v-for="account in accountStore.accountsData"
                  :key="account.id"
                  :label="account.username"
                  :value="account.id"
                >
                  {{ account.id }} - {{ account.username }}
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="Select Proxy">
              <el-select
                v-model="profile.proxy_id"
                filterable
                clearable
                placeholder="Select Proxy"
              >
                <el-option
                  v-for="proxy in proxies"
                  :key="proxy.id"
                  :label="proxy.ip"
                  :value="proxy.id"
                />
              </el-select>
            </el-form-item>

            <div class="text-center">
              <button
                :data-kt-indicator="isLoading ? 'on' : null"
                class="btn btn-primary"
                type="submit"
                :disabled="isLoading"
              >
                <span v-if="!isLoading" class="indicator-label">
                  Save
                  <i class="bi bi-arrow-right fs-3 ms-2 me-0"></i>
                </span>
                <span v-if="isLoading" class="indicator-progress">
                  Please wait...
                  <span class="spinner-border spinner-border-sm align-middle ms-2"></span>
                </span>
              </button>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from "vue";
import { useProfileStore } from "@/stores/Profile";
import { useAccountStore } from "@/stores/Account";
import { useProxyStore } from "@/stores/Proxy";

export default defineComponent({
  name: "EditProfileModal",
  props: ['profileProp'],
  setup(props, { emit }) {
    const profileStore = useProfileStore();
    const accountStore = useAccountStore();
    const proxyStore = useProxyStore();

    const profile = ref({ ...props.profile });
    const selectedAccounts = ref(profile.value.accounts || []);
    const proxies = ref([]);
    const accountLoading = ref(false);
    const isLoading = ref(false);

    const fetchAccounts = async (query) => {
      accountLoading.value = true;
      await accountStore.fetchAccounts(query); // Fetch accounts based on the query
      accountLoading.value = false;
    };

    const submit = async () => {
      isLoading.value = true;
      await profileStore.editProfile({ ...profile.value, accounts: selectedAccounts.value });
      emit('close');
      isLoading.value = false;
    };

    watch(() => props.profile, (newProfile) => {
      profile.value = { ...newProfile };
      selectedAccounts.value = profile.value.accounts || [];
    });

    // Fetch proxies when the modal is opened
    const fetchProxies = async () => {
      const response = await proxyStore.fetchProxies();
      proxies.value = response.data;
    };

    // fetchProxies();

    return {
      profile,
      selectedAccounts,
      proxies,
      accountLoading,
      isLoading,
      fetchAccounts,
      submit,
      accountStore
    };
  }
});
</script>

<style lang="scss">
.el-select {
  width: 100%;
}
</style>