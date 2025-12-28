<template>
  <!--begin::Modal - Edit Service-->
  <div
      class="modal fade"
      id="edit_service_modal"
      ref="modalRef"
      tabindex="-1"
      aria-hidden="true"
  >
    <div class="modal-dialog modal-dialog-centered mw-750px">
      <div class="modal-content rounded">
        <!-- Header -->
        <div class="modal-header pb-0 border-0 justify-content-end">
          <div
              class="btn btn-sm btn-icon btn-active-color-primary"
              data-bs-dismiss="modal"
          >
            <KTIcon icon-name="cross" icon-class="fs-1" />
          </div>
        </div>

        <!-- Body -->
        <div class="modal-body scroll-y px-10 px-lg-15 pt-0 pb-15">
          <el-form
              ref="formRef"
              :model="formData"
              :rules="rules"
              @submit.prevent="submit"
              class="form"
          >
            <div class="mb-13 text-center">
              <h1 class="mb-3">Edit Service</h1>
            </div>

            <!-- Service -->
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="fs-6 fw-semibold mb-2">
                <span class="required">Service</span>
              </label>
              <el-form-item prop="service">
                <el-input v-model="formData.service" />
              </el-form-item>
            </div>

            <!-- Title -->
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="fs-6 fw-semibold mb-2">
                <span class="required">Title</span>
              </label>
              <el-form-item prop="title">
                <el-input v-model="formData.title" />
              </el-form-item>
            </div>

            <!-- Description -->
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="fs-6 fw-semibold mb-2">
                <span class="required">Description</span>
              </label>
              <el-form-item prop="description">
                <el-input
                    v-model="formData.description"
                    type="textarea"
                    :rows="5"
                />
              </el-form-item>
            </div>

            <!-- Actions -->
            <div class="text-center">
              <button
                  type="reset"
                  class="btn btn-light me-3"
                  @click="hideModal('edit_service_modal')"
              >
                Cancel
              </button>

              <button
                  type="submit"
                  class="btn btn-lg btn-primary"
                  :data-kt-indicator="loading ? 'on' : null"
              >
                <span v-if="!loading" class="indicator-label">
                  Save Changes
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
import { defineComponent, ref, watch } from "vue";
import { hideModal } from "@/core/helpers/modal";
import ApiService from "@/core/services/ApiService";
import { useServiceStore } from "@/stores/Service";

export default defineComponent({
  name: "edit_service_modal",
  props: {
    serviceData: {
      type: Object,
      required: true,
    },
  },
  setup(props) {
    const formRef = ref();
    const modalRef = ref<HTMLElement | null>(null);
    const loading = ref(false);
    const store = useServiceStore();

    const formData = ref({
      id: null as number | null,
      service: "",
      title: "",
      description: "",
    });

    watch(
        () => props.serviceData,
        (value: any) => {

          console.log({value})
          if (!value) return;

          formData.value = {
            id: value.id,
            service: value.service,
            title: value.title,
            description: value.description,
          };
        },
        { immediate: true }
    );

    const rules = {
      service: [{ required: true, message: "Service is required", trigger: "blur" }],
      title: [{ required: true, message: "Title is required", trigger: "blur" }],
      description: [{ required: true, message: "Description is required", trigger: "blur" }],
    };

    const submit = () => {
      if (!formRef.value) return;

      formRef.value.validate((valid: boolean) => {
        if (!valid) return;

        loading.value = true;

        ApiService.post("services/update", formData.value)
            .then(() => {
              hideModal("edit_service_modal");
              store.getServices(store.services.current_page);
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
