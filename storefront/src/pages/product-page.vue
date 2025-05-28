<template>
  <div class="product">
    <div class="container">
      <div class="product__wrapper">

      </div>
    </div>
  </div>
</template>

<script setup>
import {computed, onMounted} from "vue";
import {useRoute} from "vue-router";
import {useProductbySlug} from "@/composables/products/useProductBySlug.js";

const route = useRoute()

const slug = computed(() => route.params.productSlug)

const { product, loading, getProduct } = useProductbySlug();

onMounted(async () => {
  await getProduct(slug.value)
})
</script>

<style lang="scss" scoped>

</style>