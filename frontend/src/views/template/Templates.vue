<template>
  <div class="card mb-5 mb-xl-8">
    <!--begin::Header-->
    <div class="card-header border-0 pt-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">Templates</span>

        <span class="text-muted mt-1 fw-semibold fs-7">{{ store.templates.total }} templates</span>
      </h3>
      <div class="card-toolbar">
        <!--begin::Menu-->
        <a
            class="btn btn-sm btn-success me-2"
            @click="showModal('create_template_modal')">
          Add Template
        </a>

        <a
            class="btn btn-sm btn-success me-2"
            @click="showModal('upload_media_modal')">
          Add Media
        </a>

        <a
            @click="store.deleteSelected(store.checkedTemplateRows)"
            class="btn btn-sm btn-light-danger"
            v-if="store.checkedTemplateRows.length"> Delete selected</a>
      </div>
    </div>
    <!--end::Header-->

    <!--begin::Body-->
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
            <th class="w-25px">
              <div
                  class="form-check form-check-sm form-check-custom form-check-solid"
              >

                <input
                    class="form-check-input"
                    type="checkbox"
                    @change="store.checkRows($event)"
                />
              </div>
            </th>
            <th class="min-w-150px">TEXT</th>
            <th class="min-w-120px">TYPE</th>
            <th class="min-w-100px text-end">Actions</th>
          </tr>
          </thead>
          <!--end::Table head-->

          <!--begin::Table body-->
          <tbody>
          <template v-for="(template, index) in store.templates.data" :key="index">
            <tr>
              <td>
                <div
                    class="form-check form-check-sm form-check-custom form-check-solid"
                >
                  <input
                      class="form-check-input widget-13-check"
                      type="checkbox"
                      :value="template.id"
                      v-model="store.checkedTemplateRows"
                  />
                </div>
              </td>

              <td>
                <img
                    class="me-3"
                    style="border-radius: 8px"
                    :src="getImageSrc(template.text)"
                    width="50"
                    v-if="isMultimedia(template.type)">
                <a class="text-gray-900 fw-bold text-hover-primary fs-6">{{ template.text }}</a>
              </td>
              <td>
                <a class="text-gray-900 fw-bold text-hover-primary fs-6">{{ template.type }}</a>
              </td>

              <td class="text-end">
                <a
                    @click="store.deleteSelected([template.id])"
                    class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm"
                >
                  <KTIcon icon-name="trash" icon-class="fs-3"/>
                </a>
              </td>
            </tr>
          </template>
          </tbody>
          <!--end::Table body-->
        </table>
        <el-pagination
            :current-page="store.templates.current_page"
            :page-size="configStore.pagination?.each_page?.templates"
            layout="prev, pager, next"
            :total="store.templates.total"
            @current-change="page=>store.getTemplates(page)"
        />
      </div>
    </div>
  </div>
  <create-template-modal/>
  <upload-media-modal/>

</template>

<script lang="ts">
import {defineComponent, onMounted, ref} from "vue";
import TablesWidget13 from "@/components/widgets/tables/Widget13.vue";
import CreateAccountModal from "@/components/modals/account/CreateAccountModal.vue";
import Dropdown2 from "@/components/dropdown/Dropdown2.vue";
import {showModal} from "@/core/helpers/modal";
import {useAppConfigStore} from "@/stores/AppConfig";
import AccountInstagramState from "@/components/account/AccountInstagramState.vue";
import AccountAppState from "@/components/account/AccountAppState.vue";
import AccountIsActive from "@/components/account/AccountIsActive.vue";
import AccountPost from "@/components/account/AccountPost.vue";
import CreateTemplateModal from "@/components/modals/account_information_template/CreateTemplateModal.vue";
import {useTemplateStore} from "@/stores/Template";
import UploadMediaModal from "@/components/modals/account_information_template/UploadMediaModal.vue";

export default defineComponent({
  name: "account-information-templates",
  components: {
    Dropdown2,
    TablesWidget13,
    CreateAccountModal,
    AccountAppState,
    AccountIsActive,
    AccountInstagramState,
    AccountPost,
    CreateTemplateModal,
    UploadMediaModal
  },
  setup() {

    const store = useTemplateStore();
    const configStore = useAppConfigStore();

    const getImageSrc = (src) => {
      return import.meta.env.VITE_APP_API_URL + '/storage/' + src
    }

    const isMultimedia = type => configStore.imageTemplate.includes(type)


    onMounted(store.getTemplates)

    return {
      store,
      showModal,
      getImageSrc,
      isMultimedia,
      configStore,
    };

  }
});
</script>
