<template>
  <div class="card">
    <!--begin::Card body-->
    <div class="card-body px-6">
      <div class="d-flex">
        <div
            class="form-check form-check-sm form-check-custom form-check-solid"
        >
          <input
              class="form-check-input widget-13-check"
              type="checkbox"
              :value="template.id"
              v-model="store.checkedTemplateRows"
          />
        </div>
      </div>

      <div>
        <div>
          {{ template.text }}
        </div>

        <span class="text-muted fw-semibold text-muted d-block fs-8">{{ template.caption }}</span>
        <span class="badge badge-light-success">name username pair</span>
      </div>

    </div>
  </div>
</template>

<script setup>
import {defineProps} from "vue";
import {useTemplateStore} from "@/stores/Template";
import {getImageSrc} from "@/core/helpers/helper";

const props = defineProps(["template", "card_style"]);
const store = useTemplateStore();
</script>

<style scoped>
.image-wrapper {
  width: 100%; /* Optional: Ensures the wrapper spans the column width */
  display: flex;
  justify-content: center;
  align-items: center;
}

.template-image {
  width: 200px; /* Set your desired fixed width */
  height: 200px; /* Set your desired fixed height */
  object-fit: cover; /* Ensures the image is cropped to fill the dimensions */
  border-radius: 8px; /* Optional: Rounds the corners of the image */
}
</style>
