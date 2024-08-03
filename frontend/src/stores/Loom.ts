import { defineStore } from "pinia";
import ApiService from "@/core/services/ApiService";
import Swal from "sweetalert2/dist/sweetalert2.js";

export const useLoomStore = defineStore("LoomStore", {
  state() {
    return {
      checkedLoomRows: [],

      looms: {
        data: [],
        current_page: 1,
        total: 0,
      },
      is: {
        loading: false,
        deleting: false,
        selectingLoom: false,
        uploading:false,
      },
    };
  },

  actions: {
    deleteSelected(ids) {
      this.warnIfdosntSelected(ids) &&
        Swal.fire({
          title: "Are you sure you want to delete selected looms(s)?",
          icon: "warning",
          showCancelButton: true,
          confirmButtonColor: "#3085d6",
          cancelButtonColor: "#d33",
          confirmButtonText: "Yes, delete it!",
        }).then((result) => {
          if (result.isConfirmed) {
            ApiService.post("loom/delete", { ids }).then(this.getLooms);
          }
        });
    },

    warnIfdosntSelected(selected) {
      if (selected.length) return true;

      Swal.fire({
        icon: "error",
        text: "Please select one loom to proceed",
      });

      return false;
    },

    getLooms(page = 1, withLoading = true) {
      if (withLoading) this.is.loading = true;

      this.looms.current_page = page;

      ApiService.post("looms", { page })
        .then((response) => {
          this.looms.data = response.data.data;
          this.looms.total = response.data.total;
        })
        .finally(() => {
          this.is.loading = false;
        });
    },

    checkRows(e) {
      this.checkedLoomRows = e.target.checked
        ? this.looms.data.map((loom) => loom.id)
        : [];
    },
  },
});
