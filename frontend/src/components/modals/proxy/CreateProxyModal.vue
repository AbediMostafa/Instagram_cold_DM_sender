<template>
  <!--begin::Modal - New Proxy-->
  <div
    class="modal fade"
    id="create_proxy_modal"
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
            <!-- Use your icon component -->
            <i class="bi bi-x fs-1"></i>
          </div>
          <!--end::Close-->
        </div>
        <!--begin::Modal header-->

        <!--begin::Modal body-->
        <div class="modal-body scroll-y px-10 px-lg-15 pt-0 pb-15">
          <!--begin:Form-->
          <el-form
            id="create_proxy_modal_form"
            @submit.prevent="submit"
            :model="proxyData"
            ref="formRef"
            class="form"
          >
            <!--begin::Heading-->
            <div class="mb-13 text-center">
              <h1 class="mb-3">Create New Proxy</h1>
            </div>
            <!--end::Heading-->
            <div class="fv-row my-10">
              <!--begin::Wrapper-->
              <div class="d-flex flex-stack">
                <!--begin::Label-->
                <div class="me-5">
                  <!--begin::Label-->
                  <label class="fs-6 fw-semibold">Bulk insertion?</label>
                  <!--end::Label-->

                  <!--begin::Input-->
                  <div class="fs-7 fw-semibold text-muted">
                    You can copy and paste your proxies and import many of them
                    in the following format: IP:Port:Username:Password.
                  </div>
                  <!--end::Input-->
                </div>
                <!--end::Label-->

                <!--begin::Switch-->
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
                    v-model="proxyData.bulk_insertion"
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
                <!--end::Switch-->
              </div>
              <!--begin::Wrapper-->
            </div>

            <div
              v-if="proxyData.bulk_insertion"
              class="d-flex flex-column mb-6 fv-row"
            >
              <!--begin::Label-->
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Bulk Proxy Insertion</span>
              </label>
              <!--end::Label-->
              <el-form-item prop="ip">
                <el-input
                  v-model="proxyData.proxies"
                  :rows="8"
                  type="textarea"
                  placeholder="Enter Proxies Here"
                  name="bunchInsert"
                />
              </el-form-item>
            </div>

            <div v-else>
              <div class="d-flex flex-column mb-6 fv-row">
                <!--begin::Label-->
                <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                  <span class="required">IP Address</span>
                </label>
                <!--end::Label-->
                <el-form-item prop="ip">
                  <el-input
                    v-model="proxyData.ip"
                    placeholder="Enter Proxy IP"
                    name="ip"
                  ></el-input>
                </el-form-item>
              </div>
              <div class="d-flex flex-column mb-6 fv-row">
                <!--begin::Label-->
                <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                  <span class="required">Port</span>
                </label>
                <!--end::Label-->
                <el-form-item prop="ip">
                  <el-input
                    v-model="proxyData.port"
                    placeholder="Enter Proxy Port"
                    name="ip"
                  ></el-input>
                </el-form-item>
              </div>
              <div class="d-flex flex-column mb-6 fv-row">
                <!--begin::Label-->
                <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                  <span class="required">Username</span>
                </label>
                <!--end::Label-->
                <el-form-item prop="ip">
                  <el-input
                    v-model="proxyData.username"
                    placeholder="Enter Proxy Username"
                    name="ip"
                  ></el-input>
                </el-form-item>
              </div>
              <div class="d-flex flex-column mb-6 fv-row">
                <!--begin::Label-->
                <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                  <span class="required">Password</span>
                </label>
                <!--end::Label-->
                <el-form-item prop="ip">
                  <el-input
                    v-model="proxyData.password"
                    placeholder="Enter Proxy Password"
                    name="ip"
                  ></el-input>
                </el-form-item>
              </div>
            </div>

            <!--begin::Actions-->
            <div class="text-center">
              <button
                type="reset"
                id="create_proxy_modal_cancel"
                class="btn btn-light me-3"
                @click="hideModal('create_proxy_modal')"
              >
                Cancel
              </button>

              <!--begin::Button-->
              <button
                :data-kt-indicator="loading ? 'on' : null"
                class="btn btn-lg btn-primary"
                type="submit"
              >
                <span v-if="!loading" class="indicator-label">
                  Submit
                  <!-- Use your icon component -->
                  <i class="bi bi-arrow-right fs-3 ms-2 me-0"></i>
                </span>
                <span v-if="loading" class="indicator-progress">
                  Please wait...
                  <span
                    class="spinner-border spinner-border-sm align-middle ms-2"
                  ></span>
                </span>
              </button>
              <!--end::Button-->
            </div>
            <!--end::Actions-->
          </el-form>
        </div>
        <!--end::Modal body-->
      </div>
      <!--end::Modal content-->
    </div>
    <!--end::Modal dialog-->
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from "vue";
import { hideModal } from "@/core/helpers/modal";
import ApiService from "@/core/services/ApiService";
import { useProxyStore } from "@/stores/Proxy"; // Assume you have a proxy store

export default defineComponent({
  name: "create_proxy_modal",
  setup() {
    const formRef = ref(null);
    const loading = ref(false);
    const proxyStore = useProxyStore(); // Use your proxy store

    const proxyData = ref({
      ip: "",
      port: "",
      username: "",
      password: "",
      proxies: "",
      bulk_insertion: false,
    });

    const submit = () => {
      loading.value = true;

      ApiService.post("proxy/create", proxyData.value)
        .then(() => hideModal("create_proxy_modal"))
        .then(() => proxyStore.getProxies())
        .finally(() => (loading.value = false));
    };

    watch(
      () => proxyData.value.bulk_insertion,
      function ($val) {
        if ($val) {
        }
        console.log($val);
      }
    );

    return {
      proxyData,
      submit,
      loading,
      formRef,
      hideModal,
    };
  },
});
</script>

<style lang="scss">
.el-select {
  width: 100%;
}

.el-date-editor.el-input,
.el-date-editor.el-input__inner {
  width: 100%;
}
</style>
