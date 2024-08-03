<template>
  <div class="d-flex justify-content-end mb-2">
    <!--begin::Wrapper-->
    <div>
      <div
        class="d-flex align-items-center"
        id="message-text"
        v-if="props.message?.type == 'text'"
      >
        <div
          class="p-5 rounded bg-light-primary text-dark fw-semibold mw-lg-400px"
          style="white-space: pre-line"
          data-kt-element="message-text"
        >
          {{ props.message.text }}
        </div>
        <message-state :state="props.message.state" />
      </div>
      <div
        class="d-flex align-items-center"
        v-if="props.message?.type == 'loom'"
        id="message-text"
      >
        <loom-card
          card_style="width:250px; height: auto; object-fit: cover"
          :loom="props.message.messageable"
        />
        <message-state :state="props.message.state" />
      </div>
      <span id="message-time" class="text-muted fs-7 mb-1">{{ props.message.created_at }}</span>
      <!--end::Text-->
    </div>
    <!--end::Wrapper-->
  </div>
</template>

<script setup lang="ts">
import { defineProps } from "vue";
import LoomCard from "@/components/loom/LoomCard.vue";
import MessageState from "@/components/messenger-parts/MessageState.vue";
const props = defineProps(["message"]);
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
