<template>
  <div
      class="d-flex justify-content-center mb-7 p-4 text-hover-primary btn btn-light fs-6"
      @click="$emit('displayCreateEntityPanel')"
  >
          <span class="svg-icon svg-icon-3">
              {{ text }}
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
                   xmlns="http://www.w3.org/2000/svg">
                <rect opacity="0.5" x="11.364" y="20.364" width="16" height="2" rx="1"
                      transform="rotate(-90 11.364 20.364)" fill="currentColor"></rect>
                <rect x="4.36396" y="11.364" width="16" height="2" rx="1" fill="currentColor"></rect>
              </svg>
            </span>
  </div>

</template>

<script lang="ts">
export default {
  props: ['text'],
  name: "NewEntityButton"
}
</script>