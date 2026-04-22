<template>
  <!--begin::Modal - New Target-->
  <div
      class="modal fade"
      id="add_order_modal"
      ref="newAccountModalRef"
      tabindex="-1"
      aria-hidden="true"
  >
    <!--begin::Modal dialog-->
    <div class="modal-dialog modal-dialog-centered mw-750px">
      <!--begin::Modal content-->
      <div class="modal-content rounded">
        <!--begin::Modal header-->
        <div class="modal-header pb-0 border-0 justify-content-end">
          <!--begin::Close-->
          <div
              class="btn btn-sm btn-icon btn-active-color-primary"
              data-bs-dismiss="modal"
          >
            <KTIcon icon-name="cross" icon-class="fs-1"/>
          </div>
          <!--end::Close-->
        </div>
        <!--begin::Modal header-->

        <!--begin::Modal body-->
        <div class="modal-body scroll-y px-10 px-lg-15 pt-0 pb-15">
          <!--begin::Heading-->
          <div class="mb-13 text-center">
            <h1 class="mb-3">Create New Order</h1>
          </div>

          <!--begin::Tabs-->
          <ul class="nav nav-tabs nav-line-tabs mb-8 fs-6">
            <li class="nav-item">
              <a class="nav-link" :class="{ active: activeTab === 'comment' }" href="#" @click.prevent="activeTab = 'comment'">Comment</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" :class="{ active: activeTab === 'view_story' }" href="#" @click.prevent="activeTab = 'view_story'">View Story</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" :class="{ active: activeTab === 'save_post' }" href="#" @click.prevent="activeTab = 'save_post'">Save Post</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" :class="{ active: activeTab === 'comment_and_reply' }" href="#" @click.prevent="activeTab = 'comment_and_reply'">Comment & Reply</a>
            </li>
          </ul>
          <!--end::Tabs-->

          <!--begin:Form-->
          <el-form
              id="add_order_modal_form"
              @submit.prevent="submit()"
              :model="targetData"
              :rules="rules"
              ref="formRef"
              class="form"
          >
            <div class="d-flex flex-column mb-8 fv-row">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span>Customer Name</span>
              </label>
              <el-form-item prop="customer">
                <el-input
                    v-model="targetData.customer"
                    placeholder="Enter Customer Name (optional)"
                    name="customer"
                ></el-input>
              </el-form-item>
            </div>

            <div class="d-flex flex-column mb-8 fv-row">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">Target Link</span>
              </label>
              <el-form-item prop="link">
                <el-input
                    v-model="targetData.link"
                    placeholder="Enter Target Link"
                    name="link"
                ></el-input>
              </el-form-item>
            </div>

            <div class="d-flex flex-column mb-8 fv-row" v-if="showCount">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span :class="{ required: isCountRequired }">Count</span>
              </label>
              <el-form-item prop="count">
                <el-input
                    v-model="targetData.count"
                    placeholder="Enter Count"
                    name="count"
                    type="number"
                ></el-input>
              </el-form-item>
            </div>

            <div class="d-flex flex-column mb-6 fv-row" v-if="showComments">
              <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
                <span class="required">{{ activeTab === 'comment_and_reply' ? 'Comment & Replies' : 'Comments' }}</span>
                <span v-if="activeTab === 'comment_and_reply'" class="text-muted fs-8 ms-2">(1st line = comment, rest = replies)</span>
              </label>
              <el-form-item prop="comments">
                <el-input
                    v-model="targetData.comments"
                    :rows="8"
                    type="textarea"
                    :placeholder="activeTab === 'comment_and_reply' ? 'First line: main comment\nFollowing lines: replies' : 'Enter Comments (one per line)'"
                    name="comments"
                />
              </el-form-item>
            </div>

            <!--begin::Actions-->
            <div class="text-center">
              <button
                  type="reset"
                  id="add_order_modal_cancel"
                  class="btn btn-light me-3"
                  @click="hideModal('add_order_modal')"
              >
                Cancel
              </button>

              <button
                  :data-kt-indicator="loading ? 'on' : null"
                  class="btn btn-lg btn-primary"
                  type="submit"
              >
                <span v-if="!loading" class="indicator-label">
                  Submit
                  <KTIcon icon-name="arrow-right" icon-class="fs-3 ms-2 me-0"/>
                </span>
                <span v-if="loading" class="indicator-progress">
                  Please wait...
                  <span
                      class="spinner-border spinner-border-sm align-middle ms-2"
                  ></span>
                </span>
              </button>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
.el-select {
  width: 100%;
}

.el-date-editor.el-input,
.el-date-editor.el-input__inner {
  width: 100%;
}
</style>

<script lang="ts">
import {computed, defineComponent, ref} from "vue";
import {hideModal} from "@/core/helpers/modal";
import ApiService from "@/core/services/ApiService";
import {useOrderStore} from "@/stores/Order";

export default defineComponent({
  name: "add_order_modal",
  setup() {
    const formRef = ref<null | HTMLFormElement>(null);
    const newAccountModalRef = ref<null | HTMLElement>(null);
    const loading = ref<boolean>(false);
    const store = useOrderStore();
    const activeTab = ref('comment');

    const targetData = ref({
      customer: "",
      link: "",
      count: "",
      comments: "",
    });

    // comment: comments required, no count
    // view_story: count required, no comments
    // save_post: count required, no comments
    // comment_and_reply: comments required, count optional
    const showComments = computed(() => ['comment', 'comment_and_reply'].includes(activeTab.value));
    const showCount = computed(() => ['view_story', 'save_post', 'comment_and_reply'].includes(activeTab.value));
    const isCountRequired = computed(() => ['view_story', 'save_post'].includes(activeTab.value));

    const rules = computed(() => {
      const r: any = {
        link: [
          {required: true, message: "Please input link", trigger: "blur"},
        ],
      };

      if (showComments.value) {
        r.comments = [
          {required: true, message: "Please input comments", trigger: "blur"},
        ];
      }

      if (isCountRequired.value) {
        r.count = [
          {required: true, message: "Please input count", trigger: "blur"},
        ];
      }

      return r;
    });

    const serviceCodeMap: Record<string, number> = {
      comment: 740,
      view_story: 741,
      save_post: 743,
    };

    const resetForm = () => {
      targetData.value = {
        customer: "",
        link: "",
        count: "",
        comments: "",
      };
      formRef.value?.resetFields();
    };

    const submit = () => {
      if (!formRef.value) {
        return;
      }

      formRef.value.validate((valid: boolean) => {
        if (valid) {
          loading.value = true;

          let endpoint: string;
          let payload: any;

          if (activeTab.value === 'comment_and_reply') {
            endpoint = 'api/comment-and-reply';
            payload = {
              link: targetData.value.link,
              comments: targetData.value.comments,
              quantity: targetData.value.count || 0,
              customer: targetData.value.customer || null,
            };
          } else {
            endpoint = 'api/v3';
            payload = {
              action: 'add',
              service: serviceCodeMap[activeTab.value],
              link: targetData.value.link,
              quantity: targetData.value.count,
              comments: targetData.value.comments,
              customer: targetData.value.customer || null,
            };
          }

          ApiService.post(endpoint, payload)
              .then(() => {
                resetForm();
                hideModal('add_order_modal');
                store.getOrders();
              })
              .finally(() => (loading.value = false));
        }
      });
    };

    return {
      targetData,
      submit,
      loading,
      formRef,
      rules,
      newAccountModalRef,
      hideModal,
      activeTab,
      showComments,
      showCount,
      isCountRequired,
    };
  },
});
</script>

<style lang="scss">
.override-styles {
  z-index: 99999 !important;
  pointer-events: initial;
}
</style>