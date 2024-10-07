import type {App} from "vue";
import type {AxiosResponse} from "axios";
import axios from "axios";
import VueAxios from "vue-axios";
import JwtService from "@/core/services/JwtService";
import {ElMessage, ElMessageBox} from "element-plus";
import {useUserStore} from "@/stores/User";
import router from "@/router";


/**
 * @description service to call HTTP request via Axios
 */
class ApiService {
    /**
     * @description property to share vue instance
     */
    public static vueInstance: App;

    public static check422Status(error) {
        //status code
        const status = error.response?.status;

        const msg = error.response.data.errors
            ? //Laravel validation
            Object.values(error.response.data.errors).flat().join("<br>")
            : //Custom error sent with `abort` method
            error.response.data.message;

        if (status === 422) {
            ElMessageBox.confirm(msg, "Error", {
                confirmButtonText: "Ok",
                dangerouslyUseHTMLString: true,
                type: "error",
                showCancelButton: false,
                center: true,
            });
        }
    }

    public static check401Status(error) {
        const status = error.response?.status;

        if (status === 401) {
            useUserStore().clearUser()
            setTimeout(() => router.push('sign-in'), 500)
        }
    }

    public static check403Status(error) {
        const status = error.response?.status;

        if (status === 403) {
            ElMessageBox.confirm(error.response.data.message, "Error", {
                confirmButtonText: "Ok",
                dangerouslyUseHTMLString: true,
                type: "error",
                showCancelButton: false,
                center: true,
            });
        }
    }


    /**
     * @description initialize vue axios
     */
    public static init(app: App<Element>) {

        ApiService.vueInstance = app;
        ApiService.vueInstance.use(VueAxios, axios);
        ApiService.vueInstance.axios.defaults.baseURL =
            import.meta.env.VITE_APP_API_URL;
        ApiService.vueInstance.axios.defaults.withCredentials = true;
        ApiService.vueInstance.axios.defaults.headers.common['Accept'] = 'application/json';
        ApiService.vueInstance.axios.interceptors.response.use(
            (response) => {
                // if we want to send a notification to front, we send withResponse key
                // to identify this type of responses
                if (response.data.hasOwnProperty("withResponse")) {
                    response.data.status
                        ? ElMessage.success(response.data.msg)
                        : ElMessage.error(response.data.msg);
                }

                return response;
            },
            (error) => {
                ApiService.check401Status(error);
                ApiService.check422Status(error);
                ApiService.check403Status(error);
            }
        );
    }

    /**
     * @description set the default HTTP request headers
     */
    public static setHeader(): void {
        ApiService.vueInstance.axios.defaults.headers.common[
            "Authorization"
            ] = `Token ${JwtService.getToken()}`;
        ApiService.vueInstance.axios.defaults.headers.common["Accept"] =
            "application/json";
    }

    /**
     * @description send the GET HTTP request
     * @param resource: string
     * @param params: AxiosRequestConfig
     * @returns Promise<AxiosResponse>
     */
    public static query(resource: string, params: any): Promise<AxiosResponse> {
        return ApiService.vueInstance.axios.get(resource, params);
    }

    /**
     * @description send the GET HTTP request
     * @param resource: string
     * @param slug: string
     * @returns Promise<AxiosResponse>
     */
    public static get(
        resource: string,
        slug = "" as string
    ): Promise<AxiosResponse> {
        return ApiService.vueInstance.axios.get(`${resource}/${slug}`);
    }

    /**
     * @description set the POST HTTP request
     * @param resource: string
     * @param params: AxiosRequestConfig
     * @returns Promise<AxiosResponse>
     */
    public static post(resource: string, params: any): Promise<AxiosResponse> {
        return ApiService.vueInstance.axios.post(`${resource}`, params);
    }

    /**
     * @description send the UPDATE HTTP request
     * @param resource: string
     * @param slug: string
     * @param params: AxiosRequestConfig
     * @returns Promise<AxiosResponse>
     */
    public static update(
        resource: string,
        slug: string,
        params: any
    ): Promise<AxiosResponse> {
        return ApiService.vueInstance.axios.put(`${resource}/${slug}`, params);
    }

    /**
     * @description Send the PUT HTTP request
     * @param resource: string
     * @param params: AxiosRequestConfig
     * @returns Promise<AxiosResponse>
     */
    public static put(resource: string, params: any): Promise<AxiosResponse> {
        return ApiService.vueInstance.axios.put(`${resource}`, params);
    }

    /**
     * @description Send the DELETE HTTP request
     * @param resource: string
     * @returns Promise<AxiosResponse>
     */
    public static delete(resource: string): Promise<AxiosResponse> {
        return ApiService.vueInstance.axios.delete(resource);
    }
}

export default ApiService;
