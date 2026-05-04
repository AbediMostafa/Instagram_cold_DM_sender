<template>
  <div class="card cursor-pointer" @click="toggleCheck">
    <!--begin::Card body-->
    <div class="card-body pt-3 px-6">
      <div class="my-0 d-flex justify-content-between">
        <div
            class="form-check form-check-sm form-check-custom form-check-solid my-3"
            @click.stop
        >
          <input
              class="form-check-input widget-13-check"
              type="checkbox"
              :value="template.id"
              v-model="store.checkedTemplateRows"
          />
        </div>

        <el-dropdown class="p-5 pe-0" @click.stop>
          <a class="btn btn-icon btn-bg-light btn-active-color-primary btn-sm">
            <KTIcon icon-name="category" icon-class="fs-3"/>
          </a>
          <template #dropdown>
            <el-dropdown-menu class="p-3">
              <el-dropdown-item @click="editClicked()">Edit</el-dropdown-item>
              <el-dropdown-item>Delete</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

      </div>

      <div class="d-flex align-items-start mb-8 justify-content-between">
        <div class="ms-2 image-wrapper">
          <img
              class="template-image"
              :src="getImageSrc(template.text)"
              alt="Template"
          />
        </div>
      </div>
      <div class="text-gray-700 fs-8 caption-text" v-html="formattedCaption"></div>
      <span class="badge badge-light-success">{{ template.type }}</span>
      <span class="badge badge-light-primary mt-1 ms-1"
            v-for="tag in template.tags" :key="tag.id"
      >{{ tag.title }}</span>

      <!-- Assign and Stats actions for custom templates only.
           Custom templates are uploads that get prioritized by the worker
           and tracked individually for stats. -->
      <div
          v-if="template.is_custom"
          class="d-flex gap-2 mt-3 pt-3 border-top"
          @click.stop
      >
        <a
            class="btn btn-sm btn-light-primary flex-fill"
            @click="onAssignClick"
        >
          <KTIcon icon-name="user-plus" icon-class="fs-4"/>
          Assign
        </a>

        <a
            class="btn btn-sm btn-light-info flex-fill"
            @click="onStatsClick"
        >
          <KTIcon icon-name="chart-simple" icon-class="fs-4"/>
          Stats
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import {computed, defineProps} from "vue";
import {useTemplateStore} from "@/stores/Template";
import {getImageSrc} from "@/core/helpers/helper";
import {showModal} from "@/core/helpers/modal";

const props = defineProps(["template", "card_style"]);
const store = useTemplateStore();

const editClicked = () => {
  store.selectedTemplate.id = props.template.id;
  showModal("edit_media_modal");
}

const formattedCaption = computed(() =>
    props.template?.caption?.replace(/\n/g, "<br>")
);

const toggleCheck = () => {
  const id = props.template.id
  const index = store.checkedTemplateRows.indexOf(id)

  if (index === -1) {
    store.checkedTemplateRows.push(id)
  } else {
    store.checkedTemplateRows.splice(index, 1)
  }
}

// Open the assign modal targeted at this template.
// The store stashes id and type so the modal reads them on open.
const onAssignClick = () => {
  store.openAssignModal(props.template);
  showModal("assign_accounts_modal");
}

// Fetch stats for this template and open the stats modal.
// The modal renders even when nothing has been posted yet — the
// totals show as zero and the breakdown shows an empty-state notice.
const onStatsClick = () => {
  store.fetchStats(props.template.id);
  showModal("template_stats_modal");
}

</script>

<style scoped>
.image-wrapper {
  width: 100%; /* Optional: Ensures the wrapper spans the column width */
  display: flex;
  justify-content: center;
  align-items: center;
}

.template-image {
  width: 200px; /* Set your desired fixed width */
  height: 200px; /* Set your desired fixed height */
  object-fit: cover; /* Ensures the image is cropped to fill the dimensions */
  border-radius: 8px; /* Optional: Rounds the corners of the image */
}
</style>