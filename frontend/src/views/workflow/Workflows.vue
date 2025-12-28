  <template>
    <div class="card mb-5 mb-xl-8">
      <!-- Header -->
      <div class="card-header border-0 pt-5">
        <h3 class="card-title align-items-start flex-column">
          <span class="card-label fw-bold fs-3 mb-1">Workflows</span>
          <span class="text-muted mt-1 fw-semibold fs-7">
            {{ store.workflows.total }} Workflow(s)
          </span>
        </h3>

        <div class="card-toolbar">
          <a
              class="btn btn-sm btn-success me-2"
              @click="showModal('add_workflow_modal')"
          >
            Add Workflow
          </a>

          <a
              class="btn btn-sm btn-light-primary"
              @click="store.getWorkflows()"
          >
            Refresh
          </a>
        </div>
      </div>

      <!-- Body -->
      <div class="card-body py-3">
        <div class="table-responsive">
          <table
              class="table table-row-bordered table-row-gray-100 align-middle gs-0 gy-3"
              v-loading="store.is.loading"
          >
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

              <th class="min-w-200px">TITLE</th>
              <th class="min-w-200px">SERVICE</th>
              <th class="min-w-150px">MODULES</th>
              <th class="min-w-100px text-end">Actions</th>
            </tr>
            </thead>

            <tbody>
            <tr
                v-for="workflow in store.workflows.data"
                :key="workflow.id"
            >
              <td>
                <div class="form-check form-check-sm form-check-custom form-check-solid">
                  <input
                      class="form-check-input"
                      type="checkbox"
                      :value="workflow.id"
                      v-model="store.checkedWorkflowRows"
                  />
                </div>
              </td>

              <td class="fw-bold text-gray-700 fs-7">
                {{ workflow.title }}
              </td>

              <td class="text-gray-600 fs-7">
                  <span v-if="workflow.service">
                    {{ workflow.service.service }}
                  </span>
                <span v-else class="text-muted">
                    —
                  </span>
              </td>

              <td class="text-gray-600 fs-8">
                <span
                    class="badge badge-light-info ms-1"
                    v-for="module in workflow.modules">{{ module.title }}</span>
              </td>

              <td class="text-end">
                <el-dropdown>
                  <a class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm">
                    <KTIcon icon-name="category" icon-class="fs-3" />
                  </a>

                  <template #dropdown>
                    <el-dropdown-menu class="p-3">
                      <el-dropdown-item
                          @click="editClicked(workflow)"
                      >
                        Edit
                      </el-dropdown-item>

                      <el-dropdown-item
                          @click="store.deleteSelected([workflow.id])"
                      >
                        Delete
                      </el-dropdown-item>

                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </td>
            </tr>
            </tbody>
          </table>

          <el-pagination
              :current-page="store.workflows.current_page"
              :page-size="configStore.pagination?.each_page?.default || 10"
              layout="prev, pager, next"
              :total="store.workflows.total"
              @current-change="page => store.getWorkflows(page)"
          />
        </div>
      </div>
    </div>

    <add-workflow-modal />
    <edit-workflow-modal :workflow-data="selectedWorkflow" />
  </template>

  <script lang="ts" setup>
  import { ref, onMounted } from "vue";
  import { showModal } from "@/core/helpers/modal";
  import { useAppConfigStore } from "@/stores/AppConfig";
  import { useWorkflowStore } from "@/stores/Workflow";
  import { useServiceStore } from "@/stores/Service";

  import AddWorkflowModal from "@/components/modals/workflow/AddWorkflowModal.vue";
  import EditWorkflowModal from "@/components/modals/workflow/EditWorkflowModal.vue";

  const store = useWorkflowStore();
  const serviceStore = useServiceStore();
  const configStore = useAppConfigStore();

  const selectedWorkflow = ref(null);

  const editClicked = (workflow: any) => {
    selectedWorkflow.value = workflow;
    showModal("edit_workflow_modal");
  };

  onMounted(() => {
    store.getWorkflows();
    serviceStore.getServices(); // for dropdowns in modals
  });
  </script>
