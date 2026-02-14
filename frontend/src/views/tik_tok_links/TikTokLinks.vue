<template>
  <div class="card">
    <div class="card-header">
      <h3 class="card-title">TikTok Links</h3>
      <div class="card-toolbar">
        <div class="me-2">
          <el-input
              v-model="data.search"
              style="max-width: 600px"
              :placeholder="`Search on ${data.type}` "
              class="input-with-select"
              clearable
              @clear="searchCleared"
          >
            <template #prepend>
              <el-button :icon="Search" @click="fetch"/>
            </template>

            <template #append>
              <el-select
                  v-model="data.type"
                  placeholder="Select"
                  style="width: 115px"
              >
                <el-option label="Name" value="name"/>
                <el-option label="Offer" value="offer"/>
                <el-option label="Spark Id" value="spark_id"/>
                <el-option label="Geo" value="geo"/>
                <el-option label="Post Link" value="post_link"/>
              </el-select>
            </template>
          </el-input>
        </div>


        <a @click="showModal('add_tik_tok_links_modal')" class="btn btn-sm btn-success">
          Add Link
        </a>

        <a @click="fetch" class="btn btn-sm btn-success ms-1">
          Refresh
        </a>
      </div>
    </div>

    <div class="card-body">
      <div class="table-responsive" v-loading="loading">
        <table class="table table-row-bordered">
          <thead>
          <tr class="fw-bold text-muted">
            <th>NAME AND LINK</th>
            <th>OFFER</th>
            <th>SPARK ID</th>
            <th>GEO</th>
            <th>COMMENTS</th>
            <th>LIKES</th>
            <th>SHARES</th>
            <th>SAVES</th>
            <th class="min-w-150px">PLAY COUNTS</th>
            <th class="min-w-150px">UPDATED</th>
            <th class="text-end">ACTIONS</th>

          </tr>
          </thead>
          <tbody>
          <tr v-for="row in links.data" :key="row.id">
            <td
                class="cursor-pointer text-gray-700 fw-bold text-hover-primary fs-7"
            >
              <div
                  @click="copyToClipboard(row.name)"
              >{{ row.name || '—' }}</div>
              <div
                  @click="copyToClipboard(row.post_link)"
                  class="text-muted fw-semibold text-muted fs-8">{{ row.post_link.split('?')[0] }}</div>

              <div class="badge badge-light-danger mt-1 ms-1">
                {{row.error}}
              </div>
            </td>
            <td
                class="cursor-pointer text-gray-700 fw-bold text-hover-primary fs-7"
                @click="copyToClipboard(row.offer)"
            >{{ row.offer || '—' }}
            </td>
            <td
                class="cursor-pointer text-gray-700 fw-bold text-hover-primary fs-7"
                @click="copyToClipboard(row.spark_id)"
            >
              {{
                row.spark_id
                    ? row.spark_id.length > 10
                        ? row.spark_id.slice(0, 10) + '...'
                        : row.spark_id
                    : '—'
              }}
            </td>
            <td class="fs-7">
              <span v-if="!row.geo">—</span>

              <span
                  v-else-if="row.geo.toLowerCase() === 'fr'"
                  class="badge badge-light-primary mt-1 ms-1"
              >
                {{ row.geo }}
              </span>

              <span
                  v-else-if="row.geo.toLowerCase() === 'de'"
                  class="badge badge-light-success mt-1 ms-1"
              >
              {{ row.geo }}
            </span>

              <span
                  v-else-if="['usa','us'].includes(row.geo.toLowerCase())"
                  class="badge badge-light-danger mt-1 ms-1"
              >
              US
            </span>

              <span v-else>
                {{ row.geo }}
              </span>
            </td>

            <td>{{ row.comments }}</td>
            <td>{{ row.likes }}</td>
            <td>{{ row.shares }}</td>
            <td>{{ row.saves }}</td>
            <td>{{ row.play_counts }}</td>
            <td>{{ row.updated_at }}</td>
            <td class="text-end">
              <div class="dropdown">
                <button
                    class="btn btn-sm btn-light btn-active-light-primary"
                    data-bs-toggle="dropdown"
                >
                  Actions
                </button>

                <div class="dropdown-menu dropdown-menu-end">
                  <a
                      class="dropdown-item"
                      href="#"
                      @click.prevent="openEdit(row)"
                  >
                    Edit
                  </a>

                  <a
                      class="dropdown-item text-danger"
                      href="#"
                      @click.prevent="remove(row.id)"
                  >
                    Delete
                  </a>
                </div>
              </div>
            </td>

          </tr>
          </tbody>
        </table>

        <el-pagination
            :current-page="links.current_page"
            :total="links.total"
            layout="prev, pager, next"
            @current-change="fetch"
        />
      </div>
    </div>
    <add-tik-t-ok-links-modal @saved="fetch"/>
    <edit-tik-t-ok-links-modal
        :item="selected"
        @updated="fetch"
    />
  </div>
</template>

<script setup lang="ts">
import {onMounted, reactive, ref} from 'vue'
import ApiService from '@/core/services/ApiService'
import AddTikTOkLinksModal from "@/components/modals/tik_tok_links/AddTikTOkLinksModal.vue";
import EditTikTOkLinksModal from "@/components/modals/tik_tok_links/EditTikTOkLinksModal.vue";
import {showModal} from "@/core/helpers/modal";
import {copyToClipboard} from "@/core/helpers/helper";
import {Search} from "@element-plus/icons-vue";
import search from "@/layouts/default-layout/components/search/Search.vue";


const links = ref({data: []})
const loading = ref(false)
const selected = ref<any>(null);
const data = ref({
  page: 1,
  search: '',
  type: '',
  offer: '',

});

const setData = (search, type) => {
  data.value = {search, type}
}

const fetch = (page = 1) => {
  if (typeof page !== 'number') {
    page = 1
  }
  data.value.page = page;
  loading.value = true;
  ApiService.post(`tiktok-links`, {...data.value})
      .then(r => links.value = r.data)
      .then(() => loading.value = false)

}

const searchCleared = () => {
  setData('', '')
  fetch();
}

onMounted(fetch);

const openEdit = (row: any) => {
  selected.value = row
  showModal('edit_tik_tok_links_modal')
}

const remove = (id: number) => {
  if (!confirm('Are you sure?')) return

  ApiService.delete(`tiktok-links/${id}`).then(fetch)
}

</script>
