import {defineStore} from "pinia";
import ApiService from "@/core/services/ApiService";
import {ref} from "vue";
import {hideModal} from "@/core/helpers/modal";
import Swal from "sweetalert2/dist/sweetalert2.js";


export const useThreadStore = defineStore('ThreadStore', {
    state() {
        return {
            checkedThreadsRows: [],
            threads: {
                data: [],
                page: 1,
                filters: [],
                search: {
                    text: "",
                    type: "",
                    category_id:""
                },
                total: 0,
            },
            is: {
                loading: false,
                deleting: false,
            },
            messageActions: [
                {value: "Interested", label: "interested"},
                {value: "Not Interested", label: "not interested"},
                {value: "Needs Response", label: "needs response"},
                {value: "Loom Sent", label: "loom follow up"},
                {value: "Call Booked", label: "call booked"},
            ],
            states:[
                {value: "interested", label: "is positive", class:"btn-light-success"},
                {value: "not interested", label: "is negative", class:"btn-light-danger"},
                {value: "needs response", label: "needs response", class:"btn-light-warning"},
                {value: "loom follow up", label: "loom sent", class:"btn-light-info"},
                {value: "autoreply", label: "autoreply", class:"btn-light-primary"},
                {value: "call booked", label: "call booked", class:"btn-primary"},

            ],
            state: '',
            category_id: '',
        }
    },

    actions: {
        warnIfdosntSelected(selected) {
            if (selected.length)
                return true;

            Swal.fire({
                icon: "error",
                text: "Please select one template to proceed",
            });

            return false;
        },

        getThreads(withLoading = true) {
            if (withLoading) this.is.loading = true;

            ApiService.post("get-threads", this.threads)
                .then((response) => {
                    this.threads.data = response.data.data;
                    this.threads.total = response.data.total;
                })
                .finally(() => {
                    this.is.loading = false;
                });
        },

        checkRows(e) {
            this.checkedThreadsRows = e.target.checked ?
                this.threads.data.map(template => template.id) : []
        },

        changeState(ids, state) {
            ApiService.post("lead/change-state", {ids, state});
        },

        setCategory(categoryId) {

            const data = {
                categoryId,
                ThreadIds: this.checkedThreadsRows
            }

            this.warnIfdosntSelected(this.checkedThreadsRows) &&
            ApiService.post('thread/set-category', data)
                .then(this.getThreads);
        }
    }
})