<template>
  <span class="badge badge-light-primary ms-1" v-if="state==='active'">{{ state }}</span>
  <span class="badge badge-light-warning ms-1" v-else-if="state==='challenging'">{{ state }}</span>
  <span class="badge badge-light-warning ms-1" v-else-if="state==='follow ban'">{{ state }}</span>
  <span class="badge badge-light-danger ms-1" v-else-if="state==='suspended'">{{ state }}</span>
  <span class="badge badge-light-info ms-1" v-else-if="state==='action ban'">{{ state }}</span>
  <span class="badge badge-light-info ms-1" v-else>{{ state }}</span>
</template>

<script lang="ts">
import {defineComponent} from "vue";

export default defineComponent({
  name: "account-instagram-state",
  props: {
    state: String,
  },
});
</script>
