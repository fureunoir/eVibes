<template>
  <div class="post">
    <div class="container">
      <div class="post__wrapper">

      </div>
    </div>
  </div>
</template>

<script setup>
import {computed, onMounted} from "vue";
import {usePostbySlug} from "@/composables/blog/usePostBySlug.js";
import {useRoute} from "vue-router";

const route = useRoute()

const slug = computed(() => route.params.postSlug)

const { post, loading, getPost } = usePostbySlug();

onMounted(async () => {
  await getPost(slug.value)
})
</script>

<style lang="scss" scoped>

</style>