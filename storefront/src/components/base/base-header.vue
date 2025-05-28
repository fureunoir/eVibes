<template>
  <header class="header">
    <div class="container">
      <div class="header__wrapper">

      </div>
    </div>
  </header>
</template>

<script setup>
import {onMounted} from "vue";
import {useCategories} from "@/composables/categories";

const { categories, loading, getCategories } = useCategories();

onMounted(async () => {
  await getCategories()
})
</script>

<style lang="scss" scoped>
.header {

}
</style>