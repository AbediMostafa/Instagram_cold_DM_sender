<template>
  <div class="card mb-5 mb-xl-8">
    <!--begin::Header-->
    <div class="card-header border-0 pt-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">Categories</span>
        <span class="text-muted mt-1 fw-semibold fs-7">{{ store.categories.total }} categories</span>
      </h3>
      <div class="card-toolbar">
        <!-- Add Category Button -->
        <a class="btn btn-sm btn-success me-2" @click="showModal('create_category_modal')">Add Category</a>
        <button
            type="button"
            class="btn btn-sm btn-icon btn-color-primary btn-active-light-primary"
            data-kt-menu-trigger="click"
            data-kt-menu-placement="bottom-end"
            data-kt-menu-flip="top-end"
        >
          <KTIcon icon-name="category" icon-class="fs-2"/>
        </button>
        <!-- Categories Dropdown -->
        <CategoriesDropDown />
      </div>
    </div>
    <!--end::Header-->

    <!--begin::Body-->
    <div class="card-body py-3">
      <!--begin::Table container-->
      <div class="table-responsive">
        <table
            class="table table-row-bordered table-row-gray-100 align-middle gs-0 gy-3"
            v-loading="store.is.loading"
        >
          <!--begin::Table head-->
          <thead>
          <tr class="fw-bold text-muted">
            <th class="w-25px">
              <div class="form-check form-check-sm form-check-custom form-check-solid">
                <input
                    class="form-check-input"
                    type="checkbox"
                    @change="store.checkRows($event)"
                />
              </div>
            </th>
            <th class="min-w-150px">TITLE</th>
            <th class="min-w-200px">DESCRIPTION</th>
            <th class="min-w-100px text-end">Actions</th>
          </tr>
          </thead>
          <!--end::Table head-->

          <!--begin::Table body-->
          <tbody>
          <template v-for="(category, index) in store.categories.data" :key="index">
            <tr>
              <td>
                <div class="form-check form-check-sm form-check-custom form-check-solid">
                  <input
                      class="form-check-input widget-13-check"
                      type="checkbox"
                      :value="category.id"
                      v-model="store.checkedCategoryRows"
                  />
                </div>
              </td>

              <td>
                <a class="text-gray-900 fw-bold text-hover-primary fs-6">{{ category.title }}</a>
              </td>

              <td>
                <span class="text-gray-700">{{ category.description }}</span>
              </td>

              <td class="text-end">
                <category-drop-down
                    @editClicked="editClicked"
                    :category="category"
                />
              </td>
            </tr>
          </template>
          </tbody>
          <!--end::Table body-->
        </table>
        <!--end::Table-->

        <!-- Pagination -->
        <el-pagination
            :current-page="store.categories.current_page"
            :page-size="configStore.pagination?.each_page?.categories"
            layout="prev, pager, next"
            :total="store.categories.total"
            @current-change="page => store.getCategories(page)"
        />
      </div>
      <!--end::Table container-->
    </div>
    <!--begin::Body-->
  </div>

  <!-- Modals -->
  <create-category-modal />
  <edit-category-modal :id="selectedId" />
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import CreateCategoryModal from '@/components/modals/category/CreateCategoryModal.vue';
import { showModal } from '@/core/helpers/modal';
import { useAppConfigStore } from '@/stores/AppConfig';
import EditCategoryModal from '@/components/modals/category/EditCategoryModal.vue';
import { useCategoryStore } from '@/stores/Category';
import CategoryDropDown from '@/components/category/CategoryDropDown.vue';
import CategoriesDropDown from '@/components/category/CategoriesDropDown.vue'; // Correct import

const selectedId = ref(0);
const store = useCategoryStore();
const configStore = useAppConfigStore();

const editClicked = (id) => {
  selectedId.value = id;
  showModal('edit_category_modal');
};

onMounted(store.getCategories);
</script>
