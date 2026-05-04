<template>
  <!-- Modal Structure -->
  <div
      class="modal fade"
      id="edit_media_modal"
      tabindex="-1"
      aria-hidden="true"

  >
    <div class="modal-dialog modal-dialog-centered mw-650px">
      <div class="modal-content rounded" v-loading=store.is.gettingTemplate>
        <div class="modal-header pb-0 border-0 justify-content-end">
          <div
              class="btn btn-sm btn-icon btn-active-color-primary"
              data-bs-dismiss="modal"
          >
            <KTIcon icon-name="cross" icon-class="fs-1"/>
          </div>
        </div>
        <div class="modal-body scroll-y px-10 px-lg-15 pt-0 pb-15">
          <div class="mb-13 text-center">
            <h1 class="mb-3">Edit Media</h1>
          </div>
          <div class="divider"></div>

          <div class="d-flex flex-column mb-6 fv-row">
            <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
              <span class="required">Caption</span>
            </label>
            <el-form-item prop="caption">
              <el-input
                  style="direction: rtl"
                  v-model="store.selectedTemplate.caption"
                  :rows="8"
                  type="textarea"
                  placeholder="Caption"
                  name="bunchInsert"
              />
            </el-form-item>
          </div>

          <div class="d-flex flex-column mb-8 fv-row">
            <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
              Tags
            </label>

            <el-select
                v-model="selectedTagIds"
                multiple
                filterable
                remote
                clearable
                placeholder="Search for tags"
                :remote-method="tagStore.fetchTags"
                :loading="tagStore.is.searching"
            >
              <el-option
                  v-for="tag in tagStore.searchedTags"
                  :key="tag.id"
                  :label="tag.title"
                  :value="tag.id"
              />
            </el-select>
          </div>

          <el-button type="success" @click="onSave">Edit</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {ref, watch} from "vue";
import {useTemplateStore} from "@/stores/Template";
import {useTagStore} from "@/stores/Tag";

const store = useTemplateStore();
const tagStore = useTagStore();

// Local mirror of the tag IDs currently attached to the template.
// We keep this separate from store.selectedTemplate so the user can
// freely add/remove tags without mutating the store until Save.
const selectedTagIds = ref<number[]>([]);

// Whenever a different template is selected, fetch its current state
// from the backend. The view endpoint now also returns the tags so
// they can be pre-populated in the dropdown.
watch(
    () => store.selectedTemplate.id,
    (newId) => {
      if (newId) {
        store.getTemplate();
      }
    }
);

// When the template payload arrives, seed both the dropdown selection
// and the search results so existing tags are visible by their titles
// before the user types anything.
watch(
    () => store.selectedTemplate,
    (template) => {
      const tags = (template as any)?.tags ?? [];
      selectedTagIds.value = tags.map((t: any) => t.id);

      // Make sure the option labels exist in the dropdown's option list,
      // otherwise el-select would render bare numeric IDs as labels.
      tagStore.searchedTags = mergeTagOptions(tagStore.searchedTags, tags);
    },
    {deep: true}
);

const mergeTagOptions = (existing: any[], incoming: any[]) => {
  const byId = new Map<number, any>();
  (existing ?? []).forEach(t => byId.set(t.id, t));
  (incoming ?? []).forEach(t => byId.set(t.id, t));
  return Array.from(byId.values());
};

const onSave = () => {
  
  store.updateTemplate(selectedTagIds.value);
};
</script>

<style lang="scss">
.override-styles {
  z-index: 99999 !important;
  pointer-events: initial;
}

.el-select {
  width: 100%;
}

.el-date-editor.el-input,
.el-date-editor.el-input__inner {
  width: 100%;
}

.el-upload {
  display: block;
}
</style>