<template>
  <div v-loading="store.is.loading" class="col-xl-4">
    <div class="card card-xl-stretch mb-xl-8">

      <entity-header plural="Offers" :total="`${store.categories.total} Offer`"/>
      <div class="card-body pt-5">
        <!--begin::Item-->
        <new-entity-button
            text="New Offer"
            @displayCreateEntityPanel="store.is.creatingCategory = !store.is.creatingCategory"
        />
        <div class="mb-7" v-if="store.is.creatingCategory">
          <input
              placeholder="Offer Title"
              class="form-control form-control-solid mb-2"
              v-model="store.categoryData.title">

          <input
              placeholder="Number Of Follow ups"
              class="form-control form-control-solid mb-2"
              v-model="store.categoryData.number_of_follow_ups">

          <input
              placeholder="Hour Interval"
              class="form-control form-control-solid mb-2"
              v-model="store.categoryData.hour_interval">

          <textarea
              placeholder="Offer Description"
              class="form-control form-control-solid mb-2"
              v-model="store.categoryData.description">
          </textarea>

          <create-entity-button
              :loading="store.is.creating"
              @create="store.createCategory()"
              @cancel="store.cancelCreating()"/>

        </div>
        <div class="separator separator-dashed mb-7"></div>

        <div
            v-for="category in store.categories.data"
            :key="category.id">

          <div class="d-flex align-items-center justify-content-between mb-3">

            <div v-if="category.editing">
              <input
                  placeholder="Category Title"
                  class="form-control form-control-solid mb-2"
                  v-model="store.categoryData.title">

              <input
                  placeholder="Category Title"
                  class="form-control form-control-solid mb-2"
                  v-model="store.categoryData.number_of_follow_ups">

              <input
                  placeholder="Category Title"
                  class="form-control form-control-solid mb-2"
                  v-model="store.categoryData.hour_interval">

              <textarea
                  placeholder="Category Description"
                  class="form-control form-control-solid mb-2"
                  v-model="store.categoryData.description">
              </textarea>
            </div>

            <div v-else>
              <div class="text-dark text-hover-primary fs-6">{{ category.title }}</div>
              <div class="text-muted">Follow ups : {{ category.number_of_follow_ups }}</div>
              <div class="text-muted">Hour intervals : {{ category.hour_interval }}</div>
              <div class="text-muted">{{ category.description }}</div>
            </div>

            <update-cancel-entity-pair
                v-if="category.editing"
                @updateClicked="store.updateCategory(category.id)"
                @cancelClicked="store.cancelEditing(category)"
            />
            <div class="d-flex" v-else>
              <edit-entity-button @editEntity="store.editCategory(category)"/>
              <delete-entity-button @deleteEntity="store.deleteSelected(category.id)"/>
            </div>
          </div>
          <div class="separator separator-dashed mb-7"></div>

        </div>
        <el-pagination
            v-model:current-page="store.categories.current_page"
            :total="store.categories.total"
            :page-size="5"
            layout="prev, pager, next"
            small
            background
            :hide-on-single-page="true"
            @current-change="(current)=>store.getCategories()"
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

const store = useCategoryStore();
onMounted(store.getCategories)

</script>
