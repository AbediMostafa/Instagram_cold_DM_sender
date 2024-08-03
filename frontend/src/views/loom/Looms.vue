<template>
  <!--begin::Search vertical-->
  <div>
    <!--begin::Aside-->

    <div class="flex-lg-row-fluid">
      <div class="d-flex flex-wrap flex-stack pb-7">
        <!--begin::Title-->
        <div class="d-flex flex-wrap align-items-center my-1">
          <span class="text-gray-800 fs-4">
            {{ store.looms.data.length }}
            <span class="text-gray-400 fs-5">Looms</span>
          </span>
        </div>
        <!--begin::Controls-->
        <div class="d-flex flex-wrap">
          <!--begin::Tab nav-->
          <ul class="nav nav-pills mb-2 mb-sm-0">
            <li class="nav-item m-0 me-4">
              <a
                class="btn btn-sm btn-danger ms-2"
                @click="store.deleteSelected(store.checkedLoomRows)"
                >Delete Selected</a
              >
            </li>
          </ul>
          <!--end::Tab nav-->
        </div>
        <!--end::Controls-->
      </div>

      <div class="tab-content">
        <div>
          <!--begin::Row-->
          <div v-loading="store.is.loading">
            <div class="row">
              <!--begin::Col-->
              <div
                class="col-md-3 col-xl-3 col-xxl-3 mb-6"
                v-for="loom in store.looms.data"
                :key="loom.id"
              >
                <loom-card
                  card_style="width: 100%; height: auto; object-fit: cover"
                  :loom="loom"
                />
              </div>
              <!--end::Col-->
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import LoomCard from "@/components/loom/LoomCard.vue";
import { onMounted } from "vue";
import { useLoomStore } from "@/stores/Loom";

const store = useLoomStore();

onMounted(store.getLooms);
</script>
