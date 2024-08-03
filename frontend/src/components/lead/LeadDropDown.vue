<template>
  <el-dropdown class="p-5">
    <a class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm">
      <KTIcon icon-name="category" icon-class="fs-3"/>
    </a>
    <template #dropdown>
      <el-dropdown-menu class="p-3">
        <el-dropdown-item>
          <router-link :to="{name:'process-output', params:{id:lead.id}}" class="w-100">
            View
          </router-link>
        </el-dropdown-item>
        <el-dropdown-item
            @click="store.deleteSelected([lead?.id])"
        >Delete
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
import {useLeadStore} from "@/stores/Lead";

export default defineComponent({
  name: "lead-drop-down",
  components: {AccountInstagramState,},
  props: ['lead'],
  setup() {

    return {
      showModal,
      store: useLeadStore()
    }

  }
});
</script>

<style>
.fill-flex a {
  flex: 1 !important;
}
</style>
