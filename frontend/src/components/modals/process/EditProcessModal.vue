<template>
  <!--begin::Modal - Edit Process-->
  <div
      class="modal fade"
      id="edit_process_modal"
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
              id="edit_process_modal_form"
              ref="formRef"
              :model="formData"
              :rules="rules"
              @submit.prevent="submit"
              class="form"
          >
            <div class="mb-13 text-center">
              <h1 class="mb-3">Edit Process</h1>
            </div>

            <!-- PID (readonly) -->
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="fs-6 fw-semibold mb-2">PID</label>
              <el-input v-model="formData.pid" disabled />
            </div>

            <!-- Status -->
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="fs-6 fw-semibold mb-2">Status</label>
              <el-select v-model="formData.status" disabled>
                <el-option label="Idle" value="idle" />
                <el-option label="Running" value="running" />
                <el-option label="Stopped" value="stopped" />
                <el-option label="Terminated" value="terminated" />
              </el-select>
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
                  @click="hideModal('edit_process_modal')"
              >
                Cancel
              </button>

              <button
                  class="btn btn-lg btn-primary"
                  type="submit"
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
import { useProcessStore } from "@/stores/Process";
import { useWorkflowStore } from "@/stores/Workflow";

export default defineComponent({
  name: "EditProcessModal",
  props: {
    processData: {
      type: Object,
      required: true,
    },
  },
  setup(props) {
    const formRef = ref();
    const modalRef = ref<HTMLElement | null>(null);
    const loading = ref(false);

    const processStore = useProcessStore();
    const workflowStore = useWorkflowStore();

    const formData = ref({
      id: null as number | null,
      pid: null as number | null,
      status: "",
      workflow_id: null as number | null,
    });

    const rules = {
      workflow_id: [],
    };

    // Load workflows
    workflowStore.getWorkflows(1, false);

    // Sync prop → form
    watch(
        () => props.processData,
        (newVal) => {
          if (!newVal) return;

          formData.value.id = newVal.id;
          formData.value.pid = newVal.pid;
          formData.value.status = newVal.status;
          formData.value.workflow_id = newVal.workflow_id;
        },
        { immediate: true }
    );

    const submit = () => {
      if (!formRef.value) return;

      loading.value = true;

      ApiService.post("processes/update", {
        id: formData.value.id,
        workflow_id: formData.value.workflow_id,
      })
          .then(() => {
            hideModal("edit_process_modal");
            processStore.getProcesses();
          })
          .finally(() => {
            loading.value = false;
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
