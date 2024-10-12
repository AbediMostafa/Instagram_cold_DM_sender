<template>
  <div class="d-flex align-items-center">
    <button
        @click="$emit('create')"
        class="btn btn-sm btn-light-success ms-2"
        :disabled="loading"
    >
      <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
      <span v-else>Create</span>
    </button>

    <button
        @click="$emit('cancel')"
        class="btn btn-sm btn-icon btn-light-success ms-2"
        :disabled="loading"
    >
      <img src="/media/icons/duotune/abstract/abs012.svg" alt="">
    </button>
  </div>
</template>

<script lang="ts">
export default {
  name: "CreateEntityButton",
  props: {
    loading: {
      type: Boolean,
      default: false,
    },
  },
};
</script>
