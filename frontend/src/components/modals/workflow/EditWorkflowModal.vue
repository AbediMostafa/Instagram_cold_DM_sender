<template>
  <!--begin::Modal - Edit Workflow-->
  <div class="modal fade" id="edit_workflow_modal" ref="modalRef" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered mw-750px">
      <div class="modal-content rounded">
        <div class="modal-header pb-0 border-0 justify-content-end">
          <div class="btn btn-sm btn-icon btn-active-color-primary" data-bs-dismiss="modal">
            <KTIcon icon-name="cross" icon-class="fs-1"/>
          </div>
        </div>

        <div class="modal-body scroll-y px-10 px-lg-15 pt-0 pb-15">
          <el-form id="edit_workflow_modal_form" ref="formRef" :model="formData" :rules="rules" @submit.prevent="submit"
                   class="form">

            <div class="mb-13 text-center">
              <h1 class="mb-3">Edit Workflow</h1>
            </div>

            <!-- Title -->
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Title</span>
              </label>
              <el-form-item prop="title">
                <el-input v-model="formData.title" placeholder="Workflow title"/>
              </el-form-item>
            </div>

            <!-- Service -->
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Service</span>
              </label>
              <el-form-item prop="service_id">
                <el-select v-model="formData.service_id" placeholder="Select a service">
                  <el-option v-for="service in serviceStore.services.data" :key="service.id" :label="service.title"
                             :value="service.id"/>
                </el-select>
              </el-form-item>
            </div>

            <!-- Modules / Tags -->
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span>Modules</span>
              </label>
              <el-form-item prop="modules">
                <el-select
                    v-model="formData.modules"
                    multiple
                    filterable
                    remote
                    clearable
                    placeholder="Modules"
                    :remote-method="moduleStore.fetchModules"
                    :loading="moduleStore.is.searching"
                >
                  <el-option v-for="module in moduleStore.modules.data" :key="module.id" :label="module.title"
                             :value="module.id"/>
                </el-select>
              </el-form-item>
            </div>

            <!-- Actions -->
            <div class="text-center">
              <button type="reset" class="btn btn-light me-3" @click="hideModal('edit_workflow_modal')">
                Cancel
              </button>

              <button class="btn btn-lg btn-primary" type="submit" :data-kt-indicator="loading ? 'on' : null">
                <span v-if="!loading" class="indicator-label">
                  Save Changes
                  <KTIcon icon-name="arrow-right" icon-class="fs-3 ms-2 me-0"/>
                </span>
                <span v-else class="indicator-progress">
                  Please wait...
                  <span class="spinner-border spinner-border-sm align-middle ms-2"/>
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
import {defineComponent, ref, watch} from "vue";
import {hideModal} from "@/core/helpers/modal";
import ApiService from "@/core/services/ApiService";
import {useWorkflowStore} from "@/stores/Workflow";
import {useServiceStore} from "@/stores/Service";
import {useModuleStore} from "@/stores/Module";

export default defineComponent({
  name: "EditWorkflowModal",
  props: {
    workflowData: {type: Object, required: true},
  },
  setup(props) {
    const formRef = ref();
    const modalRef = ref<HTMLElement | null>(null);
    const loading = ref(false);

    const workflowStore = useWorkflowStore();
    const serviceStore = useServiceStore();
    const moduleStore = useModuleStore();

    const formData = ref({
      id: null as number | null,
      title: "",
      service_id: null as number | null,
      modules: [] as number[], // <-- modules array
    });

    const rules = {
      title: [{required: true, message: "Title is required", trigger: "blur"}],
      service_id: [{required: true, message: "Service is required", trigger: "change"}],
    };

    // Load services & modules
    serviceStore.getServices(1, false);

    // Watch prop and update formData
    watch(
        () => props.workflowData,
        (newVal) => {
          if (!newVal) return;
          formData.value.id = newVal.id;
          formData.value.title = newVal.title;
          formData.value.service_id = newVal.service_id;
          formData.value.modules = newVal.modules.map(module => module.id);
          moduleStore.modules.data = newVal.modules;
        },
        {immediate: true}
    );

    const submit = () => {
      if (!formRef.value) return;

      formRef.value.validate((valid: boolean) => {
        if (!valid) return;

        loading.value = true;
        ApiService.post(`workflows/update`, formData.value)
            .then(() => {
              hideModal("edit_workflow_modal");
              workflowStore.getWorkflows();
            })
            .finally(() => (loading.value = false));
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
      serviceStore,
      moduleStore,
    };
  },
});
</script>

<style lang="scss">
.el-select {
  width: 100%;
}
</style>
