<template>
  <div class="card mb-5 mb-xl-8">
    <!-- Header -->
    <div class="card-header border-0 pt-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">Services</span>
        <span class="text-muted mt-1 fw-semibold fs-7">
          {{ store.services.total }} Service(s)
        </span>
      </h3>

      <div class="card-toolbar">
        <a
            class="btn btn-sm btn-success me-2"
            @click="showModal('add_service_modal')"
        >
          Add Service
        </a>

        <a
            class="btn btn-sm btn-light-primary"
            @click="store.getServices()"
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

            <th class="min-w-150px">SERVICE</th>
            <th class="min-w-200px">TITLE</th>
            <th class="min-w-120px">CREATED AT</th>
            <th class="min-w-100px text-end">Actions</th>
          </tr>
          </thead>

          <tbody>
          <tr
              v-for="service in store.services.data"
              :key="service.id"
          >
            <td>
              <div class="form-check form-check-sm form-check-custom form-check-solid">
                <input
                    class="form-check-input"
                    type="checkbox"
                    :value="service.id"
                    v-model="store.checkedServiceRows"
                />
              </div>
            </td>

            <td class="fw-bold text-gray-700 fs-7">
              {{ service.service }}
            </td>

            <td class="text-gray-700 fs-7">
              {{ service.title }}
            </td>

            <td class="text-gray-600 fs-8">
              {{ service.created_at }}
            </td>

            <td class="text-end">
              <el-dropdown>
                <a class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm">
                  <KTIcon icon-name="category" icon-class="fs-3" />
                </a>

                <template #dropdown>
                  <el-dropdown-menu class="p-3">
                    <el-dropdown-item
                        @click="store.deleteSelected([service.id])"
                    >
                      Delete
                    </el-dropdown-item>

                    <el-dropdown-item
                        @click="editClicked(service)"
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

        <el-pagination
            :current-page="store.services.current_page"
            :page-size="configStore.pagination?.each_page?.default || 10"
            layout="prev, pager, next"
            :total="store.services.total"
            @current-change="page => store.getServices(page)"
        />
      </div>
    </div>
  </div>

  <add-service-modal />
  <edit-service-modal :service-data="selectedService"/>

</template>

<script lang="ts" setup>
import { onMounted, ref } from "vue";
import { showModal } from "@/core/helpers/modal";
import { useAppConfigStore } from "@/stores/AppConfig";
import { useServiceStore } from "@/stores/Service";
import AddServiceModal from "@/components/modals/service/AddServiceModal.vue";
import EditServiceModal from "@/components/modals/service/EditServiceModal.vue";

const store = useServiceStore();
const configStore = useAppConfigStore();
const selectedService = ref(null);

onMounted(() => store.getServices());

const editClicked = (service) => {
  selectedService.value = service;

  showModal("edit_service_modal");
};
</script>
