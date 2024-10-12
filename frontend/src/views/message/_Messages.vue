<template>
  <div class="card mb-5 mb-xl-8">
    <!--begin::Header-->
    <div class="card-header border-0 pt-5 mb-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">Messages</span>
        <span class="fw-semibold text-muted fs-7 d-block lh-1">
          {{ messages.total }} Messages
        </span>
      </h3>
      <div class="card-toolbar">
        <div class="me-2">
          <el-input
              v-model="messages.serverData.search.text"
              placeholder="Please input"
              class="input-with-select"
              clearable
          >
            <template #prepend>
              <el-button :icon="Search" @click="getMessages"/>
            </template>
            <template #append>
              <el-select v-model="messages.serverData.search.type" placeholder="Select" style="width: 115px">
                <el-option label="Account" value="account"/>
                <el-option label="Lead" value="lead"/>
                <el-option label="Message" value="message"/>
              </el-select>
            </template>
          </el-input>
        </div>

        <div>
          <el-checkbox-group
              v-model="messages.serverData.filters"
              size="default"
          >
            <el-checkbox-button
                v-for="action in messageActions"
                :key="action.value"
                :value="action.value"
                :label="action.label"
                class="text-muted text-gray-400"
                @click="actionClicked"
            >
              {{ action.value }}
            </el-checkbox-button>
          </el-checkbox-group>
        </div>
        <a class="btn btn-sm btn-success ms-2" @click="getMessages">Refresh </a>

      </div>
    </div>
    <!--end::Header-->

    <div class="card-body py-3">
      <!--begin::Table container-->
      <div class="table-responsive">
        <table
            class="table table-row-bordered table-row-gray-100 align-middle gs-0 gy-3"
            v-loading="loading"
        >
          <!--begin::Table head-->
          <thead>
          <tr class="fw-bold text-muted">
            <td>
              <div class="d-flex align-items-center">
                <div class="col-3">LEAD</div>
                <div class="col-7">MESSAGE</div>
                <div class="col-2 text-end">ACTION</div>
              </div>
            </td>
          </tr>
          </thead>
          <!--begin::Table body-->
          <tbody>
          <tr
              class="alert"
              :class="`alert-${getMessageClass(message)}`"
              v-for="(message, index) in messages.data"
              :key="index"
          >
            <td>
              <div class="d-flex align-items-center w-100">
                <div class="col-3">
                  <div class="d-flex fs-7 align-items-center">
                    <div class="me-2">
                      <new-message-icon
                          class="text-success fs-2hx"
                          v-if="message.state === 'unseen'"
                      />
                      <pending-message-icon
                          class="text-warning fs-2hx"
                          v-if="message.state === 'pending'"
                      />
                      <sent-message-icon
                          class="fs-2hx"
                          v-if="message.state === 'seen'"
                      />
                    </div>

                    <div>
                      <router-link
                          :to="{
                            name: 'messages',
                            params: { id: message?.thread?.account?.id },
                          }"
                      >
                        <a
                            class="text-gray-900 fw-bold text-hover-primary fs-6"
                        >
                          {{ message?.thread?.lead?.username }}</a
                        >
                        <span
                            v-if="message.sender == 'lead'"
                            :class="`badge-${getMessageClass(message)}`"
                            class="badge ms-1">{{ message?.thread?.lead.last_state }}</span>
                      </router-link>
                      <div class="text-muted">
                        {{ message?.thread?.account?.username }}
                      </div>
                    </div>
                  </div>
                </div>
                <div class="col-8">
                  <div
                      :class="message.state === 'unseen' && 'fw-bold'"
                      class="text-gray-700 fs-7"
                      v-html="message?.text"
                  >
                  </div>
                </div>
                <div class="col-1 text-end">
                  <message-drop-down
                      :message-id="message.id"
                      :thread-id="message?.thread?.id"
                  />
                </div>
              </div>

              <div class="d-flex flex-stack flex-wrap">
                <div
                    class="d-flex align-items-center collapsible toggle collapsed w-100"
                    data-bs-toggle="collapse"
                    :data-bs-target="`#message_number_${message.id}`"
                    aria-expanded="false"
                >
                  <div
                      class="btn btn-sm btn-icon btn-active-color-primary ms-n3 me-2"
                  >
                    <KTIcon
                        icon-name="minus-square"
                        icon-class="toggle-on text-primary fs-2"
                    />
                    <KTIcon
                        icon-name="plus-square"
                        icon-class="toggle-off fs-2"
                    />
                  </div>
                  <a href="#">Reply</a>
                </div>
              </div>
              <div
                  :id="`message_number_${message.id}`"
                  class="fs-6 ps-10 collapse"
              >
                <div class="card-footer pt-4" id="kt_chat_messenger_footer">
                    <textarea
                        v-model="texts[message.id]"
                        class="form-control form-control-flush mb-3"
                        placeholder="Type a message"
                    ></textarea
                    ><!--end::Input--><!--begin:Toolbar-->
                  <div class="d-flex flex-stack">
                    <!--begin::Send-->
                    <div>
                      <button
                          class="btn btn-sm btn-primary"
                          type="submit"
                          @click="sendMessage(message.id, texts[message.id])"
                      >
                        <span v-if="!sendingMessage" class="indicator-label">
                            Send
                            <KTIcon
                                icon-name="arrow-right"
                                icon-class="fs-3 ms-2 me-0"
                            />
                          </span>
                        <span v-else>
                            <span class="spinner-border spinner-border-sm align-middle ms-2"></span>
                            Please wait...

                          </span>
                      </button>
                      <button
                          class="btn btn-sm btn-info ms-1"
                          type="submit"
                          @click="sendMessage(message.id, texts[message.id], true)"
                      >
                        <span v-if="!sendingLoom" class="indicator-label">
                            Send Loom
                            <KTIcon
                                icon-name="arrow-right"
                                icon-class="fs-3 ms-2 me-0"
                            />
                          </span>
                        <span v-else>
                            <span class="spinner-border spinner-border-sm align-middle ms-2"></span>
                            Please wait...

                          </span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </td>
          </tr>
          </tbody>
          <!--end::Table body-->
        </table>
        <!--end::Table-->
        <el-pagination
            :current-page="messages.serverData.page"
            :page-size="configStore.pagination?.each_page?.messages"
            layout="prev, pager, next"
            :total="messages.total"
            @current-change="(page) => changePageGetMessages(page)"
        />
      </div>
      <!--end::Table container-->
    </div>
    <!--begin::Body-->
  </div>
</template>

<script lang="ts" setup>
import {onMounted, ref} from "vue";
import {onBeforeRouteLeave} from "vue-router";
import ApiService from "@/core/services/ApiService";
import {useAppConfigStore} from "@/stores/AppConfig";
import MessageDropDown from "@/components/messenger-parts/MessageDropDown.vue";
import {useDebounceFn} from "@vueuse/core";
import NewMessageIcon from "@/components/icons/NewMessageIcon.vue";
import PendingMessageIcon from "@/components/icons/PendingMessageIcon.vue";
import SentMessageIcon from "@/components/icons/SentMessageIcon.vue";
import {ElMessageBox} from "element-plus";
import { Search } from '@element-plus/icons-vue'

const loading = ref(false);
const sendingMessage = ref(false);
const sendingLoom = ref(false);
const configStore = useAppConfigStore();
const messages = ref({
  data: [],
  serverData: {
    page: 1,
    filters: [],
    search:{
      text:'',
      type:''
    }
  },
  total: 0,
});
const texts = ref({});

const messageActions = ref([
  {value: "Interested", label: "interested"},
  {value: "Not Interested", label: "not interested"},
  {value: "Needs Response", label: "needs response"},
  {value: "Loom Sent", label: "loom follow up"},
  {value: "Call Booked", label: "call booked"},
]);

const actionClicked = useDebounceFn(() => getMessages(), 1000);

const changePageGetMessages = (page) => {
  messages.value.serverData.page = page;
  getMessages();
};

const getMessages = (withLoading = true) => {
  if (withLoading) loading.value = true;

  ApiService.post("messages", messages.value.serverData)
      .then((response) => {
        messages.value.data = response.data.data;
        messages.value.total = response.data.total;
      })
      .finally(() => {
        loading.value = false;
      });
};

const getMessageClass = (message) => {
  if (message.sender != "lead") {
    return false;
  }

  if (message?.thread?.lead.last_state == "interested") {
    return "success";
  }

  if (message?.thread?.lead.last_state == "not interested") {
    return "danger";
  }

  if (message?.thread?.lead.last_state == "needs response") {
    return "warning";
  }

  if (message?.thread?.lead.last_state == "call booked") {
    return "primary";
  }

  const loomStates = ["loom follow up", "unseen loom reply", "seen loom reply"];

  if (loomStates.includes(message?.thread?.lead.last_state)) {
    return "loom-sent";
  }
};
onMounted(getMessages);

const sendMessage = (messageId, text, sendLoom = false) => {
  if (text.trim().length === 0) return true;

  const loomUrlPattern = /loom\.com/;
  sendLoom ? sendingLoom.value = true : sendingMessage.value = true;

  if (!sendLoom && loomUrlPattern.test(text)) {
    ElMessageBox.confirm(
        'It looks like you are trying to send a Loom link as a custom message. Looms should send with `Sen Loom` button Are you sure you want to continue?',
        'Warning',
        {
          confirmButtonText: 'Send as Custom Message',
          cancelButtonText: 'Cancel',
          type: 'warning',
        }
    ).then(() => sendCustomMessage(messageId, text, sendLoom = false))
        .catch(() => sendingMessage.value = false);
  } else {
    // If it's not a Loom URL or it's a Loom message, proceed as normal
    sendCustomMessage(messageId, text, sendLoom);
  }
};

const sendCustomMessage = (messageId, text, sendLoom = false) => {
  ApiService.post(
      "command/create-custom-message-with-message_id",
      {messageId, text, sendLoom}
  ).then(() => {
    sendLoom ? sendingLoom.value = false : sendingMessage.value = false
  })

}
</script>

<style>
.alert-loom-sent {
  background: #e6dbff;
}

.el-checkbox-button__inner{
  color: #a8aab4;
}

</style>
