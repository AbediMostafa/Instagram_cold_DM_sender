<template>
  <div class="modal fade" id="global_tag_manager_modal">
    <div class="modal-dialog">
      <div class="modal-content">

        <div class="modal-header">
          <h5 class="modal-title">Tag Manager</h5>
        </div>

        <div class="modal-body">

          <!-- Add New Tag -->
          <div class="d-flex mb-3">
            <input
                v-model="newTag"
                class="form-control me-2"
                placeholder="Enter new tag"
                @keyup.enter="addTag"
            />
            <button
                class="btn btn-primary"
                :disabled="adding"
                @click="addTag"
            >
              <span v-if="adding" class="spinner-border spinner-border-sm"></span>
              <span v-else>Add</span>
            </button>
          </div>

          <!-- Tags List -->
          <div class="d-flex flex-wrap gap-2">
            <span
                v-for="tag in allTags"
                :key="tag.id"
                class="badge badge-light-info d-flex align-items-center"
            >
              {{ tag.title }}

              <i
                  class="ms-2 cursor-pointer"
                  @click="deleteTag(tag.id)"
              >
                ✕
              </i>
            </span>
          </div>

        </div>

        <div class="modal-footer">
          <button class="btn btn-light" data-bs-dismiss="modal">
            Close
          </button>
        </div>

      </div>
    </div>
  </div>
</template>
<script setup lang="ts">

import {ref} from 'vue'
import ApiService from '@/core/services/ApiService'
import {hideModal} from '@/core/helpers/modal'

const allTags = ref < any[] > ([])
const newTag = ref('')
const adding = ref(false)

const fetchTags = async () => {
  const res = await ApiService.post('tik-tok-tags')
  allTags.value = res.data
}

const addTag = async () => {

  if (!newTag.value.trim()) return

  adding.value = true

  const res = await ApiService.post('tik-tok-tags/store', {
    title: newTag.value
  })

  fetchTags()

  newTag.value = ''
  adding.value = false
}

const deleteTag = async (id) => {

  if (!confirm('Are you sure?')) return

  await ApiService.delete(`tik-tok-tags/${id}`)

  allTags.value = allTags.value.filter(t => t.id !== id)
}

fetchTags()

</script>