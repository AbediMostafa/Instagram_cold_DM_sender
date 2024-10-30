<template>
  <div class="modal fade" id="export_leads_modal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered mw-650px">
      <div class="modal-content rounded">
        <div class="modal-header pb-0 border-0 justify-content-end">
          <div class="btn btn-sm btn-icon btn-active-color-primary" data-bs-dismiss="modal">
            <KTIcon icon-name="cross" icon-class="fs-1"/>
          </div>
        </div>
        <div class="modal-body scroll-y px-10 px-lg-15 pt-0 pb-15">
          <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" class="form" @submit.prevent="submit">
            <div class="mb-13 text-center">
              <h1 class="mb-3">Export Leads</h1>
            </div>

            <!-- Number of Leads Input -->
            <div class="d-flex flex-column mb-8 fv-row">
              <el-form-item label="Number of Leads" prop="numberOfLeads">
                <el-input v-model="form.numberOfLeads" type="number" placeholder="Enter number of leads"/>
              </el-form-item>
            </div>

            <!-- Category (Offer) Dropdown -->
            <div class="d-flex flex-column mb-8 fv-row">
              <el-form-item label="Category (Offer)" prop="categoryId">
                <el-select v-model="form.categoryId" placeholder="Select Category (Offer)">
                  <el-option
                      v-for="category in categoryStore.categoriesForDropDown"
                      :key="category.id"
                      :label="category.title"
                      :value="category.id"
                  />
                </el-select>
              </el-form-item>
            </div>

            <!-- Tag Dropdown -->
            <div class="d-flex flex-column mb-8 fv-row">
              <el-form-item label="Tags" prop="tags">
                <el-select
                    multiple
                    filterable
                    clearable
                    v-model="form.tags"
                    placeholder="Select Tags">
                  <el-option
                      v-for="tag in tagStore.tags.data"
                      :key="tag.id"
                      :label="tag.title"
                      :value="tag.id"
                  />
                </el-select>
              </el-form-item>
            </div>

            <div class="text-center">
              <button type="reset" id="export_leads_modal_cancel" class="btn btn-light me-3"
                      @click="hideModal('export_leads_modal')">Cancel
              </button>
              <button :data-kt-indicator="loading ? 'on' : null" class="btn btn-lg btn-primary" type="submit">
                <span v-if="!loading" class="indicator-label">
                  Export
                  <KTIcon icon-name="arrow-right" icon-class="fs-3 ms-2 me-0"/>
                </span>
                <span v-if="loading" class="indicator-progress">
                  Please wait...
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
import {defineComponent, ref, onMounted} from 'vue';
import ApiService from '@/core/services/ApiService';
import {hideModal} from '@/core/helpers/modal';
import {useCategoryStore} from "@/stores/Category";
import {useTagStore} from "@/stores/Tag";

export default defineComponent({
  name: 'export_leads_modal',
  setup() {
    const formRef = ref(null);
    const loading = ref(false);
    const categoryStore = useCategoryStore();
    const tagStore = useTagStore();

    const form = ref({
      numberOfLeads: null,
      categoryId: null,
      tags: null,
    });

    const rules = ref({
      numberOfLeads: [
        {required: true, message: 'Please enter the number of leads', trigger: 'blur'},
      ],
    });

    onMounted(()=> {
      categoryStore.getCategoriesForDropDown();
      tagStore.getTags();
    });

    const submit = async () => {
      formRef.value?.validate(async (valid) => {
        if (!valid) return;
        loading.value = true;

        try {
          await ApiService.post('lead/export', form.value, {
            responseType: 'blob' // Important for file download
          }).then(response => {
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'leads.csv'); // File name
            document.body.appendChild(link);
            link.click();
          });

        } catch (error) {
          console.error('Error exporting leads:', error);
        } finally {
          loading.value = false;
          hideModal('export_leads_modal');
        }
      });
    };

    return {
      submit,
      loading,
      formRef,
      form,
      rules,
      categoryStore,
      hideModal,
      tagStore,
    };
  },
});
</script>

<style>
.el-form-item__label{
  justify-content: flex-start!important;
}
</style>
