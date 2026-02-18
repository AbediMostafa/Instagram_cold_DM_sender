<template>
  <div class="modal fade" id="tag_manager_modal">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Manage Tags</h5>
        </div>
        <div class="modal-body">
          <el-select
              v-model="selectedTags"
              multiple
              filterable
              style="width:100%"
          >
            <el-option
                v-for="tag in allTags"
                :key="tag.id"
                :label="tag.title"
                :value="tag.id"
            />
          </el-select>
        </div>

        <div class="modal-footer">
          <button class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
          <button class="btn btn-primary" @click="save">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, watch} from 'vue'
import ApiService from '@/core/services/ApiService'
import {hideModal} from "@/core/helpers/modal";

const props = defineProps(['item'])
const emit = defineEmits(['updated'])

const selectedTags = ref<number[]>([])
const allTags = ref<any[]>([])

watch(() => props.item, (val) => {
  if (val) {
    selectedTags.value = val.tags?.map(t => t.id) || []
  }
})

const fetchTags = async () => {
  const res = await ApiService.post('tik-tok-tags')
  allTags.value = res.data
}

fetchTags()

const save = async () => {
  await ApiService.post(
      `tiktok-links/${props.item.id}/tags`,
      {tags: selectedTags.value}
  )

  emit('updated')
  hideModal('tag_manager_modal')
}
</script>
