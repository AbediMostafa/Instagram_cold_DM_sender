<template>
  <!--begin::Search vertical-->
  <div>
    <!--begin::Aside-->

    <div class="flex-lg-row-fluid">
      <div class="d-flex flex-wrap flex-stack pb-7">
        <!--begin::Title-->
        <div class="d-flex flex-wrap align-items-center my-1">
          <span class="text-gray-800 fs-4">
            {{ store.templates.data.length }}
            <span class="text-gray-400 fs-5">{{ store.templates.receivedType }}s</span>
          </span>
        </div>
        <!--begin::Controls-->
        <div class="d-flex flex-wrap" v-has-any-of-these-roles="['user']">
          <!--begin::Tab nav-->
          <ul class="nav nav-pills mb-2 mb-sm-0">
            <li class="nav-item m-0 ">
              <a
                  v-if="store.checkedTemplateRows.length"
                  class="btn btn-sm btn-danger me-2"
                  @click="store.deleteSelected(store.checkedTemplateRows)"
              >Delete Selected</a
              >
            </li>
            <li class="nav-item m-0 ">
              <a
                  class="btn btn-sm btn-success me-2"
                  @click="showModal('create_template_modal')">
                Add Template
              </a>
            </li>
            <li class="nav-item m-0 ">
              <a
                  class="btn btn-sm btn-success me-2"
                  @click="showModal('upload_media_modal')">
                Add Media
              </a>

            </li>
            <li class="nav-item m-0 ">
              <button
                  type="button"
                  class="btn btn-sm btn-icon btn-color-primary btn-active-light-primary"
                  data-kt-menu-trigger="click"
                  data-kt-menu-placement="bottom-end"
                  data-kt-menu-flip="top-end"
              >
                <KTIcon icon-name="category" icon-class="fs-2"/>
              </button>
              <templates-drop-down/>

            </li>
          </ul>
          <!--end::Tab nav-->
        </div>
        <!--end::Controls-->
      </div>

      <div class="tab-content">
        <div>
          <!--begin::Row-->
          <div v-loading="store.is.loading" class="container-fluid">
            <div class="row">
              <div
                  class="col-sm-6 col-md-4 col-lg-3 mb-6"
                  v-for="(template, index) in store.templates.data"
                  :key="index"
              >
                <template  v-if="['username', 'bio'].includes(store.templates.receivedType)">
                  <username-card :template="template"/>
                </template>

                <template  v-if="store.templates.receivedType === 'avatar'">
                  <avatar-card :template="template"/>
                </template>

                <template  v-if="store.templates.receivedType === 'image-post'">
                  <image-post-card :template="template"/>
                </template>

                <template  v-if="store.templates.receivedType === 'carousel'">
                  <carousel-card :carousel="template"/>
                </template>

                <template  v-if="store.templates.receivedType === 'video-post'">
                  <video-post-card :templates="template"/>
                </template>

                <template  v-if="store.templates.receivedType === 'name'">
                  <name-card :template="template"/>
                </template>
              </div>
              <!--end::Col-->
            </div>
          </div>
        </div>
      </div>
    </div>
    <create-template-modal/>
    <upload-media-modal/>
    <edit-media-modal />

  </div>
</template>
<script setup lang="ts">
import LoomCard from "@/components/loom/LoomCard.vue";
import {onMounted} from "vue";
import {useLoomStore} from "@/stores/Loom";
import {useTemplateStore} from "@/stores/Template";
import {useAppConfigStore} from "@/stores/AppConfig";
import AvatarCard from "@/views/template/AvatarCard.vue";
import CarouselCard from "@/views/template/CarouselCard.vue";
import UsernameCard from "@/views/template/UsernameCard.vue";
import VideoPostCard from "@/views/template/VideoPostCard.vue";
import ImagePostCard from "@/views/template/ImagePostCard.vue";
import NameCard from "@/views/template/NameCard.vue";
import {showModal} from "@/core/helpers/modal";
import UploadMediaModal from "@/components/modals/account_information_template/UploadMediaModal.vue";
import CreateTemplateModal from "@/components/modals/account_information_template/CreateTemplateModal.vue";
import TemplatesDropDown from "@/components/template/TemplatesDropDown.vue";
import EditMediaModal from "@/components/modals/account_information_template/EditMediaModal.vue";

const store = useTemplateStore();
const configStore = useAppConfigStore();

const getImageSrc = (src) => {
  return import.meta.env.VITE_APP_API_URL + '/storage/' + src
}

const isMultimedia = type => configStore.imageTemplate.includes(type)


onMounted(store.getTemplates)
// onMounted(store.getTemplates)
</script>
