<template>
  <el-dialog
      v-model="visible"
      title="Order Actions"
      width="700px"
      destroy-on-close
  >
    <el-table
        :data="actions"
        v-loading="loading"
        style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80"/>

      <el-table-column prop="type" label="Type" width="120">
        <template #default="{ row }">
          <span>{{ row.type?.replace('_', ' ') }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="content" label="Content" min-width="150">
        <template #default="{ row }">
          <span v-if="row.content">{{ row.content }}</span>
          <span v-else class="text-muted">—</span>
        </template>
      </el-table-column>

      <el-table-column label="Account" width="130">
        <template #default="{ row }">
          <span v-if="row.account">{{ row.account.username }}</span>
          <span v-else class="text-muted">—</span>
        </template>
      </el-table-column>

      <el-table-column prop="status" label="Status" width="110">
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
import ApiService from "@/core/services/ApiService";

const visible = ref(false)
const loading = ref(false)
const actions = ref([])

const open = async (orderId: number) => {
  visible.value = true
  loading.value = true

  ApiService.post("order/get-actions", {orderId})
      .then((response) => {
        actions.value = response.data;
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