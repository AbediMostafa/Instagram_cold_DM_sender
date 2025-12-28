<template>
  <div class="card mb-5 mb-xl-8">
    <!-- Header -->
    <div class="card-header border-0 pt-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">Modules</span>
        <span class="text-muted mt-1 fw-semibold fs-7">
          {{ store.modules.total }} Module(s)
        </span>
      </h3>

      <div class="card-toolbar">
        <a
            class="btn btn-sm btn-success me-2"
            @click="showModal('add_module_modal')"
        >
          Add Module
        </a>

        <a
            class="btn btn-sm btn-light-primary"
            @click="store.getModules()"
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
            <th class="min-w-200px">CLASS NAME</th>
            <th class="min-w-300px">WORKFLOWS</th>
            <th class="min-w-100px text-end">Actions</th>
          </tr>
          </thead>

          <tbody>
          <tr
              v-for="module in store.modules.data"
              :key="module.id"
          >
            <td>
              <div class="form-check form-check-sm form-check-custom form-check-solid">
                <input
                    class="form-check-input"
                    type="checkbox"
                    :value="module.id"
                    v-model="store.checkedModuleRows"
                />
              </div>
            </td>

            <td class="fw-bold text-gray-700 fs-7">
              {{ module.title }}
            </td>

            <td class="text-gray-600 fs-7">
              {{ module.class_name }}
            </td>

            <td class="text-gray-600 fs-7">
              <span
                  class="badge badge-light-info ms-1"
                  v-if="module.workflows"
                  v-for="workflow in module.workflows">
                {{ workflow.title }}
              </span>
              <span v-else class="text-muted">—</span>
            </td>

            <td class="text-end">
              <el-dropdown>
                <a class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm">
                  <KTIcon icon-name="category" icon-class="fs-3" />
                </a>

                <template #dropdown>
                  <el-dropdown-menu class="p-3">
                    <el-dropdown-item
                        @click="editClicked(module)"
                    >
                      Edit
                    </el-dropdown-item>

                    <el-dropdown-item
                        @click="store.deleteSelected([module.id])"
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
            :current-page="store.modules.current_page"
            :page-size="configStore.pagination?.each_page?.default || 75"
            layout="prev, pager, next"
            :total="store.modules.total"
            @current-change="page => store.getModules(page)"
        />
      </div>
    </div>
  </div>

  <add-module-modal />
  <edit-module-modal :module-data="selectedModule" />
</template>

<script lang="ts" setup>
import { ref, onMounted } from "vue";
import { showModal } from "@/core/helpers/modal";
import { useAppConfigStore } from "@/stores/AppConfig";
import { useModuleStore } from "@/stores/Module";
import { useWorkflowStore } from "@/stores/Workflow";

import AddModuleModal from "@/components/modals/module/AddModuleModal.vue";
import EditModuleModal from "@/components/modals/module/EditModuleModal.vue";

const store = useModuleStore();
const workflowStore = useWorkflowStore();
const configStore = useAppConfigStore();

const selectedModule = ref(null);

const editClicked = (module: any) => {
  selectedModule.value = module;
  showModal("edit_module_modal");
};

onMounted(() => {
  store.getModules();
  workflowStore.getWorkflows(); // for workflow dropdowns in modals
});
</script>
