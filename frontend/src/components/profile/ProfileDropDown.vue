<template>
  <el-dropdown class="p-5">
    <a class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm">
      <KTIcon icon-name="category" icon-class="fs-3"/>
    </a>
    <template #dropdown>
      <el-dropdown-menu class="p-3">
        <el-dropdown-item @click="openEditModal">Edit</el-dropdown-item>
        <el-dropdown-item @click="store.deleteSelected([profile?.id])">Delete</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>

  <!-- Modal for editing profile -->
</template>

<script lang="ts">
import { defineComponent, ref } from "vue";
import {useProfileStore} from "@/stores/Profile";

export default defineComponent({
  name: "ProfileDropDown",
  props: ['profile'],
  emits: ['editClicked'],
  setup(props, { emit }) {
    const store = useProfileStore();

    const openEditModal = () => {
      emit('editClicked', props.profile);
    };

    return {
      store,
      openEditModal,
    };
  }
});
</script>