<template>
  <el-card shadow="always" class="template-card" @click="toggleCheck">
    <!-- Image or Thumbnail -->
    <div class="my-0 d-flex justify-content-between">
      <div
          class="form-check form-check-sm form-check-custom form-check-solid my-3"
      >
        <input
            class="form-check-input widget-13-check"
            type="checkbox"
            :value="videoTemplate?.carousel_id"
            v-model="store.checkedTemplateRows"
        />
      </div>

      <el-dropdown class="p-5 pe-0">
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

    <el-image
        v-if="imageTemplate"
        :src="getImageSrc(imageTemplate.text)"
        fit="cover"
        class="image-preview"
        lazy
    />
    <!-- Video -->
    <video
        v-if="videoTemplate"
        :src="getImageSrc(videoTemplate.text)"
        controls
        class="video-player"
    ></video>
    <!-- Caption -->
    <div class="text-gray-700 fs-8 caption-text"  v-html="formattedCaption"></div>

    <span class="badge badge-light-success">Video Post</span>
    <span class="badge badge-light-primary mt-1 ms-1"
          v-for="tag in videoTemplate?.tags" :key="tag.id"
    >{{ tag.title }}</span>

    <!-- Assign and Stats actions for custom video posts only.
         Assignment targets the video record; the worker resolves the
         cover image later via carousel_id. -->
    <div
        v-if="videoTemplate?.is_custom"
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
  </el-card>
</template>

<script setup>
import {computed, defineProps} from "vue";
import {ElCard, ElImage} from "element-plus";
import {useTemplateStore} from "@/stores/Template";
import {showModal} from "@/core/helpers/modal";

const store = useTemplateStore();
const props = defineProps(["templates"]);

// Extract image and video templates
const imageTemplate = computed(() =>
    props.templates.find((template) => template.sub_type === "image")
);

const videoTemplate = computed(() =>
    props.templates.find((template) => template.sub_type === "video")
);

// Utility to construct the media URL
const getImageSrc = (src) => `${import.meta.env.VITE_APP_API_URL}/storage/${src}`;

const editClicked = () => {
  store.selectedTemplate.id = videoTemplate.value.id;
  showModal("edit_media_modal");
}

const formattedCaption = computed(() => {
  const caption = videoTemplate.value?.caption || imageTemplate.value?.caption || "";
  return caption?.replace(/\n/g, "<br>");
});

const toggleCheck = () => {
  const carouselId = videoTemplate.value.carousel_id
  const index = store.checkedTemplateRows.indexOf(carouselId)

  if (index === -1) {
    store.checkedTemplateRows.push(carouselId)
  } else {
    store.checkedTemplateRows.splice(index, 1)
  }
}

// Assignment always targets the video record. The cover image is
// resolved later by the worker through the shared carousel_id.
const onAssignClick = () => {
  if (!videoTemplate.value) return;

  store.openAssignModal(videoTemplate.value);
  showModal("assign_accounts_modal");
}

// Fetch stats for the video record and open the stats modal.
// The modal renders even when nothing has been posted yet.
const onStatsClick = () => {
  if (!videoTemplate.value) return;

  store.fetchStats(videoTemplate.value.id);
  showModal("template_stats_modal");
}

// cutMorThanNCharacters(videoTemplate?.caption || imageTemplate?.caption, 200)
</script>

<style scoped>
.template-card {
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 20px;
}

.image-preview {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 8px 8px 0 0;
}

.video-player {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 0 0 8px 8px;
}
</style>