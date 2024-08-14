<template>
  <div class="mb-5 mb-xl-8">
    <div class="d-flex flex-column flex-lg-row">
      <!--begin::Sidebar-->
      <div
        class="flex-column flex-lg-row-auto w-100 w-lg-300px w-xl-400px mb-10 mb-lg-0"
      >
        <!--begin::Contacts-->
        <div class="card card-flush" v-loading="is.threadsLoading">
          <div v-if="threads.length">
            <div class="card-header pt-7">
              <div class="d-flex justify-content-center flex-column me-3">
                <a
                  href="#"
                  class="fs-4 fw-bold text-gray-900 text-hover-primary me-1 mb-2 lh-1"
                >
                  Leads </a
                ><!--begin::Info-->
                <div class="mb-0 lh-1">
                  <span class="fs-7 fw-semibold text-muted">
                    {{ threads.length }} Leads
                  </span>
                </div>
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
              >
                <div v-for="thread in threads">
                  <div
                    class="alert d-flex flex-stack py-4"
                    :class="getThreadClass(thread)"
                  >
                    <div class="d-flex align-items-center">
                      <!--begin::Avatar-->
                      <div class="symbol symbol-45px symbol-circle">
                        <img src="/media/avatars/blank.png" />
                        <div
                          v-if="thread.unread_messages_count"
                          style="top: 12px"
                          class="symbol-badge bg-danger start-100 border-4 h-10px w-10px ms-n2 mt-n2"
                        ></div>
                      </div>
                      <!--end::Avatar-->
                      <!--begin::Details-->
                      <div class="ms-5">
                        <a
                          @click="threadClicked(thread)"
                          class="fs-5 fw-bold text-gray-900 text-hover-primary mb-2 cursor-pointer"
                          >{{ thread.lead.username }}</a
                        >

                        <div class="d-flex">
                          <div class="badge badge-light text-muted me-2">
                            {{ thread.messages_count }} messages
                          </div>
                          <div class="badge badge-light-info">
                            {{ thread.lead.last_state }}
                          </div>
                        </div>
                      </div>
                      <!--end::Details-->
                    </div>
                    <!--end::Details-->
                    <!--begin::Lat seen-->
                    <div class="align-items-end ms-2">
                      <!--                      <account-thread-drop-down :thread-id="thread.id"/>-->
                      <message-drop-down :thread-id="thread.id" />
                    </div>
                    <!--end::Lat seen-->
                  </div>
                  <!--end::User-->
                  <!--begin::Separator-->
                  <div class="separator separator-dashed d-none"></div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="card-body d-flex flex-column flex-center p-10">
            <!--begin::Heading-->
            <div class="mb-2">
              <!--begin::Title-->
              <h2 class="fw-semibold text-center lh-lg text-gray-700">
                Apparently, this account
                <br />
                did not send any
                <span class="fw-bolder">messages</span>
                yet
              </h2>
              <!--end::Title-->
              <!--begin::Illustration-->
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
              <!--end::Illustration-->
            </div>
          </div>

          <!--end::Card body-->
        </div>
        <!--end::Contacts-->
      </div>
      <!--end::Sidebar-->
      <!--begin::Content-->
      <div
        class="flex-lg-row-fluid ms-lg-7 ms-xl-10"
        v-loading="is.messagesLoading"
      >
        <!--begin::Messenger-->
        <div v-if="messages.length" class="card">
          <!--begin::Card header-->

          <messenger-header :username="selectedThread?.lead?.username" />
          <!--end::Card header-->
          <!--begin::Card body-->
          <div class="card-body" id="kt_chat_messenger_body">
            <!--begin::Messages-->
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
              <!--begin::Message(in)-->
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

              <!--end::Message(template for in)-->
            </div>
            <!--end::Messages-->
          </div>
          <!--end::Card body-->
          <!--begin::Card footer-->
          <div class="card-footer pt-4" id="kt_chat_messenger_footer">
            <textarea
              v-model="message"
              class="form-control form-control-flush mb-3"
              rows="1"
              data-kt-element="input"
              placeholder="Type a message"
            ></textarea>
            <!--end::Input-->
            <!--begin:Toolbar-->
            <div class="d-flex flex-stack">
              <!--begin::Actions-->
              <el-button
                type="button"
                @click="showModal('upload_loom_modal')"
                class="btn btn-sm btn-icon btn-active-light-primary me-1"
              >
                <i class="bi bi-paperclip fs-3"></i>
              </el-button>
              <!--end::Actions-->
              <!--begin::Send-->

              <div>
                <button
                  :data-kt-indicator="is.messageSending ? 'on' : null"
                  :disabled="is.messageSending"
                  class="btn btn-primary me-2 btn-sm"
                  type="submit"
                  @click="sendMessage(sendLoom = false)"
                >
                  <span v-if="!is.messageSending" class="indicator-label">
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
          <!--end::Card footer-->
        </div>
        <div v-else class="card h-xl-100">
          <!--begin::Body-->
          <div class="card-body d-flex flex-column flex-center">
            <!--begin::Heading-->
            <div class="mb-2">
              <!--begin::Title-->
              <h1 class="fw-semibold text-gray-800 text-center lh-lg">
                Select a Lead to see the
                <br />
                <span class="fw-bolder">Messages</span>
              </h1>
              <!--end::Title-->
              <!--begin::Illustration-->
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
              <!--end::Illustration-->
            </div>
          </div>
          <!--end::Body-->
        </div>
      </div>
      <!--end::Content-->
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
import { onMounted, ref } from "vue";
import ApiService from "@/core/services/ApiService";
import MessengerHeader from "@/components/messenger-parts/MessengerHeader.vue";
import MessageIn from "@/components/messenger-parts/MessageIn.vue";
import MessageOut from "@/components/messenger-parts/MessageOut.vue";
import MessageDropDown from "@/components/messenger-parts/MessageDropDown.vue";
import { ElMessageBox } from "element-plus";
import { showModal } from "@/core/helpers/modal";
import UploadLoomModal from "@/components/modals/loom/UploadLoomModal.vue";

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

  is.value.messageSending = true;

  const data = {
    thread_id: selectedThread.value.id,
    account_id: props.id,
    lead_id: selectedThread.value.lead.id,
    text: message.value,
    sendLoom: !!sendLoom,
  };

  ApiService.post("command/create-custom-message", data)
    .then(() => threadClicked(selectedThread.value))
    .then(() => (message.value = ""))
    .finally(() => {
      getThreads();
      is.value.messageSending = false;
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
    .catch(() => {});
};

const getThreads = (withLoading = true) => {
  if (withLoading) is.value.threadsLoading = true;

  ApiService.post("threads", { account_id: props.id })
    .then((response) => (threads.value = response.data))
    .finally(() => (is.value.threadsLoading = false));
};

const threadClicked = (thread) => {
  selectedThread.value = thread;
  is.value.messagesLoading = true;
  ApiService.post("thread/view", { thread_id: thread.id })
    .then((response) => (messages.value = response.data))
    .finally(() => {
      is.value.messagesLoading = false;
      getThreads(false);
    });
};

onMounted(getThreads);
</script>

<style>
.loom-sent {
  background: #e6dbff;
}
</style>
