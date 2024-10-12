<template>
  <div class="d-flex flex-column">
    <input class="form-control form-control-solid"
           :value="modelValue"
           @input="$emit('update:modelValue', $event.target.value)"
           v-if="ifStatement">
    <a class="text-dark text-hover-primary fs-6" v-else>{{ title }}</a>
  </div>

</template>

<script lang="ts">
export default {
  props: ['ifStatement', 'title', 'modelValue'],
  name: "EntityTitleInputPair",
}
</script>