<template>
  <div class="card">
    <!--begin::Card body-->
    <div class="card-body pt-3 px-6">
      <div class="my-0 d-flex">
        <div
          class="form-check form-check-sm form-check-custom form-check-solid my-3"
        >
          <input
            class="form-check-input widget-13-check"
            type="checkbox"
            :value="loom.id"
            v-model="store.checkedLoomRows"
          />
        </div>
      </div>

      <div class="d-flex align-items-start mb-8 justify-content-between">
        <div class="ms-2">
          <video
            :style="props.card_style"
            controls
            :src="getLoomPath(props.loom.path)"
          ></video>
        </div>
      </div>
      <div class="text-gray-700">{{ loom.original_name }}</div>
      <loom-state :state="loom.state" />
      <div class="separator separator-dashed my-5"></div>
      <div class="d-flex mt-3">
        <div class="text-muted fs-8">{{ loom.description }}</div>
      </div>
      <!--end::Info-->
    </div>
    <!--end::Card body-->
  </div>
</template>

<script setup>
import { defineProps } from "vue";
import LoomState from "@/components/loom/LoomState.vue";
import { useLoomStore } from "@/stores/Loom";

const props = defineProps(["loom", "card_style"]);
const store = useLoomStore();
const getLoomPath = (path) =>
  `${import.meta.env.VITE_APP_API_URL}/storage/${path}`;
</script>

