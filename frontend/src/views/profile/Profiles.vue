<template>
  <div class="card mb-5 mb-xl-8">
      <div class="card-header border-0 pt-5">
      <h3 class="card-title align-items-start flex-column">
        <span class="card-label fw-bold fs-3 mb-1">Profiles</span>
        <span class="text-muted mt-1 fw-semibold fs-7">{{ profileStore.profiles.total }} profiles</span>
      </h3>
      <!--      profileStore.profiles.data-->
      <div class="card-toolbar">
        <button 
          class="btn btn-sm btn-danger me-2" 
          @click="profileStore.deleteSelected([])"
          v-if="profileStore.checkedProfileRows?.length"
        >
          Delete Selected ({{ profileStore.checkedProfileRows?.length }})
        </button>
        <button class="btn btn-sm btn-success me-2" @click="showModal('create_profile_modal')">Add Profile</button>
        <button class="btn btn-sm btn-light-success me-2" @click="profileStore.getProfiles">Refresh</button>
        <button
            :data-kt-indicator="profileStore.is.assigning ? 'on' : null"
            class="btn btn-sm btn-light-primary me-2"
            type="submit"
            :disabled="profileStore.is.assigning"
            @click="profileStore.assignProfiles()"
        >
            <span v-if="!profileStore.is.assigning" class="indicator-label">
              Assign Profiles
              <i class="bi bi-arrow-right fs-3 ms-2 me-0"></i>
            </span>
          <span v-if="profileStore.is.assigning" class="indicator-progress">
                Please wait...
                <span class="spinner-border spinner-border-sm align-middle ms-2"></span>
              </span>
        </button>

        <el-input
            v-model="profileStore.profiles.search.text"
            style="width:350px"
            placeholder="Please input"
            class="input-with-select"
            clearable
            @clear="profileStore.getProfiles"
            @click.stop
        >
          <template #prepend>
            <el-button  @click="profileStore.getProfiles">
              Filter
            </el-button>
          </template>
          <template #append>
            <el-select
                v-model="profileStore.profiles.search.type"
                placeholder="Select"
                style="width: 115px"
            >
              <el-option label="Profile" value="profile"/>
              <el-option label="Account" value="account"/>
              <el-option label="Proxy" value="proxy"/>
            </el-select>
          </template>
        </el-input>

      </div>
    </div>

    <div class="card-body">
      <div class="table-responsive">
        <table class="table" v-loading="profileStore.is.loading">
          <thead>
          <tr class="fw-bold text-muted">
            <th class="w-20px">
              <div class="form-check form-check-sm form-check-custom form-check-solid">
                <input
                    class="form-check-input"
                    type="checkbox"
                    @change="profileStore.checkRows($event)"
                />
              </div>
            </th>
            <th>ID</th>
            <th>Title</th>
            <th>Accounts</th>
            <th>Proxy</th>
            <th>Folder</th>
            <th class="text-end">Actions</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="profile in profileStore.profiles.data" :key="profile.id">
            <td>
              <div class="form-check form-check-sm form-check-custom form-check-solid">
                <input
                    class="form-check-input widget-13-check"
                    type="checkbox"
                    :value="profile.id"
                    v-model="profileStore.checkedProfileRows"
                />
              </div>
            </td>
            <td @click="copyToClipboard(profile.id)">{{ profile.id }}</td>
            <td>
              <span @click="copyToClipboard(profile.title)">{{ profile.title }}</span>
              <div>
                <span
                    @click="copyToClipboard(profile.profile_id)"
                    class="text-muted fw-semibold text-muted fs-8">{{ profile.profile_id }}</span>
              </div>

            </td>
            <td>
              <span
                  class="badge py-2 px-3 fs-8 me-1"
                  v-for="account in profile.accounts"
                  :key="account.username"
                  :class="account.instagram_state=='active'?'badge-light-success':'badge-light-danger'"
              >
                <span @click="copyToClipboard(account.id)">{{ account.id }}</span>.
                <span @click="copyToClipboard( account.username)">{{ account.username }}</span>
                  </span>
            </td>
            <td @click="copyToClipboard(profile.proxy?.ip)">{{ profile.proxy?.ip }}</td>
            <td>{{ profile.folder }}</td>
            <td class="text-end">
              <profile-drop-down
                @editClicked="editClicked(profile)"
                :profile="profile"
              />
            </td>
          </tr>
          </tbody>
        </table>
        <el-pagination
            :current-page="profileStore.profiles.current_page"
            :page-size="configStore.pagination?.each_page?.profiles"
            layout="prev, pager, next"
            :total="profileStore.profiles.total"
            @current-change="page => profileStore.getProfiles(page)"
        />
      </div>
    </div>
  </div>

  <create-profile-modal/>
  <edit-profile-modal :profileProp="selectedProfile" v-if="selectedProfile"/>
</template>

<script setup>
import {onMounted, ref} from "vue";
import {useProfileStore} from "@/stores/Profile";
import ProfileDropDown from "@/components/profile/ProfileDropDown.vue";
import CreateProfileModal from "@/components/modals/profile/CreateProfileModal.vue";
import EditProfileModal from "@/components/modals/profile/EditProfileModal.vue";
import {showModal} from "@/core/helpers/modal";
import {useAppConfigStore} from "@/stores/AppConfig";
import {copyToClipboard} from "@/core/helpers/helper";


const profileStore = useProfileStore();
const configStore = useAppConfigStore();
const selectedProfile = ref(null);

const editClicked = (profile) => {
  console.log(profile);
  selectedProfile.value = profile
  showModal("edit_profile_modal");
};

onMounted(profileStore.getProfiles);
</script>
