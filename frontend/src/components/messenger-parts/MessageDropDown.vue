<template>
  <el-dropdown class="p-5" @click.stop>
    <a class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm">
      <KTIcon icon-name="category" icon-class="fs-3"/>
    </a>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item
            v-for="state in store.states" @click="store.changeState([threadId],state.value)">
          <a :class="`w-100 btn ${state.class} btn-sm`">{{ state.label }}</a>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script lang="ts" setup>
import {useThreadStore} from "@/stores/Thread";

const store = useThreadStore()
const props = defineProps(["threadId"])

</script>

<style>
.el-message-box {
  width: 550px !important;
  min-width: 550px !important;
}

.el-message-box__content {
  text-align: left !important;
}
</style>
