<template>
  <div class="d-flex">
    <button
        @click="$emit('updateClicked')"
        class="btn btn-sm btn-success mx-2"
        :disabled="loading"
    >
      <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
      <span v-else>Update</span>

    </button>

    <button
        @click="$emit('cancelClicked')"
        class="btn btn-icon  w-30px h-30px"
        :disabled="loading"
    >
      <!--begin::Svg Icon | path: icons/duotune/general/gen019.svg-->
      <span class="svg-icon svg-icon-3 badge badge-light-success">
        <img src="/media/icons/duotune/abstract/abs012.svg" alt="">
      </span>
      <!--end::Svg Icon-->
    </button>
  </div>
</template>

<script lang="ts">
export default {
  props: {
    loading: {
      type: Boolean,
      default: false,
    },
  },
}
</script>