<template>
  <!--begin::Pricing-->
  <div class="card card-flush pt-3 mb-5 mb-lg-10" v-loading="loading">
    <!--begin::Card header-->
    <div class="card-header">
      <!--begin::Card title-->
      <div class="card-title">
        <h2 class="fw-bold">Dm Statistics</h2>
      </div>
      <div class="card-toolbar">
        <button
            type="button"
            class="btn btn-light-primary"
            @click="getDailyDmStatistics(dailyStatistics.current_page)"
        >
          Refresh
        </button>
      </div>
    </div>
    <!--end::Card header-->

    <!--begin::Card body-->
    <div class="card-body pt-0">
      <!--begin::Table wrapper-->
      <div class="table-responsive">
        <!--begin::Table-->
        <table
            class="table align-middle table-row-dashed fs-6 fw-semibold gy-4"
            id="kt_subscription_products_table"
        >
          <!--begin::Table head-->
          <thead>
          <tr class="text-start text-muted fw-bold fs-7 text-uppercase gs-0">
            <th class="min-w-100px">date</th>
            <th class="min-w-100px">cold dms</th>
            <th class="min-w-120px">first follow ups</th>
            <th class="min-w-150px">second follow ups</th>
            <th class="min-w-150px">third follow ups</th>
            <th class="min-w-130px">looms sent</th>
            <th class="min-w-130px">calls booked</th>
            <th class="min-w-150px">active accounts</th>
          </tr>
          </thead>
          <!--end::Table head-->

          <!--begin::Table body-->
          <tbody class="text-gray-600">
          <tr
              v-for="statistic in dailyStatistics.data"
              :key="statistic.date"
              class="odd"
          >
            <td>{{ statistic.date }}</td>
            <td>
              <div class="fs-4">{{ statistic.total_cold_dms }}</div>
              <div>
                <span class="badge badge-light-success fs-base me-1">
                  <i class="ki-duotone ki-arrow-up-right me-1 text-success"><span class="path1"></span><span class="path2"></span></i>
                  {{ statistic.successful_cold_dms }}</span>
                <span class="badge badge-light-danger fs-base">
                  <i class="ki-duotone ki-arrow-down-right me-1 text-danger"><span class="path1"></span><span class="path2"></span></i>
                  {{ statistic.failed_cold_dms }}</span>
              </div>
            </td>
            <td>
              <div class="fs-4">{{ statistic.total_first_follow_ups }}</div>
              <div>
                <span class="badge badge-light-success fs-base me-1">
                  <i class="ki-duotone ki-arrow-up-right me-1 text-success"><span class="path1"></span><span class="path2"></span></i>
                  {{ statistic.successful_first_follow_ups }}</span>
                <span class="badge badge-light-danger fs-base">
                  <i class="ki-duotone ki-arrow-down-right me-1 text-danger"><span class="path1"></span><span class="path2"></span></i>
                  {{ statistic.failed_first_follow_ups }}</span>
              </div>
            </td>
            <td class="fs-4">{{ statistic.second_follow_ups }}</td>
            <td class="fs-4">{{ statistic.third_follow_ups }}</td>
            <td>{{ statistic.looms_sent_out }}</td>
            <td>{{ statistic.call_booked }}</td>
            <td>{{ statistic.active_accounts }}</td>
          </tr>
          </tbody>
          <!--end::Table body-->
        </table>
        <!--end::Table-->
      </div>
      <!--end::Table wrapper-->
    </div>
    <!--end::Card body-->
    <el-pagination
        :current-page="dailyStatistics.current_page"
        :page-size="configStore.pagination?.each_page?.daily_dm_statistics"
        layout="prev, pager, next"
        :total="dailyStatistics.total"
        @current-change="(page) => getDailyDmStatistics(page)"
    />
  </div>

  <!--end::Pricing-->
</template>

<script lang="ts" setup>
import {onMounted, ref} from "vue";
import ApiService from "@/core/services/ApiService";
import {useAppConfigStore} from "@/stores/AppConfig";
import {useUserStore} from "@/stores/User";

const configStore = useAppConfigStore();
const loading = ref(false);
const dailyStatistics = ref({
  data: [],
  current_page: 1,
  total: 0,
});

const store = useUserStore()

const getDailyDmStatistics = (page = 1) => {
  loading.value = true;

  ApiService.post("dashboard/dm-statistics", {page})
      .then((response) => {
        dailyStatistics.value.data = response.data.data;
        dailyStatistics.value.total = response.data.total;
        dailyStatistics.value.current_page = response.data.current_page

      })
      .finally(() => (loading.value = false));
};

onMounted(getDailyDmStatistics);
</script>
