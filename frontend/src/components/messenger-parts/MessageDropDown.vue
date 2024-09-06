<template>
  <el-dropdown class="p-5" @click.stop>
    <a class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm">
      <KTIcon icon-name="category" icon-class="fs-3" />
    </a>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item @click="changeThreadState('interested')">
          <a class="w-100 btn btn-light-success btn-sm">is positive</a>
        </el-dropdown-item>

        <el-dropdown-item @click="changeThreadState('not interested')">
          <a class="w-100 btn btn-light-danger btn-sm">is negative</a>
        </el-dropdown-item>

        <el-dropdown-item @click="changeThreadState('needs response')">
          <a class="w-100 btn btn-light-warning btn-sm">needs response</a>
        </el-dropdown-item>

        <el-dropdown-item @click="changeThreadState('loom follow up')">
          <a class="w-100 btn btn-light-info btn-sm">loom sent</a>
        </el-dropdown-item>

        <el-dropdown-item @click="changeThreadState('dm follow up')">
          <a class="w-100 btn btn-light-primary btn-sm">autoreply</a>
        </el-dropdown-item>

        <el-dropdown-item @click="changeThreadState('call booked')">
          <a class="w-100 btn btn-primary btn-sm">call booked</a>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import { useAccountStore } from "@/stores/Account";
import { showModal } from "@/core/helpers/modal";
import ApiService from "@/core/services/ApiService";
import { ElMessageBox } from "element-plus";

export default defineComponent({
  name: "message-drop-down",
  props: ["threadId", "messageId"],
  setup(props) {
    const changeThreadState = (state) => {
      const data = {
        threadId: props.threadId,
        state,
        messageId: props.messageId,
      };
      ApiService.post("lead/change-state", data);
    };

    return {
      showModal,
      changeThreadState,
      store: useAccountStore(),
    };
  },
});
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
