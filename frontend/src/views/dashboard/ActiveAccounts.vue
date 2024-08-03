<template>
  <div
    class="card card-flush pt-3 mb-5 mb-lg-10"
    data-kt-subscriptions-form="pricing"
  >
    <div class="card-header">
      <div class="card-title">
        <h2 class="fw-bold">Running Accounts</h2>
      </div>

      <div class="card-toolbar">
        <a class="btn btn-light-primary" data-bs-toggle="modal">Refresh</a>
      </div>
    </div>

    <div class="card-body pt-0">
      <div id="kt_create_new_payment_method">
        <div v-for="runningAccount in runningAccounts" :key="runningAccount.id">
          <div class="py-1">
            <div class="py-3 d-flex flex-stack flex-wrap">
              <div
                class="d-flex align-items-center collapsible toggle collapsed"
                data-bs-toggle="collapse"
                :data-bs-target="`#account_number_${runningAccount.id}`"
                aria-expanded="false"
              >
                <div
                  class="btn btn-sm btn-icon btn-active-color-primary ms-n3 me-2"
                >
                  <KTIcon
                    icon-name="minus-square"
                    icon-class="toggle-on text-primary fs-2"
                  />
                  <KTIcon
                    icon-name="plus-square"
                    icon-class="toggle-off fs-2"
                  />
                </div>
                <div class="symbol symbol-50px symbol-circle me-4">
                  <img
                    :src="getAvatarPath(runningAccount)"
                    @error="(e) => (e.target.src = '/media/avatars/blank.png')"
                  />
                </div>

                <div class="me-3">
                  <div class="d-flex align-items-center fw-bold">
                    {{ runningAccount.username }}
                    <account-instagram-state  :state="runningAccount.instagram_state"/>
                    <account-app-state  :state="runningAccount.app_state" class="ms-1"/>
                  </div>
                  <div class="text-muted">{{ runningAccount.log }}</div>
                </div>
              </div>
            </div>

            <div
              :id="`account_number_${runningAccount.id}`"
              class="fs-6 ps-10 collapse"
              style=""
            >
              <active-account-menu className="h-xl-100 my-5"/>
            </div>
          </div>

          <div class="separator separator-dashed"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import ApiService from "@/core/services/ApiService";
import { onMounted, ref } from "vue";
import AccountInstagramState from "@/components/account/AccountInstagramState.vue";
import AccountAppState from "@/components/account/AccountAppState.vue";
import ActiveAccountMenu from "@/views/dashboard/ActiveAccountMenu.vue";


const runningAccounts = ref([]);
const is = ref({
  gettingRunningAccounts: false,
});

const getAvatarPath = (account) => {
  return (
    import.meta.env.VITE_APP_API_URL + "/storage/" + account.templates[0]?.text
  );
};

const getRunningAccounts = () => {
  is.value.gettingRunningAccounts = true;
  ApiService.post("dashboard/running-accounts")
    .then((response) => (runningAccounts.value = response.data))
    .finally(() => (is.value.gettingRunningAccounts = false));
};

onMounted(getRunningAccounts);
</script>
