<template>
  <div v-loading="store.is.loading" class="col-xl-8">
    <div class="card card-xl-stretch mb-xl-8">

      <entity-header plural="DM Posts" :total="`${store.dmPosts.total} DM Post`" />
      <div class="card-body pt-5 persian-font">
        <!--begin::Item-->
        <new-entity-button
            text="New DM Post"
            @displayCreateEntityPanel="store.is.creatingDmPost = !store.is.creatingDmPost"
        />
        <div class="mb-7" v-if="store.is.creatingDmPost">
          <div class="row">
            <el-input
                v-model="store.dmPostData.title"
                placeholder="DM Post Content"
                class="input-with-select mb-2 col-10"
                clearable
            >
              <template #append>
                <el-select
                    v-model="store.dmPostData.category"
                    placeholder="Category"
                    style="width: 120px"
                >
                  <el-option
                      :label="category.title"
                      :value="category.id"
                      v-for="category in categoryStore.categories.data"
                  />
                </el-select>
              </template>
            </el-input>
            <el-input
                class="col-2"
                v-model="store.dmPostData.priority"
                placeholder="Priority"
                clearable
            />

          </div>


          <create-entity-button
              :loading="store.is.creating"
              @create="store.createDmPost()"
              @cancel="store.cancelCreating()"
          />
        </div>

        <div class="separator separator-dashed mb-3"></div>

        <div v-for="dmPost in store.dmPosts.data" :key="dmPost.id">
          <div class="d-flex align-items-center justify-content-between mb-1">

            <div v-if="dmPost.editing">
              <el-input
                  v-model="store.dmPostData.title"
                  placeholder="DM Post Content"
                  class="input-with-select"
                  clearable
              >
                <template #append>
                  <el-select
                      v-model="store.dmPostData.category"
                      placeholder="Select"
                      style="width: 115px"
                  >
                    <el-option
                        :label="category.title"
                        :value="category.id"
                        v-for="category in categoryStore.categories.data"
                    />
                  </el-select>
                </template>
              </el-input>
              <el-input
                  class="mt-2"
                  v-model="store.dmPostData.priority"
                  placeholder="Priority"
                  clearable
              />
            </div>

            <div v-else>
              <div class="text-dark text-hover-primary fs-6">{{ dmPost.title }}</div>
              <div class="text-muted fs-7">
                priority :

                {{ dmPost.priority }}</div>
              <div class="text-muted fs-7">{{ dmPost.category?.title }}</div>
            </div>

            <update-cancel-entity-pair
                v-if="dmPost.editing"
                @updateClicked="store.updateDmPost(dmPost.id)"
                @cancelClicked="store.cancelEditing(dmPost)"
            />
            <div class="d-flex" v-else>
              <edit-entity-button @editEntity="store.editDmPost(dmPost)" />
              <delete-entity-button @deleteEntity="store.deleteSelected(dmPost.id)" />
            </div>
          </div>
          <div class="separator separator-dashed mb-3"></div>
        </div>

        <el-pagination
            v-model:current-page="store.dmPosts.current_page"
            :total="store.dmPosts.total"
            :page-size="20"
            layout="prev, pager, next"
            small
            background
            :hide-on-single-page="true"
            @current-change="(current) => store.getDmPosts(current)"
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
import { useDmPostStore } from "@/stores/DmPost";

const categoryStore = useCategoryStore();
const store = useDmPostStore();

onMounted(store.getDmPosts);
</script>
