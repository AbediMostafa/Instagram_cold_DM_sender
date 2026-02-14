<template>
  <div
      class="modal fade"
      id="edit_tik_tok_links_modal"
      tabindex="-1"
      aria-hidden="true"
  >
    <div class="modal-dialog modal-dialog-centered mw-750px">
      <div class="modal-content rounded">

        <div class="modal-header border-0">
          <h2 class="fw-bold">Edit TikTok Post</h2>

          <div
              class="btn btn-sm btn-icon"
              data-bs-dismiss="modal"
          >
            ✕
          </div>
        </div>

        <div class="modal-body px-10 pb-10">
          <el-form :model="form" label-width="120px">
            <el-form-item label="Name">
              <el-input v-model="form.name" />
            </el-form-item>

            <el-form-item label="Offer">
              <el-input v-model="form.offer" />
            </el-form-item>

            <el-form-item label="Spark ID">
              <el-input v-model="form.spark_id" />
            </el-form-item>

            <el-form-item label="Geo">
              <el-input v-model="form.geo" />
            </el-form-item>

            <el-form-item label="Post Link">
              <el-input v-model="form.post_link" />
            </el-form-item>

            <div class="d-flex justify-content-end pt-5">
              <el-button type="primary" @click="submit">
                Update
              </el-button>
            </div>
          </el-form>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import ApiService from '@/core/services/ApiService'
import { hideModal } from '@/core/helpers/modal'

const props = defineProps<{
  item: any
}>()

const emit = defineEmits(['updated'])

const form = reactive({
  name: '',
  offer: '',
  spark_id: '',
  geo: '',
  post_link: '',
})

watch(
    () => props.item,
    (val) => {
      if (!val) return
      Object.assign(form, val)
    },
    { immediate: true }
)

const submit = () => {
  ApiService.put(`tiktok-links/${props.item.id}`, {form}).then(() => {
    hideModal('edit_tik_tok_links_modal')
    emit('updated')
  })
}
</script>

