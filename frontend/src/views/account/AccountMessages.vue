<template>
  <div class="mb-5 mb-xl-8">
    <div class="d-flex flex-column flex-lg-row">
      <!-- Sidebar -->
      <div
          class="flex-column flex-lg-row-auto w-100 w-lg-300px w-xl-400px mb-10 mb-lg-0"
      >
        <div class="card card-flush" v-loading="is.threadsLoading">
          <div v-if="threads.length">
            <div class="card-header pt-7">
              <div class="d-flex justify-content-center me-3">

                <div>
                  <a
                      href="#"
                      class="fs-4 fw-bold text-gray-900 text-hover-primary me-1 mb-2 lh-1"
                  >
                    Leads
                  </a>
                  <div class="mb-0 lh-1">
                  <span class="fs-7 fw-semibold text-muted">
                    {{ totalThreads }} Leads
                  </span>
                  </div>
                </div>

                <el-input
                    v-model="searchText"
                    placeholder="Search leads"
                    clearable
                    class="mb-4 w-200px ms-15"
                    @clear="getThreads()"
                >
                  <template #prepend >
                    <el-button :icon="Search" @click="debouncedGetThreads" />
                  </template>
                </el-input>



              </div>
            </div>
            <div class="card-body pt-5" id="kt_chat_contacts_body">
              <div
                  class="scroll-y me-n5 pe-5 h-200px h-lg-auto"
                  data-kt-scroll="true"
                  data-kt-scroll-activate="{default: false, lg: true}"
                  data-kt-scroll-max-height="auto"
                  data-kt-scroll-dependencies="#kt_header, #kt_toolbar, #kt_footer, #kt_chat_contacts_header"
                  data-kt-scroll-wrappers="#kt_content, #kt_chat_contacts_body"
                  data-kt-scroll-offset="5px"
                  style="max-height: 500px"
                  ref="el"
              >
                <div v-for="thread in threads" :key="thread.id">
                  <div
                      class="alert d-flex flex-stack py-4"
                      :class="getThreadClass(thread)"
                  >
                    <div class="d-flex align-items-center">
                      <div class="symbol symbol-45px symbol-circle">
                        <img src="/media/avatars/blank.png"/>
                        <div
                            v-if="thread.unread_messages_count"
                            style="top: 12px"
                            class="symbol-badge bg-danger start-100 border-4 h-10px w-10px ms-n2 mt-n2"
                        ></div>
                      </div>
                      <div class="ms-5">
                        <a
                            @click="threadClicked(thread)"
                            class="fs-5 fw-bold text-gray-900 text-hover-primary mb-2 cursor-pointer"
                        >{{ thread.lead.username }}</a>

                        <div class="d-flex">
                          <div class="badge badge-light text-muted me-2">
                            {{ thread.messages_count }} messages
                          </div>
                          <div class="badge badge-light-info">
                            {{ thread.lead.last_state }}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="align-items-end ms-2">
                      <message-drop-down :thread-id="thread.id"/>
                    </div>
                  </div>
                  <div class="separator separator-dashed d-none"></div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="card-body d-flex flex-column flex-center p-10">
            <div class="mb-2">
              <h2 class="fw-semibold text-center lh-lg text-gray-700">
                Apparently, this account
                <br/>
                did not send any
                <span class="fw-bolder">messages</span>
                yet
              </h2>
              <div class="pt-20 text-center">
                <img
                    src="/media/svg/illustrations/easy/2.svg"
                    class="theme-light-show w-200px"
                    alt=""
                />
                <img
                    src="/media/svg/illustrations/easy/2-dark.svg"
                    class="theme-dark-show w-200px"
                    alt=""
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- Content -->
      <div
          class="flex-lg-row-fluid ms-lg-7 ms-xl-10"
          v-loading="is.messagesLoading"
      >
        <div v-if="messages.length" class="card">
          <messenger-header :username="selectedThread?.lead?.username"/>
          <div class="card-body" id="kt_chat_messenger_body">
            <div
                class="scroll-y me-n5 pe-5 h-700px h-lg-auto"
                data-kt-element="messages"
                data-kt-scroll="true"
                data-kt-scroll-activate="{default: false, lg: true}"
                data-kt-scroll-max-height="auto"
                data-kt-scroll-dependencies="#kt_header, #kt_toolbar, #kt_footer, #kt_chat_messenger_header, #kt_chat_messenger_footer"
                data-kt-scroll-wrappers="#kt_content, #kt_chat_messenger_body"
                data-kt-scroll-offset="5px"
                style="max-height: 500px"
            >
              <div v-for="message in messages" :key="message.id">
                <message-out
                    v-if="message.sender === 'account'"
                    :message="message"
                />
                <message-in
                    :name="selectedThread?.lead?.username"
                    :time="message.created_at"
                    :text="message.text"
                    v-else
                />
              </div>
            </div>
          </div>
          <div class="card-footer pt-4" id="kt_chat_messenger_footer">
            <textarea
                v-model="message"
                class="form-control form-control-flush mb-3"
                rows="1"
                data-kt-element="input"
                placeholder="Type a message"
            ></textarea>
            <div class="d-flex flex-stack">
              <el-button
                  type="button"
                  @click="showModal('upload_loom_modal')"
                  class="btn btn-sm btn-icon btn-active-light-primary me-1"
              >
                <i class="bi bi-paperclip fs-3"></i>
              </el-button>
              <div>
                <button
                    :data-kt-indicator="is.messageSending ? 'on' : null"
                    :disabled="is.messageSending"
                    class="btn btn-primary me-2 btn-sm"
                    type="submit"
                    @click="sendMessage(sendLoom = false)"
                >
                  <span v-if="!is.messageSending" class="indicator-label d-flex">
                    Send
                    <KTIcon
                        icon-name="arrow-right"
                        icon-class="fs-3 ms-2 me-0"
                    />
                  </span>
                  <span v-else class="indicator-progress">
                    Please wait...
                    <span
                        class="spinner-border spinner-border-sm align-middle ms-2"
                    ></span>
                  </span>
                </button>
                <button
                    :data-kt-indicator="is.loomSending ? 'on' : null"
                    :disabled="is.loomSending"
                    class="btn btn-info me-2 btn-sm"
                    type="submit"
                    @click="sendMessage(sendLoom = true)"
                >
                  <span v-if="!is.loomSending" class="indicator-label d-flex">
                    Send Loom
                    <KTIcon
                        icon-name="arrow-right"
                        icon-class="fs-3 ms-2 me-0"
                    />
                  </span>
                  <span v-else class="indicator-progress">
                    Please wait...
                    <span
                        class="spinner-border spinner-border-sm align-middle ms-2"
                    ></span>
                  </span>
                </button>
                <button
                    :data-kt-indicator="is.refreshing ? 'on' : null"
                    :disabled="is.refreshing"
                    class="btn btn-light-success ms-2 btn-sm"
                    type="submit"
                    @click="refresh"
                >
                  <span v-if="!is.refreshing" class="indicator-label">
                    Refresh
                  </span>
                  <span v-else class="indicator-progress">
                    Please wait...
                    <span
                        class="spinner-border spinner-border-sm align-middle ms-2"
                    ></span>
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="card h-xl-100">
          <div class="card-body d-flex flex-column flex-center">
            <div class="mb-2">
              <h1 class="fw-semibold text-gray-800 text-center lh-lg">
                Select a Lead to see the
                <br/>
                <span class="fw-bolder">Messages</span>
              </h1>
              <div class="py-10 text-center">
                <img
                    src="/media/svg/illustrations/easy/1.svg"
                    class="theme-light-show w-200px"
                    alt=""
                />
                <img
                    src="/media/svg/illustrations/easy/1-dark.svg"
                    class="theme-dark-show w-200px"
                    alt=""
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <upload-loom-modal
      :account_id="props.id"
      :lead_id="selectedThread?.lead?.id"
      :thread_id="selectedThread?.id"
      @getMessages="threadClicked(selectedThread)"
  />
</template>

<script lang="ts" setup>
import {onMounted, ref} from 'vue'
import {useInfiniteScroll, useDebounceFn} from '@vueuse/core'
import ApiService from "@/core/services/ApiService";
import MessengerHeader from "@/components/messenger-parts/MessengerHeader.vue";
import MessageIn from "@/components/messenger-parts/MessageIn.vue";
import MessageOut from "@/components/messenger-parts/MessageOut.vue";
import MessageDropDown from "@/components/messenger-parts/MessageDropDown.vue";
import {ElMessageBox} from "element-plus";
import {showModal} from "@/core/helpers/modal";
import UploadLoomModal from "@/components/modals/loom/UploadLoomModal.vue";
import {Search} from '@element-plus/icons-vue'


const is = ref({
  threadsLoading: false,
  messagesLoading: false,
  messageSending: false,
  loomSending: false,
  refreshing: false,
});

const props = defineProps(["id"]);
const threads = ref([]);
const selectedThread = ref({});
const message = ref("");
const messages = ref([]);
const page = ref(1); // Current page
const totalThreads = ref(0); // Total number of threads

const el = ref(null);
const searchText = ref(""); // Add search text state

const getThreadClass = (thread) => {
  if (thread?.lead.last_state == "interested") {
    return "alert-success";
  }
  if (thread?.lead.last_state == "not interested") {
    return "alert-danger";
  }
  if (thread?.lead.last_state == "needs response") {
    return "alert-warning";
  }
  const loomStates = ["loom follow up", "unseen loom reply", "seen loom reply"];
  if (loomStates.includes(thread?.lead.last_state)) {
    return "loom-sent";
  }
};

const sendMessage = (sendLoom = false) => {
  if (message.value.trim().length === 0) return true;
  sendLoom ? is.value.loomSending = true : is.value.messageSending = true;

  const loomUrlPattern = /loom\.com/;
  if (!sendLoom && loomUrlPattern.test(message.value)) {
    ElMessageBox.confirm(
        'It looks like you are trying to send a Loom link as a custom message. Looms should send with `Sen Loom` button Are you sure you want to continue?',
        'Warning',
        {
          confirmButtonText: 'Send as Custom Message',
          cancelButtonText: 'Cancel',
          type: 'warning',
        }
    ).then(sendCustomMessage).catch(() => is.value.messageSending = false);
  } else {
    sendCustomMessage(sendLoom);
  }
};

const sendCustomMessage = (sendLoom = false) => {
  const data = {
    thread_id: selectedThread.value.id,
    account_id: props.id,
    lead_id: selectedThread.value.lead.id,
    text: message.value,
    sendLoom: !!sendLoom,
  };

  ApiService.post('command/create-custom-message', data)
      .then(() => threadClicked(selectedThread.value))
      .then(() => (message.value = ''))
      .finally(() => {
        getThreads();
        sendLoom ? is.value.loomSending = false : is.value.messageSending = false;
      });
};

const refresh = () => {
  const template = `
        <div class='notice d-flex bg-light-warning rounded border-warning border border-dashed p-6 my-5'>
          <span class="svg-icon svg-icon-2tx svg-icon-warning me-4">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect opacity="0.3" x="2" y="2" width="20" height="20" rx="10" fill="currentColor"></rect>
                  <rect x="11" y="14" width="7" height="2" rx="1" transform="rotate(-90 11 14)" fill="currentColor"></rect>
                  <rect x="11" y="17" width="2" height="2" rx="1" transform="rotate(-90 11 17)" fill="currentColor"></rect>
                </svg>
          </span>
           <div class='d-flex flex-stack flex-grow-1'>
             <div class="fw-semibold">
                  <div class="fs-6 text-gray-700">
                       Minimize the use of the refresh button as much as you can, overuse may result in your account being suspended
                  </div>
             </div>
           </div>
       </div>
     `;

  ElMessageBox.confirm(template, {
    confirmButtonText: `Refresh`,
    dangerouslyUseHTMLString: true,
    center: true,
    cancelButtonText: "Cancel",
  })
      .then(() => {
        is.value.refreshing = true;

        ApiService.post("command/create-get-directs", {
          account_id: props.id,
        }).finally(() => {
          getThreads();
          is.value.refreshing = false;
        });
      })
      .catch(() => {
      });
};

const getThreads = (withLoading = true) => {
  if (withLoading) is.value.threadsLoading = true;

  ApiService.post("threads", {
    account_id: props.id,
    page: page.value,
    search: searchText.value,
  }).then((response) => {
    if (page.value === 1) {
      threads.value = response.data.data;
    } else {
      threads.value.push(...response.data.data);
    }
    totalThreads.value = response.data.total;
  }).finally(() => is.value.threadsLoading = false);
};

const threadClicked = (thread) => {
  selectedThread.value = thread;
  is.value.messagesLoading = true;
  ApiService.post("thread/view", {thread_id: thread.id})
      .then((response) => (messages.value = response.data))
      .finally(() => {
        is.value.messagesLoading = false;
        getThreads(false);
      });
};

useInfiniteScroll(el, () => {
  if (threads.value.length >= totalThreads.value) {
    return false;
  } else {
    page.value++;
    getThreads(true);
  }
});

const debouncedGetThreads = useDebounceFn(getThreads, 500);

onMounted(() => {
  getThreads();
});
</script>

<style>
.loom-sent {
  background: #e6dbff;
}
</style>
