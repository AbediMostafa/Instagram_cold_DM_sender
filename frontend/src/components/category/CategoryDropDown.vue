<template>
  <el-dropdown class="p-5">
    <a class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm">
      <KTIcon icon-name="category" icon-class="fs-3" />
    </a>
    <template #dropdown>
      <el-dropdown-menu class="p-3">
        <!-- Edit Action -->
        <el-dropdown-item @click="$emit('editClicked', category.id)">Edit</el-dropdown-item>

        <!-- Delete Action -->
        <el-dropdown-item @click="store.deleteSelected([category.id])">Delete</el-dropdown-item>

        <!-- Activate/Deactivate Action -->
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useCategoryStore } from '@/stores/Category';

export default defineComponent({
  name: 'CategoryDropDown',
  props: {
    category: {
      type: Object,
      required: true,
    },
  },
  setup() {
    return {
      store: useCategoryStore(),
    };
  },
});
</script>

<style>
.fill-flex a {
  flex: 1 !important;
}
</style>
