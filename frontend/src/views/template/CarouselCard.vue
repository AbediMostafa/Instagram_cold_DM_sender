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
              :value="carousel[0].carousel_id"
              v-model="store.checkedTemplateRows"
          />
        </div>
      </div>

      <div class="image-wrapper">
          <el-carousel
              :autoplay="false"
              :trigger="'click'"
              style="height: 215px"
              indicator-position="none"
          >
            <el-carousel-item v-for="item in carousel" :key="item">
              <img
                  class="template-image"
                  :src="getImageSrc(item.text)"
                  alt="Template"
              />
            </el-carousel-item>
          </el-carousel>
      </div>
      <div
          class="text-gray-700 fs-8">{{cutMorThanNCharacters(carousel[0].caption, 200) }}</div>

      <span class="badge badge-light-success">Carousel</span>
      <span class="badge badge-light-info">{{ carousel[0]?.category?.title }}</span>
    </div>
  </div>
</template>

<script setup>
import {defineProps} from "vue";
import {useTemplateStore} from "@/stores/Template";
import {getImageSrc} from "@/core/helpers/helper";
import {cutMorThanNCharacters} from "@/core/helpers/helper";

const props = defineProps(["carousel", "card_style"]);
const store = useTemplateStore();
</script>

<style scoped>
.image-wrapper {
  text-align: center;
  width: 100%; /* Optional: Ensures the wrapper spans the column width */
}

.template-image {
  width: 200px; /* Set your desired fixed width */
  height: 200px; /* Set your desired fixed height */
  object-fit: cover; /* Ensures the image is cropped to fill the dimensions */
  border-radius: 8px; /* Optional: Rounds the corners of the image */
}
</style>
