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
              :multiple=true
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

          <div class="d-flex flex-column mb-8 fv-row">
            <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
              Tags
            </label>

            <el-form-item prop="selectedTags">
              <el-select
                  v-model="tags"
                  multiple
                  filterable
                  remote
                  clearable
                  placeholder="Search for tags"
                  :remote-method="tagStore.fetchTags"
                  :loading="tagStore.is.searching"
              >
                <el-option
                    v-for="tag in tagStore.searchedTags"
                    :key="tag.id"
                    :label="tag.title"
                    :value="tag.id"
                />
              </el-select>
            </el-form-item>
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
import {useTagStore} from "@/stores/Tag";

const uploadRef = ref();
const category = ref('');
const caption = ref("");
const tags = ref([]);
const mediaType = ref("avatar");
const tagStore = useTagStore()

const mediaTypes = ref([
  {value: "profile image", label: "avatar"},
  {value: "post image", label: "image-post"},
  {value: "carousel", label: "carousel"},
  {value: "video", label: "video-post"},
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
  formData.append("category", category.value);
  formData.append("uid", file.uid);
  formData.append("file", file);
  tags.value.forEach((tagId) => {
    formData.append('tags[]', tagId);
  });

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
