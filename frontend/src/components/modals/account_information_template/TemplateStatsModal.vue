<template>
  <div
      class="modal fade"
      id="template_stats_modal"
      tabindex="-1"
      aria-hidden="true"
  >
    <div class="modal-dialog modal-dialog-centered modal-xl">
      <div class="modal-content rounded" v-loading="store.is.loadingStats">

        <div class="modal-header">
          <h2 class="fw-bold">Template stats</h2>
          <div
              class="btn btn-icon btn-sm btn-active-icon-primary"
              data-bs-dismiss="modal"
              aria-label="Close"
          >
            <KTIcon icon-name="cross" icon-class="fs-1"/>
          </div>
        </div>

        <div class="modal-body py-8 px-lg-12">

          <!-- Aggregated KPI cards. All values render as 0 when no
               posts have completed yet, which is the expected initial
               state for newly assigned custom templates. -->
          <div class="row g-3 mb-8">
            <div class="col-6 col-md-4 col-lg-2">
              <div class="card bg-light-primary h-100">
                <div class="card-body p-4 text-center">
                  <div class="fs-2 fw-bold text-primary">{{ totals.total_posts }}</div>
                  <div class="text-muted fs-7">Posts</div>
                </div>
              </div>
            </div>

            <div class="col-6 col-md-4 col-lg-2">
              <div class="card bg-light-danger h-100">
                <div class="card-body p-4 text-center">
                  <div class="fs-2 fw-bold text-danger">{{ totals.total_likes }}</div>
                  <div class="text-muted fs-7">Likes</div>
                </div>
              </div>
            </div>

            <div class="col-6 col-md-4 col-lg-2">
              <div class="card bg-light-info h-100">
                <div class="card-body p-4 text-center">
                  <div class="fs-2 fw-bold text-info">{{ totals.total_comments }}</div>
                  <div class="text-muted fs-7">Comments</div>
                </div>
              </div>
            </div>

            <div class="col-6 col-md-4 col-lg-2">
              <div class="card bg-light-success h-100">
                <div class="card-body p-4 text-center">
                  <div class="fs-2 fw-bold text-success">{{ totals.total_views }}</div>
                  <div class="text-muted fs-7">Views</div>
                </div>
              </div>
            </div>

            <div class="col-6 col-md-4 col-lg-2">
              <div class="card bg-light-warning h-100">
                <div class="card-body p-4 text-center">
                  <div class="fs-2 fw-bold text-warning">{{ totals.total_saves }}</div>
                  <div class="text-muted fs-7">Saves</div>
                </div>
              </div>
            </div>

            <div class="col-6 col-md-4 col-lg-2">
              <div class="card bg-light-dark h-100">
                <div class="card-body p-4 text-center">
                  <div class="fs-2 fw-bold text-dark">{{ totals.total_reposts }}</div>
                  <div class="text-muted fs-7">Reposts</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Per-account breakdown. Empty state covers two cases:
               nothing has been posted yet, and stats simply not
               collected yet for any completed posts. -->
          <h4 class="fw-semibold mb-4">Per-account breakdown</h4>

          <div
              v-if="!store.stats.breakdown.length"
              class="text-muted fs-7 p-6 bg-light rounded text-center"
          >
            No posts yet. Stats will appear here once the worker has
            posted this template to assigned accounts.
          </div>

          <div v-else class="table-responsive">
            <table class="table table-row-bordered table-row-gray-100 align-middle gy-3">
              <thead>
              <tr class="fw-bold text-muted">
                <th>Account</th>
                <th class="text-end">Likes</th>
                <th class="text-end">Comments</th>
                <th class="text-end">Views</th>
                <th class="text-end">Saves</th>
                <th class="text-end">Reposts</th>
                <!-- Label kept as "Posted at" for clarity even though
                     the underlying column is created_at; the worker
                     overwrites created_at with the real post time. -->
                <th>Posted at</th>
                <th>Last updated</th>
                <th class="text-end">Link</th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="row in store.stats.breakdown" :key="row.id">
                <td class="fw-semibold text-gray-800">
                  {{ row.account?.username ?? `#${row.account_id}` }}
                </td>
                <td class="text-end">{{ row.like_count }}</td>
                <td class="text-end">{{ row.comment_count }}</td>
                <td class="text-end">{{ row.view_count }}</td>
                <td class="text-end">{{ row.save_count }}</td>
                <td class="text-end">{{ row.repost_count }}</td>
                <td class="text-muted fs-7">{{ formatPostedAt(row.created_at) }}</td>
                <td class="text-muted fs-7">
                  <el-tooltip
                      v-if="row.updated_at"
                      :content="formatPostedAt(row.updated_at)"
                      placement="top"
                  >
                    <span>{{ formatRelative(row.updated_at) }}</span>
                  </el-tooltip>
                  <span v-else>-</span>
                </td>
                <td class="text-end">
                  <a
                      v-if="row.url"
                      :href="row.url"
                      target="_blank"
                      rel="noopener"
                      class="btn btn-icon btn-sm btn-light-primary"
                  >
                    <KTIcon icon-name="exit-up" icon-class="fs-4"/>
                  </a>
                  <span v-else class="text-muted fs-7">-</span>
                </td>
              </tr>
              </tbody>
            </table>
          </div>

        </div>

        <div class="modal-footer flex-center">
          <button
              type="button"
              class="btn btn-light"
              data-bs-dismiss="modal"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {computed} from "vue";
import moment from "moment";
import {useTemplateStore} from "@/stores/Template";

const store = useTemplateStore();

// Coerce nullable totals to zero so the KPI cards render cleanly
// even when the backend returns nulls from SUM() over no rows.
const totals = computed(() => {
  const t = store.stats.totals ?? {};
  return {
    total_posts: t.total_posts ?? 0,
    total_likes: t.total_likes ?? 0,
    total_comments: t.total_comments ?? 0,
    total_views: t.total_views ?? 0,
    total_saves: t.total_saves ?? 0,
    total_reposts: t.total_reposts ?? 0,
  };
});

// Format ISO timestamps from the backend
// into a compact "YYYY-MM-DD HH:MM:SS" form. The timezone and the
// fractional seconds are dropped because they are noise here.
const formatPostedAt = (raw: string | null | undefined) => {
  if (!raw) return '-';

  // Take everything before the dot or the trailing Z, whichever
  // comes first, then swap the T for a space.
  const cleaned = String(raw).split('.')[0].replace('Z', '');
  return cleaned.replace('T', ' ');
};

// Render a timestamp as a human-friendly relative string ("10 minutes
// ago"). Used in the Last updated column with an el-tooltip showing
// the exact time on hover.
const formatRelative = (raw: string | null | undefined) => {
  if (!raw) return '-';
  return moment(raw).fromNow();
};
</script>