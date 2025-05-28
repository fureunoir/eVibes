<template>
  <div class="blog">
    <div class="container">
      <div class="blog__wrapper">

      </div>
    </div>
  </div>
</template>

<script setup>
import {usePosts} from "@/composables/blog";
import {onMounted} from "vue";

const { posts, loading, getPosts } = usePosts();

onMounted(async () => {
  await getPosts()
})
</script>

<style lang="scss" scoped>

</style>