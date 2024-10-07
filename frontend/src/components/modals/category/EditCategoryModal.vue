<template>
  <div class="modal fade" id="edit_category_modal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered mw-650px">
      <div class="modal-content rounded">
        <div class="modal-header pb-0 border-0 justify-content-end">
          <div class="btn btn-sm btn-icon btn-active-color-primary" data-bs-dismiss="modal">
            <KTIcon icon-name="cross" icon-class="fs-1" />
          </div>
        </div>
        <div class="modal-body scroll-y px-10 px-lg-15 pt-0 pb-15">
          <el-form
              ref="formRef"
              :model="categoryData"
              :rules="rules"
              @submit.prevent="submit"
              class="form"
          >
            <div class="mb-13 text-center">
              <h1 class="mb-3">Edit Category</h1>
            </div>

            <!-- Title Input -->
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Title</span>
              </label>
              <el-form-item prop="title">
                <el-input v-model="categoryData.title" placeholder="Enter Category Title" />
              </el-form-item>
            </div>

            <!-- Description Input -->
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span>Description</span>
              </label>
              <el-form-item prop="description">
                <el-input v-model="categoryData.description" placeholder="Enter Category Description" />
              </el-form-item>
            </div>

            <!-- Actions -->
            <div class="text-center">
              <button
                  type="reset"
                  class="btn btn-light me-3"
                  @click="hideModal('edit_category_modal')"
              >
                Cancel
              </button>
              <button
                  :data-kt-indicator="loading ? 'on' : null"
                  class="btn btn-lg btn-primary"
                  type="submit"
              >
                <span v-if="!loading">Save Changes</span>
                <span v-if="loading" class="indicator-progress">Please wait...
                  <span class="spinner-border spinner-border-sm align-middle ms-2"></span>
                </span>
              </button>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue';
import { hideModal } from '@/core/helpers/modal';
import ApiService from '@/core/services/ApiService';
import { useCategoryStore } from '@/stores/Category';

export default defineComponent({
  name: 'EditCategoryModal',
  props: {
    id: {
      type: Number,
      required: true,
    },
  },
  setup(props) {
    const formRef = ref(null);
    const loading = ref(false);
    const categoryData = ref({
      title: '',
      description: '',
    });

    const rules = ref({
      title: [{ required: true, message: 'Please input title', trigger: 'blur' }],
    });

    const store = useCategoryStore();

    // Fetch category data when the `id` prop changes
    watch(
        () => props.id,
        async (categoryId) => {
          if (categoryId) {
            try {
              const response = await ApiService.post(`categories/view`, {categoryId});
              categoryData.value = response.data;
            } catch (error) {
              console.error('Error fetching category:', error);
            }
          }
        }
    );

    const submit = () => {
      if (!formRef.value) return;

      formRef.value.validate(async (valid) => {
        if (valid) {
          loading.value = true;
          try {
            await ApiService.post(`categories/edit/${props.id}`, categoryData.value);
            hideModal('edit_category_modal');
            store.getCategories();
          } catch (error) {
            console.error('Error updating category:', error);
          } finally {
            loading.value = false;
          }
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

<style lang="scss">
.override-styles {
  z-index: 99999 !important;
  pointer-events: initial;
}
</style>
