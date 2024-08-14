<template>
  <div class="card mb-5 mb-xl-8">
    <!--begin::Header-->
    <div class="card-header border-0 pt-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">Proxies</span>
        <span class="text-muted mt-1 fw-semibold fs-7"
          >{{ proxyStore.proxies.total }} proxies</span
        >
      </h3>
      <div class="card-toolbar">
        <a class="btn btn-sm btn-primary me-2" @click="proxyStore.getProxies()"
          >Refresh</a
        >
        <a
          class="btn btn-sm btn-success me-2"
          @click="showModal('create_proxy_modal')"
          >Add Proxy</a
        >
        <!-- Additional toolbar items here -->
      </div>
    </div>
    <!--end::Header-->

    <!--begin::Body-->
    <div class="card-body py-3">
      <!--begin::Table container-->
      <div class="table-responsive">
        <table
          class="table table-row-bordered table-row-gray-100 align-middle gs-0 gy-3"
          v-loading="proxyStore.is.loading"
        >
          <!--begin::Table head-->
          <thead>
            <tr class="fw-bold text-muted">
              <th class="min-w-50px">ID</th>
              <th class="min-w-150px">IP</th>
              <th class="min-w-80px">Port</th>
              <th class="min-w-120px">Username</th>
              <th class="min-w-100px">Password</th>
              <th class="min-w-150px">Account</th>
              <th class="min-w-150px">State</th>
              <th class="min-w-100px text-end">Actions</th>
            </tr>
          </thead>
          <!--end::Table head-->

          <!--begin::Table body-->
          <tbody>
            <template
              v-for="(proxy, index) in proxyStore.proxies.data"
              :key="index"
            >
              <tr>
                <td>{{ proxy.id }}</td>
                <td>{{ proxy.ip }}</td>
                <td>{{ proxy.port }}</td>
                <td>{{ proxy.username }}</td>
                <td>{{ proxy.password }}</td>
                <td>
                  <span
                    class="badge py-2 px-3 fs-7 me-1"
                    v-for="account in proxy.accounts"
                    :key="account.username"
                    :class="account.instagram_state=='active'?'badge-light-info':'badge-light-danger'"
                  >
                    {{ account.id }}.{{ account.username }}
                  </span>
                </td>
                <td>
                  <span
                    class="badge py-2 px-3 fs-7 badge-light-success"
                    v-if="proxy.state == 'active'"
                    >active</span
                  >
                  <span class="badge py-2 px-3 fs-7 badge-light-success" v-else
                    >inactive</span
                  >
                </td>
                <td class="text-end">
                  <a
                    @click="proxyStore.deleteSelected([proxy.id])"
                    class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm"
                  >
                    <KTIcon icon-name="trash" icon-class="fs-3" />
                  </a>
                </td>
              </tr>
            </template>
          </tbody>
          <!--end::Table body-->
        </table>
        <!--end::Table-->

        <el-pagination
          :current-page="proxyStore.proxies.current_page"
          :page-size="configStore.pagination?.each_page?.proxies"
          layout="prev, pager, next"
          :total="proxyStore.proxies.total"
          @current-change="(page) => proxyStore.getProxies(page)"
        />
      </div>
      <!--end::Table container-->
    </div>
    <!--end::Body-->
  </div>
  <create-proxy-modal />
</template>

<script lang="ts" setup>
import { ref, onMounted } from "vue";
import { useProxyStore } from "@/stores/Proxy";
import { showModal } from "@/core/helpers/modal";
import CreateProxyModal from "@/components/modals/proxy/CreateProxyModal.vue";
import { useAppConfigStore } from "@/stores/AppConfig";

const proxyStore = useProxyStore();
const configStore = useAppConfigStore();

onMounted(proxyStore.getProxies);
</script>
