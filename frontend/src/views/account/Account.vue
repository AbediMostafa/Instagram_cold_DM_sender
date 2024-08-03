<template>
  <!--begin::Navbar-->
  <div class="card mb-5 mb-xl-10">
    <div class="card-body pt-9 pb-0" v-loading="loading">
      <!--begin::Details-->
      <div class="d-flex flex-wrap flex-sm-nowrap mb-3">
        <!--begin: Pic-->
        <div class="me-7 mb-4">
          <div
            class="symbol symbol-100px symbol-lg-160px symbol-fixed position-relative"
          >
            <img
              v-if="account.avatar_changed"
              :src="getAvatarPath(account)"
              @error="(e) => (e.target.src = '/media/avatars/blank.png')"
            />
            <img v-else src="/media/avatars/blank.png" />
            <div
              :class="account.is_active ? 'bg-success' : 'bg-danger'"
              class="position-absolute translate-middle bottom-0 start-100 bg-success mb-6 rounded-circle border border-4 border-white h-20px w-20px"
            ></div>
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
                  >{{ account.username }}</a
                >
                <account-instagram-state :state="account.instagram_state" />
                <account-app-state class="ms-2" :state="account.app_state" />
              </div>
              <!--end::Name-->

              <!--begin::Info-->
              <div class="d-flex flex-wrap fw-semibold fs-6 pe-2">
                <a
                  v-if="account.name"
                  class="d-flex align-items-center text-gray-500 text-hover-primary me-5 mb-2"
                >
                  <KTIcon icon-name="profile-circle" icon-class="fs-4 me-1" />
                  {{ account.name }}
                </a>
              </div>

              <div>
                <span
                  class="d-flex align-items-center text-gray-500 text-hover-primary me-5 mb-2"
                >
                  {{ account.bio }}
                </span>
              </div>
              <!--end::Info-->
            </div>
            <!--end::User-->

            <!--begin::Actions-->
            <div class="d-flex my-4">
              <router-link
                :to="{ name: 'accounts' }"
                class="btn btn-sm btn-light me-2"
              >
                back
              </router-link>
              <a @click="getAccount" class="btn btn-sm btn-light-primary me-2">
                refresh
              </a>
              <a
                class="btn btn-light-danger btn-sm"
                v-if="account?.is_active"
                @click="
                  store.changeProperty(
                    [account?.id],
                    'is_active',
                    0,
                    `${account.username} deactivated successfully`,
                    getAccount
                  )
                "
                >Deactivate</a
              >

              <a
                class="btn btn-light-success btn-sm"
                v-else
                @click="
                  store.changeProperty(
                    [account?.id],
                    'is_active',
                    1,
                    `${account.username} activated successfully`,
                    getAccount
                  )
                "
                >Activate</a
              >

<!--              <div class="me-0">-->
<!--                <button-->
<!--                  class="btn btn-sm btn-icon btn-bg-light btn-active-color-primary"-->
<!--                  data-kt-menu-trigger="click"-->
<!--                  data-kt-menu-placement="bottom-end"-->
<!--                  data-kt-menu-flip="top-end"-->
<!--                >-->
<!--                  <i class="bi bi-three-dots fs-3"></i>-->
<!--                </button>-->
<!--                <Dropdown3></Dropdown3>-->
<!--              </div>-->
              <!--end::Menu-->
            </div>
            <!--end::Actions-->
          </div>

          <div class="d-flex flex-wrap flex-stack">
            <!--begin::Wrapper-->
            <div class="d-flex flex-column flex-grow-1 pe-8">
              <!--begin::Stats-->
              <div class="d-flex flex-wrap">
                <!--begin::Stat-->
                <div
                  class="border border-gray-300 border-dashed rounded min-w-125px py-3 px-4 me-6 mb-3"
                >
                  <!--begin::Number-->
                  <div class="d-flex align-items-center">
                    <!--begin::Svg Icon | path: icons/duotune/arrows/arr066.svg-->
                    <span class="svg-icon svg-icon-3 svg-icon-success me-2">
                      <svg
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <rect
                          opacity="0.5"
                          x="13"
                          y="6"
                          width="13"
                          height="2"
                          rx="1"
                          transform="rotate(90 13 6)"
                          fill="currentColor"
                        ></rect>
                        <path
                          d="M12.5657 8.56569L16.75 12.75C17.1642 13.1642 17.8358 13.1642 18.25 12.75C18.6642 12.3358 18.6642 11.6642 18.25 11.25L12.7071 5.70711C12.3166 5.31658 11.6834 5.31658 11.2929 5.70711L5.75 11.25C5.33579 11.6642 5.33579 12.3358 5.75 12.75C6.16421 13.1642 6.83579 13.1642 7.25 12.75L11.4343 8.56569C11.7467 8.25327 12.2533 8.25327 12.5657 8.56569Z"
                          fill="currentColor"
                        ></path>
                      </svg>
                    </span>
                    <!--end::Svg Icon-->
                    <div class="fs-2 fw-bold counted">
                      {{ account.following_count }}
                    </div>
                  </div>
                  <!--end::Number-->
                  <!--begin::Label-->
                  <div class="fw-semibold fs-6 text-gray-400">Followings</div>
                  <!--end::Label-->
                </div>
                <div
                  class="border border-gray-300 border-dashed rounded min-w-125px py-3 px-4 me-6 mb-3"
                >
                  <!--begin::Number-->
                  <div class="d-flex align-items-center">
                    <!--begin::Svg Icon | path: icons/duotune/arrows/arr066.svg-->
                    <span class="svg-icon svg-icon-3 svg-icon-success me-2">
                      <svg
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <rect
                          opacity="0.5"
                          x="13"
                          y="6"
                          width="13"
                          height="2"
                          rx="1"
                          transform="rotate(90 13 6)"
                          fill="currentColor"
                        ></rect>
                        <path
                          d="M12.5657 8.56569L16.75 12.75C17.1642 13.1642 17.8358 13.1642 18.25 12.75C18.6642 12.3358 18.6642 11.6642 18.25 11.25L12.7071 5.70711C12.3166 5.31658 11.6834 5.31658 11.2929 5.70711L5.75 11.25C5.33579 11.6642 5.33579 12.3358 5.75 12.75C6.16421 13.1642 6.83579 13.1642 7.25 12.75L11.4343 8.56569C11.7467 8.25327 12.2533 8.25327 12.5657 8.56569Z"
                          fill="currentColor"
                        ></path>
                      </svg>
                    </span>
                    <!--end::Svg Icon-->
                    <div class="fs-2 fw-bold counted">
                      {{ account.dm_count }}
                    </div>
                  </div>
                  <!--end::Number-->
                  <!--begin::Label-->
                  <div class="fw-semibold fs-6 text-gray-400">Dms</div>
                  <!--end::Label-->
                </div>
                <div
                  class="border border-gray-300 border-dashed rounded min-w-125px py-3 px-4 me-6 mb-3"
                >
                  <!--begin::Number-->
                  <div class="d-flex align-items-center">
                    <!--begin::Svg Icon | path: icons/duotune/arrows/arr066.svg-->
                    <span class="svg-icon svg-icon-3 svg-icon-success me-2">
                      <svg
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <rect
                          opacity="0.5"
                          x="13"
                          y="6"
                          width="13"
                          height="2"
                          rx="1"
                          transform="rotate(90 13 6)"
                          fill="currentColor"
                        ></rect>
                        <path
                          d="M12.5657 8.56569L16.75 12.75C17.1642 13.1642 17.8358 13.1642 18.25 12.75C18.6642 12.3358 18.6642 11.6642 18.25 11.25L12.7071 5.70711C12.3166 5.31658 11.6834 5.31658 11.2929 5.70711L5.75 11.25C5.33579 11.6642 5.33579 12.3358 5.75 12.75C6.16421 13.1642 6.83579 13.1642 7.25 12.75L11.4343 8.56569C11.7467 8.25327 12.2533 8.25327 12.5657 8.56569Z"
                          fill="currentColor"
                        ></path>
                      </svg>
                    </span>
                    <!--end::Svg Icon-->
                    <div class="fs-2 fw-bold counted">
                      {{ account.image_post_count }}
                    </div>
                  </div>
                  <!--end::Number-->
                  <!--begin::Label-->
                  <div class="fw-semibold fs-6 text-gray-400">Image Posts</div>
                  <!--end::Label-->
                </div>
              </div>
              <!--end::Stats-->
            </div>
            <!--end::Wrapper-->
            <!--begin::Progress-->
            <div
              class="d-flex align-items-center w-200px w-sm-300px flex-column mt-3"
            >
              <div class="d-flex justify-content-between w-100 mt-auto mb-2">
                <span class="fw-semibold fs-6 text-gray-400"
                  >Successful Rate Of Commands</span
                >
                <span class="fw-bold fs-6"
                  >{{ getCommandPercentage(account) }}%</span
                >
              </div>
              <div class="h-5px mx-3 w-100 bg-light mb-3">
                <div
                  class="bg-success rounded h-5px"
                  role="progressbar"
                  :style="`width: ${getCommandPercentage(account)}%;`"
                  aria-valuenow="50"
                  aria-valuemin="0"
                  aria-valuemax="100"
                ></div>
              </div>
            </div>
            <!--end::Progress-->
          </div>
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
          <li class="nav-item">
            <router-link
              :to="{ name: 'messages', params: { id: account.id } }"
              class="nav-link text-active-primary me-6"
              active-class="active"
            >
              Messages
            </router-link>
          </li>
          <!--begin::Nav item-->
          <li class="nav-item">
            <router-link
              :to="{ name: 'process-output', params: { id: account.id } }"
              class="nav-link text-active-primary me-6"
              active-class="active"
            >
              Command Output
            </router-link>
          </li>

          <!--          <li class="nav-item">-->
          <!--            <router-link-->
          <!--                to="/crafted/account/settings"-->
          <!--                class="nav-link text-active-primary me-6"-->
          <!--                active-class="active"-->
          <!--            >-->
          <!--              Settings-->
          <!--            </router-link>-->
          <!--          </li>-->
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
import { getAssetPath } from "@/core/helpers/assets";
import { defineComponent, onMounted, ref } from "vue";
import Dropdown3 from "@/components/dropdown/Dropdown3.vue";
import ApiService from "@/core/services/ApiService";
import AccountInstagramState from "@/components/account/AccountInstagramState.vue";
import AccountAppState from "@/components/account/AccountAppState.vue";
import { useAccountStore } from "@/stores/Account";

export default defineComponent({
  name: "kt-account",
  components: {
    Dropdown3,
    AccountInstagramState,
    AccountAppState,
  },
  props: ["id"],
  setup(props) {
    const account = ref({});
    const loading = ref(false);

    const getAccount = () => {
      loading.value = true;
      ApiService.post("account/view", { id: props.id })
        .then((response) => (account.value = response.data))
        .finally(() => (loading.value = false));
    };
    const getAvatarPath = (account) => {
      return (
        import.meta.env.VITE_APP_API_URL +
        "/storage/" +
        account.templates[0]?.text
      );
    };

    const getCommandPercentage = (account) => {
      if (!account.total_commands) return 0;

      return Math.ceil(
        (account.successful_commands / account.total_commands) * 100
      );
    };

    onMounted(getAccount);

    return {
      loading,
      account,
      getAccount,
      getAssetPath,
      getAvatarPath,
      getCommandPercentage,
      store: useAccountStore(),
    };
  },
});
</script>
