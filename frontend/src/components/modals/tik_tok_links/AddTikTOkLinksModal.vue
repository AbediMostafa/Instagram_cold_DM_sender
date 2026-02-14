<template>
  <!--begin::Modal - Add TikTok Link-->
  <div
      class='modal fade'
      id='add_tik_tok_links_modal'
      ref='tikTokModalRef'
      tabindex='-1'
      aria-hidden='true'
  >
    <!--begin::Modal dialog-->
    <div class='modal-dialog modal-dialog-centered mw-750px'>
      <!--begin::Modal content-->
      <div class='modal-content rounded'>

        <!--begin::Modal header-->
        <div class='modal-header border-0'>
          <h2 class='fw-bold'>Add TikTok Post</h2>

          <div
              class='btn btn-sm btn-icon btn-active-color-primary'
              data-bs-dismiss='modal'
          >
            <KTIcon icon-name='cross' icon-class='fs-1'/>
          </div>
        </div>
        <!--end::Modal header-->

        <!--begin::Modal body-->
        <div class='modal-body px-10 px-lg-15 pb-10'>
          <!-- Bulk Switch -->
          <div class="d-flex flex-stack mb-6">
            <label class="fs-6 fw-semibold">Bulk insertion?</label>
            <label class="form-check form-switch form-check-custom form-check-solid">
              <input
                  class="form-check-input"
                  type="checkbox"
                  v-model="form.bulk_insertion"
                  @change="bulkChanged"
              />
              <span class="form-check-label fw-semibold text-muted">Yes</span>
            </label>
          </div>

          <el-form
              :model='form'
              label-width='120px'
              label-position='left'
              @submit.prevent='submit'
          >
            <!-- Bulk textarea -->
            <div v-if="form.bulk_insertion" class="mb-6">
              <el-form-item label='Bulk TikTok Links'>
                <el-input
                    type="textarea"
                    :rows="8"
                    v-model="form.bulk_links"
                    placeholder="Paste TikTok posts here, one per line: Name,Offer,Spark ID,Geo,Post Link"
                />
              </el-form-item>
            </div>

            <!-- Single inputs -->
            <div v-else>
              <el-form-item label='Name'>
                <el-input v-model='form.name'/>
              </el-form-item>

              <el-form-item label='Offer'>
                <el-input v-model='form.offer'/>
              </el-form-item>

              <el-form-item label='Spark ID'>
                <el-input v-model='form.spark_id'/>
              </el-form-item>

              <el-form-item label='Geo'>
                <el-input v-model='form.geo'/>
              </el-form-item>

              <el-form-item label='Post Link'>
                <el-input v-model='form.post_link'/>
              </el-form-item>
            </div>

            <!-- Actions -->
            <div class='d-flex justify-content-end pt-5'>
              <el-button
                  type='primary'
                  native-type='submit'
              >
                Save
              </el-button>
            </div>
          </el-form>
        </div>
        <!--end::Modal body-->

      </div>
      <!--end::Modal content-->
    </div>
    <!--end::Modal dialog-->
  </div>
  <!--end::Modal-->
</template>

<script setup lang='ts'>
import {reactive} from 'vue'
import {useRouter} from 'vue-router'
import ApiService from '@/core/services/ApiService'
import {hideModal} from "@/core/helpers/modal";

const router = useRouter();
const emit = defineEmits(['saved'])

const form = reactive({
  name: '',
  offer: '',
  spark_id: '',
  geo: '',
  post_link: '',
  bulk_insertion: false,
  bulk_links: '', // textarea for bulk insertion
})

const bulkChanged = () => {
  console.log('Bulk insertion toggled:', form.bulk_insertion)
}

const submit = () => {
  if (form.bulk_insertion && form.bulk_links.trim()) {
    // Split lines and map each line to a TikTok post object
    const posts = form.bulk_links
        .split('\n')
        .map(line => {
          const [name, offer, spark_id, geo, post_link] = line.split(',')
          return {name, offer, spark_id, geo, post_link}
        })
        .filter(p => p.name) // remove empty lines
    ApiService.post('tiktok-links/create', {posts})
        .then(() => {
          hideModal('add_tik_tok_links_modal')
          emit('saved')
        })
  } else {
    const data = {
      name: form.name,
      offer: form.offer,
      spark_id: form.spark_id,
      geo: form.geo,
      post_link: form.post_link,
    }
    // Single post submission
    ApiService.post('tiktok-links/create', {posts: [data]})
        .then(() => {
          hideModal('add_tik_tok_links_modal')
          emit('saved')
        })
  }
}
</script>
