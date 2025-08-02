<template>
  <div v-loading="store.is.loading" class="col-xl-4">
    <div class="card card-xl-stretch mb-xl-8">

      <entity-header plural="Lead Sources" :total="`${store.leadSources.total} Lead Source`"/>
      <div class="card-body pt-5 persian-font">
        <!--begin::Item-->
        <new-entity-button
            text="New Lead Source"
            @displayCreateEntityPanel="store.is.creatingLeadSource = !store.is.creatingLeadSource"
        />
        <div class="mb-7" v-if="store.is.creatingLeadSource">
          <el-input
              v-model="store.leadSourceData.title"
              placeholder="Lead Source Title"
              class="input-with-select mb-2"
              clearable
          >
            <template #append>
              <el-select
                  v-model="store.leadSourceData.category"
                  placeholder="category"
                  style="width: 120px"
              >
                <el-option :label="category.title" :value="category.id" v-for="category in categoryStore.categories.data" />
              </el-select>
            </template>
          </el-input>

          <create-entity-button
              :loading="store.is.creating"
              @create="store.createLeadSource()"
              @cancel="store.cancelCreating()"
          />
        </div>

        <div class="separator separator-dashed mb-3"></div>

        <div v-for="leadSource in store.leadSources.data" :key="leadSource.id">
          <div class="d-flex align-items-center justify-content-between mb-1">

            <div v-if="leadSource.editing">
              <el-input
                  v-model="store.leadSourceData.title"
                  placeholder="Lead Source Title"
                  class="input-with-select"
                  clearable
              >
                <template #append>
                  <el-select
                      v-model="store.leadSourceData.category"
                      placeholder="Select"
                      style="width: 115px"
                  >
                    <el-option :label="category.title" :value="category.id" v-for="category in categoryStore.categories.data" />
                  </el-select>
                </template>
              </el-input>
            </div>

            <div v-else>
              <div class="text-dark text-hover-primary fs-6">{{ leadSource.title }}</div>
              <div class="text-muted fs-7">{{ leadSource.category?.title }}</div>
            </div>

            <update-cancel-entity-pair
                v-if="leadSource.editing"
                @updateClicked="store.updateLeadSource(leadSource.id)"
                @cancelClicked="store.cancelEditing(leadSource)"
            />
            <div class="d-flex" v-else>
              <edit-entity-button @editEntity="store.editLeadSource(leadSource)" />
              <delete-entity-button @deleteEntity="store.deleteSelected(leadSource.id)" />
            </div>
          </div>
          <div class="separator separator-dashed mb-3"></div>
        </div>

        <el-pagination
            v-model:current-page="store.leadSources.current_page"
            :total="store.leadSources.total"
            :page-size="20"
            layout="prev, pager, next"
            small
            background
            :hide-on-single-page="true"
            @current-change="(current) => store.getLeadSources(current)"
        />
        <!--end::Item-->
      </div>
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
import { useCategoryStore } from "@/stores/Category";
import { onMounted } from "vue";
import { useLeadSourceStore } from "@/stores/LeadSource";

const categoryStore = useCategoryStore();
const store = useLeadSourceStore();

onMounted(store.getLeadSources);
</script>
