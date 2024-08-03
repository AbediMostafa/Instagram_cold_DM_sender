<template>
  <el-dropdown class="p-5">
    <a class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm">
      <KTIcon icon-name="category" icon-class="fs-3"/>
    </a>
    <template #dropdown>
      <el-dropdown-menu class="p-3">
        <el-dropdown-item>
          <router-link :to="{name:'process-output', params:{id:account.id}}" class="w-100">
            View
          </router-link>
        </el-dropdown-item>
        <el-dropdown-item @click="$emit('editClicked')">Edit</el-dropdown-item>
        <el-dropdown-item
            @click="store.deleteSelected([account?.id])"
        >Delete
        </el-dropdown-item>
        <el-dropdown-item divided>
          <a class="btn btn-light-danger btn-sm"
             v-if="account?.is_active"
             @click="store.changeProperty([account?.id], 'is_active',0, `${account.username} deactivated successfully`, store.getAccounts)"
          >Deactivate</a>

          <a class="btn btn-light-success btn-sm"
             v-else
             @click="store.changeProperty([account?.id], 'is_active',1, `${account.username} activated successfully`, store.getAccounts)"
          >Activate</a>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>

</template>

<script lang="ts">
import {defineComponent} from "vue";
import {useAccountStore} from "@/stores/Account";
import AccountInstagramState from "@/components/account/AccountInstagramState.vue";
import {showModal} from "@/core/helpers/modal";

export default defineComponent({
  name: "account-drop-down",
  components: {AccountInstagramState,},
  props: ['account'],
  setup() {

    return {
      showModal,
      store: useAccountStore()
    }

  }
});
</script>

<style>
.fill-flex a {
  flex: 1 !important;
}
</style>
