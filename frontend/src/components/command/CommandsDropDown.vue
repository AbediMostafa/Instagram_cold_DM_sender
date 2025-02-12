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
        <!-- Filter by Account -->
        <el-input
            class="mt-2"
            v-model="store.queryParams.account"
            placeholder="Search by Account"
            clearable
            @clear="store.getCommands"
        />

        <!-- Filter by Lead -->
        <el-input
            class="mt-2"
            v-model="store.queryParams.lead"
            placeholder="Search by Lead"
            clearable
            @clear="store.getCommands"
        />

        <!-- Filter by Type -->
        <el-select
            style="width: 100%"
            class="mt-2"
            v-model="store.queryParams.type"
            placeholder="Filter by Type"
            clearable
            @clear="store.getCommands"
        >
          <el-option
              v-for="type in store.commandTypes"
              :key="type"
              :label="type"
              :value="type"
          />
        </el-select>

        <!-- Filter by Statuses -->
        <el-select
            style="width: 100%"
            class="mt-2"
            v-model="store.queryParams.status"
            clearable
            placeholder="Filter by Status"
        >
          <el-option
              v-for="status in store.commandStatuses"
              :key="status"
              :label="status"
              :value="status"
          />
        </el-select>

        <!-- Filter by Category -->
        <el-select
            style="width: 100%"
            class="mt-2"
            v-model="store.queryParams.category_id"
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

        <div class="fill-flex d-flex align-items-center mt-4">
          <a class="btn btn-sm btn-light-primary" @click="store.getCommands()">Filter</a>
        </div>

      </div>
    </div>

  </div>
  <!--end::Menu 2-->
</template>
<script lang="ts">
import {defineComponent, onMounted, ref} from 'vue';
import {useCategoryStore} from '@/stores/Category';
import {useCommandStore} from "@/stores/Command";

export default defineComponent({
  name: 'accounts-drop-down',
  components: {},
  setup() {
    const store = useCommandStore()
    const categoryStore = useCategoryStore();

    // Fetch categories and tags when the component is mounted
    onMounted(() => {
      categoryStore.getCategories();
      store.getCommandTypes();
      store.getCommandStatuses();
    });

    return {
      store,
      categoryStore,
    };
  },
});
</script>
