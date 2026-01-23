<template>
  <div class="card mb-5 mb-xl-8">
    <!-- Header -->
    <div class="card-header border-0 pt-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">Processes</span>
        <span class="text-muted mt-1 fw-semibold fs-7">
          {{ store.processes.total }} Process(es)
        </span>
      </h3>

      <div class="card-toolbar">
        <a class="btn btn-sm btn-light-primary me-2" @click="store.getProcesses()">
          Refresh
        </a>

        <button
            type="button"
            class="btn btn-sm btn-icon btn-color-primary btn-active-light-primary"
            data-kt-menu-trigger="click"
            data-kt-menu-placement="bottom-end"
        >
          <KTIcon icon-name="category" icon-class="fs-2"/>
          <div
              class="menu menu-sub menu-sub-dropdown menu-column menu-rounded menu-gray-600 menu-state-bg-light-primary fw-semibold w-350px"
              data-kt-menu="true"
          >
            <!--begin::Menu item-->
            <div class="menu-item px-3">
              <div class="menu-content fs-6 text-gray-900 fw-bold px-3 py-4">
                Quick Actions
              </div>
            </div>
            <!--end::Menu item-->

            <!--begin::Menu separator-->
            <div class="separator mb-3 opacity-75"></div>

            <!--begin::Menu item-->
            <div class="menu-item ">
              <div class="px-3">
                <a
                    class="btn btn-light-danger btn-sm px-4 w-100"
                    @click="store.deleteSelected(store.checkedProcessRows)"
                >Delete Selected</a>
              </div>
            </div>
            <div class="menu-item ">
              <div class="px-3 d-flex align-items-center justify-content-center">
                <a
                    class="btn btn-light-success btn-sm px-4 w-100"
                    @click="store.setStatusTo('running',store.checkedProcessRows)"
                >Start Selected</a>
                <a
                    class="btn btn-light-danger btn-sm px-4 w-100 ms-1"
                    @click="store.setStatusTo('stopped',store.checkedProcessRows)"
                >Stop Selected</a>
              </div>
            </div>
            <div class="menu-item ">
              <div
                  @click.stop
                  class="px-3 d-flex align-items-center justify-content-center">
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
                <a
                    class="btn btn-light-success btn-sm px-4 w-50 ms-2"
                    @click="store.setWorkflow(formData.workflow_id, store.checkedProcessRows)"
                >Set Workflow</a>
              </div>
            </div>

          </div>


        </button>
      </div>
    </div>

    <!-- Body -->
    <div class="card-body py-3">
      <div class="table-responsive">
        <table
            class="table table-row-bordered table-row-gray-100 align-middle gs-0 gy-3"
            v-loading="store.is.loading"
        >
          <!-- Table Head -->
          <thead>
          <tr class="fw-bold text-muted">
            <th class="w-25px">
              <div class="form-check form-check-sm form-check-custom form-check-solid">
                <input
                    class="form-check-input"
                    type="checkbox"
                    @change="store.checkRows($event)"
                />
              </div>
            </th>
            <th class="min-w-120px">PID</th>
            <th class="min-w-120px">STATUS</th>
            <th class="min-w-150px">WORKFLOW</th>
            <th class="min-w-150px">LAST CHECKED</th>
            <th class="min-w-150px">CREATED AT</th>
            <th class="min-w-100px text-end">Actions</th>
          </tr>
          </thead>

          <!-- Table Body -->
          <tbody>
          <tr
              v-for="(process, index) in store.processes.data"
              :key="index"
          >
            <td>
              <div class="form-check form-check-sm form-check-custom form-check-solid">
                <input
                    class="form-check-input"
                    type="checkbox"
                    :value="process.id"
                    v-model="store.checkedProcessRows"
                />
              </div>
            </td>

            <td>
                <span class="fw-bold fs-7 text-gray-800">
                  {{ process.pid }}
                </span>
            </td>

            <td>
                <span
                    class="badge"
                    :class="{
                    'badge-light-success': process.status === 'running',
                    'badge-light-info': process.status === 'idle',
                    'badge-light-danger': process.status === 'terminated',
                    'badge-light-warning': process.status === 'stopped',
                  }"
                >
                  {{ process.status }}
                </span>
            </td>

            <td>
                <span class="fw-bold fs-7 text-gray-700">
                  {{ process.workflow?.title ?? '-' }}
                </span>
            </td>

            <td>
                <span class="fs-8 text-gray-600">
                  {{ process.last_checked_at ?? '-' }}
                </span>
            </td>

            <td>
                <span class="fs-8 text-gray-600">
                  {{ process.created_at }}
                </span>
            </td>

            <td class="d-flex align-items-center justify-content-end">

              <div>
                <a
                    @click="toggleProcess(process)"
                    class="btn btn-sm fs-8 px-3 py-2"
                    :class="process.status === 'running'
                ? 'btn-light-danger'
                : 'btn-light-success'"
                >
                    <span
                        v-if="is.toggling && currentProcessId === process.id"
                    >
                      Please wait...
                      <span class="spinner-border spinner-border-sm align-middle ms-2"></span>
                    </span>

                  <span v-else>
                    {{ process.status === 'running' ? 'Stop' : 'Start' }}
                  </span>
                </a>

              </div>
              <el-dropdown class="p-5">
                <a class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm">
                  <KTIcon icon-name="category" icon-class="fs-3"/>
                </a>
                <template #dropdown>
                  <el-dropdown-menu class="p-3">
                    <el-dropdown-item
                        @click="store.deleteSelected([process.id])"
                    >
                      Delete
                    </el-dropdown-item>

                    <el-dropdown-item
                        @click="editProcess(process)"
                    >
                      Edit
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </td>
          </tr>
          </tbody>
        </table>

        <!-- Pagination -->
        <el-pagination
            :current-page="store.processes.current_page"
            :page-size="75"
            layout="prev, pager, next"
            :total="store.processes.total"
            @current-change="page => store.getProcesses(page)"
        />
      </div>
    </div>
    <edit-process-modal :process-data="processData"/>
  </div>
</template>

<script lang="ts" setup>
import {onMounted, reactive, ref} from "vue";
import {useProcessStore} from "@/stores/Process";
import EditProcessModal from "@/components/modals/process/EditProcessModal.vue";
import {showModal} from "@/core/helpers/modal";
import ApiService from "@/core/services/ApiService";
import {useWorkflowStore} from "@/stores/workflow";

const store = useProcessStore();
const formData = reactive({
  workflow_id:'',
})
const processData = ref(null);
const is = reactive({
  toggling: false
});
const workflowStore = useWorkflowStore();
workflowStore.getWorkflows(1, false);


const currentProcessId = ref('')


const toggleProcess = process => {

  is.toggling = true;
  currentProcessId.value = process.id;

  ApiService.post("processes/toggle-process", {id: process.id})
      .then(store.getProcesses)
      .finally(() => {
        is.toggling = false;
      });

}

const editProcess = (process) => {
  processData.value = process
  showModal("edit_process_modal");
}

onMounted(() => {
  store.getProcesses();
});

const clicked = () => {

  alert(store.checkedProcessRows)
}


</script>
