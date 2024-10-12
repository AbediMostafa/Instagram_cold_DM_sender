<template>
  <div class="d-flex align-items-center justify-content-between mb-7">
    <div class="d-flex align-items-center position-relative">
      <div>
        <span class="svg-icon svg-icon-3 position-absolute ms-3 mt-2">
          <inline-svg src="/media/icons/duotune/general/gen021.svg"/>
        </span>
        <input
            type="text"
            :value="modelValue"
            @input="$emit('update:modelValue', $event.target.value)"
            class="form-control form-control-white form-control-sm ps-9"
            placeholder="Search "
        />
      </div>
      <span class="btn btn-sm btn-light-success ms-2" @click="$emit('searchClicked')">
            Search
      </span>
      <span class="btn btn-sm btn-icon btn-light-success ms-2" @click="$emit('cancelClicked')">
          <i class="bi bi-arrow-clockwise fs-4"></i>
      </span>
    </div>

  </div>

</template>

<script lang="ts">
export default {
  props: ['modelValue'],
  name: "SearchEntity"
}
</script>