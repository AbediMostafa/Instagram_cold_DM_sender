<template>
  <div class="card mb-5 mb-xl-8">
    <!--begin::Header-->
    <div class="card-header border-0 pt-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">Commands</span>
        <span class="text-muted mt-1 fw-semibold fs-7">{{ store.commands.total }} commands</span>
      </h3>
      <div class="card-toolbar">
        <!--begin::Menu-->
        <button
            type="button"
            class="btn btn-sm btn-icon btn-color-primary btn-active-light-primary"
            data-kt-menu-trigger="click"
            data-kt-menu-placement="bottom-end"
            data-kt-menu-flip="top-end"
        >
          <KTIcon icon-name="category" icon-class="fs-2"/>
        </button>
        <commands-drop-down/>
      </div>

    </div>
    <!--end::Header-->

    <!--begin::Body-->
    <div class="card-body py-3">
      <!--begin::Table container-->
      <div class="table-responsive">
        <table
            class="table table-row-bordered table-row-gray-100 align-middle gs-0 gy-3"
            v-loading="store.is.loading"
        >
          <!--begin::Table head-->
          <thead>
          <tr class="fw-bold text-muted">
            <th class="min-w-150px">ACCOUNT</th>
            <th class="min-w-150px">LEAD</th>
            <th class="min-w-130px">TYPE</th>
            <th class="min-w-150px">CREATED AT</th>
          </tr>
          </thead>
          <!--end::Table head-->

          <!--begin::Table body-->
          <tbody>
          <template
              v-for="(command, index) in store.commands.data"
              :key="index"
          >
            <tr>

              <td>
                <a class="text-gray-900 fw-bold text-hover-primary fs-7">
                  <span  @click="copyToClipboard(command.id)">{{ command.id }}</span>
                  -
                  <span  @click="copyToClipboard(command.account?.username)">{{ command.account?.username }}</span>
                </a>
              </td>

              <td>
                <a
                    @click="copyToClipboard(command.lead?.username)"
                    class="text-gray-900 fw-bold text-hover-primary fs-7">
                  {{ command.lead?.username }}
                </a>
                <div class="text-muted">Sequence : {{ command.times }}</div>
              </td>

              <td>
                <a class="text-gray-900 fw-bold text-hover-primary fs-7">
                  {{ command.type }}
                </a>
                <span class="badge ms-2" :class="`badge-light-${classType(command.state)}`">{{ command.state }}</span>

              </td>

              <td>
                <a class="text-gray-900 fw-bold text-hover-primary fs-7">
                  {{ command.created_at }}
                </a>

              </td>

            </tr>
          </template>
          </tbody>
          <!--end::Table body-->
        </table>
        <!--end::Table-->

        <el-pagination
            :current-page="store.commands.current_page"
            :page-size="configStore.pagination?.each_page?.commands"
            layout="prev, pager, next"
            :total="store.commands.total"
            @current-change="(page) => store.getCommands(page)"
        />
      </div>
      <!--end::Table container-->
    </div>
    <!--begin::Body-->
  </div>
</template>

<script lang="ts" setup>
import {onMounted} from "vue";
import {useAppConfigStore} from "@/stores/AppConfig";
import {useCommandStore} from "@/stores/Command";
import {copyToClipboard} from "@/core/helpers/helper";
import CommandsDropDown from "@/components/command/CommandsDropDown.vue";

const store = useCommandStore();
const configStore = useAppConfigStore();
onMounted(store.getCommands);

const classType = state => {
  return {
    'pending': 'warning',
    'processing': 'info',
    'success': 'success',
    'fail': 'danger',
  }[state]
}
</script>
