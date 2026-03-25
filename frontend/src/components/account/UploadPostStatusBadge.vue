<template>
  <span
      v-if="status && status !== 'none'"
      class="badge fs-9"
      :class="badgeClass"
  >
    {{ status }}
  </span>
</template>

<script lang="ts">
import {computed, defineComponent} from "vue";

export default defineComponent({
  name: "upload-post-status-badge",
  props: {
    status: {
      type: String,
      default: "none",
    },
  },
  setup(props) {
    const badgeClass = computed(() => {
      const classes = {
        connected: "badge-light-success",
        pending: "badge-light-warning",
        connecting: "badge-light-info",
        failed: "badge-light-danger",
        disconnecting: "badge-light-warning",
        none: "badge-light",
      };
      return classes[props.status] || "badge-light";
    });

    return { badgeClass };
  },
});
</script>
