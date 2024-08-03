<template>
  <div class="mb-5 mb-xl-8 card" v-loading="loading">
    <div class="card-header border-0pt-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">Process output</span>
      </h3>

      <div class="card-toolbar">
        <a @click="getProcessOutput" class="btn btn-sm btn-light-primary">Refresh</a>
        <a @click="deleteProcessOutput" class="btn btn-sm btn-light-danger ms-2">Delete</a>
      </div>
    </div>

    <div class="card-body py-3">
      <div class="editor p-5 rounded">
        <div v-for="output in processOutput">
          [ {{ output.created_at }} ] : {{ output.log }}
        </div>

        <div>
          <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <circle class="spinner_b2T7" cx="4" cy="12" r="3"/>
            <circle class="spinner_b2T7 spinner_YRVV" cx="12" cy="12" r="3"/>
            <circle class="spinner_b2T7 spinner_c9oY" cx="20" cy="12" r="3"/>
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>

import {ref} from "vue";
import ApiService from "@/core/services/ApiService";
import {onBeforeRouteLeave} from "vue-router";

const loading = ref(true);
const processOutput = ref({});
const props = defineProps(['id']);

const getProcessOutput = (withLoading = true) => {
  if (withLoading)
    loading.value = true;

  ApiService.post('clis', {account_id: props.id})
      .then(response => processOutput.value = response.data)
      .finally(() => loading.value = false)
}

const getProcessWithInterval = setInterval(() => getProcessOutput(false), 4000)

onBeforeRouteLeave(() => clearInterval(getProcessWithInterval))
</script>

<style>
.editor {
  background: black;
  color: #cdcccc;
  font-family: monospace;
  font-size: 14px;
  overflow-y: auto;
  height: 500px
}

.spinner_b2T7 {
  animation: spinner_xe7Q .8s linear infinite
}

.spinner_YRVV {
  animation-delay: -.65s
}

.spinner_c9oY {
  animation-delay: -.5s
}

@keyframes spinner_xe7Q {
  93.75%, 100% {
    r: 3px
  }
  46.875% {
    r: .2px
  }
}
</style>