import {useUserStore} from "../../stores/User";

const applyDirectives = app => {
    app.directive('has-any-of-these-roles', {
        mounted: (el, binding) => {
            if (useUserStore().$hasNotAnyOfTheseRoles(binding.value)) {
                if (el.parentNode) {
                    el.parentNode.removeChild(el);
                } else {
                    console.error('Parent node not found for element:', el);
                }
            }
        }
    })
}

export default applyDirectives;