<template>
  <span class="badge badge-light-warning" v-if="props.state === 'uploaded'">{{ props.state }}</span>
  <span class="badge badge-light-info" v-if="props.state === 'pending'">{{ props.state }}</span>
  <span class="badge badge-light-success" v-if="props.state === 'sent'">{{ props.state }}</span>
</template>

<script setup lang="ts">
import {defineProps} from "vue";

const props = defineProps(["state"]);
</script>
