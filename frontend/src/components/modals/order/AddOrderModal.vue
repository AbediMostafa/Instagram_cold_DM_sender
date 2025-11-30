<template>
  <!--begin::Modal - New Target-->
  <div
      class="modal fade"
      id="add_order_modal"
      ref="newAccountModalRef"
      tabindex="-1"
      aria-hidden="true"
  >
    <!--begin::Modal dialog-->
    <div class="modal-dialog modal-dialog-centered mw-750px">
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
          <!--begin:Form-->
          <el-form
              id="add_order_modal_form"
              @submit.prevent="submit()"
              :model="targetData"
              :rules="rules"
              ref="formRef"
              class="form"
          >
            <!--begin::Heading-->
            <div class="mb-13 text-center">
              <h1 class="mb-3">Create New Order</h1>
            </div>
            <div class="d-flex flex-column mb-8 fv-row">
              <!--begin::Label-->
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Customer Name</span>
              </label>
              <!--end::Label-->

              <el-form-item prop="customer">
                <el-input
                    v-model="targetData.customer"
                    placeholder="Enter Account Username"
                    name="customer"
                ></el-input>
              </el-form-item>
            </div>
            <div class="d-flex flex-column mb-8 fv-row">
              <!--begin::Label-->
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Target Link</span>
              </label>
              <!--end::Label-->

              <el-form-item prop="link">
                <el-input
                    v-model="targetData.link"
                    placeholder="Enter Account Username"
                    name="link"
                ></el-input>
              </el-form-item>
            </div>
            <div class="d-flex flex-column mb-8 fv-row">
              <!--begin::Label-->
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Count</span>
              </label>
              <!--end::Label-->

              <el-form-item prop="count">
                <el-input
                    v-model="targetData.count"
                    placeholder="Enter Account Username"
                    name="count"
                    disabled

                ></el-input>
              </el-form-item>
            </div>


            <!--end::Heading-->
            <div
                class="d-flex flex-column mb-6 fv-row"
            >
              <!--begin::Label-->
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Comments</span>
              </label>
              <!--end::Label-->
              <el-form-item prop="ip">
                <el-input
                    v-model="targetData.comments"
                    :rows="8"
                    type="textarea"
                    placeholder="Enter Accounts Here"
                    name="bunchInsert"
                />
              </el-form-item>

            </div>


            <!--begin::Input group-->
            <!--begin::Actions-->
            <div class="text-center">
              <button
                  type="reset"
                  id="add_order_modal_cancel"
                  class="btn btn-light me-3"
                  @click="hideModal('add_order_modal')"
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
                  <KTIcon icon-name="arrow-right" icon-class="fs-3 ms-2 me-0"/>
                </span>
                <span v-if="loading" class="indicator-progress">
                  Please wait...
                  <span
                      class="spinner-border spinner-border-sm align-middle ms-2"
                  ></span>
                </span>
              </button>
            </div>
          </el-form>
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
import {defineComponent, onMounted, ref,watch} from "vue";
import {hideModal} from "@/core/helpers/modal";
import ApiService from "@/core/services/ApiService";
import {useAccountStore} from "@/stores/Account";
import {useCategoryStore} from "@/stores/Category";
import {useTagStore} from "@/stores/Tag";
import {useOrderStore} from "@/stores/Order";

export default defineComponent({
  name: "add_order_modal",
  setup() {
    const formRef = ref<null | HTMLFormElement>(null);
    const newAccountModalRef = ref<null | HTMLElement>(null);
    const loading = ref<boolean>(false);
    const store = useOrderStore();

    const targetData = ref({
      customer: "",
      link: "",
      count: "",
      comments: "",
    });

    const rules = ref({
      comments: [
        {required: true, message: "Please input comments", trigger: "blur"},
      ],
      link: [
        {required: true, message: "Please input link", trigger: "blur"},
      ],
    });

    const submit = () => {
      if (!formRef.value) {
        return;
      }

      formRef.value.validate((valid: boolean) => {
        if (valid) {
          loading.value = true;

          ApiService.post("orders/create", targetData.value)
              // .then(() => hideModal("add_order_modal"))
              .then(() => store.getOrders())
              .finally(() => (loading.value = false));
        }
      });
    };
    watch(
        () => targetData.value.comments,
        (value) => {
          if (!value) {
            targetData.value.count = 0;
            return;
          }

          // محاسبه تعداد خطوط واقعی
          const lines = value
              .split('\n')
              .map(l => l.trim())
              .filter(l => l.length > 0);

          targetData.value.count = lines.length;
        }
    );

    return {
      targetData,
      submit,
      loading,
      formRef,
      rules,
      newAccountModalRef,
      hideModal,
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
