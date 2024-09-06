import {defineStore} from "pinia";
import ApiService from "@/core/services/ApiService";
import router from "@/router";

export const useUserStore = defineStore("UserStore", {
    state() {
        return {
            users: {
                data: [],
                current_page: 1,
                total: 0,
                filters: [],
                search: '',
                dateRange: '',
            },
            is: {
                loading: false,
            },
        };
    },

    actions: {
        reAssignUser() {
            const user = localStorage.getItem('user');

            if (user) {
                return this.user = JSON.parse(user)
            }

            this.clearUser();
            router.push('sign-in');
        },
        login(data) {
            this.is.loading = true;

            ApiService.post("login", data)
                .then(response => response.data.status && this.handleSuccessLogin(response.data))
                .finally(() => this.is.loading = false);
        },
        signOut(){
            ApiService.post("sign-out")
                .then(this.clearUser)
                .finally(() => router.push('sign-in'));

        },

        clearUser() {
            localStorage.removeItem('user');
            this.user = ''
        },

        handleSuccessLogin(data) {
            this.setUser(data.user)
            router.push({name: 'dashboard'})
        },

        setUser(userObject) {

            if (typeof userObject === 'object') {
                this.user = userObject
                const user = JSON.stringify(userObject)
                return localStorage.setItem('user', user)
            }

            throw new Error(`Cannot set user because ${userObject} is not object`)
        },
        getUser() {
            return this.user;
        },
    },
});
