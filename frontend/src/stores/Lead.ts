import { defineStore } from "pinia";
import ApiService from "@/core/services/ApiService";
import Swal from "sweetalert2/dist/sweetalert2.js";

export const useLeadStore = defineStore("LeadStore", {
  state() {
    return {
      checkedLeadRows: [],
      leads: {
        data: [],
        current_page: 1,
        total: 0,
        category_id:''
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
          title: "Are you sure you want to delete selected leads(s)?",
          icon: "warning",
          showCancelButton: true,
          confirmButtonColor: "#3085d6",
          cancelButtonColor: "#d33",
          confirmButtonText: "Yes, delete it!",
        }).then((result) => {
          /* Read more about isConfirmed, isDenied below */
          if (result.isConfirmed) {
            ApiService.post("lead/delete", { ids }).then(this.getLeads);
          }
        });
    },

    warnIfdosntSelected(selected) {
      if (selected.length) return true;

      Swal.fire({
        icon: "error",
        text: "Please select one lead to proceed",
      });

      return false;
    },

    getLeads(page = 1, withLoading = true) {
      if (withLoading) this.is.loading = true;

      this.leads.current_page = page;

      ApiService.post("leads", { page })
        .then((response) => {
          this.leads.data = response.data.data;
          this.leads.total = response.data.total;
        })
        .finally(() => {
          this.is.loading = false;
        });
    },

    checkRows(e) {
      this.checkedLeadRows = e.target.checked
        ? this.leads.data.map((lead) => lead.id)
        : [];
    },
    setCategory(){
      const data = {
        categoryId:this.leads.category_id,
        leadIds :this.checkedLeadRows
      }

      this.warnIfdosntSelected(this.checkedLeadRows) &&
      ApiService.post('lead/set-category', data)
          .then(this.getLeads);

    }
  },
});
