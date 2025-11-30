<template>
  <div class="card mb-5 mb-xl-8">
    <!--begin::Header-->
    <div class="card-header border-0 pt-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">Orders</span>
        <span class="text-muted mt-1 fw-semibold fs-7">{{ store.orders.total }} Order</span>
      </h3>

      <div class="card-toolbar" v-has-any-of-these-roles="['user']">
        <!--begin::Menu-->
        <a class="btn btn-sm btn-success me-2" @click="showModal('add_order_modal')">Add Order</a>
        <a class="btn btn-sm btn-light-primary me-2" @click="store.getOrders()">Refresh</a>

        <button
            type="button"
            class="btn btn-sm btn-icon btn-color-primary btn-active-light-primary"
            data-kt-menu-trigger="click"
            data-kt-menu-placement="bottom-end"
            data-kt-menu-flip="top-end"
        >
          <KTIcon icon-name="category" icon-class="fs-2"/>
        </button>

      </div>
    </div>
    <!--end::Header-->

    <!--begin::Body-->
    <div class="card-body py-3">
      <!--begin::Table container-->
      <div class="table-responsive">
        <table
            class="table table-row-bordered table-row-gray-100 align-middle gs-0 gy-3"
            v-loading="store.is.loading"
        >
          <!--begin::Table head-->
          <thead>
          <tr class="fw-bold text-muted">
            <th class="w-25px">
              <div class="form-check form-check-sm form-check-custom form-check-solid">
                <input class="form-check-input" type="checkbox" @change="store.checkRows($event)"/>
              </div>
            </th>
            <th class="min-w-150px">CUSTOMER</th>
            <th class="min-w-120px">LINK</th>
            <th class="min-w-120px">COUNT/SENT</th>
            <th class="min-w-100px text-end">Actions</th>
          </tr>
          </thead>
          <!--end::Table head-->

          <!--begin::Table body-->
          <tbody>
          <template v-for="(order, index) in store.orders.data" :key="index">
            <tr>
              <td>
                <div class="form-check form-check-sm form-check-custom form-check-solid">
                  <input class="form-check-input widget-13-check" type="checkbox" :value="order.id"
                         v-model="store.checkedOrderRows"/>
                </div>
              </td>

              <td>
                <a class="text-gray-700 fw-bold text-hover-primary fs-7">{{ order.id }} -{{ order.customer }}</a>
                <a class="badge ms-2 badge-light-success " v-if="order.status=='Completed'">{{ order.status }}</a>
                <a class="badge ms-2 badge-light-primary" v-if="order.status=='In progress'">{{ order.status }}</a>
                <a class="badge ms-2 badge-light-warning" v-if="order.status=='Pending'">{{ order.status }}</a>
                <div v-if="order.status=='Canceled'">
                  <div class="badge ms-2 badge-light-danger" v-if="order.description">{{ order.description }}</div>
                  <a class="badge ms-2 badge-light-danger" v-else>{{ order.status }}</a>
                </div>
                <div class="text-gray-600 fw-bold text-hover-primary fs-8">{{ order.service_type }}</div>

              </td>

              <td>
                <a class="text-gray-700 fw-bold text-hover-primary fs-7" :href="order.target_link"
                   target="_blank">{{ order.target_link }}</a>
              </td>

              <td>
                <div>
                  <span class="text-gray-700 fw-bold text-hover-primary fs-7">{{ order.total_count }}</span>/
                  <span class="text-gray-700 fw-bold text-hover-primary fs-7">{{ order.completed_count }}</span>
                </div>

              </td>
              <td class="text-end">
                <el-dropdown class="p-5">
                  <a class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm">
                    <KTIcon icon-name="category" icon-class="fs-3"/>
                  </a>
                  <template #dropdown>
                    <el-dropdown-menu class="p-3">
                      <el-dropdown-item @click="store.deleteSelected([order.id])">Delete</el-dropdown-item>
                      <el-dropdown-item @click="store.finish(order.id)">Finish</el-dropdown-item>
                      <el-dropdown-item @click="store.fail(order.id)">Fail</el-dropdown-item>
                      <el-dropdown-item @click="store.reset(order.id)">Reset</el-dropdown-item>
                      <el-dropdown-item @click="store.changProcessingCommentsToFree(order.id)">Change Processing To Free</el-dropdown-item>
                      <el-dropdown-item @click="store.getOrders(store.orders.current_page, false)">Refresh
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>

              </td>

            </tr>
          </template>
          </tbody>
          <!--end::Table body-->
        </table>
        <!--end::Table-->

        <el-pagination
            :current-page="store.orders.current_page"
            :page-size="configStore.pagination?.each_page?.leads"
            layout="prev, pager, next"
            :total="store.orders.total"
            @current-change="page => store.getOrders(page)"
        />
      </div>
      <!--end::Table container-->
    </div>
    <!--begin::Body-->
  </div>
  <add-order-modals/>

</template>

<script lang="ts" setup>
import {onMounted, ref} from 'vue';
import AddOrderModals from "@/components/modals/order/AddOrderModal.vue";
import CreateLeadModal from '@/components/modals/lead/CreateLeadModal.vue';
import ExportLeadModal from "@/components/modals/lead/ExportLeadModal.vue";
import {showModal} from '@/core/helpers/modal';
import {useAppConfigStore} from '@/stores/AppConfig';
import EditLeadModal from '@/components/modals/lead/EditLeadModal.vue';
import LeadLastState from '@/components/lead/LeadLastState.vue';
import LeadDropDown from '@/components/lead/LeadDropDown.vue';
import LeadsDropDown from '@/components/lead/LeadsDropDown.vue';
import {useLeadStore} from '@/stores/Lead';
import {useTagStore} from '@/stores/Tag';
import {useCategoryStore} from '@/stores/Category';
import {useOrderStore} from "@/stores/Order";

const selectedId = ref(0);
const store = useOrderStore();
const configStore = useAppConfigStore();
const categoryStore = useCategoryStore();

// Function to handle editing a lead
const editClicked = id => {
  selectedId.value = id;
  showModal('edit_lead_modal');
};

// Fetch leads, tags, and categories on mount
onMounted(() => {
  store.getOrders();
  categoryStore.getCategories();  // Fetch all categories for the dropdown
});
</script>
