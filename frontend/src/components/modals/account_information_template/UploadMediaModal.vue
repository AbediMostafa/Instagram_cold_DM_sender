<template>
  <!--begin::Modal - New Target-->
  <div
    class="modal fade"
    id="upload_media_modal"
    tabindex="-1"
    aria-hidden="true"
  >
    <!--begin::Modal dialog-->
    <div class="modal-dialog modal-dialog-centered mw-650px">
      <!--begin::Modal content-->
      <div class="modal-content rounded">
        <!--begin::Modal header-->
        <div class="modal-header pb-0 border-0 justify-content-end">
          <!--begin::Close-->
          <div
            class="btn btn-sm btn-icon btn-active-color-primary"
            data-bs-dismiss="modal"
          >
            <KTIcon icon-name="cross" icon-class="fs-1" />
          </div>
          <!--end::Close-->
        </div>
        <!--begin::Modal header-->

        <!--begin::Modal body-->
        <div class="modal-body scroll-y px-10 px-lg-15 pt-0 pb-15">
          <div class="mb-13 text-center">
            <h1 class="mb-3">Upload New Template</h1>
          </div>

          <div class="divider"></div>
          <div v-if="!useAsAvatarModel" class="d-flex flex-column mb-6 fv-row">
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

          <el-upload
            ref="uploadRef"
            class="upload-demo"
            :action="uploadServerUrl"
            :auto-upload="true"
            :on-success="handleSuccess"
            :on-error="handleError"
          >
            <template #trigger>
              <el-button type="primary">select file</el-button>
            </template>

            <template #tip>
              <div
                class="notice d-flex bg-light-warning rounded border-warning border border-dashed mt-7 p-3"
              >
                <i class="ki-duotone ki-information-5 fs-2tx text-warning me-4"
                  ><span class="path1"></span><span class="path2"></span
                  ><span class="path3"></span></i
                ><!--begin::Wrapper-->
                <div class="d-flex flex-stack flex-grow-1">
                  <!--begin::Content-->
                  <div class="fw-semibold">
                    <div class="fs-6 text-gray-600">
                      Only image/video files allowed
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </el-upload>

          <div class="fv-row my-7">
            <!--begin::Wrapper-->
            <div class="d-flex flex-stack">
              <!--begin::Label-->
              <div class="me-5">
                <!--begin::Label-->
                <label class="fs-6 fw-semibold">Use the image as Avatar?</label>
                <!--end::Label-->

                <!--begin::Input-->
                <div class="fs-7 fw-semibold text-muted">
                  If not used as an avatar, the image will be used as a post
                  image, and videos will be used as video posts
                </div>
                <!--end::Input-->
              </div>

              <label
                class="form-check form-switch form-check-custom form-check-solid"
              >
                <!--begin::Input-->
                <input
                  class="form-check-input"
                  name="billing"
                  type="checkbox"
                  value="1"
                  id="use_as_avatar_checkbox"
                  v-model="useAsAvatarModel"
                />
                <!--end::Input-->

                <!--begin::Label-->
                <span
                  class="form-check-label fw-semibold text-muted"
                  for="use_as_avatar_checkbox"
                >
                  Yes
                </span>
                <!--end::Label-->
              </label>
            </div>
            <!--begin::Wrapper-->
          </div>

          <!--begin:Form-->
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
.el-select {
  width: 100%;
}

.el-date-editor.el-input,
.el-date-editor.el-input__inner {
  width: 100%;
}
</style>

<script lang="ts">
import { computed, defineComponent, ref } from "vue";
import { hideModal } from "@/core/helpers/modal";
import { useTemplateStore } from "@/stores/Template";
import { ElMessage } from "element-plus";

export default defineComponent({
  name: "upload_media_modal",
  setup() {
    const uploadRef = ref();
    const caption = ref("");
    const useAsAvatarModel = ref();
    const store = useTemplateStore();

    const uploadServerUrl = computed(() => {
      const encodedCaption = encodeURIComponent(caption.value);

      const url = useAsAvatarModel.value
        ? `/template/upload-file?use-as-avatar=1&caption=${encodedCaption}`
        : `/template/upload-file?caption=${encodedCaption}`;

      return import.meta.env.VITE_APP_API_URL + url;
    });
    const handleSuccess = () => store.getTemplates();
    const handleError = () =>
      ElMessage.error("Problem uploading file to the server");

    return {
      caption,
      uploadRef,
      hideModal,
      uploadServerUrl,
      handleSuccess,
      handleError,
      useAsAvatarModel,
    };
  },
});
</script>

<style lang="scss">
.override-styles {
  z-index: 99999 !important;
  pointer-events: initial;
}
</style>
