<script setup>
import { RouterView } from 'vue-router'
import {onMounted} from "vue";
import {useRefresh} from "@/composables/auth";
import {useCompanyInfo} from "@/composables/company";
import {useLanguages} from "@/composables/languages/index.js";
import BaseHeader from "@/components/base/base-header.vue";
import BaseFooter from "@/components/base/base-footer.vue";

const { refresh } = useRefresh();
const { getCompanyInfo } = useCompanyInfo();
const { getLanguages } = useLanguages();

onMounted(async () => {
  await refresh()
  await getCompanyInfo()
  await getLanguages()

  setInterval(async () => {
    await refresh()
  }, 600000)
})
</script>

<template>
  <main class="main" id="top">
    <base-header />
    <RouterView v-slot="{ Component }">
      <Transition name="opacity" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
    <base-footer />
  </main>
</template>

<style scoped>

</style>
