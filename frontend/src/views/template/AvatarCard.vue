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
              :value="template.id"
              v-model="store.checkedTemplateRows"
          />
        </div>
      </div>

      <div class="d-flex align-items-start mb-8 justify-content-between">
        <div class="ms-2 image-wrapper">
          <img
              class="template-image"
              :src="getImageSrc(template.text)"
              alt="Template"
          />
        </div>
      </div>
      <span class="badge badge-light-success">{{ template.type }}</span>
      <span class="badge badge-light-primary mt-1 ms-1"
            v-for="tag in template.tags" :key="tag.id"
      >{{ tag.title }}</span>

    </div>
  </div>
</template>

<script setup>
import {defineProps} from "vue";
import {useTemplateStore} from "@/stores/Template";
import {getImageSrc} from "@/core/helpers/helper";
import {cutMorThanNCharacters} from "@/core/helpers/helper";

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
