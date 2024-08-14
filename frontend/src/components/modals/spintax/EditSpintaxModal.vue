<template>
  <!--begin::Modal - New Spintax-->
  <div
      class="modal fade"
      id="create_spintax_modal"
      ref="newSpintaxModalRef"
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
              id="create_spintax_modal_form"
              @submit.prevent="submit()"
              :model="store.createSpintaxData"
              :rules="rules"
              ref="formRef"
              class="form"
          >
            <!--begin::Heading-->
            <div class="mb-13 text-center">
              <h1 class="mb-3">Edit {{store.spintax.name}}</h1>
            </div>

            <!--begin::Input group-->
            <div class="d-flex flex-column mb-8 fv-row">
              <!--begin::Label-->
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Name</span>
              </label>
              <!--end::Label-->

              <el-form-item prop="name">
                <el-input
                    v-model="store.spintax.name"
                    placeholder="Enter Spintax Name"
                    name="name"
                ></el-input>
              </el-form-item>
            </div>

            <div class="d-flex flex-column mb-8 fv-row">
              <!--begin::Label-->
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Type</span>
              </label>
              <!--end::Label-->

              <el-form-item prop="type">
                <el-select v-model="store.spintax.type" placeholder="Select Type">
                  <el-option
                      v-for="type in spintaxTypes"
                      :key="type"
                      :label="type"
                      :value="type"
                  />
                </el-select>
              </el-form-item>
            </div>

            <div class="d-flex flex-column mb-8 fv-row">
              <!--begin::Label-->
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Text</span>
              </label>
              <!--end::Label-->

              <el-form-item prop="text">
                <el-input
                    type="textarea"
                    v-model="store.spintax.text"
                    placeholder="Enter Spintax Text"
                    name="text"
                    :rows="6"
                ></el-input>
              </el-form-item>
            </div>

            <!--begin::Actions-->
            <div class="text-center">
              <button
                  type="reset"
                  id="create_spintax_modal_cancel"
                  class="btn btn-light me-3"
                  @click="hideModal('create_spintax_modal')"
              >
                Cancel
              </button>

              <!--begin::Button-->
              <button
                  :data-kt-indicator="store.is.creating ? 'on' : null"
                  class="btn btn-lg btn-primary"
                  type="submit"
              >
                <span v-if="!store.is.creating" class="indicator-label">
                  Submit
                  <KTIcon icon-name="arrow-right" icon-class="fs-3 ms-2 me-0"/>
                </span>
                <span v-if="store.is.creating" class="indicator-progress">
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

<script setup lang="ts">
import {ref} from "vue";
import {hideModal} from "@/core/helpers/modal";
import {useSpintaxStore} from "@/stores/Spintax";

const store = useSpintaxStore();
const formRef = ref(null);

const rules = ref({
  name: [{required: true, message: "Please input name", trigger: "blur"}],
  type: [{required: true, message: "Please select type", trigger: "change"}],
  text: [{required: true, message: "Please input text", trigger: "blur"}],
});

const spintaxTypes = ['cold dm',
  'first dm follow up',
  'second dm follow up',
  'third dm follow up',];


const submit = () => {
  if (!formRef.value)
    return;

  formRef.value.validate((valid: boolean) => valid && store.createSpintax());
};

</script>

<style lang="scss">
.el-select {
  width: 100%;
}

.el-date-editor.el-input,
.el-date-editor.el-input__inner {
  width: 100%;
}
</style>
