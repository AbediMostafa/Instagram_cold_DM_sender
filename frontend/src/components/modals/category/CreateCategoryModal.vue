<template>
  <div class="modal fade" id="create_category_modal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered mw-650px">
      <div class="modal-content rounded">
        <div class="modal-header pb-0 border-0 justify-content-end">
          <div class="btn btn-sm btn-icon btn-active-color-primary" data-bs-dismiss="modal">
            <KTIcon icon-name="cross" icon-class="fs-1"/>
          </div>
        </div>
        <div class="modal-body scroll-y px-10 px-lg-15 pt-0 pb-15">
          <el-form
              @submit.prevent="submit"
              :model="categoryData"
              :rules="rules"
              ref="formRef"
              class="form"
          >
            <div class="mb-13 text-center">
              <h1 class="mb-3">Create New Category</h1>
            </div>
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Title</span>
              </label>
              <el-form-item prop="title">
                <el-input v-model="categoryData.title" placeholder="Enter Category Title"></el-input>
              </el-form-item>
            </div>
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span>Description</span>
              </label>
              <el-form-item prop="description">
                <el-input v-model="categoryData.description" placeholder="Enter Category Description"></el-input>
              </el-form-item>
            </div>
            <div class="text-center">
              <button type="reset" class="btn btn-light me-3" @click="hideModal('create_category_modal')">Cancel
              </button>
              <button :data-kt-indicator="loading ? 'on' : null" class="btn btn-lg btn-primary" type="submit">
                <span v-if="!loading">Submit</span>
                <span v-if="loading" class="indicator-progress">Please wait...<span
                    class="spinner-border spinner-border-sm align-middle ms-2"></span></span>
              </button>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import {defineComponent, ref} from "vue";
import {hideModal} from "@/core/helpers/modal";
import ApiService from "@/core/services/ApiService";
import {useCategoryStore} from "@/stores/Category";

export default defineComponent({
  name: "CreateCategoryModal",
  setup() {
    const formRef = ref(null);
    const loading = ref(false);
    const store = useCategoryStore();
    const categoryData = ref({
      title: "",
      description: "",
    });

    const rules = ref({
      title: [{required: true, message: "Please input title", trigger: "blur"}],
    });

    const submit = () => {
      if (!formRef.value) return;

      formRef.value.validate((valid) => {
        if (valid) {
          loading.value = true;
          ApiService.post('categories/create', categoryData.value)
              .then(store.getCategories)
              .then(() => hideModal("create_category_modal"))
              .finally(() => loading.value = false);
        }
      });
    };

    return {
      categoryData,
      submit,
      loading,
      formRef,
      rules,
      hideModal,
    };
  },
});
</script>
