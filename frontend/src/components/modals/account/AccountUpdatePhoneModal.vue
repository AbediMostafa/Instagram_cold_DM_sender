<template>
  <!--begin::Modal - New Target-->
  <div
      class="modal fade"
      id="account_update_phone"
      tabindex="-1"
      aria-hidden="true"
  >
    <!--begin::Modal dialog-->
    <div class="modal-dialog modal-dialog-centered mw-650px">
      <!--begin::Modal content-->
      <div class="modal-content rounded">
        <!--begin::Modal header-->
        <div class="modal-header pb-0 border-0 justify-content-end">
          <!--begin::Close-->
          <div
              class="btn btn-sm btn-icon btn-active-color-primary"
              data-bs-dismiss="modal"
          >
            <KTIcon icon-name="cross" icon-class="fs-1"/>
          </div>
          <!--end::Close-->
        </div>
        <!--begin::Modal header-->

        <!--begin::Modal body-->
        <div class="modal-body scroll-y px-10 px-lg-15 pt-0 pb-15">
          <!--begin::Heading-->
          <div class="mb-13 text-center">
            <h1 class="mb-3">Edit Account</h1>
          </div>
          <!--end::Heading-->

          <!--begin::Input group-->
          <div class="d-flex flex-column mb-8 fv-row">
            <!--begin::Label-->
            <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
              <span class="required">Username Like</span>
            </label>
            <!--end::Label-->
            <div class="justify-content-between d-flex align-items-center">

              <el-input
                  v-model="usernameLike"
                  placeholder="Username"
                  name="username"
              ></el-input>

              <button
                  :data-kt-indicator="is.findingAccounts ? 'on' : null"
                  class="btn btn-sm btn-light-success ms-2 "
                  type="submit"
                  @click="findAccounts"
                  style="min-width: 13rem"
              >
                <span v-if="!is.findingAccounts" class="indicator-label">
                  Find Accounts
                </span>
                <span v-if="is.findingAccounts" class="indicator-progress">
                  Please wait...
                  <span
                      class="spinner-border spinner-border-sm align-middle ms-2"
                  ></span>
                </span>
              </button>

            </div>
            <div class="justify-content-between d-flex align-items-center mt-2">

              <el-input
                  v-model="phone"
                  placeholder="Phone"
                  name="Phone"
              ></el-input>

              <button
                  :data-kt-indicator="is.updatingPhone ? 'on' : null"
                  class="btn btn-sm btn-light-primary ms-2 "
                  type="submit"
                  @click="updatePhone"
                  style="min-width: 13rem"
              >
                <span v-if="!is.updatingPhone" class="indicator-label">
                  Update Phone
                </span>
                <span v-if="is.updatingPhone" class="indicator-progress">
                  Please wait...
                  <span
                      class="spinner-border spinner-border-sm align-middle ms-2"
                  ></span>
                </span>
              </button>

            </div>

            <div
                class="scroll-y me-n5 pe-5 h-200px h-lg-auto"
                data-kt-scroll="true"
                data-kt-scroll-activate="{default: false, lg: true}"
                data-kt-scroll-max-height="auto"
                data-kt-scroll-dependencies="#kt_header, #kt_toolbar, #kt_footer, #kt_chat_contacts_header"
                data-kt-scroll-wrappers="#kt_content, #kt_chat_contacts_body"
                data-kt-scroll-offset="5px"
                style="max-height: 300px"

            >
              <div v-loading = "is.findingAccounts">
              <div
                  v-for="account in accounts" :key="account.id">
                  <div class="d-flex align-items-center my-2">
                    <div class="symbol symbol-35px symbol-circle">
                      <img src="/media/avatars/blank.png"/>
                    </div>
                    <div class="ms-5">
                      <a
                          class="fs-7 text-gray-900 text-hover-primary mb-2"
                      >{{ account.username }}</a>

                      <div class="d-flex">
                        <div class="badge badge-light text-muted me-2">
                          {{ account.phone }}
                        </div>
                      </div>
                    </div>
                  </div>
                <div class="separator separator-dashed"></div>
              </div>
              </div>
            </div>

          </div>
          <!--begin::Actions-->
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
.el-select {
  width: 100%;
}

.el-date-editor.el-input,
.el-date-editor.el-input__inner {
  width: 100%;
}
</style>

<script lang="ts">
import {getAssetPath} from "@/core/helpers/assets";
import {defineComponent, ref} from "vue";
import {hideModal} from "@/core/helpers/modal";
import ApiService from "@/core/services/ApiService";
import {useAccountStore} from "@/stores/Account";
import MessageDropDown from "@/components/messenger-parts/MessageDropDown.vue";


export default defineComponent({
  name: "account_update_phone",
  components: {MessageDropDown},
  setup(props) {
    const formRef = ref<null | HTMLFormElement>(null);
    const store = useAccountStore();
    const usernameLike = ref('');
    const phone = ref('');
    const accounts = ref([]);
    const is = ref({
      findingAccounts: false
    });

    const rules = ref({
      username: [{required: true, message: "Please input username", trigger: "blur"},],
      password: [{required: true, message: "Please input password", trigger: "blur"},],
    });

    const findAccounts = () => {
      is.value.findingAccounts = true
      ApiService.post('account/find-accounts', {query: usernameLike.value})
          .then(response => {
            accounts.value = response.data.accounts
          })
          .finally(() => is.value.findingAccounts = false)
    }

    const updatePhone = ()=>{

    }


    return {
      is,
      usernameLike,
      updatePhone,
      formRef,
      rules,
      getAssetPath,
      hideModal,
      findAccounts,
      accounts,
    };
  },
});
</script>

<style lang="scss">
.override-styles {
  z-index: 99999 !important;
  pointer-events: initial;
}
</style>
