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
        <div class="me-2 d-flex align-items-center">
          <el-input
              v-model="range.from"
              placeholder="From ID"
              size="small"
              style="width: 60px"
              class="me-1"
              clearable
          />
          <el-input
              v-model="range.to"
              placeholder="To ID"
              size="small"
              style="width: 60px"
              class="me-1"

              clearable
          />

          <el-button
              type="primary"
              size="small"
              @click="selectRange"
          >
            Select Range
          </el-button>

          <el-button
              size="small"
              type="danger"
              plain
              @click="clearSelection"
          >
            Clear
          </el-button>
        </div>

        <div class="me-2">
          <!--          <a class="btn btn-sm btn-light-success ms-2" @click="store.resetIsUsed()">Reset</a>-->

          <!--          <el-date-picker-->
          <!--              v-model="store.accounts.dateRange"-->
          <!--              type="daterange"-->
          <!--              range-separator="To"-->
          <!--              start-placeholder="Start date"-->
          <!--              end-placeholder="End date"-->
          <!--              @change="actionClicked"-->
          <!--              value-format="YYYY-MM-DD"-->
          <!--              style="max-width: 250px;"-->
          <!--          />-->
        </div>
        <div class="me-2">
          <el-input
              v-model="store.accounts.search"
              style="max-width: 600px"
              placeholder="Search on username"
              class="input-with-select"
              clearable
              @clear="actionClicked"
          >
            <template #prepend>
              <el-button :icon="Search" @click="store.getAccounts"/>
            </template>

            <template #append>
              <el-select
                  v-model="store.accounts.type"
                  placeholder="Select"
                  style="width: 115px"
              >
                <el-option label="Account" value="account"/>
                <el-option label="Phone" value="phone"/>
                <el-option label="Account Id" value="accountId"/>
                <el-option label="Profile" value="profile"/>
                <el-option label="Proxy" value="proxy"/>
              </el-select>
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
              {{ action.label }}
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
            <th class="w-20px">
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
            <th class="min-w-100px">QUICK ACTIONS</th>

            <th class="min-w-300px">SERVICE</th>


            <th class="min-w-200px cursor-pointer" @click="sortBy('created_at')">
              CREATED / SUSPENDED AT
              <i v-if="store.accounts.sortBy === 'created_at' && !store.accounts.sortDesc"
                 class="bi bi-caret-up-fill"></i>
              <i v-if="store.accounts.sortBy === 'created_at' && store.accounts.sortDesc"
                 class="bi bi-caret-down-fill"></i>
            </th>

            <th class="text-end">
              ACTIONS
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
                    <a
                        class="text-gray-900 fw-bold text-hover-primary fs-7">
                      <span
                          @click="copyToClipboard(account.id)"
                      >{{ account.id }}</span>
                      -
                      <span
                          @click="copyToClipboard(account.username)"
                      >{{ account.username }}</span>
                    </a>


                    <div>

                        <span
                            @click="copyToClipboard(account.phone)"
                            class="text-muted fw-semibold text-muted d-block fs-8">
                    {{ account.name }}
                  </span>
                      <span
                          @click="copyToClipboard(account.password)"
                          class="text-muted fw-semibold text-muted fs-8">{{ account.password }}</span>
                      <account-instagram-state :state="account.instagram_state"/>
                      <account-app-state :state="account.app_state"/>
                    </div>
                    <span
                        @click="store.fetchOtpAndCopy(account.secret_key)"
                        class="text-muted fw-semibold text-muted d-block fs-8">
                    {{ account.secret_key }}
                  </span>

                    <div class="mt-1">
                      <span
                          @click="copyToClipboard(account.proxy)"
                          v-if="account.proxy"
                          class="text-muted fw-semibold text-muted py-1 px-2
                        rounded border-dashed border-2 fs-8 border ">
                        {{ account.proxy?.ip }}
                      </span>

                      <span
                          v-if="account.profile"
                          @click="copyToClipboard(account.profile?.title)"
                          class="text-muted fw-semibold text-muted py-1 px-2
                      rounded border-dashed border-2 fs-8 border ms-1">
                        {{ account.profile?.title }}
                      </span>

                    </div>


                  </div>
                </div>
              </td>
              <td>
                <a
                    @click="store.startSingleProfile(account.id)"
                    class="btn btn-light-success btn-sm fs-8 px-3 py-2">
                  <span v-if="store.is.profileStarting && store.currentStartingAccount== account.id">
                  Please wait...
                  <span
                      class="spinner-border spinner-border-sm align-middle ms-2"
                  ></span>
                </span>
                  <span v-else>Start Profile</span>

                </a>
              </td>
              <td>
                <span
                    v-if="account.service"
                    class="text-muted fs-8 border border-dashed px-3 py-1 rounded border-2 border-info-subtle"
                >{{ account.service?.title }}</span
                >

                <div>
                  <span class="badge badge-light-primary mt-1 ms-1"
                        v-for="tag in account.tags"
                  >{{ tag.title }}</span>
                </div>

                <div>
                  <span
                      @click="copyToClipboard(account.email)"
                      class="text-muted fw-semibold text-muted fs-8">{{ account.email }}</span>
                  <div
                      @click="copyToClipboard(account.email_password)"
                      class="text-muted fw-semibold text-muted fs-8">{{ account.email_password }}
                  </div>
                </div>
              </td>

              <td>
                <span class="text-muted fw-semibold text-muted fs-8">{{ account.created_at_ago }} / </span>
                <span class="text-muted fw-semibold text-muted fs-8">{{ account.latest_warning_created_at_ago }}</span>
                <div>
                <span class="badge badge-light-warning mt-1 ms-1"
                      v-for="warning in account.warnings"
                >{{ warning.cause }}</span>
                </div>

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
  <account-update-phone-modal/>
</template>

<script lang="ts" setup>
import {onMounted, ref} from "vue";
import CreateAccountModal from "@/components/modals/account/CreateAccountModal.vue";
import {showModal} from "@/core/helpers/modal";
import {useAppConfigStore} from "@/stores/AppConfig";
import AccountInstagramState from "@/components/account/AccountInstagramState.vue";
import AccountAppState from "@/components/account/AccountAppState.vue";
import AccountsDropDown from "@/components/account/AccountsDropDown.vue";
import AccountDropDown from "@/components/account/AccountDropDown.vue";
import {useAccountStore} from "@/stores/Account";
import EditAccountModal from "@/components/modals/account/EditAccountModal.vue";
import AccountUpdatePhoneModal from "@/components/modals/account/AccountUpdatePhoneModal.vue";
import {useDebounceFn} from "@vueuse/core";
import {Search} from '@element-plus/icons-vue'
import {copyToClipboard} from "@/core/helpers/helper";

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

onMounted(store.getAccounts);


const range = ref({
  from: null,
  to: null,
})

const selectRange = () => {
  if (!range.value.from || !range.value.to) return

  const from = Number(range.value.from)
  const to = Number(range.value.to)

  const min = Math.min(from, to)
  const max = Math.max(from, to)

  const selectedIds = store.accounts.data
      .filter(acc => acc.id >= min && acc.id <= max)
      .map(acc => acc.id)

  store.checkedAccountRows = [
    ...new Set([...store.checkedAccountRows, ...selectedIds]),
  ]
}

const clearSelection = () => {
  store.checkedAccountRows = []
}

</script>
