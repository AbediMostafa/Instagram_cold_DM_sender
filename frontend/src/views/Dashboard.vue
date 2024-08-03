<template>
  <!--begin::Layout-->
  <div class="d-flex flex-column flex-lg-row">
    <div class="flex-lg-row-fluid me-lg-15 order-2 order-lg-1 mb-10 mb-lg-0">
      <daily-dm-statistics />
<!--      <active-accounts />-->
    </div>
  </div>
</template>

<script lang="ts" setup>
import DailyDmStatistics from "@/views/dashboard/DailyDmStatistics.vue";
import ActiveAccounts from "@/views/dashboard/ActiveAccounts.vue";
</script>
