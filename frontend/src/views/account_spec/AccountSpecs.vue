<template>
  <div class="card mb-5 mb-xl-8">
    <!-- Header -->
    <div class="card-header border-0 pt-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">Account Specs</span>
        <span class="text-muted mt-1 fw-semibold fs-7">{{ store.accountSpecs.total }} accounts</span>
      </h3>

      <div class="card-toolbar d-flex align-items-center">
        <!-- Search -->
        <el-input
            v-model="store.accountSpecs.search"
            placeholder="Search username"
            clearable
            @clear="actionClicked"
            style="max-width: 400px;"
        >
          <template #prepend>
            <el-button :icon="Search" @click="store.getAccountSpecs"/>
          </template>
        </el-input>
      </div>
    </div>

    <!-- Body -->
    <div class="card-body py-3">
      <div class="table-responsive">
        <table class="table table-row-bordered table-row-gray-100 align-middle gs-0 gy-3" v-loading="store.is.loading">
          <thead>
          <tr class="fw-bold text-muted">
            <th class="min-w-150px">USERNAME</th>
            <th class="min-w-100px">REELS COUNT</th>
            <th class="min-w-100px">AVG VIEWS</th>
            <th class="min-w-100px">MIN VIEWS</th>
            <th class="min-w-100px">MAX VIEWS</th>
            <th class="min-w-100px">TOTAL VIEWS</th>
            <th class="min-w-150px">LAST SCAN</th>
          </tr>
          </thead>

          <tbody>
          <template v-for="account in store.accountSpecs.data" :key="account.id">
            <tr>
              <td>
                <a class="text-gray-900 fw-bold text-hover-primary fs-7">
                  <span @click="copyToClipboard(account.id)">{{ account.id }}</span>
                  -
                  <span @click="copyToClipboard(account.username)">{{ account.username }}</span>
                </a>
              </td>
              <td>{{ account.specs?.reels_count }}</td>
              <td>{{ account.specs?.avg_reel_views }}</td>
              <td>{{ account.specs?.min_reel_views }}</td>
              <td>{{ account.specs?.max_reel_views }}</td>
              <td>{{ account.specs?.total_reel_views }}</td>
              <td>{{ account.specs?.last_reels_scan_at }}</td>
            </tr>
          </template>
          </tbody>
        </table>

        <!-- Pagination -->
        <el-pagination
            :current-page="store.accountSpecs.current_page"
            :page-size="configStore.pagination?.each_page?.accounts"
            layout="prev, pager, next"
            :total="store.accountSpecs.total"
            @current-change="(page) => store.getAccountSpecs(page)"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {ref, onMounted} from 'vue';
import {Search} from '@element-plus/icons-vue';
import {useAccountStore} from '@/stores/Account';
import {useAppConfigStore} from '@/stores/AppConfig';
import {useDebounceFn} from '@vueuse/core';
import {useAccountSpecStore} from "@/stores/AccountSpec";
import {copyToClipboard} from "@/core/helpers/helper";

const store = useAccountSpecStore();
const configStore = useAppConfigStore();

const actionClicked = useDebounceFn(() => store.getAccountSpecs(store.accountSpecs.current_page), 300);

const sortBy = (field: string) => store.sortAccountSpecsBy(field);

onMounted(() => {
  store.getAccountSpecs();
});
</script>
