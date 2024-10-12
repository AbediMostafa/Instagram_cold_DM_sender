<template>
  <div v-loading="store.is.loading" class="col-xl-4">
    <div class="card card-xl-stretch mb-xl-8">
      <entity-header plural="Tags" :total="`${store.tags.total} Tag`"/>
      <div class="card-body pt-5">
        <!--begin::Item-->
        <new-entity-button
            text="New Tag"
            @displayCreateEntityPanel="store.is.creatingTag = !store.is.creatingTag"
        />
        <div class="mb-7" v-if="store.is.creatingTag">
          <input
              placeholder="Tag Title"
              class="form-control form-control-solid mb-2"
              v-model="store.tagData.title">

          <create-entity-button
              :loading="store.is.creating"
              @create="store.createTag()"
              @cancel="store.cancelCreating()"/>
        </div>
        <div class="separator separator-dashed mb-7"></div>

        <div
            v-for="tag in store.tags.data"
            :key="tag.id">

          <div class="d-flex align-items-center justify-content-between mb-3">

            <div v-if="tag.editing">
              <input
                  placeholder="Tag Title"
                  class="form-control form-control-solid mb-2"
                  v-model="store.tagData.title">
            </div>

            <div v-else>
              <div class="text-dark text-hover-primary fs-6">{{ tag.title }}</div>
            </div>

            <update-cancel-entity-pair
                v-if="tag.editing"
                :loading="store.is.editing"
                @updateClicked="store.updateTag(tag)"
                @cancelClicked="store.cancelEditing(tag)"
            />
            <div class="d-flex" v-else>
              <edit-entity-button @editEntity="store.editTag(tag)"/>
              <delete-entity-button @deleteEntity="store.deleteSelected(tag.id)"/>
            </div>
          </div>
          <div class="separator separator-dashed mb-7"></div>

        </div>
        <el-pagination
            v-model:current-page="store.tags.current_page"
            :total="store.tags.total"
            :page-size="5"
            layout="prev, pager, next"
            small
            background
            :hide-on-single-page="true"
            @current-change="(current)=>store.getTags(current)"
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
import {useTagStore} from "@/stores/Tag";
import {onMounted} from "vue";

const store = useTagStore();
onMounted(store.getTags)

</script>
