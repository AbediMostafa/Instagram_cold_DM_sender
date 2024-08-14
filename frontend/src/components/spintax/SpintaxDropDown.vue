<template>
  <el-dropdown class="p-5">
    <a class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm">
      <KTIcon icon-name="category" icon-class="fs-3"/>
    </a>
    <template #dropdown>
      <el-dropdown-menu class="p-3">
        <el-dropdown-item  @click="store.viewSpintax(props.id)">
            View
        </el-dropdown-item>
        <el-dropdown-item @click="store.viewSpintax(props.id)">
          Edit
        </el-dropdown-item>
        <el-dropdown-item
        >Delete
        </el-dropdown-item>
        <el-dropdown-item divided>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>

</template>

<script setup lang="ts">

import {useSpintaxStore} from "@/stores/Spintax";
import { defineProps } from "vue";

const props = defineProps(['id']);
const store = useSpintaxStore()


</script>

<style>
.fill-flex a {
  flex: 1 !important;
}
</style>
