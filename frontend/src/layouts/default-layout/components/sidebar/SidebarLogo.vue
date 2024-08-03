<template>
  <!--begin::Logo-->
  <div class="d-flex justify-content-center app-sidebar-logo px-6" id="kt_app_sidebar_logo">
    <!--begin::Logo image-->
    <router-link to="/">
      <img src="/media/logos/logo.webp" class="rounded w-55px">
    </router-link>
    <!--end::Logo image-->
    <!--begin::Sidebar toggle-->
    <div
      v-if="sidebarToggleDisplay"
      ref="toggleRef"
      id="kt_app_sidebar_toggle"
      class="app-sidebar-toggle btn btn-icon btn-shadow btn-sm btn-color-muted btn-active-color-primary h-30px w-30px position-absolute top-50 start-100 translate-middle rotate"
      data-kt-toggle="true"
      data-kt-toggle-state="active"
      data-kt-toggle-target="body"
      data-kt-toggle-name="app-sidebar-minimize"
    >
      <KTIcon icon-name="black-left-line" icon-class="fs-3 rotate-180 ms-1" />
    </div>
    <!--end::Sidebar toggle-->
  </div>
  <!--end::Logo-->
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ToggleComponent } from "@/assets/ts/components";
import { getAssetPath } from "@/core/helpers/assets";
import {
  layout,
  sidebarToggleDisplay,
  themeMode,
} from "@/layouts/default-layout/config/helper";

interface IProps {
  sidebarRef: HTMLElement | null;
}

const props = defineProps<IProps>();

const toggleRef = ref<HTMLFormElement | null>(null);

onMounted(() => {
  setTimeout(() => {
    const toggleObj = ToggleComponent.getInstance(
      toggleRef.value!
    ) as ToggleComponent | null;

    if (toggleObj === null) {
      return;
    }

    // Add a class to prevent sidebar hover effect after toggle click
    toggleObj.on("kt.toggle.change", function () {
      // Set animation state
      props.sidebarRef?.classList.add("animating");

      // Wait till animation finishes
      setTimeout(function () {
        // Remove animation state
        props.sidebarRef?.classList.remove("animating");
      }, 300);
    });
  }, 1);
});
</script>
