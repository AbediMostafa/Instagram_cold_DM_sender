import { defineStore } from "pinia";
import ApiService from "@/core/services/ApiService";

export const useAppConfigStore = defineStore("AppConfigStore", {
  state() {
    return {
      pagination: {},
      imageTemplate: [],
    };
  },

  actions: {
    getAppConfigs() {
      ApiService.post("app-config", {}).then((response) => {
        this.pagination = response.data.pagination;
        this.imageTemplate = response.data.template.image_type;
      });
    },
  },
});
