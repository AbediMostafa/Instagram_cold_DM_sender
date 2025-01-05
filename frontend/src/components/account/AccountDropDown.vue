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
        <el-dropdown-item @click="store.deleteSelected([account?.id])">Delete</el-dropdown-item>
        <el-dropdown-item @click="store.deleteWarning([account?.id])">Delete Warning</el-dropdown-item>
        <el-dropdown-item @click="store.makeActive([account?.id])">Make Active</el-dropdown-item>
        <el-dropdown-item @click="store.clearNextLogin([account?.id])">Clear Next Login</el-dropdown-item>
        <el-dropdown-item @click="store.clearProfile([account?.id])">Clear Profile</el-dropdown-item>
        <el-dropdown-item @click="profileStore.assignProfiles([account?.id])">Assign Profile</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>

</template>

<script lang="ts">
import {defineComponent} from "vue";
import {useAccountStore} from "@/stores/Account";
import AccountInstagramState from "@/components/account/AccountInstagramState.vue";
import {showModal} from "@/core/helpers/modal";
import {useProfileStore} from "@/stores/Profile";

export default defineComponent({
  name: "account-drop-down",
  components: {AccountInstagramState,},
  props: ['account'],
  setup() {

    return {
      showModal,
      store: useAccountStore(),
      profileStore:useProfileStore()
    }

  }
});
</script>

<style>
.fill-flex a {
  flex: 1 !important;
}
</style>
