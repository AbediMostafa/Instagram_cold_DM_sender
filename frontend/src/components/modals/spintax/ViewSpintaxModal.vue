<template>
  <!--begin::Modal - New Spintax-->
  <div
      class="modal fade"
      id="view_spintax_modal"
      ref="newSpintaxModalRef"
      tabindex="-1"
      aria-hidden="true"
  >
    <!--begin::Modal dialog-->
    <div class="modal-dialog modal-dialog-centered mw-650px" v-loading="store.is.loadingSpintax">
      <!--begin::Modal content-->
      <div class="modal-content rounded">
        <!--begin::Modal header-->
        <div class="modal-header pb-0 border-0 justify-content-end">
          <!--begin::Close-->
          <div
              class="btn btn-sm btn-icon btn-active-color-primary"
              data-bs-dismiss="modal"
          >
            <KTIcon icon-name="cross" icon-class="fs-1"/>
          </div>
          <!--end::Close-->
        </div>
        <!--begin::Modal header-->

        <!--begin::Modal body-->
        <div class="modal-body scroll-y px-10 px-lg-15 pt-0 pb-15">
          <!--begin:Form-->
          <div class="mb-13 text-center">
            <h1 class="mb-3"> {{store.spintax.name}}</h1>
          </div>

          <!--begin::Input group-->
          <div class="d-flex flex-column mb-8 fv-row">
            <!--begin::Label-->
            <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
              <span class="text-muted">Name</span>
            </label>

            <span>
              {{store.spintax.name}}
            </span>

            <!--end::Label-->
          </div>

          <div class="d-flex flex-column mb-8 fv-row">
            <!--begin::Label-->
            <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
              <span class="text-muted">Type</span>
            </label>
            <span>
              {{store.spintax.type}}
            </span>

          </div>

          <div class="d-flex flex-column mb-8 fv-row">
            <!--begin::Label-->
            <label class="d-flex align-items-center fs-6 fw-semibold mb-2">
              <span class="text-muted">Text</span>
            </label>
            <span>
              {{store.spintax.text}}
            </span>

          </div>

          <!--begin::Actions-->
          <div class="text-center">
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

import {useSpintaxStore} from "@/stores/Spintax";

const store = useSpintaxStore()

</script>
