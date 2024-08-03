<template>
  <!--begin::Modal - New Target-->
  <div
      class="modal fade"
      id="upload_loom_modal"
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
            <KTIcon icon-name="cross" icon-class="fs-1"/>
          </div>
          <!--end::Close-->
        </div>
        <!--begin::Modal header-->

        <!--begin::Modal body-->
        <div class="modal-body scroll-y px-10 px-lg-15 pt-0 pb-15">
          <div class="mb-13 text-center">
            <h1 class="mb-3">Upload New Loom</h1>
          </div>

          <div class="divider"></div>
          <div class="d-flex flex-column mb-6 fv-row">
            <!--begin::Label-->
            <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
              <span>Description</span>
            </label>
            <!--end::Label-->
            <el-form-item prop="ip">
              <el-input
                  v-model="description"
                  :rows="4"
                  type="textarea"
                  placeholder="Loom Description"
              />
            </el-form-item>
          </div>

          <el-upload
              class="upload-demo"
              :action="uploadServerUrl"
              :on-success="handleSuccess"
              :on-error="handleError"
          >
            <!--            :on-error="()=>ElMessage.error('Problem uploading loom to the server')"-->

            <template #trigger>
              <el-button type="primary">select file</el-button>
            </template>
          </el-upload>
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

<script setup lang="ts">
import {computed, ref, defineProps, defineEmits} from "vue";
import {ElMessage, ElMessageBox} from "element-plus";
import {hideModal} from "@/core/helpers/modal";


const props = defineProps(['account_id', 'lead_id', "thread_id"])
const emit = defineEmits(['getMessages']);

const description = ref("");

const uploadServerUrl = computed(() => {
  const url = `/command/create-upload-loom?description=${description.value}&account_id=${props.account_id}&lead_id=${props.lead_id}&thread_id=${props.thread_id}`;

  return import.meta.env.VITE_APP_API_URL + url;
});

const handleError = (error) => {
  if (error.status === 422) {
    [
      "A file with the same name already exists.",
      "File storage failed",
      "Database operation failed",
    ].forEach((errorMsg) => {
      if (error.message.includes(errorMsg)) {
        ElMessageBox.confirm(errorMsg, "Error", {
          confirmButtonText: "Ok",
          dangerouslyUseHTMLString: true,
          type: "error",
          showCancelButton: false,
          center: true,
        });
      }
    });
  }
  description.value = "";
  console.log(error.message);
};

const handleSuccess = () => {
  ElMessage.success("Loom uploaded successfully.");
  description.value = "";
  emit("getMessages");
  hideModal("upload_loom_modal");
};
</script>

