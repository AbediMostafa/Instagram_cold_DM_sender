<template>
  <div class="card mb-5 mb-xl-8">
    <!--begin::Header-->
    <div class="card-header border-0 pt-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">2Factor</span>
      </h3>
      <el-input
          v-model="twoFactor"
          placeholder="Enter the 2fa key here"
          class="input-with-select"
          clearable
      >
      </el-input>
    </div>
    <!--end::Header-->

    <!--begin::Body-->
  </div>
</template>

<script lang="ts" setup>
import { ref, watch} from "vue";
import {useAccountStore} from "@/stores/Account";

const accountStore = useAccountStore();
const twoFactor = ref('');


watch(twoFactor, (newSecret) => {
  accountStore.fetchOtpAndCopy(newSecret)
})
</script>
