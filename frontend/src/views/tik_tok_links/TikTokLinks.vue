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
        <a @click="forceRun" class="btn btn-sm btn-primary">
            <span class="d-flex align-items-center justify-content-center" v-if="forceRunning">
              <span class="spinner-border spinner-border-sm me-2"></span>
              <span> Please wait</span>
            </span>

          <span v-else>Force Run</span>

        </a>

        <a @click="showModal('add_tik_tok_links_modal')" class="btn btn-sm btn-success ms-1">
          Add Link
        </a>


        <a @click="fetch" class="btn btn-sm btn-success ms-1">
          Refresh
        </a>
      </div>
    </div>

    <div class="card-body" v-loading="loading">
      <div class="table-responsive">
        <table
            class='table table-row-bordered'
            style='table-layout:fixed'
        >
          <thead ref='tableHead'>
          <tr class="fw-bold text-muted">
            <th @click="sort('name')" style="cursor:pointer;position: relative; width: 180px;">
              NAME
              <span v-if="data.sort_by === 'name'">
                {{ data.sort_direction === 'asc' ? '▲' : '▼' }}
              </span>
            </th>

            <th style="width:150px;">IMAGES</th>
            <th @click="sort('post_link')" style="cursor:pointer;position: relative; width: 280px;">
              LINK
              <span v-if="data.sort_by === 'post_link'">
                {{ data.sort_direction === 'asc' ? '▲' : '▼' }}
              </span>
            </th>
            <th @click="sort('offer')" style="cursor:pointer;position: relative; width: 70px;">
              OFFER
              <span v-if="data.sort_by === 'offer'">
                {{ data.sort_direction === 'asc' ? '▲' : '▼' }}
              </span>
            </th>
            <th @click="sort('spark_id')" style="cursor:pointer;position: relative; width: 110px;">
              SPARK ID
              <span v-if="data.sort_by === 'spark_id'">
                {{ data.sort_direction === 'asc' ? '▲' : '▼' }}
              </span>
            </th>
            <th @click="sort('geo')" style="cursor:pointer;position: relative; width: 60px;">
              GEO
              <span v-if="data.sort_by === 'geo'">
                {{ data.sort_direction === 'asc' ? '▲' : '▼' }}
              </span>
            </th>

            <th @click="sort('comments')" style="cursor:pointer;position: relative; width: 100px;">
              COMMENTS
              <span v-if="data.sort_by === 'comments'">
                {{ data.sort_direction === 'asc' ? '▲' : '▼' }}
              </span>
            </th>

            <th @click="sort('likes')" style="cursor:pointer;position: relative; width: 60px;">
              LIKES
              <span v-if="data.sort_by === 'likes'">
                {{ data.sort_direction === 'asc' ? '▲' : '▼' }}
              </span>
            </th>

            <th @click="sort('shares')" style="cursor:pointer;position: relative; width: 80px;">
              SHARES
              <span v-if="data.sort_by === 'shares'">
                {{ data.sort_direction === 'asc' ? '▲' : '▼' }}
              </span>
            </th>

            <th @click="sort('saves')" style="cursor:pointer;position: relative; width: 80px;">
              SAVES
              <span v-if="data.sort_by === 'saves'">
                {{ data.sort_direction === 'asc' ? '▲' : '▼' }}
              </span>
            </th>

            <th @click="sort('play_counts')" style="cursor:pointer;position: relative; width: 100px;">
              PLAY COUNTS
              <span v-if="data.sort_by === 'play_counts'">
                {{ data.sort_direction === 'asc' ? '▲' : '▼' }}
              </span>
            </th>

            <th @click="sort('updated_at')" style="cursor:pointer;position: relative; width: 100px;">
              UPDATED
              <span v-if="data.sort_by === 'updated_at'">
                {{ data.sort_direction === 'asc' ? '▲' : '▼' }}
              </span>
            </th>

            <th style="position: relative; width: 100px;">
              TAGS
            </th>

            <th style="position: relative; width: 80px;">ACTIONS</th>

          </tr>
          </thead>
          <tbody>
          <tr v-for="row in links.data" :key="row.id">
            <td
                class="cursor-pointer text-gray-700 fw-bold text-hover-primary fs-7"
            >
              <div
                  @click="copyToClipboard(row.name)"
              >{{ row.name || '—' }}
              </div>
              <div class="badge badge-light-danger mt-1 ms-1">
                {{ row.error }}
              </div>
            </td>

            <td>
              <div v-if="row.images?.length" class="image-stack">
                <img
                    v-for="(img, i) in row.images.slice(0,3)"
                    :key="i"
                    :src="img"
                    class="thumb"
                    @click="openGallery(row.images, i)"
                />
              </div>

              <span v-else>—</span>
            </td>

            <td
                class="cursor-pointer text-gray-700 fw-bold text-hover-primary fs-7"
            >
              <div
                  @click="copyToClipboard(row.post_link)"
                  class="text-muted fw-semibold text-muted fs-8">{{ row.post_link.split('?')[0] }}
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

            <td>{{ formatNumber(row.comments) }}</td>
            <td>{{ formatNumber(row.likes) }}</td>
            <td>{{ formatNumber(row.shares) }}</td>
            <td>{{ formatNumber(row.saves) }}</td>
            <td>{{ formatNumber(row.play_counts) }}</td>
            <td>{{ row.updated_at }}</td>
            <td>
              <div class="d-flex flex-wrap gap-1">
                <span
                    v-for="tag in row.tags"
                    :key="tag.id"
                    class="badge badge-light-info cursor-pointer"
                    @click="editTags(row)"
                >
                  {{ tag.title }}
                </span>

                <span
                    class="badge badge-light-primary cursor-pointer"
                    @click="editTags(row)"
                >
                  + Add
                </span>
               </div>
             </td>

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
                  <a
                      class="dropdown-item"
                      href="#"
                      @click.prevent="generateImages(row)"
                  >
                    <span class="d-flex align-items-center justify-content-center" v-if="generatingImage">
                      <span class="spinner-border spinner-border-sm me-2"></span>
                      <span> Please wait</span>
                    </span>
                    Generate Images
                  </a>
                </div>
              </div>
            </td>

          </tr>
          </tbody>
        </table>

      </div>
    </div>
    <add-tik-t-ok-links-modal @saved="fetch"/>
    <edit-tik-t-ok-links-modal
        :item="selected"
        @updated="fetch"
    />

    <TagManagerModal
        :item="selected"
        @updated="fetch"
    />
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, nextTick} from 'vue'
import ApiService from '@/core/services/ApiService'
import AddTikTOkLinksModal from "@/components/modals/tik_tok_links/AddTikTOkLinksModal.vue";
import EditTikTOkLinksModal from "@/components/modals/tik_tok_links/EditTikTOkLinksModal.vue";
import {showModal} from "@/core/helpers/modal";
import {copyToClipboard} from "@/core/helpers/helper";
import {Search} from "@element-plus/icons-vue";
import TagManagerModal from "@/components/modals/TagManagerModal.vue";
import search from "@/layouts/default-layout/components/search/Search.vue";


const links = ref({data: []})
const loading = ref(false);
const generatingImage = ref(false);
const forceRunning = ref(false);
const selected = ref<any>(null);
const data = ref({
  page: 1,
  search: '',
  type: '',
  offer: '',
  sort_by: 'updated_at',
  sort_direction: 'desc'

});
const tableHead = ref<HTMLElement | null>(null);

const editTags = (row:any) => {
  selected.value = row
  showModal('tag_manager_modal')
}

const generateImages = async (row: any) => {
  try {
    const response = await ApiService.post(
        `tiktok-links/download-images`,
        {id: row.id},
        {responseType: 'blob'}
    )

    // const url = window.URL.createObjectURL(new Blob([response]))
    const url = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `images_${row.id}.zip`)
    document.body.appendChild(link)
    link.click()
    // link.remove()

  } catch (e) {
    alert('Zip not ready yet')
  }
}

const formatNumber = (value: number | string) => {
  if (value === null || value === undefined) return '-'
  return new Intl.NumberFormat('en-US').format(Number(value))
}

const sort = (column: string) => {
  if (data.value.sort_by === column) {
    data.value.sort_direction =
        data.value.sort_direction === 'asc' ? 'desc' : 'asc'
  } else {
    data.value.sort_by = column
    data.value.sort_direction = 'asc'
  }

  fetch()
}

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
      .then(r => links.value = r)
      .then(() => loading.value = false)

}

const searchCleared = () => {
  setData('', '')
  fetch();
}

onMounted(async () => {
  fetch();
  await nextTick()
  makeColumnsResizable()
})

const openEdit = (row: any) => {
  selected.value = row
  showModal('edit_tik_tok_links_modal')
}

const remove = (id: number) => {
  if (!confirm('Are you sure?')) return

  ApiService.delete(`tiktok-links/${id}`).then(fetch)
}

const makeColumnsResizable = () => {
  const ths = tableHead.value?.querySelectorAll('th')
  if (!ths) return

  ths.forEach((th: any) => {
    th.style.position = 'relative'

    const resizer = document.createElement('div')
    resizer.className = 'column-resizer'
    th.appendChild(resizer)

    let startX = 0
    let startWidth = 0
    let isResizing = false

    const onMouseMove = (e: MouseEvent) => {
      const diff = e.pageX - startX

      // فقط اگر واقعاً حرکت داشته باشیم
      if (Math.abs(diff) > 3) {
        isResizing = true
      }

      const width = startWidth + diff
      if (width > 50) {
        th.style.width = width + 'px'
      }
    }

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove)
      document.removeEventListener('mouseup', onMouseUp)

      resizer.classList.remove('resizing')

      // جلوگیری از اجرای click روی th
      if (isResizing) {
        const preventClick = (e: Event) => {
          e.stopPropagation()
          e.preventDefault()
          th.removeEventListener('click', preventClick, true)
        }

        th.addEventListener('click', preventClick, true)
      }

      setTimeout(() => {
        isResizing = false
      }, 0)
    }

    resizer.addEventListener('mousedown', (e: MouseEvent) => {
      e.stopPropagation()
      e.preventDefault()

      startX = e.pageX
      startWidth = th.offsetWidth
      isResizing = false

      resizer.classList.add('resizing')

      document.addEventListener('mousemove', onMouseMove)
      document.addEventListener('mouseup', onMouseUp)
    })
  })
}

const openGallery = (images: string[], index: number) => {
  window.open(images[index], '_blank')
}

const forceRun = () => {
  forceRunning.value = true;
  ApiService.post(`tiktok-links/force-run`)
      .finally(() => forceRunning.value = false)

}

</script>

<style>
.column-resizer {
  position: absolute;
  top: 0;
  right: 0;
  width: 8px;
  height: 100%;
  cursor: col-resize;
  background-color: transparent;
  transition: background-color 0.2s ease;
}

/* خط نازک همیشه دیده شود */
.column-resizer::after {
  content: '';
  position: absolute;
  right: 3px;
  top: 0;
  width: 2px;
  height: 100%;
  background-color: #e0e0e0;
  transition: background-color 0.2s ease;
}

/* وقتی hover می‌کنیم */
.column-resizer:hover::after {
  background-color: #3b82f6;
}

/* وقتی در حال drag هست */
.column-resizer.resizing::after {
  background-color: #2563eb;
  width: 3px;
}

thead {
  position: sticky;
  top: 0;
  z-index: 20;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);

}

thead th {
  background-color: #f8f9fa !important; /* کاملاً opaque */
}

.table-responsive {
  cursor: grab;
  scroll-behavior: smooth;
  max-height: 70vh; /* هرچقدر خواستی */
  overflow: auto;
}

.table-responsive.dragging {
  cursor: grabbing;
}


.image-stack {
  display: flex;
  gap: 6px;
}

.thumb {
  width: 55px;
  height: 55px;
  object-fit: cover;
  border-radius: 10px;
  cursor: pointer;
  transition: 0.2s ease;
}

.thumb:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
}


</style>
