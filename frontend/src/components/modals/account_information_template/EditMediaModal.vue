<template>
  <!-- Modal Structure -->
  <div
      class="modal fade"
      id="edit_media_modal"
      tabindex="-1"
      aria-hidden="true"

  >
    <div class="modal-dialog modal-dialog-centered mw-650px">
      <div class="modal-content rounded" v-loading=store.is.gettingTemplate>
        <div class="modal-header pb-0 border-0 justify-content-end">
          <div
              class="btn btn-sm btn-icon btn-active-color-primary"
              data-bs-dismiss="modal"
          >
            <KTIcon icon-name="cross" icon-class="fs-1"/>
          </div>
        </div>
        <div class="modal-body scroll-y px-10 px-lg-15 pt-0 pb-15">
          <div class="mb-13 text-center">
            <h1 class="mb-3">Edit Media</h1>
          </div>
          <div class="divider"></div>
          <div class="d-flex flex-column mb-6 fv-row">
            <!--begin::Label-->
            <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
              <span class="required">Caption</span>
            </label>
            <!--end::Label-->
            <el-form-item prop="caption">
              <el-input
                  style="direction: rtl"
                  v-model="store.selectedTemplate.caption"
                  :rows="8"
                  type="textarea"
                  placeholder="Caption"
                  name="bunchInsert"
              />
            </el-form-item>
          </div>

          <div class="d-flex flex-column mb-8 fv-row">
            <!--begin::Label-->
            <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
              <span class="required">Category</span>
            </label>
            <!--end::Label-->
            <el-select
                v-if="categoryStore.categories.data.length"
                v-model="store.selectedTemplate.category_id" placeholder="Select">
              <el-option
                  v-for="item in categoryStore.categories.data"
                  :key="item.id"
                  :label="item.title"
                  :value="item.id"
              />
            </el-select>

          </div>
          <!-- Upload Button -->
          <el-button type="success" @click="store.updateTemplate()">Edit</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {ref, onMounted, defineProps, watch} from "vue";
import {useTemplateStore} from "@/stores/Template";
import {useCategoryStore} from "@/stores/Category";
import ApiService from "@/core/services/ApiService";

const props = defineProps(['id']);
const store = useTemplateStore();
const categoryStore = useCategoryStore()

watch(() => store.selectedTemplate.id, () => store.getTemplate())

</script>

<style lang="scss">
.override-styles {
  z-index: 99999 !important;
  pointer-events: initial;
}

.el-select {
  width: 100%;
}

.el-date-editor.el-input,
.el-date-editor.el-input__inner {
  width: 100%;
}

.el-upload {
  display: block;
}
</style>
