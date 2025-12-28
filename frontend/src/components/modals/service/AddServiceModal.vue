<template>
  <!--begin::Modal - New Service-->
  <div
      class="modal fade"
      id="add_service_modal"
      ref="modalRef"
      tabindex="-1"
      aria-hidden="true"
  >
    <!--begin::Modal dialog-->
    <div class="modal-dialog modal-dialog-centered mw-750px">
      <!--begin::Modal content-->
      <div class="modal-content rounded">
        <!--begin::Modal header-->
        <div class="modal-header pb-0 border-0 justify-content-end">
          <div
              class="btn btn-sm btn-icon btn-active-color-primary"
              data-bs-dismiss="modal"
          >
            <KTIcon icon-name="cross" icon-class="fs-1" />
          </div>
        </div>

        <!--begin::Modal body-->
        <div class="modal-body scroll-y px-10 px-lg-15 pt-0 pb-15">
          <el-form
              id="add_service_modal_form"
              ref="formRef"
              :model="formData"
              :rules="rules"
              @submit.prevent="submit"
              class="form"
          >
            <div class="mb-13 text-center">
              <h1 class="mb-3">Create New Service</h1>
            </div>

            <!-- Service key -->
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Service</span>
              </label>
              <el-form-item prop="service">
                <el-input
                    v-model="formData.service"
                    placeholder="Service key (e.g. instagram_dm)"
                />
              </el-form-item>
            </div>

            <!-- Title -->
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Title</span>
              </label>
              <el-form-item prop="title">
                <el-input
                    v-model="formData.title"
                    placeholder="Service title"
                />
              </el-form-item>
            </div>

            <!-- Description -->
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Description</span>
              </label>
              <el-form-item prop="description">
                <el-input
                    v-model="formData.description"
                    type="textarea"
                    :rows="5"
                    placeholder="Service description"
                />
              </el-form-item>
            </div>

            <!-- Actions -->
            <div class="text-center">
              <button
                  type="reset"
                  class="btn btn-light me-3"
                  @click="hideModal('add_service_modal')"
              >
                Cancel
              </button>

              <button
                  class="btn btn-lg btn-primary"
                  type="submit"
                  :data-kt-indicator="loading ? 'on' : null"
              >
                <span v-if="!loading" class="indicator-label">
                  Submit
                  <KTIcon icon-name="arrow-right" icon-class="fs-3 ms-2 me-0" />
                </span>
                <span v-else class="indicator-progress">
                  Please wait...
                  <span class="spinner-border spinner-border-sm align-middle ms-2" />
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
import { defineComponent, ref } from "vue";
import { hideModal } from "@/core/helpers/modal";
import ApiService from "@/core/services/ApiService";
import { useServiceStore } from "@/stores/Service";

export default defineComponent({
  name: "add_service_modal",
  setup() {
    const formRef = ref();
    const modalRef = ref<HTMLElement | null>(null);
    const loading = ref(false);
    const store = useServiceStore();

    const formData = ref({
      service: "",
      title: "",
      description: "",
    });

    const rules = {
      service: [
        { required: true, message: "Service is required", trigger: "blur" },
      ],
      title: [
        { required: true, message: "Title is required", trigger: "blur" },
      ],
      description: [
        { required: true, message: "Description is required", trigger: "blur" },
      ],
    };

    const submit = () => {
      if (!formRef.value) return;

      formRef.value.validate((valid: boolean) => {
        if (!valid) return;

        loading.value = true;

        ApiService.post("services/create", formData.value)
            .then(() => {
              hideModal("add_service_modal");
              store.getServices();
            })
            .finally(() => {
              loading.value = false;
            });
      });
    };

    return {
      formRef,
      modalRef,
      formData,
      rules,
      submit,
      loading,
      hideModal,
    };
  },
});
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
