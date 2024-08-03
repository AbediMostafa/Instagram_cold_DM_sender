<template>
  <!--begin::Navbar-->
  <div class="card mb-5 mb-xl-10">
    <div class="card-body pt-9 pb-0">
      <!--begin::Details-->
      <div class="d-flex flex-wrap flex-sm-nowrap mb-3">
        <!--begin: Pic-->
        <div class="me-7 mb-4">
          <div
              class="symbol symbol-100px symbol-lg-160px symbol-fixed position-relative"
          >
            <img :src="getAssetPath('media/avatars/blank.png')" alt="image"/>
          </div>
        </div>
        <!--end::Pic-->

        <!--begin::Info-->
        <div class="flex-grow-1">
          <!--begin::Title-->
          <div
              class="d-flex justify-content-between align-items-start flex-wrap mb-2"
          >
            <!--begin::User-->
            <div class="d-flex flex-column">
              <!--begin::Name-->
              <div class="d-flex align-items-center mb-2">
                <a
                    href="#"
                    class="text-gray-800 text-hover-primary fs-2 fw-bold me-1"
                >{{ lead.username }}</a
                >
                <lead-last-state :state="lead.last_state"/>
              </div>
              <!--end::Name-->

              <!--begin::Info-->
              <div class="d-flex flex-wrap fw-semibold fs-6 pe-2">
                <a
                    v-if="lead?.account?.last_state"
                    class="d-flex align-items-center text-gray-500 text-hover-primary me-5 mb-2">
                  <KTIcon icon-name="profile-circle" icon-class="fs-4 me-1"/>
                  {{ lead?.account?.last_state }}
                </a>
              </div>
            </div>
            <!--end::User-->

            <!--begin::Actions-->
            <div class="d-flex my-4">
              <a
                  @click="getLead"
                  class="btn btn-sm btn-light me-2"
                  id="kt_user_follow_button"
              >
                <KTIcon icon-name="check" icon-class="fs-3 d-none"/>
                Refresh
              </a>

              <a
                  href="#"
                  class="btn btn-sm btn-primary me-3"
                  data-bs-toggle="modal"
                  data-bs-target="#kt_modal_offer_a_deal"
              >Start</a
              >

              <!--begin::Menu-->
              <div class="me-0">
                <button
                    class="btn btn-sm btn-icon btn-bg-light btn-active-color-primary"
                    data-kt-menu-trigger="click"
                    data-kt-menu-placement="bottom-end"
                    data-kt-menu-flip="top-end"
                >
                  <i class="bi bi-three-dots fs-3"></i>
                </button>
                <Dropdown3></Dropdown3>
              </div>
              <!--end::Menu-->
            </div>
            <!--end::Actions-->
          </div>
          <!--end::Title-->

          <!--begin::Stats-->
          <!--end::Stats-->
        </div>
        <!--end::Info-->
      </div>
      <!--end::Details-->

      <!--begin::Navs-->
      <div class="d-flex overflow-auto h-55px">
        <ul
            class="nav nav-stretch nav-line-tabs nav-line-tabs-2x border-transparent fs-5 fw-bold flex-nowrap"
        >
          <!--begin::Nav item-->
          <li class="nav-item">
            <router-link
                :to="{name:'process-output', params:{id:account.id}}"
                class="nav-link text-active-primary me-6"
                active-class="active"
            >
              Command Output
            </router-link>
          </li>
          <!--end::Nav item-->
          <!--begin::Nav item-->
          <li class="nav-item">
            <router-link
                to="/crafted/account/settings"
                class="nav-link text-active-primary me-6"
                active-class="active"
            >
              Settings
            </router-link>
          </li>
          <!--end::Nav item-->
        </ul>
      </div>
      <!--begin::Navs-->
    </div>
  </div>
  <!--end::Navbar-->
  <router-view></router-view>
</template>

<script lang="ts">
import {getAssetPath} from "@/core/helpers/assets";
import {defineComponent, onMounted, ref} from "vue";
import Dropdown3 from "@/components/dropdown/Dropdown3.vue";
import ApiService from "@/core/services/ApiService";
import LeadLastState from "@/components/lead/LeadLastState.vue";

export default defineComponent({
  name: "kt-account",
  components: {
    LeadLastState,
    Dropdown3,
  },
  props: ['id'],
  setup(props) {

    const account = ref({});

    const getLead = () =>
        ApiService.post('lead/view', {id: props.id})
            .then(response => account.value = response.data)


    onMounted(getLead)

    return {
      account,
      getAssetPath,
      getLead,
    };
  },
});
</script>
