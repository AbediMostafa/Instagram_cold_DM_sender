import {defineStore} from "pinia";
import ApiService from "@/core/services/ApiService";

export const useCountryStore = defineStore("CountryStore", {
    state() {
        return {
            countries: [],
            is: {
                searching: false,
            },
        };
    },

    actions: {
        fetchCountries(q = '') {
            this.is.searching = true;

            ApiService.post("countries", {q})
                .then(response => {
                    this.countries = response.data;
                })
                .finally(() => {
                    this.is.searching = false;
                });
        },
    },
});