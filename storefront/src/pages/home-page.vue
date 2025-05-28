<template>
  <div>

  </div>
</template>

<script setup>
import {onMounted} from "vue";
import {useRoute} from "vue-router";
import {useUserActivation} from "@/composables/user";
import DepositForm from "@/components/forms/deposit-form.vue";
import LoginForm from "@/components/forms/login-form.vue";

const route = useRoute()

const { activateUser } = useUserActivation();

onMounted( async () => {
  if (route.name === "activate-user") {
    await activateUser()
  }
})
</script>

<style lang="scss" scoped>

</style>