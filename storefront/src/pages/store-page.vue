<template>
  <div class="store">
    <div class="container">
      <div class="store__wrapper">

      </div>
    </div>
  </div>
</template>

<script setup>
import {onMounted} from "vue";
import {useProducts} from "@/composables/products/index.js";

const { products, pageInfo, loading, getProducts } = useProducts();

onMounted(async () => {
  await getProducts({})
  console.log('products:', products)
  console.log('pageInfo:', pageInfo)
})
</script>

<style lang="scss" scoped>
.store {

}
</style>