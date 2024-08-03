<template>
  <!--begin::Modal - New Target-->
  <div
      class="modal fade"
      id="edit_account_modal"
      tabindex="-1"
      aria-hidden="true"
      v-loading=is.gettingAccount
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
              id="edit_account_modal_form"
              @submit.prevent="submit()"
              :model="account"
              :rules="rules"
              ref="formRef"
              class="form"
          >
            <!--begin::Heading-->
            <div class="mb-13 text-center">
              <h1 class="mb-3">Edit Account</h1>
            </div>
            <!--end::Heading-->

            <!--begin::Input group-->
            <div class="d-flex flex-column mb-8 fv-row">
              <!--begin::Label-->
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Username</span>
              </label>
              <!--end::Label-->

              <el-form-item prop="username">
                <el-input
                    v-model="account.username"
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
                    v-model="account.password"
                    placeholder="Enter Account Password"
                    name="password"
                ></el-input>
              </el-form-item>
            </div>
            <div class="d-flex flex-column mb-8 fv-row">
              <!--begin::Label-->
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Instagram State</span>
              </label>
              <!--end::Label-->
              <div style="margin-top: 5px">
                <el-radio-group v-model="account.instagram_state">
                  <el-radio-button label="active" value="active" />
                  <el-radio-button label="challenging" value="challenging" />
                  <el-radio-button label="action ban" value="action ban" />
                  <el-radio-button label="suspended" value="suspended" />
                </el-radio-group>
              </div>
            </div>

            <!--begin::Actions-->
            <div class="text-center">
              <button
                  type="reset"
                  id="edit_account_modal_cancel"
                  class="btn btn-light me-3"
                  @click="hideModal('edit_account_modal')"
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
                  Edit
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
import {getAssetPath} from "@/core/helpers/assets";
import {computed, defineComponent, onMounted, ref, watch} from "vue";
import {hideModal} from "@/core/helpers/modal";
import Swal from "sweetalert2/dist/sweetalert2.js";
import ApiService from "@/core/services/ApiService";
import {useAccountStore} from "@/stores/Account";

export default defineComponent({
  name: "edit_account_modal",
  props: ['id'],
  setup(props) {
    const formRef = ref<null | HTMLFormElement>(null);
    const loading = ref<boolean>(false);
    const store = useAccountStore()
    const account = ref({})
    const is = ref({
      gettingAccount: false
    });

    const rules = ref({
      username: [{required: true, message: "Please input username", trigger: "blur"},],
      password: [{required: true, message: "Please input password", trigger: "blur"},],
    });

    const getAccount = () => {
      is.value.gettingAccount = true
      ApiService.post('account/view', {id: props.id})
          .then(response => account.value = response.data)
          .finally(() => is.value.gettingAccount = false)
    }

    watch(() => props.id, () => getAccount())

    const submit = () => {
      if (!formRef.value) {
        return;
      }

      formRef.value.validate((valid: boolean) => {
        if (valid) {
          loading.value = true;

          ApiService.post('account/edit', {id: props.id, ...account.value})
              .then(() => hideModal("edit_account_modal"))
              .then(() => store.getAccounts())
              .finally(() => loading.value = false)
        }
      });
    };

    return {
      is,
      account,
      submit,
      loading,
      formRef,
      rules,
      getAssetPath,
      hideModal,
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
