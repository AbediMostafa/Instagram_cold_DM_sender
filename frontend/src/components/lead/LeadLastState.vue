<template>
  <span class="badge ms-2" :class="`badge-light-${classType(state)}`">{{ state }}</span>
</template>

<script lang="ts">
import {defineComponent} from "vue";

export default defineComponent({
  name: "lead-last-state",
  props: {
    state: String,
  },

  setup() {
    const classType = state => {
      return {
        'free': 'primary',
        'followed': 'success',
        'dm follow up': 'success',
        'unseen dm reply': 'success',
        'seen dm reply': 'success',
        'auto dm reply': 'success',
        'interested': 'info',
        'failed dm': 'danger',
        'not interested': 'danger',
        'loom follow up': 'info',
        'unseen loom reply': 'info',
        'seen loom reply': 'info',
      }[state]
    }

    return {
      classType
    }
  }
});
</script>
