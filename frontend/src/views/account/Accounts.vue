<template>
  <div class="card mb-5 mb-xl-8">
    <!--begin::Header-->
    <div class="card-header border-0 pt-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">Accounts</span>
        <span class="text-muted mt-1 fw-semibold fs-7">{{ store.accounts.total }} accounts</span>
      </h3>
      <div class="card-toolbar">
        <!--begin::Menu-->
        <div class="me-2">
          <el-date-picker
              v-model="store.accounts.dateRange"
              type="daterange"
              range-separator="To"
              start-placeholder="Start date"
              end-placeholder="End date"
              @change="actionClicked"
              value-format="YYYY-MM-DD"
              style="max-width: 300px;"
          />
        </div>
        <div class="me-2">
          <el-input
              v-model="store.accounts.search"
              style="max-width: 600px"
              placeholder="Search on username"
              class="input-with-select"
              clearable
          >
            <template #prepend>
              <el-button :icon="Search" @click="store.getAccounts"/>
            </template>
          </el-input>
        </div>
        <div class="me-2">
          <el-checkbox-group
              v-model="store.accounts.filters"
              size="default"
          >
            <el-checkbox-button
                v-for="action in store.accountStates"
                :key="action.value"
                :value="action.value"
                :label="action.label"
                @click="actionClicked"
            >
              {{ action.value }}
            </el-checkbox-button>
          </el-checkbox-group>
        </div>
        <button
            type="button"
            class="btn btn-sm btn-icon btn-color-primary btn-active-light-primary"
            data-kt-menu-trigger="click"
            data-kt-menu-placement="bottom-end"
            data-kt-menu-flip="top-end"
        >
          <KTIcon icon-name="category" icon-class="fs-2"/>
        </button>
        <accounts-drop-down/>
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

            <th class="min-w-120px cursor-pointer" @click="sortBy('total_cold_dms')">
              COLD DMS
              <i v-if="store.accounts.sortBy === 'total_cold_dms' && !store.accounts.sortDesc" class="bi bi-caret-up-fill"></i>
              <i v-if="store.accounts.sortBy === 'total_cold_dms' && store.accounts.sortDesc" class="bi bi-caret-down-fill"></i>
            </th>
            <th class="min-w-120px cursor-pointer" @click="sortBy('total_follow_ups')">
              FOLLOW UPS
              <i v-if="store.accounts.sortBy === 'total_follow_ups' && !store.accounts.sortDesc" class="bi bi-caret-up-fill"></i>
              <i v-if="store.accounts.sortBy === 'total_follow_ups' && store.accounts.sortDesc" class="bi bi-caret-down-fill"></i>
            </th>
            <th class="min-w-120px cursor-pointer" @click="sortBy('total_replies')">
              RESPONSES
              <i v-if="store.accounts.sortBy === 'total_replies' && !store.accounts.sortDesc" class="bi bi-caret-up-fill"></i>
              <i v-if="store.accounts.sortBy === 'total_replies' && store.accounts.sortDesc" class="bi bi-caret-down-fill"></i>
            </th>

            <th class="min-w-120px">IS ACTIVE</th>

            <th class="min-w-120px cursor-pointer" @click="sortBy('created_at')">
              CREATED AT / SUSPENDED AT
              <i v-if="store.accounts.sortBy === 'created_at' && !store.accounts.sortDesc" class="bi bi-caret-up-fill"></i>
              <i v-if="store.accounts.sortBy === 'created_at' && store.accounts.sortDesc" class="bi bi-caret-down-fill"></i>
            </th>

            <th class="min-w-100px text-end">

              Actions

            </th>
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
                    <img v-else src="/media/avatars/blank.png"/>
                    <div
                        v-if="account.priority == 0"
                        style="top: 12px"
                        class="symbol-badge bg-danger start-100 border-4 h-10px w-10px ms-n2 mt-n2"
                    ></div>
                  </div>

                  <div class="ms-4">
                    <a class="text-gray-900 fw-bold text-hover-primary fs-7">{{ account.id }} - {{
                        account.username
                      }}</a>


                    <div>
                      <span class="text-muted fw-semibold text-muted fs-8">{{ account.password }}</span>
                      <account-instagram-state :state="account.instagram_state"/>
                      <account-app-state :state="account.app_state"/>
                    </div>
                    <span class="text-muted fw-semibold text-muted d-block fs-8">
                    {{ account.secret_key }}
                  </span>


                  </div>
                </div>
              </td>
              <td>
                <span class="fw-semibold d-block fs-7">{{ account.total_cold_dms }}</span>
              </td>

              <td>
                <span class="fw-semibold d-block fs-7">{{ account.total_follow_ups }}</span>
              </td>

              <td>
                <span class="fw-semibold d-block fs-7">{{ account.total_replies }}</span>
              </td>

              <td><account-is-active :is-active="account.is_active"/></td>
              <td>
                <div>{{account.created_at_ago}}</div>
                <div>{{account.latest_warning_created_at_ago}}</div>
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
  <create-account-modal/>
  <edit-account-modal :id="selectedId"/>
</template>

<script lang="ts" setup>
import {onMounted, ref} from "vue";
import CreateAccountModal from "@/components/modals/account/CreateAccountModal.vue";
import {showModal} from "@/core/helpers/modal";
import {useAppConfigStore} from "@/stores/AppConfig";
import AccountInstagramState from "@/components/account/AccountInstagramState.vue";
import AccountAppState from "@/components/account/AccountAppState.vue";
import AccountIsActive from "@/components/account/AccountIsActive.vue";
import AccountPost from "@/components/account/AccountPost.vue";
import AccountsDropDown from "@/components/account/AccountsDropDown.vue";
import AccountDropDown from "@/components/account/AccountDropDown.vue";
import {useAccountStore} from "@/stores/Account";
import EditAccountModal from "@/components/modals/account/EditAccountModal.vue";
import {onBeforeRouteLeave} from "vue-router";
import {useDebounceFn} from "@vueuse/core";
import {Search} from '@element-plus/icons-vue'


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

const actionClicked = useDebounceFn(() => store.getAccounts(store.accounts.current_page), 300);

const sortBy = (field) => {
  store.sortBy(field);
};

const clearSort = () => {
  store.clearSort();
};


onMounted(store.getAccounts);
// const getAccountsWithInterval = setInterval(
//   () => store.getAccounts(store.accounts.current_page, false),
//   4000
// );
//
// onBeforeRouteLeave(() => clearInterval(getAccountsWithInterval));
</script>
