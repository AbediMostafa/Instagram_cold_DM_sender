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
            <th class="min-w-200px">PROXY</th>
            <th class="min-w-150px">TYPE</th>
            <th class="min-w-150px">PROVIDER</th>
            <th class="min-w-150px">PROVIDER USERNAME</th>
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
              <td>
                <a class="text-gray-700 fw-bold text-hover-primary fs-7">
                  <span
                      @click="copyToClipboard(proxy.ip)"
                  >{{ proxy.ip }}</span> :

                  <span
                      @click="copyToClipboard(proxy.port)"
                  >{{ proxy.port }}</span>
                </a>

                <div>
                  <span class="badge badge-light-primary ms-1">
                    <span
                        @click="copyToClipboard(proxy.username)"
                    >

                      {{
                        proxy.username
                            ? proxy.username.length > 15
                                ? proxy.username.slice(0, 12) + '...'
                                : proxy.username
                            : '—'
                      }}


                    </span>@

                    <span
                        @click="copyToClipboard(proxy.password)"
                    >
                    {{
                        proxy.password
                            ? proxy.password.length > 12
                                ? proxy.password.slice(0, 12) + '...'
                                : proxy.password
                            : '—'
                      }}
                    </span>
                    </span>
                </div>
              </td>
              <td>
                <a class="text-gray-700 fw-bold text-hover-primary fs-7">
                  {{ proxy.type }}
                </a>
              </td>

              <td>
                <a class="text-gray-700 fw-bold text-hover-primary fs-7">
                  {{ proxy.provider_name }}
                </a>
              </td>

              <td>
                <a class="text-gray-700 fw-bold text-hover-primary fs-7">
                  {{ proxy.provider_username }}
                </a>
              </td>


              <td class="text-end">
                <a
                    @click="proxyStore.deleteSelected([proxy.id])"
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
  <create-proxy-modal/>
</template>

<script lang="ts" setup>
import {ref, onMounted} from "vue";
import {useProxyStore} from "@/stores/Proxy";
import {showModal} from "@/core/helpers/modal";
import CreateProxyModal from "@/components/modals/proxy/CreateProxyModal.vue";
import {useAppConfigStore} from "@/stores/AppConfig";
import {copyToClipboard} from "@/core/helpers/helper";

const proxyStore = useProxyStore();
const configStore = useAppConfigStore();

onMounted(proxyStore.getProxies);
</script>
