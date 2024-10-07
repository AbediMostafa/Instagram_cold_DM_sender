<template>
  <!-- Modal Structure -->
  <div
      class="modal fade"
      id="upload_media_modal"
      tabindex="-1"
      aria-hidden="true"
  >
    <div class="modal-dialog modal-dialog-centered mw-650px">
      <div class="modal-content rounded">
        <div class="modal-header pb-0 border-0 justify-content-end">
          <div
              class="btn btn-sm btn-icon btn-active-color-primary"
              data-bs-dismiss="modal"
          >
            <KTIcon icon-name="cross" icon-class="fs-1"/>
          </div>
        </div>
        <div class="modal-body scroll-y px-10 px-lg-15 pt-0 pb-15">
          <div class="mb-13 text-center">
            <h1 class="mb-3">Upload New Template</h1>
          </div>
          <div class="divider"></div>
          <el-upload
              class="mb-5"
              ref="uploadRef"
              :auto-upload="false"
              :multiple="mediaType === 'carousel' || mediaType === 'video-post'"
              :on-success="handleSuccess"
              :http-request="uploadFiles"
          >
            <template #trigger>
              <el-button type="primary" @click="uploadRef.clearFiles()"
              >select file
              </el-button
              >
            </template>
          </el-upload>

          <div
              v-if="mediaType !== 'avatar'"
              class="d-flex flex-column mb-6 fv-row"
          >
            <!--begin::Label-->
            <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
              <span class="required">Caption</span>
            </label>
            <!--end::Label-->

            <el-form-item prop="ip">
              <el-input
                  v-model="caption"
                  :rows="8"
                  type="textarea"
                  placeholder="Caption"
                  name="bunchInsert"
              />
            </el-form-item>
          </div>

          <!-- Media Type Selection -->
          <div class="d-flex flex-column mb-10 fv-row">
            <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
              <span class="required">Media Type</span>
            </label>
            <el-radio-group v-model="mediaType" size="default">
              <el-radio-button
                  v-for="type in mediaTypes"
                  :key="type.value"
                  :value="type.value"
                  :label="type.label"
              >
                {{ type.value }}
              </el-radio-button>
            </el-radio-group>
          </div>

          <!-- Theme Selection for Carousel -->
          <div
              class="d-flex flex-column mb-10 fv-row"
              v-if="mediaType === 'carousel'"
          >
            <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
              <span class="required">Theme</span>
            </label>
            <el-radio-group v-model="theme" size="default">
              <el-radio-button
                  v-for="theme in themes"
                  :key="theme.value"
                  :value="theme.value"
                  :label="theme.label"
              >
                {{ theme.value }}
              </el-radio-button>
            </el-radio-group>
          </div>

          <div class="d-flex flex-column mb-8 fv-row">
            <!--begin::Label-->
            <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
              <span class="required">Category</span>
              <span class="required">{{ category }}</span>
            </label>
            <!--end::Label-->
            <el-select
                v-if="categoryStore.categories.data.length"
                v-model="category" placeholder="Select">
              <el-option
                  v-for="item in categoryStore.categories.data"
                  :key="item.id"
                  :label="item.title"
                  :value="item.id"
              />
            </el-select>

          </div>


          <!-- Upload Button -->
          <el-button type="success" @click="uploadFile">Upload</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {ref, computed, onMounted} from "vue";
import {hideModal} from "@/core/helpers/modal";
import {useTemplateStore} from "@/stores/Template";
import {ElMessageBox} from "element-plus";
import {useCategoryStore} from "@/stores/Category";

const uploadRef = ref();
const category = ref('');
const caption = ref("");
const mediaType = ref("avatar");
const mediaTypes = ref([
  {value: "profile image", label: "avatar"},
  {value: "post image", label: "image-post"},
  {value: "carousel", label: "carousel"},
  {value: "video", label: "video-post"},
]);

const theme = ref("yellow");
const themes = ref([
  {value: "yellow", label: "yellow"},
  {value: "red", label: "red"},
  {value: "purple", label: "purple"},
  {value: "orange", label: "orange"},
  {value: "green", label: "green"},
  {value: "blue", label: "blue"},
  {value: "aquamarine", label: "aquamarine"},
]);

const carouselId = ref("");
const store = useTemplateStore();
const categoryStore = useCategoryStore()

const uploadServerUrl = computed(() => `${import.meta.env.VITE_APP_API_URL}/template/upload-file`);

const handleSuccess = store.getTemplates;

const uploadFile = () => {
  if (mediaType.value === "carousel" || mediaType.value === "video-post") {
    carouselId.value =
        Date.now().toString(36) + Math.random().toString(36).substring(2);
  }
  uploadRef.value.submit();
};

const uploadFiles = async ({file, files}) => {
  const formData = new FormData();
  formData.append("caption", caption.value);
  // formData.append("caption", encodeURIComponent(caption.value));
  formData.append("carouselId", carouselId.value);
  formData.append("mediaType", mediaType.value);
  formData.append("theme", theme.value);
  formData.append("category", category.value);
  formData.append("uid", file.uid);
  formData.append("file", file);

  try {
    const response = await fetch(uploadServerUrl.value, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      // If the status is not 2xx, throw an error with the response
      const errorData = await response.json(); // Parse the JSON response body

      if (response.status === 422) {
        await ElMessageBox.confirm(errorData.message, "Error", {
          confirmButtonText: "Ok",
          dangerouslyUseHTMLString: true,
          type: "error",
          showCancelButton: false,
          center: true,
        });
      }
    }

    // If the request was successful, handle success
    handleSuccess();
    hideModal("upload_media_modal");
  } catch (error) {
  }
};

onMounted(categoryStore.getCategories)

</script>

<style lang="scss">
.override-styles {
  z-index: 99999 !important;
  pointer-events: initial;
}

.el-select {
  width: 100%;
}

.el-date-editor.el-input,
.el-date-editor.el-input__inner {
  width: 100%;
}

.el-upload {
  display: block;
}
</style>
