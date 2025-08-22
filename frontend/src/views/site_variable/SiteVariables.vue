<template>
  <div class="d-flex flex-column flex-column-fluid">
    <!--begin::Toolbar-->
    <!--begin::Content-->
    <div id="kt_app_content" class="app-content flex-column-fluid">
      <!--begin::Content container-->
      <div id="kt_app_content_container" class="app-container container-xxl">
        <!--begin::Row-->
        <div class="row g-5 g-xl-8">
          <el-input
              v-model="twoFactor"
              placeholder="Enter the 2fa key here"
              class="input-with-select"
              clearable
          >
          </el-input>
          <categories/>
          <tags/>
          <hashtags/>
          <lead-source/>
          <dm-post/>
        </div>
        <!--end::Row-->
      </div>
      <!--end::Content container-->
    </div>
    <!--end::Content-->
  </div>

</template>

<script lang="ts" setup>
import Categories from "@/views/site_variable/Categories.vue";
import Tags from "@/views/site_variable/Tags.vue";
import Hashtags from "@/views/site_variable/Hashtags.vue";
import LeadSource from "@/views/site_variable/LeadSource.vue";
import DmPost from "@/views/site_variable/DmPost.vue";
import {useAccountStore} from "@/stores/Account";
import {ref, watch} from "vue";

const accountStore = useAccountStore();
const twoFactor = ref('');


watch(twoFactor, (newSecret) => {
  accountStore.fetchOtpAndCopy(newSecret)
})
</script>
