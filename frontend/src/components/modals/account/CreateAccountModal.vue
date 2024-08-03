<template>
  <!--begin::Modal - New Target-->
  <div
      class="modal fade"
      id="create_account_modal"
      ref="newAccountModalRef"
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
          <!--begin:Form-->
          <el-form
              id="create_account_modal_form"
              @submit.prevent="submit()"
              :model="targetData"
              :rules="rules"
              ref="formRef"
              class="form"
          >
            <!--begin::Heading-->
            <div class="mb-13 text-center">
              <h1 class="mb-3">Create New Account</h1>
            </div>

            <div class="fv-row my-10">
              <!--begin::Wrapper-->
              <div class="d-flex flex-stack">
                <!--begin::Label-->
                <div class="me-5">
                  <!--begin::Label-->
                  <label class="fs-6 fw-semibold">Bulk insertion?</label>
                  <!--end::Label-->

                  <!--begin::Input-->
                  <div class="fs-7 fw-semibold text-muted">
                    You can copy and paste your Accounts and import many of them
                    in the following format: Username,Password,2FA code.
                  </div>
                  <!--end::Input-->
                </div>
                <!--end::Label-->

                <!--begin::Switch-->
                <label
                    class="form-check form-switch form-check-custom form-check-solid"
                >
                  <!--begin::Input-->
                  <input
                      class="form-check-input"
                      name="billing"
                      type="checkbox"
                      value="1"
                      id="account_bulk_insertion"
                      v-model="targetData.bulk_insertion"
                      @change="bulkInsertionChanged"
                  />
                  <!--end::Input-->

                  <!--begin::Label-->
                  <span
                      class="form-check-label fw-semibold text-muted"
                      for="account_bulk_insertion"
                  >
                    Yes
                  </span>
                  <!--end::Label-->
                </label>
                <!--end::Switch-->
              </div>
              <!--begin::Wrapper-->
            </div>

            <!--end::Heading-->
            <div
                v-if="targetData.bulk_insertion"
                class="d-flex flex-column mb-6 fv-row"
            >
              <!--begin::Label-->
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Bulk Account Insertion</span>
              </label>
              <!--end::Label-->
              <el-form-item prop="ip">
                <el-input
                    v-model="targetData.accounts"
                    :rows="8"
                    type="textarea"
                    placeholder="Enter Accounts Here"
                    name="bunchInsert"
                />
              </el-form-item>
            </div>


            <!--begin::Input group-->
            <div v-else>
              <div class="d-flex flex-column mb-8 fv-row">
                <!--begin::Label-->
                <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                  <span class="required">Username</span>
                </label>
                <!--end::Label-->

                <el-form-item prop="username">
                  <el-input
                      v-model="targetData.username"
                      placeholder="Enter Account Username"
                      name="username"
                  ></el-input>
                </el-form-item>
              </div>
              <div class="d-flex flex-column mb-8 fv-row">
                <!--begin::Label-->
                <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                  <span class="required">Password</span>
                </label>
                <!--end::Label-->

                <el-form-item prop="password">
                  <el-input
                      v-model="targetData.password"
                      placeholder="Enter Account Password"
                      name="password"
                  ></el-input>
                </el-form-item>
              </div>
              <div class="d-flex flex-column mb-8 fv-row">
                <!--begin::Label-->
                <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                  <span class="required">Secret Key</span>
                </label>
                <!--end::Label-->

                <el-form-item prop="password">
                  <el-input
                      v-model="targetData.secret_key"
                      placeholder="Enter Account Password"
                      name="password"
                  ></el-input>
                </el-form-item>
              </div>
            </div>

            <!--begin::Actions-->
            <div class="text-center">
              <button
                  type="reset"
                  id="create_account_modal_cancel"
                  class="btn btn-light me-3"
                  @click="hideModal('create_account_modal')"
              >
                Cancel
              </button>

              <!--begin::Button-->
              <button
                  :data-kt-indicator="loading ? 'on' : null"
                  class="btn btn-lg btn-primary"
                  type="submit"
              >
                <span v-if="!loading" class="indicator-label">
                  Submit
                  <KTIcon icon-name="arrow-right" icon-class="fs-3 ms-2 me-0"/>
                </span>
                <span v-if="loading" class="indicator-progress">
                  Please wait...
                  <span
                      class="spinner-border spinner-border-sm align-middle ms-2"
                  ></span>
                </span>
              </button>
            </div>
          </el-form>
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
import {defineComponent, ref} from "vue";
import {hideModal} from "@/core/helpers/modal";
import ApiService from "@/core/services/ApiService";
import {useAccountStore} from "@/stores/Account";

export default defineComponent({
  name: "create_account_modal",
  setup() {
    const formRef = ref<null | HTMLFormElement>(null);
    const newAccountModalRef = ref<null | HTMLElement>(null);
    const loading = ref<boolean>(false);
    const store = useAccountStore();

    const targetData = ref({
      username: "",
      password: "",
      secret_key: "",
      accounts: "",
      bulk_insertion: false,
    });

    const rules = ref({
      username: [
        {required: true, message: "Please input username", trigger: "blur"},
      ],
      password: [
        {required: true, message: "Please input password", trigger: "blur"},
      ],
    });

    const submit = () => {
      if (!formRef.value) {
        return;
      }

      formRef.value.validate((valid: boolean) => {
        if (valid) {
          loading.value = true;

          ApiService.post("account/create", targetData.value)
              .then(() => hideModal("create_account_modal"))
              .then(() => store.getAccounts())
              .finally(() => (loading.value = false));
        }
      });
    };

    const bulkInsertionChanged = ()=>{
      console.log(targetData.value.bulk_insertion);
    }

    return {
      targetData,
      submit,
      loading,
      formRef,
      rules,
      newAccountModalRef,
      hideModal,
      bulkInsertionChanged
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
