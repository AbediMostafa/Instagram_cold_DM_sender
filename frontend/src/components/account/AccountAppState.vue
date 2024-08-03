<template>
  <span v-if="state==='idle'" class="badge py-2 px-3 fs-7 badge-secondary text-gray-600 ">{{ state }}</span>
  <span v-else class="badge py-2 px-3 fs-7 badge-light-success">{{ state }}</span>
</template>

<script lang="ts">
import {defineComponent} from "vue";

export default defineComponent({
  name: "account-app-state",
  props: {
    state: String,
  },
});
</script>
