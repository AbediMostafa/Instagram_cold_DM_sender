<template>
  <div class="d-flex justify-content-start mb-2">
    <!--begin::Wrapper-->
    <div class="d-flex align-items-start">
      <!--begin::User-->
<!--      <div class="d-flex align-items-center mb-2">-->
<!--        <div class="symbol symbol-35px symbol-circle">-->
<!--          <img alt="Pic" src="/media/avatars/blank.png"/>-->
<!--        </div>-->

<!--        &lt;!&ndash;begin::Details&ndash;&gt;-->
<!--        <div class="ms-3">-->
<!--          <a-->
<!--              href="#"-->
<!--              class="fs-5 fw-bold text-gray-900 text-hover-primary me-1"-->
<!--          >{{ name }}</a-->
<!--          >-->
<!--          <span class="text-muted fs-7 mb-1">{{ time }}</span>-->
<!--        </div>-->
<!--        &lt;!&ndash;end::Details&ndash;&gt;-->
<!--      </div>-->
      <!--end::User-->

      <!--begin::Text-->
      <div
          class="p-5 rounded bg-light-info text-dark fw-semibold mw-lg-400px text-start"
          id="message-text"
          style="white-space: pre-line;"
          data-kt-element="message-text"
      >
        {{ text }}
      </div>
      <span id="message-time" class="text-muted fs-7 mb-1">{{ time }}</span>

      <!--end::Text-->
    </div>
  </div>
  <!--end::Wrapper-->
</template>

<script lang="ts">
import {defineComponent} from "vue";

export default defineComponent({
  name: "message-out",
  props: {
    name: String,
    time: String,
    text: String,
  },
});
</script>

<style scoped>
#message-time {
  opacity: 0;
  transition: all 300ms ease;
}

#message-text:hover + #message-time {
  opacity: 1;
}

</style>
