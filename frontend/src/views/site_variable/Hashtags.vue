<template>
  <div v-loading="store.is.loading" class="col-xl-4">
    <div class="card card-xl-stretch mb-xl-8">

      <entity-header plural="Hashtags" :total="`${store.hashtags.total} Hashtag`"/>
      <div class="card-body pt-5 persian-font">
        <!--begin::Item-->
        <new-entity-button
            text="New Hashtag"
            @displayCreateEntityPanel="store.is.creatingHashtag = !store.is.creatingHashtag"
        />
        <div class="mb-7" v-if="store.is.creatingHashtag">
          <el-input
              v-model="store.hashtagData.title"
              placeholder="Hashtag Title"
              class="input-with-select mb-2"

              clearable
          >
            <template #append>
              <el-select
                  v-model="store.hashtagData.category"
                  placeholder="category"
                  style="width: 120px"
              >

                <el-option :label="category.title" :value="category.id" v-for="category in categoryStore.categories.data"/>
              </el-select>
            </template>
          </el-input>

          <create-entity-button
              :loading="store.is.creating"
              @create="store.createHashtag()"
              @cancel="store.cancelCreating()"/>

        </div>
        <div class="separator separator-dashed mb-3"></div>

        <div
            v-for="hashtag in store.hashtags.data"
            :key="hashtag.id">

          <div class="d-flex align-items-center justify-content-between mb-1">

            <div v-if="hashtag.editing">
              <el-input
                  v-model="store.hashtagData.title"
                  placeholder="Hashtag Title"
                  class="input-with-select"
                  clearable
              >
                <template #append>
                  <el-select
                      v-model="store.hashtagData.category"
                      placeholder="Select"
                      style="width: 115px"
                  >

                    <el-option :label="category.title" :value="category.id" v-for="category in categoryStore.categories.data"/>
                  </el-select>
                </template>
              </el-input>

            </div>

            <div v-else>
              <div class="text-dark text-hover-primary fs-6">{{ hashtag.title }}</div>
              <div class="text-muted fs-7">{{ hashtag.category?.title }}</div>
            </div>

            <update-cancel-entity-pair
                v-if="hashtag.editing"
                @updateClicked="store.updateHashtag(hashtag.id)"
                @cancelClicked="store.cancelEditing(hashtag)"
            />
            <div class="d-flex" v-else>
              <edit-entity-button @editEntity="store.editHashtag(hashtag)"/>
              <delete-entity-button @deleteEntity="store.deleteSelected(hashtag.id)"/>
            </div>
          </div>
          <div class="separator separator-dashed mb-3"></div>

        </div>
        <el-pagination
            v-model:current-page="store.hashtags.current_page"
            :total="store.hashtags.total"
            :page-size="20"
            layout="prev, pager, next"
            small
            background
            :hide-on-single-page="true"
            @current-change="(current)=>store.getHashtags(current)"
        />
        <!--end::Item-->
      </div>
      <!--end::Body-->
    </div>
  </div>
</template>

<script lang="ts" setup>

import EntityHeader from "@/components/site_variable/EntityHeader.vue";
import NewEntityButton from "@/components/site_variable/NewEntityButton.vue";
import CreateEntityButton from "@/components/site_variable/CreateEntityButton.vue";
import UpdateCancelEntityPair from "@/components/site_variable/UpdateCancelEntityPair.vue";
import EditEntityButton from "@/components/site_variable/EditEntityButton.vue";
import DeleteEntityButton from "@/components/site_variable/DeleteEntityButton.vue";
import {useCategoryStore} from "@/stores/Category";
import {onMounted} from "vue";
import {Search} from "@element-plus/icons-vue";
import {useHashtagStore} from "@/stores/Hashtag";

const categoryStore = useCategoryStore();
const store = useHashtagStore();

onMounted(store.getHashtags)

</script>

