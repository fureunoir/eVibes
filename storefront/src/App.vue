<script setup>
import { RouterView } from 'vue-router'
import {useRefresh} from "@/composables/auth/useRefresh.js";
import {onMounted} from "vue";

const { refresh } = useRefresh();

onMounted(async () => {
  await refresh()

  setInterval(async () => {
    await refresh()
  }, 600000)
})
</script>

<template>
  <main class="main" id="top">
    <RouterView v-slot="{ Component }">
      <Transition name="opacity" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </main>
</template>

<style scoped>

</style>
