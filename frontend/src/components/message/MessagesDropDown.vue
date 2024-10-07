<template>
  <!--begin::Menu 2-->
  <div
      class="menu menu-sub menu-sub-dropdown menu-column menu-rounded menu-gray-600 menu-state-bg-light-primary fw-semibold w-350px"
      data-kt-menu="true"
  >
    <!--begin::Menu item-->
    <div class="menu-item px-3">
      <div class="menu-content fs-6 text-gray-900 fw-bold px-3 py-4">
        Filters
      </div>
    </div>

    <!--begin::Menu item-->
    <div class="menu-item ">
      <div class="menu-content px-3 fill-flex d-flex align-items-center">
        <el-input
            v-model="store.threads.search.text"
            placeholder="Please input"
            class="input-with-select"
            clearable
            @clear="store.getThreads"
            @click.stop
        >
          <template #prepend>
            <el-button  @click="store.getThreads">
              Filter
            </el-button>
          </template>
          <template #append>
            <el-select
                v-model="store.threads.search.type"
                placeholder="Select"
                style="width: 115px"
            >
              <el-option label="Account" value="account"/>
              <el-option label="Lead" value="lead"/>
              <el-option label="Message" value="message"/>
            </el-select>
          </template>
        </el-input>

      </div>
    </div>
    <div class="menu-item ">
      <div class="menu-content px-3 justify-content-between d-flex align-items-center">
        <el-select
            style="width: 265px"
            v-model="store.threads.search.category_id" placeholder="Change Category">
          <el-option
              v-for="item in categoryStore.categories.data"
              :key="item.id"
              :label="item.title"
              :value="item.id"
          />

          <el-option
              label="All Categories"
              :value="null"
          />
        </el-select>
        <a class="btn btn-sm btn-light-success ms-1" @click="store.getThreads">Filter</a>
      </div>
    </div>

    <div class="menu-item px-3">
      <div class="menu-content fs-6 text-gray-900 fw-bold px-3 py-4">
        Change Category And Status
      </div>
    </div>
    <div class="menu-item ">
      <div class="menu-content px-3 justify-content-between d-flex align-items-center">
        <el-select
            style="width: 220px"
            v-model="store.category_id" placeholder="Select Category">
          <el-option
              v-for="item in categoryStore.categories.data"
              :key="item.id"
              :label="item.title"
              :value="item.id"
          />

          <el-option
              label="Clear Category"
              :value="null"
          />
        </el-select>
        <a class="btn btn-sm btn-light-success ms-1" @click="store.setCategory(store.category_id)"> Set Category</a>
      </div>
    </div>
    <div class="menu-item ">
      <div class="menu-content px-3 justify-content-between d-flex align-items-center">
        <el-select
            style="width: 220px"
            v-model="store.state" placeholder="Select Status">

          <el-option
              class="m-2"
              v-for="item in store.states"
              :key="item.value"
              :label="item.label"
              :value="item.value"
          />

        </el-select>
        <a class="btn btn-sm btn-light-success ms-1"
           @click="store.changeState(store.checkedThreadsRows, store.state)">
          Set Status</a>
      </div>
    </div>

  </div>
  <!--end::Menu 2-->
</template>

<script lang="ts" setup>
import {Search} from "@element-plus/icons-vue";
import {useThreadStore} from "@/stores/Thread";
import {useCategoryStore} from "@/stores/Category";
import {onMounted} from "vue";

const store = useThreadStore()
const categoryStore = useCategoryStore()

onMounted(categoryStore.getCategories)
</script>

<style>
.fill-flex a {
  flex: 1 !important;
}
</style>
