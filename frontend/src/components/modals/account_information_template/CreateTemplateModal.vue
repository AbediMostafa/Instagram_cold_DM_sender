<template>
  <!--begin::Modal - New Target-->
  <div
      class="modal fade"
      id="create_template_modal"
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
          <!--begin:Form-->
          <el-form
              id="create_template_modal_form"
              @submit.prevent="submit()"
              :model="targetData"
              :rules="rules"
              ref="formRef"
              class="form"
          >
            <!--begin::Heading-->
            <div class="mb-13 text-center">
              <h1 class="mb-3">Create New Template</h1>
            </div>

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
                    You can copy and paste your Templates and import many of them
                    in the following format: phrase1,phrase2,phrase3.
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
                      id="account_bulk_insertion"
                      v-model="targetData.bulk_insertion"
                  />
                  <!--end::Input-->

                  <!--begin::Label-->
                  <span
                      class="form-check-label fw-semibold text-muted"
                      for="account_bulk_insertion"
                  >
                    Yes
                  </span>
                  <!--end::Label-->
                </label>
                <!--end::Switch-->
              </div>
              <!--begin::Wrapper-->
            </div>

            <div class="d-flex flex-column mb-8 fv-row" v-if="targetData.bulk_insertion">
              <!--begin::Label-->
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Text</span>
              </label>

              <el-form-item prop="text">
                <el-input
                    type="textarea"
                    :rows="8"
                    v-model="targetData.text"
                    placeholder="Enter text"
                    name="text"
                ></el-input>
              </el-form-item>
            </div>

            <div v-else>
              <div class="d-flex flex-column mb-8 fv-row">
                <!--begin::Label-->
                <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                  <span class="required">Text</span>
                </label>

                <el-form-item prop="text">
                  <el-input
                      :type="targetData.type =='bio' ? 'textarea' :'input'"
                      v-model="targetData.text"
                      placeholder="Enter text"
                      name="text"
                  ></el-input>
                </el-form-item>
              </div>
              <div class="d-flex flex-column mb-8 fv-row" v-if="targetData.type=='name-username'">
                <!--begin::Label-->
                <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                  <span class="required">Name</span>
                </label>

                <el-form-item prop="text">
                  <el-input
                      type="input"
                      v-model="targetData.name"
                      placeholder="Enter name"
                      name="text"
                  ></el-input>
                </el-form-item>
              </div>

            </div>
            <div class="d-flex flex-column mb-8 fv-row">
              <!--begin::Label-->
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Template type</span>
              </label>

              <el-form-item prop="type">
                <el-select
                    v-model="targetData.type"
                    placeholder="Select type of template"
                    size="large"
                >
                  <el-option
                      v-for="item in templateTypes"
                      :key="item"
                      :label="item"
                      :value="item"
                  />
                </el-select>
              </el-form-item>
            </div>

            <div class="d-flex flex-column mb-8 fv-row">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                Tags
              </label>

              <el-form-item prop="selectedTags">
                <el-select
                    v-model="targetData.tags"
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

            <!--begin::Actions-->
            <div class="text-center">
              <button
                  type="reset"
                  id="create_template_modal_cancel"
                  class="btn btn-light me-3"
                  @click="hideModal('create_template_modal')"
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
import {defineComponent, onMounted, ref} from "vue";
import {hideModal} from "@/core/helpers/modal";
import ApiService from "@/core/services/ApiService";
import {useAccountStore} from "@/stores/Account";
import {useTemplateStore} from "@/stores/Template";
import {useTagStore} from "@/stores/Tag";

export default defineComponent({
  name: "create_template_modal",
  setup() {
    const formRef = ref<null | HTMLFormElement>(null);
    const loading = ref<boolean>(false);
    const store = useTemplateStore();
    const tagStore = useTagStore()

    const templateTypes = ref([
      "name",
      "username",
      "bio",
      "name-username",
    ]);

    const targetData = ref({
      text: "",
      name: "",
      type: "",
      bulk_insertion: false,
      tags: [],

    });

    const rules = ref({
      text: [
        {
          required: true,
          message: "Please input template text",
          trigger: "blur",
        },
      ],
      type: [
        {
          required: true,
          message: "Please select template type",
          trigger: "blur",
        },
      ],
    });

    const submit = () => {
      if (!formRef.value) {
        return;
      }

      formRef.value.validate((valid: boolean) => {
        if (valid) {
          loading.value = true;

          ApiService.post("template/create", targetData.value)
              .then(console.log)
          // .then(() => hideModal("create_template_modal"))
          // .then(() => store.getTemplates())
          // .finally(() => (loading.value = false));
        }
      });
    };


    return {
      templateTypes,
      targetData,
      submit,
      loading,
      formRef,
      rules,
      hideModal,
      tagStore,

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
