<template>
  <div class="card mb-5 mb-xl-8">
    <!--begin::Header-->
    <div class="card-header border-0 pt-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">Accounts</span>

        <span class="text-muted mt-1 fw-semibold fs-7"
          >{{ store.accounts.total }} accounts</span
        >
      </h3>
      <div class="card-toolbar">
        <!--begin::Menu-->
        <a
          class="btn btn-sm btn-success me-2"
          @click="showModal('create_account_modal')"
          >Add Account</a
        >
        <button
          type="button"
          class="btn btn-sm btn-icon btn-color-primary btn-active-light-primary"
          data-kt-menu-trigger="click"
          data-kt-menu-placement="bottom-end"
          data-kt-menu-flip="top-end"
        >
          <KTIcon icon-name="category" icon-class="fs-2" />
        </button>
        <accounts-drop-down />
      </div>
    </div>
    <!--end::Header-->

    <!--begin::Body-->
    <div class="card-body py-3">
      <!--begin::Table container-->
      <div class="table-responsive">
        <table
          class="table table-row-bordered table-row-gray-100 align-middle gs-0 gy-3"
          v-loading="store.is.loading"
        >
          <!--begin::Table head-->
          <thead>
            <tr class="fw-bold text-muted">
              <th class="w-25px">
                <div
                  class="form-check form-check-sm form-check-custom form-check-solid"
                >
                  <input
                    class="form-check-input"
                    type="checkbox"
                    @change="store.checkRows($event)"
                  />
                </div>
              </th>
              <th class="min-w-150px">USERNAME</th>
              <th class="min-w-120px">EMAIL</th>
              <th class="min-w-120px w-500px">STATE</th>
              <th class="min-w-120px">IS ACTIVE</th>
              <th class="min-w-100px text-end">Actions</th>
            </tr>
          </thead>
          <!--end::Table head-->

          <!--begin::Table body-->
          <tbody>
            <template
              v-for="(account, index) in store.accounts.data"
              :key="index"
            >
              <tr>
                <td>
                  <div
                    class="form-check form-check-sm form-check-custom form-check-solid"
                  >
                    <input
                      class="form-check-input widget-13-check"
                      type="checkbox"
                      :value="account.id"
                      v-model="store.checkedAccountRows"
                    />
                  </div>
                </td>

                <td>
                  <div class="d-flex align-items-center">
                    <div class="symbol symbol-50px symbol-circle">
                      <img
                        v-if="account.avatar_changed"
                        :src="getAvatarPath(account)"
                        @error="
                          (e) => (e.target.src = '/media/avatars/blank.png')
                        "
                      />
                      <img v-else src="/media/avatars/blank.png" />
                      <div
                        v-if="account.priority == 0"
                        style="top: 12px"
                        class="symbol-badge bg-danger start-100 border-4 h-10px w-10px ms-n2 mt-n2"
                      ></div>
                    </div>

                    <div class="ms-4">
                      <router-link
                        :to="{ name: 'messages', params: { id: account.id } }"
                      >
                        <a
                          class="text-gray-900 fw-bold text-hover-primary fs-7"
                          >{{account.id}} - {{ account.username }}</a
                        >
                        <account-instagram-state
                          :state="account.instagram_state"
                        />
                        <span
                          class="text-muted fw-semibold text-muted d-block fs-7"
                          >{{ account.password }}</span
                        >
                      </router-link>
                    </div>
                  </div>
                </td>
                <td>
                    <span
                        class="fw-semibold d-block fs-7"
                    >{{ account.email }}</span>
                </td>

                <td>
                  <account-app-state :state="account.app_state" />
                  <span
                    class="text-muted fw-semibold text-muted d-block fs-8 mt-2"
                    >{{ account.log }}</span
                  >
                </td>

                <td>
                  <account-is-active :is-active="account.is_active" />
                </td>

                <td class="text-end">
                  <account-drop-down
                    @editClicked="editClicked(account.id)"
                    :account="account"
                  />
                </td>
              </tr>
            </template>
          </tbody>
          <!--end::Table body-->
        </table>
        <!--end::Table-->

        <el-pagination
          :current-page="store.accounts.current_page"
          :page-size="configStore.pagination?.each_page?.accounts"
          layout="prev, pager, next"
          :total="store.accounts.total"
          @current-change="(page) => store.getAccounts(page)"
        />
      </div>
      <!--end::Table container-->
    </div>
    <!--begin::Body-->
  </div>
  <create-account-modal />
  <edit-account-modal :id="selectedId" />
</template>

<script lang="ts" setup>
import { onMounted, ref } from "vue";
import CreateAccountModal from "@/components/modals/account/CreateAccountModal.vue";
import { getAssetPath } from "@/core/helpers/assets";
import { showModal } from "@/core/helpers/modal";
import { useAppConfigStore } from "@/stores/AppConfig";
import AccountInstagramState from "@/components/account/AccountInstagramState.vue";
import AccountAppState from "@/components/account/AccountAppState.vue";
import AccountIsActive from "@/components/account/AccountIsActive.vue";
import AccountPost from "@/components/account/AccountPost.vue";
import AccountsDropDown from "@/components/account/AccountsDropDown.vue";
import AccountDropDown from "@/components/account/AccountDropDown.vue";
import { useAccountStore } from "@/stores/Account";
import EditAccountModal from "@/components/modals/account/EditAccountModal.vue";
import { onBeforeRouteLeave } from "vue-router";

const selectedId = ref(0);
const store = useAccountStore();
const configStore = useAppConfigStore();
const editClicked = (id) => {
  selectedId.value = id;
  showModal("edit_account_modal");
};

const getAvatarPath = (account) => {
  return (
    import.meta.env.VITE_APP_API_URL + "/storage/" + account.templates[0]?.text
  );
};

onMounted(store.getAccounts);
const getAccountsWithInterval = setInterval(
  () => store.getAccounts(store.accounts.current_page, false),
  4000
);

onBeforeRouteLeave(() => clearInterval(getAccountsWithInterval));
</script>
