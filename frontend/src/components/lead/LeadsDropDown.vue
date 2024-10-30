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
            v-model="store.queryParams.tags"
            multiple
            filterable
            remote
            clearable
            placeholder="Filter by Tags"
            :remote-method="fetchTags"
            :loading="tagLoading"
        >
          <el-option
              v-for="tag in tagStore.tags.data"
              :key="tag.id"
              :label="tag.title"
              :value="tag.id"
          />
        </el-select>

        <!-- Filter by Category -->
        <el-select
            class="mt-2"
            v-model="store.queryParams.category"
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

        <!-- Filter by Statuses -->
        <el-select
            class="mt-2"
            v-model="store.queryParams.statuses"
            multiple
            clearable
            placeholder="Filter by Statuses"
        >
          <el-option
              v-for="status in store.statuses"
              :key="status"
              :label="status"
              :value="status"
          />
        </el-select>
        <el-select
            class="mt-2"
            v-model="store.queryParams.users"
            multiple
            clearable
            placeholder="Filter by Users"
        >
          <el-option
              v-for="user in userStore.usersForDropDown"
              :key="user.id"
              :label="user.name"
              :value="user.id"
          />
        </el-select>
        <div class="fill-flex d-flex align-items-center mt-4">
          <a class="btn btn-sm btn-light-primary" @click="store.getLeads()">Filter</a>

        </div>

      </div>
    </div>
    <div class="separator mb-3 opacity-75"></div>
    <div class="menu-item ">
      <div class="menu-content fs-6 text-gray-900 fw-bold px-3">
        Quick Actions
      </div>
      <div class="menu-content px-3 fill-flex d-flex align-items-center">
        <a
            class="btn btn-light-danger btn-sm px-4"
            @click="store.deleteSelected(store.checkedLeadRows)"
        >
          Delete Selected
        </a>
      </div>
    </div>

    <div class="menu-item">
      <div class="menu-content px-3 justify-content-between d-flex align-items-center">
        <!-- Set Offer -->
        <el-select
            style="width: 242px"
            v-model="store.leads.category_id"
            placeholder="Select Offer"
        >
          <el-option
              v-for="item in categoryStore.categories.data"
              :key="item.id"
              :label="item.title"
              :value="item.id"
          />

          <el-option
              label="Clear Offer"
              :value="null"
          />
        </el-select>

        <a class="btn btn-sm btn-light-success ms-1" @click="store.setCategory()">
          Set Offer
        </a>
      </div>
    </div>
  </div>
  <!--end::Menu 2-->
</template>
<script lang="ts">
import { defineComponent, onMounted, ref } from 'vue';
import {useLeadStore} from "@/stores/Lead";
import { useCategoryStore } from '@/stores/Category';
import { useTagStore } from '@/stores/Tag';
import {useUserStore} from "@/stores/User";

export default defineComponent({
  name: 'accounts-drop-down',
  components: {},
  setup() {
    const categoryStore = useCategoryStore();
    const tagStore = useTagStore();
    const store = useLeadStore()
    const userStore = useUserStore()
    const tagLoading = ref(false);

    // Fetch categories and tags when the component is mounted
    onMounted(() => {
      categoryStore.getCategories();
      tagStore.getTags();
      store.getStatuses();
      userStore.getUsersByName()
    });

    // Method to fetch tags based on the search query
    const fetchTags = async (query) => {
      if (!query) return;
      tagLoading.value = true;
      try {
        await tagStore.getTags({ query });
      } catch (error) {
        console.error('Error fetching tags:', error);
      } finally {
        tagLoading.value = false;
      }
    };

    return {
      store,
      categoryStore,
      fetchTags,
      tagLoading,
      tagStore,
      userStore,
    };
  },
});
</script>
