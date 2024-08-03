import { defineStore } from "pinia";
import ApiService from "@/core/services/ApiService";
import { ref } from "vue";
import { hideModal } from "@/core/helpers/modal";
import Swal from "sweetalert2/dist/sweetalert2.js";

export const useAccountStore = defineStore("AccountStore", {
  state() {
    return {
      checkedAccountRows: [],
      accounts: {
        data: [],
        current_page: 1,
        total: 0,
      },
      is: {
        loading: false,
        deleting: false,
      },
    };
  },

  actions: {
    deleteSelected(ids) {
      this.warnIfdosntSelected(ids) &&
        Swal.fire({
          title: "Are you sure you want to delete selected account(s)?",
          icon: "warning",
          showCancelButton: true,
          confirmButtonColor: "#3085d6",
          cancelButtonColor: "#d33",
          confirmButtonText: "Yes, delete it!",
        }).then((result) => {
          /* Read more about isConfirmed, isDenied below */
          if (result.isConfirmed) {
            ApiService.post("account/delete", { ids }).then(this.getAccounts);
          }
        });
    },

    changeProperty(ids, key, value, msg, handler) {
      this.warnIfdosntSelected(ids) &&
        ApiService.post("account/change-property", {
          ids,
          key,
          value,
          msg,
        }).then(handler);
    },
    warnIfdosntSelected(selected) {
      if (selected.length) return true;

      Swal.fire({
        icon: "error",
        text: "Please select one account to proceed",
      });

      return false;
    },

    getAccounts(page = 1, withLoading = true) {
      if (withLoading) this.is.loading = true;

      this.accounts.current_page = page;

      ApiService.post("accounts", { page })
        .then((response) => {
          this.accounts.data = response.data.data;
          this.accounts.total = response.data.total;
        })
        .finally(() => {
          this.is.loading = false;
        });
    },

    checkRows(e) {
      this.checkedAccountRows = e.target.checked
        ? this.accounts.data.map((account) => account.id)
        : [];
    },
  },
});
