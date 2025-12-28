<template>
  <!--begin::Modal - New Module-->
  <div
      class="modal fade"
      id="add_module_modal"
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
              id="add_module_modal_form"
              ref="formRef"
              :model="formData"
              :rules="rules"
              @submit.prevent="submit"
              class="form"
          >
            <div class="mb-13 text-center">
              <h1 class="mb-3">Create New Module</h1>
            </div>

            <!-- Title -->
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Title</span>
              </label>
              <el-form-item prop="title">
                <el-input
                    v-model="formData.title"
                    placeholder="Module title"
                />
              </el-form-item>
            </div>

            <!-- Module Path -->
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Module Path</span>
              </label>
              <el-form-item prop="module_path">
                <el-input
                    v-model="formData.module_path"
                    placeholder="e.g. App\\Modules\\Instagram"
                />
              </el-form-item>
            </div>

            <!-- Class Name -->
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Class Name</span>
              </label>
              <el-form-item prop="class_name">
                <el-input
                    v-model="formData.class_name"
                    placeholder="e.g. InstagramModule"
                />
              </el-form-item>
            </div>

            <!-- Workflow -->
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span>Workflow</span>
              </label>
              <el-form-item prop="workflow_id">
                <el-select
                    v-model="formData.workflow_id"
                    placeholder="Select a workflow"
                    clearable
                >
                  <el-option
                      v-for="workflow in workflowStore.workflows.data"
                      :key="workflow.id"
                      :label="workflow.title"
                      :value="workflow.id"
                  />
                </el-select>
              </el-form-item>
            </div>

            <!-- Actions -->
            <div class="text-center">
              <button
                  type="reset"
                  class="btn btn-light me-3"
                  @click="hideModal('add_module_modal')"
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
import { defineComponent, ref, onMounted } from "vue";
import { hideModal } from "@/core/helpers/modal";
import ApiService from "@/core/services/ApiService";
import { useModuleStore } from "@/stores/Module";
import { useWorkflowStore } from "@/stores/Workflow";

export default defineComponent({
  name: "AddModuleModal",
  setup() {
    const formRef = ref();
    const modalRef = ref<HTMLElement | null>(null);
    const loading = ref(false);

    const moduleStore = useModuleStore();
    const workflowStore = useWorkflowStore();

    const formData = ref({
      title: "",
      module_path: "",
      class_name: "",
      workflow_id: null as number | null,
    });

    const rules = {
      title: [{ required: true, message: "Title is required", trigger: "blur" }],
      module_path: [{ required: true, message: "Module path is required", trigger: "blur" }],
      class_name: [{ required: true, message: "Class name is required", trigger: "blur" }],
    };

    onMounted(() => {
      workflowStore.getWorkflows(1, false);
    });

    const submit = () => {
      if (!formRef.value) return;

      formRef.value.validate((valid: boolean) => {
        if (!valid) return;

        loading.value = true;

        ApiService.post("modules/create", formData.value)
            .then(() => {
              hideModal("add_module_modal");
              moduleStore.getModules();
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
      workflowStore,
    };
  },
});
</script>

<style lang="scss">
.el-select {
  width: 100%;
}
</style>
