<template>
  <!--begin::Menu 2-->
  <div
      class="menu menu-sub menu-sub-dropdown menu-column menu-rounded menu-gray-600 menu-state-bg-light-primary fw-semibold w-350px"
      data-kt-menu="true"
  >
    <!--begin::Menu item-->
    <div class="menu-item">
      <div class="menu-content fs-6 text-gray-900 fw-bold px-3 py-4">
        Filter
      </div>
      <div class="menu-content px-3 ">
        <!-- Filter by Tags -->
        <el-select
            v-model="store.templates.queryParams.tags"
            multiple
            filterable
            remote
            clearable
            placeholder="Filter by Tags"
            :remote-method="fetchTags"
            :loading="tagLoading"
        >
          <el-option
              v-for="tag in tagStore.searchedTags"
              :key="tag.id"
              :label="tag.title"
              :value="tag.id"
          />
        </el-select>

        <!-- Filter by Category -->
        <el-select
            class="mt-2"
            v-model="store.templates.queryParams.category_id"
            placeholder="Filter by Offer"
            clearable
        >
          <el-option
              v-for="category in categoryStore.categories.data"
              :key="category.id"
              :label="category.title"
              :value="category.id"
          />
        </el-select>

        <!-- Filter by Types -->
        <el-select
            class="mt-2"
            v-model="store.templates.queryParams.type"
            clearable
            placeholder="Filter by Types"
        >
          <el-option
              v-for="status in store.types"
              :key="status"
              :label="status"
              :value="status"
          />
        </el-select>

        <!-- Filter by Colors -->
        <el-select
            class="mt-2"
            v-model="store.templates.queryParams.color"
            clearable
            placeholder="Filter by Colors"
            v-if="store.templates.receivedType === 'carousel'"
        >
          <el-option
              v-for="color in store.colors"
              :key="color.id"
              :label="color.title"
              :value="color.id"
          />
        </el-select>
        <div class="fill-flex d-flex align-items-center mt-4">
          <a class="btn btn-sm btn-light-primary" @click="store.getTemplates()">Filter</a>
        </div>
      </div>
    </div>
  </div>
  <!--end::Menu 2-->
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useCategoryStore } from '@/stores/Category';
import { useTagStore } from '@/stores/Tag';
import {useTemplateStore} from "@/stores/Template";

const categoryStore = useCategoryStore();
const tagStore = useTagStore();
const store = useTemplateStore();
const tagLoading = ref(false);

// Fetch categories and tags when the component is mounted
onMounted(() => {
  categoryStore.getCategories();
  store.fetchTypes();
});

// Method to fetch tags based on the search query
const fetchTags = async (query: string) => {
  if (!query) return;
  tagLoading.value = true;
  try {
    await tagStore.fetchTags( query);
  } catch (error) {
    console.error('Error fetching tags:', error);
  } finally {
    tagLoading.value = false;
  }
};
</script>
