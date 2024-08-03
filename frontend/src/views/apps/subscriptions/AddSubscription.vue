<template>
  <!--begin::Layout-->
  <div class="d-flex flex-column flex-lg-row">
    <div class="flex-lg-row-fluid me-lg-15 order-2 order-lg-1 mb-10 mb-lg-0">
        <Products></Products>
        <PaymentMethod></PaymentMethod>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import Products from "@/components/subscriptions/add/Products.vue";
import PaymentMethod from "@/components/subscriptions/add/PaymentMethod.vue";

export default defineComponent({
  name: "kt-add-subscription",
  components: {
    Products,
    PaymentMethod,
  },
});
</script>
