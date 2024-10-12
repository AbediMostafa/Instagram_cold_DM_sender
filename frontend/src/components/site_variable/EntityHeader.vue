<template>
  <div class="card-header border-0 pt-5">
    <h3 class="card-title align-items-start flex-column">
      <span class="card-label fw-bold text-dark">{{ plural }}</span>
      <span class="text-muted mt-1 fw-semibold fs-7">{{ total }}</span>
    </h3>
  </div>

</template>

<script lang="ts">
export default {
  props: ['plural', 'total'],
  name: "EntityHeader.vue"
}
</script>