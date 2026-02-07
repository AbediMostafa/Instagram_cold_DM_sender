<template>
  <el-dialog
      v-model="visible"
      title="Order Comments"
      destroy-on-close
  >
    <el-table
        :data="comments"
        v-loading="loading"
        style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="100"/>

      <el-table-column prop="content" label="Comment"/>

      <el-table-column prop="status" label="Status" width="120">
        <template #default="{ row }">
          <el-tag
              :type="statusColor(row.status)"
              effect="light"
          >
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>

    </el-table>

    <template #footer>
      <el-button @click="visible = false">Close</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import {ref} from 'vue'
import axios from 'axios'
import ApiService from "@/core/services/ApiService";

const visible = ref(false)
const loading = ref(false)
const comments = ref([])

const open = async (orderId: number) => {
  visible.value = true
  loading.value = true

  ApiService.post("order/get-comment", {orderId})
      .then((response) => {
        comments.value = response.data;
      })
      .finally(() => {
        loading.value = false

      });
}

const statusColor = (status: string) => {
  switch (status) {
    case 'free':
      return 'info'
    case 'processing':
      return 'warning'
    case 'sent':
      return 'success'
    case 'failed':
      return 'danger'
    default:
      return ''
  }
}

defineExpose({open})
</script>
