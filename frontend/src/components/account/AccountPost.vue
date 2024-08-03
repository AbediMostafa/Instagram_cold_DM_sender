<template>
  <span v-if="post" class="badge py-2 px-3 fs-7 badge-light-success">yes</span>
  <span v-else class="badge py-2 px-3 fs-7 badge-secondary text-gray-600 ">no</span>
</template>

<script lang="ts">
import {defineComponent} from "vue";

export default defineComponent({
  name: "account-post",
  props: ['post'],
});
</script>
