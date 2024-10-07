<template>
  <div class="card mb-5 mb-xl-8">
    <!--begin::Header-->
    <div class="card-header border-0 pt-5 mb-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">Threads</span>
        <span class="fw-semibold text-muted fs-7 d-block lh-1">
          {{ store.threads.total }} Threads
        </span>
      </h3>
      <div class="card-toolbar">
        <div class="me-2">
          <el-checkbox-group
              v-model="store.threads.filters"
              size="default"
          >
            <el-checkbox-button
                v-for="action in store.messageActions"
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
        <a class="btn btn-sm btn-success ms-2" @click="store.getThreads">Refresh </a>
        <button
            type="button"
            class="btn btn-sm btn-icon btn-color-primary btn-active-light-primary ms-2"
            data-kt-menu-trigger="click"
            data-kt-menu-placement="bottom-end"
            data-kt-menu-flip="top-end"
        >
          <KTIcon icon-name="category" icon-class="fs-2"/>
          <messages-drop-down/>
        </button>
      </div>
    </div>
    <!--end::Header-->

    <div class="card-body py-3">
      <!--begin::Table container-->
      <div class="table-responsive">
        <table
            class="table table-row-bordered table-row-gray-100 align-middle gs-0 gy-3"
            v-loading="store.is.loading"
        >
          <!--begin::Table head-->
          <thead>
          <tr class="fw-bold text-muted">
            <td>
              <div class="d-flex align-items-center">
                <div class="col-3">
                  <div class="d-flex">
                    <div
                        class="form-check form-check-sm form-check-custom form-check-solid me-2"
                    >
                      <input
                          class="form-check-input"
                          type="checkbox"
                          @change="store.checkRows($event)"
                      />
                    </div>
                    LEAD
                  </div>
                  </div>
                <div class="col-6">MESSAGE</div>
                <div class="col-2">CATEGORY</div>
                <div class="col-1 text-end">ACTION</div>
              </div>
            </td>
          </tr>
          </thead>
          <!--begin::Table body-->
          <tbody>
          <tr
              class="alert"
              :class="`alert-${getMessageClass(thread)}`"
              v-for="(thread, index) in store.threads.data"
              :key="index"
          >
            <td>
              <div class="d-flex align-items-center w-100">
                <div class="col-3">

                  <div class="d-flex fs-7 align-items-center">
                    <div class="me-2 d-flex align-items-center">
                      <div
                          class="form-check form-check-sm form-check-custom form-check-solid me-2"
                      >
                        <input
                            class="form-check-input widget-13-check"
                            type="checkbox"
                            :value="thread.id"
                            v-model="store.checkedThreadsRows"
                        />
                      </div>

                      <new-message-icon
                          class="text-success fs-2hx"
                          v-if="hasMessageOf(thread, 'unseen')"
                      />
                      <pending-message-icon
                          class="text-warning fs-2hx"
                          v-else-if="hasMessageOf(thread, 'pending')"
                      />
                      <sent-message-icon
                          class="fs-2hx"
                          v-else
                      />
                    </div>

                    <div>
                      <router-link
                          :to="{
                            name: 'messages',
                            params: { id: thread?.account?.id },
                          }"
                      >
                        <a class="text-gray-900 fw-bold text-hover-primary fs-6">{{ thread?.lead?.username }}</a>
                        <span
                            :class="`badge-${getMessageClass(thread)}`"
                            class="badge ms-1"
                        >{{ thread?.lead.last_state }}</span
                        >
                      </router-link>
                      <div class="text-muted">
                        {{ thread?.account?.username }}
                      </div>
                    </div>
                  </div>
                </div>
                <div class="col-6 px-2">
                  <div
                      :class="thread.messages[thread.messages.length-1]?.state === 'unseen' && 'fw-bold'"
                      class="text-gray-700 fs-7"
                      v-html="thread.messages[thread.messages.length-1].text"

                  ></div>

                </div>
                <div class="col-2">{{thread.category?.title}}</div>
                <div class="col-1 text-end">
                  <message-drop-down :thread-id="thread?.id"/>
                </div>
              </div>

              <div class="d-flex flex-stack flex-wrap">
                <div
                    class="d-flex align-items-center collapsible toggle collapsed w-100"
                    data-bs-toggle="collapse"
                    :data-bs-target="`#message_number_${thread.id}`"
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
                  :id="`message_number_${thread.id}`"
                  class="fs-6 ps-10 collapse"
              >
                <div class="flex-lg-row-fluid ms-lg-7 ms-xl-10">
                  <div v-if="thread.messages.length" class="card">
                    <messenger-header :username="thread?.lead?.username"/>
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
                        <div v-for="message in thread.messages" :key="message.id">
                          <message-out
                              v-if="message.sender === 'account'"
                              :message="message"
                          />
                          <message-in
                              :name="thread?.lead?.username"
                              :time="message.created_at"
                              :text="message.text"
                              v-else
                          />
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

                <div class="card-footer pt-4" id="kt_chat_messenger_footer">
                    <textarea
                        v-model="texts[thread.id]"
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
                          @click="sendMessage(thread, texts[thread.id])"
                      >
                          <span v-if="!sendingMessage" class="indicator-label">
                            Send
                            <KTIcon
                                icon-name="arrow-right"
                                icon-class="fs-3 ms-2 me-0"
                            />
                          </span>
                        <span v-else>
                            <span
                                class="spinner-border spinner-border-sm align-middle ms-2"
                            ></span>
                            Please wait...
                          </span>
                      </button>
                      <button
                          class="btn btn-sm btn-info ms-1"
                          type="submit"
                          @click=" sendMessage(thread, texts[thread.id], true)"
                      >
                          <span v-if="!sendingLoom" class="indicator-label">
                            Send Loom
                            <KTIcon
                                icon-name="arrow-right"
                                icon-class="fs-3 ms-2 me-0"
                            />
                          </span>
                        <span v-else>
                            <span
                                class="spinner-border spinner-border-sm align-middle ms-2"
                            ></span>
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
            :current-page="store.threads.page"
            :page-size="configStore.pagination?.each_page?.messages"
            layout="prev, pager, next"
            :total="store.threads.total"
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
import ApiService from "@/core/services/ApiService";
import {useAppConfigStore} from "@/stores/AppConfig";
import {useThreadStore} from "@/stores/Thread";
import MessageDropDown from "@/components/messenger-parts/MessageDropDown.vue";
import {useDebounceFn} from "@vueuse/core";
import NewMessageIcon from "@/components/icons/NewMessageIcon.vue";
import PendingMessageIcon from "@/components/icons/PendingMessageIcon.vue";
import SentMessageIcon from "@/components/icons/SentMessageIcon.vue";
import {ElMessageBox} from "element-plus";
import MessageIn from "@/components/messenger-parts/MessageIn.vue";
import MessengerHeader from "@/components/messenger-parts/MessengerHeader.vue";
import MessageOut from "@/components/messenger-parts/MessageOut.vue";
import MessagesDropDown from "@/components/message/MessagesDropDown.vue";

const loading = ref(false);
const sendingMessage = ref(false);
const sendingLoom = ref(false);
const configStore = useAppConfigStore();
const store = useThreadStore()
const texts = ref({});

const actionClicked = useDebounceFn(() => store.getThreads(), 1000);

const changePageGetMessages = (page) => {
  store.threads.page = page;
  store.getThreads();
};

const getMessageClass = (thread) => {
  // if (message.sender != "lead") {
  //   return false;
  // }

  if (thread?.lead?.last_state == "interested") {
    return "success";
  }

  if (thread?.lead?.last_state == "not interested") {
    return "danger";
  }

  if (thread?.lead?.last_state == "needs response") {
    return "warning";
  }

  if (thread?.lead?.last_state == "call booked") {
    return "primary";
  }

  const loomStates = ["loom follow up", "unseen loom reply", "seen loom reply"];

  if (loomStates.includes(thread?.lead?.last_state)) {
    return "loom-sent";
  }
};
onMounted(store.getThreads);

const sendMessage = (thread, text, sendLoom = false) => {
  if (text.trim().length === 0) return true;

  const loomUrlPattern = /loom\.com/;
  sendLoom ? (sendingLoom.value = true) : (sendingMessage.value = true);

  if (!sendLoom && loomUrlPattern.test(text)) {
    ElMessageBox.confirm(
        "It looks like you are trying to send a Loom link as a custom message. Looms should send with `Sen Loom` button Are you sure you want to continue?",
        "Warning",
        {
          confirmButtonText: "Send as Custom Message",
          cancelButtonText: "Cancel",
          type: "warning",
        }
    )
        .then(() => sendCustomMessage(thread, text, (sendLoom = false)))
        .catch(() => (sendingMessage.value = false));
  } else {
    // If it's not a Loom URL or it's a Loom message, proceed as normal
    sendCustomMessage(thread, text, sendLoom);
  }
};

const sendCustomMessage = (thread, text, sendLoom = false) => {
  ApiService.post("command/create-custom-message", {
    thread_id: thread.id,
    account_id: thread?.account?.id,
    lead_id: thread?.lead?.id,
    text,
    sendLoom,
  }).then(() => {
    sendLoom ? (sendingLoom.value = false) : (sendingMessage.value = false);
  });
};

const hasMessageOf = (thread, _type) => thread.messages.some(message => message.state == _type);
</script>

<style>
.alert-loom-sent {
  background: #e6dbff;
}

.el-checkbox-button__inner {
  color: #a8aab4;
}

.badge-loom-sent {
  color: #ffffff;
  background-color: #36a39e;
}

</style>
