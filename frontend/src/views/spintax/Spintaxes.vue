<template>
  <div class="card mb-5 mb-xl-8">
    <!--begin::Header-->
    <div class="card-header border-0 pt-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">Spintaxes</span>
      </h3>
      <div class="card-toolbar">
        <!--begin::Menu-->
        <div class="me-2">
          <a
              class="btn btn-sm btn-success"
              @click="showModal('create_spintax_modal')"
          >Add Spintax</a
          >
        </div>
        <div class="me-2">
          <a
              class="btn btn-sm btn-light-primary"
              @click="store.getSpintaxes"
          >Refresh</a
          >
        </div>

        <!-- Other toolbar buttons can go here -->
      </div>
    </div>
    <!--end::Header-->

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
            <td>
              <div class="d-flex align-items-center">
                <div class="col-3">NAME</div>
                <div class="col-2">CATEGORY</div>
                <div class="col-6">TEXT</div>
                <div class="col-1 text-end">ACTIONS</div>
              </div>
            </td>
          </tr>
          </thead>
          <!--begin::Table body-->
          <tbody>
          <tr v-for="(spintax, index) in store.spintaxes.data" :key="index">
            <td>
              <div class="d-flex align-items-center w-100">
                <div class="col-3 p-2">
                  <a class="text-gray-900 fw-bold text-hover-primary fs-6">
                    {{ spintax.name }}
                  </a>
                  <div>
                    <span :class="`badge ${store.getTypeClass(spintax.type)} mt-1`">{{ spintax.type }}</span>
                  </div>
                </div>
                <div class="col-2">
                  <div class="text-gray-700 fs-7 p-2">{{ spintax.category?.title }}</div>
                </div>
                <div class="col-6">
                  <a class="text-gray-700 fs-7">
                    {{
                      spintax.text.length > 300
                          ? spintax.text.substring(0, 300) + " ..."
                          : spintax.text
                    }}
                  </a>
                </div>
                <div class="col-1 text-end">
                  <spintax-drop-down :id="spintax.id"/>
                </div>
              </div>
            </td>
          </tr>
          </tbody>
          <!--end::Table body-->
        </table>
        <!--end::Table-->
        <el-pagination
            :current-page="store.spintaxes.current_page"
            :page-size="configStore.pagination?.each_page?.spintaxes"
            layout="prev, pager, next"
            :total="store.spintaxes.total"
            @current-change="(page) => store.getSpintaxes(page)"
        />
      </div>
      <!--end::Table container-->
    </div>
    <!--begin::Body-->
  </div>
  <create-spintax-modal/>
  <view-spintax-modal/>
</template>

<script lang="ts" setup>
import {onMounted, ref} from "vue";
import CreateSpintaxModal from "@/components/modals/spintax/CreateSpintaxModal.vue"; // Import the CreateSpintaxModal component
import {showModal} from "@/core/helpers/modal";
import {useAppConfigStore} from "@/stores/AppConfig";
import SpintaxDropDown from "@/components/spintax/SpintaxDropDown.vue";
import {useSpintaxStore} from "@/stores/Spintax";
import ViewSpintaxModal from "@/components/modals/spintax/ViewSpintaxModal.vue";

const configStore = useAppConfigStore();
const store = useSpintaxStore();
onMounted(store.getSpintaxes);
</script>

<style>
.table .col-2,
.table .col-6 {
  display: inline-block;
}
</style>
