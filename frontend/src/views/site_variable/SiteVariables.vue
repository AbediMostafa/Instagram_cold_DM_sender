<template>
  <div class="d-flex flex-column flex-column-fluid">
    <!--begin::Toolbar-->
    <!--begin::Content-->
    <div id="kt_app_content" class="app-content flex-column-fluid">
      <!--begin::Content container-->
      <div id="kt_app_content_container" class="app-container container-xxl">
        <!--begin::Row-->
        <div class="row g-5 g-xl-8">
          <categories/>
          <tags/>
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
</script>
