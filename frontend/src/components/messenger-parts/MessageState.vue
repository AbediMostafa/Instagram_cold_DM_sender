<template>
  <div class="ms-2">
    <i v-if="props.state == 'pending'" class="ki-duotone ki-time fs-2x">
      <span class="path1"></span>
      <span class="path2"></span>
    </i>

    <i v-else class="ki-duotone ki-double-check text-success fs-2x">
      <span class="path1"></span>
      <span class="path2"></span>
    </i>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from "vue";

const props = defineProps(["state"]);
</script>
