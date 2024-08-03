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
      const stateText = {
        "dm follow up": {
          title: "autoreply",
          text: 'The lead will be returned to the "follow-up" status, and we will send a follow-up request every 48 hours',
        },

        interested: {
          title: "is positive",
          text: 'The lead will be marked as "interested" and will await the Loom video.',
        },

        "not interested": {
          title: "is negative",
          text: 'The lead will be marked as "not interested" and will be removed from the direct message (DM) cycle.',
        },

        "needs response": {
          title: "needs response",
          text: "The lead will be out of the follow-up cycle until the end of the conversation",
        },

        "loom follow up": {
          title: "Loom sent",
          text: "We will initiate the Loom follow-up, sending an appropriate message every 48 hours",
        },
      };

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
