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
            <th class="min-w-150px">successful cold dms</th>
            <th class="min-w-150px">failed cold dms</th>
            <th class="min-w-150px">dm follow ups</th>
            <th class="min-w-150px">loom follow ups</th>
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
            <td>{{ statistic.total_cold_dms }}</td>
            <td>{{ statistic.successful_cold_dms }}</td>
            <td>{{ statistic.failed_cold_dms }}</td>
            <td>{{ statistic.successful_dm_follow_ups }}</td>
            <td>{{ statistic.successful_loom_follow_ups }}</td>
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

const configStore = useAppConfigStore();
const loading = ref(false);
const dailyStatistics = ref({
  data: [],
  current_page: 1,
  total: 0,
});

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
