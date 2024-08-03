<template>
  <span v-if="isActive" class="badge py-2 px-3 fs-7 badge-light-success">active</span>
  <span v-else class="badge py-2 px-3 fs-7 badge-secondary text-gray-600 ">inactive</span>
</template>

<script lang="ts">
import {defineComponent} from "vue";

export default defineComponent({
  name: "account-is-active",
  props: ['isActive'],
});
</script>
