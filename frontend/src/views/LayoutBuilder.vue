<template>
  <!--begin::Layout Builder Notice-->

  <div class="card mb-10">
    <div class="card-body">
      <!-- General Settings Section -->
      <div class="form-group mb-8">
        <label class="fs-6 fw-semibold">General Settings</label>

        <label class="form-check form-switch form-check-custom form-check-solid">

          <span class="text-gray-700 fw-bold text-nowrap me-6">Turn on critical mode</span>
          <input
              class="form-check-input"
              type="checkbox"
              v-model="settingsData.critical_only_mode"
          />
        </label>


      </div>

      <!-- Proxy Type Section -->
      <div class="form-group mb-8">
        <label class="fs-6 fw-semibold">Proxy Type</label>
        <div class="fs-7 fw-semibold text-muted mb-3">
          Select one of these proxy types for the entire automation
        </div>

        <div class="d-flex">
          <div
              v-for="(proxyType, index) in proxyTypes"
              :key="index"
              class="form-check form-check-custom form-check-success form-check-solid form-check-sm me-7"
          >
            <input
                v-model="settingsData.proxy_type"
                class="form-check-input"
                type="radio"
                :value="proxyType"
                :id="'proxy_type_' + index"
            />
            <label
                class="form-check-label text-gray-700 fw-bold text-nowrap"
                :for="'proxy_type_' + index"
            >
              {{ proxyType }}
            </label>
          </div>
        </div>
      </div>

      <div class="separator separator-dashed my-7"></div>

      <!-- Post Settings Section -->
      <div class="form-group mb-8">
        <div class="mb-3">
          <label class="fs-6 fw-semibold">Post Settings</label>
          <div class="fs-7 fw-semibold text-muted">
            Control automatic posting and set account age restrictions for posting.
          </div>
        </div>

        <div>
          <!-- Auto Post Toggle -->
          <label class="form-check form-switch form-check-custom form-check-solid">

            <span class="text-gray-700 fw-bold text-nowrap me-6">Send Post From Folder Automatically</span>
            <input
                class="form-check-input"
                type="checkbox"
                v-model="settingsData.can_send_post_from_folder"
            />
          </label>

          <!-- Allowed Posting Age Input -->
          <div class="d-flex mt-6 align-items-center">
            <span class="text-gray-700 fw-bold text-nowrap me-6">Allowed Posting Age</span>

            <el-form-item prop="allowed_posting_age">
              <el-input
                  v-model="settingsData.allowed_posting_age"
                  type="text"
              ></el-input>
            </el-form-item>
          </div>
        </div>
      </div>

      <div class="separator separator-dashed my-7"></div>

      <!-- Batch Size Settings Section -->
      <div class="form-group mb-8">
        <div class="mb-5">
          <label class="fs-6 fw-semibold">Batch Size Settings</label>
          <div class="fs-7 fw-semibold text-muted">
            Configure the number of items to process per batch for different actions.
          </div>
        </div>

        <div class="row">
          <!-- Save Post Batch Size -->
          <div class="col-md-6 mb-5">
            <label class="form-label fw-bold text-gray-700">Save Post Batch Size</label>
            <el-input
                v-model="settingsData.save_post_batch_size"
                type="number"
                placeholder="5"
            ></el-input>
            <div class="fs-7 text-muted mt-1">Number of orders to process per account in save post</div>
          </div>

          <!-- Comment Batch Size -->
          <div class="col-md-6 mb-5">
            <label class="form-label fw-bold text-gray-700">Comment Batch Size</label>
            <el-input
                v-model="settingsData.comment_batch_size"
                type="number"
                placeholder="3"
            ></el-input>
            <div class="fs-7 text-muted mt-1">Number of orders to process per account in comment</div>
          </div>

          <!-- Order Prepare Batch Size -->
          <div class="col-md-6 mb-5">
            <label class="form-label fw-bold text-gray-700">Order Prepare Batch Size</label>
            <el-input
                v-model="settingsData.order_prepare_batch_size"
                type="text"
                placeholder="3"
            ></el-input>
            <div class="fs-7 text-muted mt-1">Batch size for preparing orders (view_story, save_post)</div>
          </div>

          <!-- View Story Batch Size -->
          <div class="col-md-6 mb-5">
            <label class="form-label fw-bold text-gray-700">View Story Batch Size</label>
            <el-input
                v-model="settingsData.view_story_batch_size"
                type="text"
                placeholder="8"
            ></el-input>
            <div class="fs-7 text-muted mt-1">Batch size for viewing stories</div>
          </div>
        </div>
      </div>
    </div>

    <div class="card-footer py-6">
      <button
          type="submit"
          class="btn btn-primary"
          @click="saveSettings"
      >
      <span v-if="is.saving">
        Please wait...
        <span class="spinner-border spinner-border-sm align-middle ms-2"></span>
      </span>
        <span v-else>Save</span>
      </button>
    </div>
  </div>

  <!--begin::Card-->
</template>

<script lang="ts">
import {getAssetPath} from "@/core/helpers/assets";
import {defineComponent, onMounted, reactive, ref} from "vue";
import {themeName} from "@/core/helpers/system";
import ApiService from "@/core/services/ApiService";

export default defineComponent({
  name: "layout-builder",
  setup() {
    const proxyTypes = ref([]);

    const settingsData = reactive({
      'proxy_type': '',
      'can_send_post_from_folder': '',
      'allowed_posting_age': '',
      'critical_only_mode': '',
      'save_post_batch_size': '',
      'comment_batch_size': '',
      'order_prepare_batch_size': '',
      'view_story_batch_size': '',
    });

    const is = ref({
      saving: false,
    })

    const getSettings = () => {
      ApiService.post("settings", {})
          .then((response) => {
            proxyTypes.value = response.data.proxy_types;
            settingsData.proxy_type = response.data.proxy_type;
            settingsData.can_send_post_from_folder = Boolean(Number(response.data.can_send_post_from_folder));
            settingsData.critical_only_mode = Boolean(Number(response.data.critical_only_mode));
            settingsData.allowed_posting_age = response.data.allowed_posting_age;
            settingsData.save_post_batch_size = response.data.save_post_batch_size;
            settingsData.comment_batch_size = response.data.comment_batch_size;
            settingsData.order_prepare_batch_size = response.data.order_prepare_batch_size;
            settingsData.view_story_batch_size = response.data.view_story_batch_size;
          })
    }

    const saveSettings = () => {
      is.value.saving = true
      ApiService.post("setting/update", settingsData)
          .then(console.log)
          .finally(() => is.value.saving = false)
    }

    onMounted(() => {
      getSettings()
    });


    return {
      themeName,
      getAssetPath,
      proxyTypes,
      settingsData,
      saveSettings,
      is,
    };
  },
});
</script>

<style>
.el-form-item {
  margin-bottom: 0;
}
</style>