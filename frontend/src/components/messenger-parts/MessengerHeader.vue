<template>
  <div class="card-header" id="kt_chat_messenger_header">
    <!--begin::Title-->
    <div class="card-title">
      <!--begin::User-->
      <div class="d-flex justify-content-center flex-column me-3">
        <a class="fs-4 fw-bold text-gray-900 text-hover-primary me-1 mb-2 lh-1">{{ username }}</a>
        <!--begin::Info-->
        <div class="mb-0 lh-1">
          <span class="badge badge-success badge-circle w-10px h-10px me-1"></span>
          <span class="fs-7 fw-semibold text-muted">Active</span>
        </div>
        <!--end::Info-->
      </div>
      <!--end::User-->
    </div>
    <!--end::Title-->
    <!--begin::Card toolbar-->
    <div class="card-toolbar">
      <!--begin::Menu-->
      <div class="me-n3">
        <button class="btn btn-sm btn-icon btn-active-light-primary" data-kt-menu-trigger="click"
                data-kt-menu-placement="bottom-end">
          <i class="bi bi-three-dots fs-2"></i>
        </button>
        <!--begin::Menu 3-->
        <div
            class="menu menu-sub menu-sub-dropdown menu-column menu-rounded menu-gray-800 menu-state-bg-light-primary fw-semibold w-200px py-3"
            data-kt-menu="true" style="">
          <!--begin::Heading-->
          <div class="menu-item px-3">
            <div class="menu-content text-muted pb-2 px-3 fs-7 text-uppercase">Contacts</div>
          </div>
          <!--end::Heading-->
          <!--begin::Menu item-->
          <div class="menu-item px-3">
            <a href="#" class="menu-link px-3" data-bs-toggle="modal" data-bs-target="#kt_modal_users_search">Add
              Contact</a>
          </div>
          <!--end::Menu item-->
          <!--begin::Menu item-->
          <div class="menu-item px-3">
            <a href="#" class="menu-link flex-stack px-3" data-bs-toggle="modal"
               data-bs-target="#kt_modal_invite_friends">Invite Contacts
              <i class="fas fa-exclamation-circle ms-2 fs-7" data-bs-toggle="tooltip"
                 aria-label="Specify a contact email to send an invitation" data-kt-initialized="1"></i></a>
          </div>
          <!--end::Menu item-->
          <!--begin::Menu item-->
          <div class="menu-item px-3" data-kt-menu-trigger="hover" data-kt-menu-placement="right-start">
            <a href="#" class="menu-link px-3">
              <span class="menu-title">Groups</span>
              <span class="menu-arrow"></span>
            </a>
            <!--begin::Menu sub-->
            <div class="menu-sub menu-sub-dropdown w-175px py-4">
              <!--begin::Menu item-->
              <div class="menu-item px-3">
                <a href="#" class="menu-link px-3" data-bs-toggle="tooltip" data-kt-initialized="1">Create
                  Group</a>
              </div>
              <!--end::Menu item-->
              <!--begin::Menu item-->
              <div class="menu-item px-3">
                <a href="#" class="menu-link px-3" data-bs-toggle="tooltip" data-kt-initialized="1">Invite
                  Members</a>
              </div>
              <!--end::Menu item-->
              <!--begin::Menu item-->
              <div class="menu-item px-3">
                <a href="#" class="menu-link px-3" data-bs-toggle="tooltip" data-kt-initialized="1">Settings</a>
              </div>
              <!--end::Menu item-->
            </div>
            <!--end::Menu sub-->
          </div>
          <!--end::Menu item-->
          <!--begin::Menu item-->
          <div class="menu-item px-3 my-1">
            <a href="#" class="menu-link px-3" data-bs-toggle="tooltip" data-kt-initialized="1">Settings</a>
          </div>
          <!--end::Menu item-->
        </div>
        <!--end::Menu 3-->
      </div>
      <!--end::Menu-->
    </div>
    <!--end::Card toolbar-->
  </div>

</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "message-out",
  props: {
    username: String,
  },
});
</script>
