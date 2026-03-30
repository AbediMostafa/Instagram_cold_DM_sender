<template>
  <div class="card mb-5 mb-xl-8">
    <!--begin::Header-->
    <div class="card-header border-0 pt-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">Leads</span>
        <span class="text-muted mt-1 fw-semibold fs-7">{{ store.leads.total }} leads</span>
      </h3>

      <div class="card-toolbar" v-has-any-of-these-roles="['user']">
        <!--begin::Menu-->
        <a class="btn btn-sm btn-success me-2" @click="showModal('create_lead_modal')">Add Lead</a>
        <a class="btn btn-sm btn-light-success me-2" @click="showModal('export_leads_modal')">Get Lead</a>
        <a class="btn btn-sm btn-light-primary me-2" @click="store.getLeads()">Refresh</a>

        <button
            type="button"
            class="btn btn-sm btn-icon btn-color-primary btn-active-light-primary"
            data-kt-menu-trigger="click"
            data-kt-menu-placement="bottom-end"
            data-kt-menu-flip="top-end"
        >
          <KTIcon icon-name="category" icon-class="fs-2"/>
        </button>

          <leads-drop-down/>
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
            <th class="min-w-150px">USERNAME</th>
            <th class="min-w-120px">TAGS</th>
            <th class="min-w-120px">CATEGORY</th>
            <th class="min-w-120px">USER</th>
            <th class="min-w-120px">ACCOUNT</th>
            <th class="min-w-100px text-end">Actions</th>
          </tr>
          </thead>
          <!--end::Table head-->

          <!--begin::Table body-->
          <tbody>
          <template v-for="(lead, index) in store.leads.data" :key="index">
            <tr>
              <td>
                <div class="form-check form-check-sm form-check-custom form-check-solid">
                  <input class="form-check-input widget-13-check" type="checkbox" :value="lead.id"
                         v-model="store.checkedLeadRows"/>
                </div>
              </td>

              <td>
                  <a class="text-gray-700 fw-bold text-hover-primary fs-7"
                     @click="copyToClipboard(lead.username)"
                  >{{ lead.username }}</a>
                  <lead-last-state :state="lead.last_state"/>
              </td>

              <td>
                <span class="badge ms-2 badge-light-success" v-for="tag in lead.tags">{{ tag.title }}</span>
              </td>

              <td>
                <a v-if="lead.category" class="text-gray-700 fw-bold text-hover-primary fs-7">{{
                    lead.category.title
                  }}</a>
              </td>

              <td>
                <div v-if="lead.user">
                  <a class="text-gray-700 fw-bold text-hover-primary fs-7">{{ lead.user.name }}</a><br/>
                  <div  class="badge ms-2 badge-light-info">{{ lead.user.email }}</div>
                </div>

              </td>
              <td>
                <a v-if="lead.account" class="text-gray-700 fw-bold text-hover-primary fs-7">{{
                    lead.account.username
                  }}</a>
              </td>

              <td class="text-end" v-has-any-of-these-roles="['user']">
                <lead-drop-down @editClicked="editClicked(lead.id)" :lead="lead"/>
              </td>
            </tr>
          </template>
          </tbody>
          <!--end::Table body-->
        </table>
        <!--end::Table-->

        <el-pagination
            :current-page="store.leads.current_page"
            :page-size="configStore.pagination?.each_page?.leads"
            layout="prev, pager, next"
            :total="store.leads.total"
            @current-change="page => store.getLeads(page)"
        />
      </div>
      <!--end::Table container-->
    </div>
    <!--begin::Body-->
  </div>

  <create-lead-modal/>
  <export-lead-modal/>
  <edit-lead-modal :id="selectedId"/>
</template>

<script lang="ts" setup>
import {onMounted, ref} from 'vue';
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
import {copyToClipboard} from "@/core/helpers/helper";


const selectedId = ref(0);
const store = useLeadStore();
const configStore = useAppConfigStore();
const categoryStore = useCategoryStore();

// Function to handle editing a lead
const editClicked = id => {
  selectedId.value = id;
  showModal('edit_lead_modal');
};

// Fetch leads, tags, and categories on mount
onMounted(() => {
  store.getLeads();
  categoryStore.getCategories();  // Fetch all categories for the dropdown
});
</script>
