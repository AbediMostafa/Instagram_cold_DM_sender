<template>
  <div class="modal fade" id="create_lead_modal" tabindex="-1" aria-hidden="true">
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
              <h1 class="mb-3">Import Leads from CSV</h1>
            </div>

            <!-- Tag Input -->
            <div class="d-flex flex-column mb-8 fv-row">
              <el-form-item label="Select Tags" prop="selectedTags">
                <el-select
                    v-model="form.selectedTags"
                    multiple
                    filterable
                    remote
                    clearable
                    placeholder="Search for tags"
                    :remote-method="tagStore.fetchTags"
                    :loading="tagLoading"
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

            <!-- CSV Upload Section -->
            <div class="d-flex flex-column mb-8 fv-row">
              <el-form-item label="Upload CSV" prop="csvFile">
                <input type="file" @change="onFileChange" accept=".csv"/>
              </el-form-item>
            </div>

            <div class="text-center">
              <button type="reset" id="create_lead_modal_cancel" class="btn btn-light me-3"
                      @click="hideModal('create_lead_modal')">Cancel
              </button>
              <button :data-kt-indicator="loading ? 'on' : null" class="btn btn-lg btn-primary" type="submit">
                <span v-if="!loading" class="indicator-label">
                  Submit
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
import { defineComponent, ref, onMounted } from 'vue';
import { hideModal } from '@/core/helpers/modal';
import ApiService from '@/core/services/ApiService';
import { useLeadStore } from '@/stores/Lead';
import {useTagStore} from "@/stores/Tag";

export default defineComponent({
  name: 'create_lead_modal',
  setup() {
    const formRef = ref<null | HTMLFormElement>(null);
    const loading = ref<boolean>(false);
    const store = useLeadStore();
    const tagStore = useTagStore();

    // For handling the CSV file upload
    const csvFile = ref<File | null>(null);

    // For managing tags
    const selectedTags = ref<Array<any>>([]);
    const tagLoading = ref<boolean>(false);

    const form = ref({
      selectedTags: [],
      csvFile: null,
    });

    const rules = ref({
      selectedTags: [
        { required: true, message: 'Please select at least one tag', trigger: 'blur' },
      ],
      csvFile: [
        { required: true, message: 'Please upload a CSV file', trigger: 'change' },
      ],
    });

    const onFileChange = (event: Event) => {
      const file = (event.target as HTMLInputElement).files?.[0];
      if (file) {
        form.value.csvFile = file;
      }
    };

    const submit = () => {
      formRef.value?.validate((valid) => {
        if (!valid) return;

        loading.value = true;

        const formData = new FormData();
        formData.append('file', form.value.csvFile);

        if (form.value.selectedTags.length > 0) {
          formData.append('tags', JSON.stringify(form.value.selectedTags));
        }

        ApiService.post('lead/import', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
            .then(() => {
              store.getLeads();
              hideModal('create_lead_modal');
            })
            .catch((error) => {
              console.error(error);
            })
            .finally(() => {
              loading.value = false;
            });
      });
    };

    return {
      tagStore,
      submit,
      loading,
      formRef,
      hideModal,
      onFileChange,
      selectedTags,
      tagLoading,
      form,
      rules,
    };
  },
});
</script>
