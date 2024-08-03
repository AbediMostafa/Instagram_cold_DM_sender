<template>
  <!--begin::Modal - New Target-->
  <div
      class="modal fade"
      id="edit_lead_modal"
      tabindex="-1"
      aria-hidden="true"
      v-loading=is.gettingLead
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
              id="edit_lead_modal_form"
              @submit.prevent="submit()"
              :model="lead"
              :rules="rules"
              ref="formRef"
              class="form"
          >
            <!--begin::Heading-->
            <div class="mb-13 text-center">
              <h1 class="mb-3">Edit Lead</h1>
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
                    v-model="lead.username"
                    placeholder="Enter Account Username"
                    name="username"
                ></el-input>
              </el-form-item>
            </div>
            <!--begin::Actions-->
            <div class="text-center">
              <button
                  type="reset"
                  id="edit_lead_modal_cancel"
                  class="btn btn-light me-3"
                  @click="hideModal('edit_lead_modal')"
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
import {defineComponent, ref, watch} from "vue";
import {hideModal} from "@/core/helpers/modal";
import ApiService from "@/core/services/ApiService";
import {useLeadStore} from "@/stores/Lead";

export default defineComponent({
  name: "edit_lead_modal",
  props: ['id'],
  setup(props) {
    const formRef = ref<null | HTMLFormElement>(null);
    const loading = ref<boolean>(false);
    const store = useLeadStore()
    const lead = ref({})
    const is = ref({
      gettingLead: false
    });

    const rules = ref({
      username: [{required: true, message: "Please input username", trigger: "blur"},],
    });

    const getLead = () => {
      is.value.gettingLead = true
      ApiService.post('lead/view', {id: props.id})
          .then(response => lead.value = response.data)
          .finally(() => is.value.gettingLead = false)
    }

    watch(() => props.id, () => getLead())

    const submit = () => {
      if (!formRef.value) {
        return;
      }

      formRef.value.validate((valid: boolean) => {
        if (valid) {
          loading.value = true;

          ApiService.post('lead/edit', {id: props.id, ...lead.value})
              .then(() => hideModal("edit_lead_modal"))
              .then(() => store.getLeads())
              .finally(() => loading.value = false)
        }
      });
    };

    return {
      is,
      lead,
      submit,
      loading,
      formRef,
      rules,
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
