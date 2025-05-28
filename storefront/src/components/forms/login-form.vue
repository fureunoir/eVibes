<template>
  <form @submit.prevent="handleLogin()" class="form">
    <ui-input
        :type="'email'"
        :placeholder="t('fields.email')"
        :rules="[isEmail]"
        v-model="email"
    />
    <ui-input
        :type="'password'"
        :placeholder="t('fields.password')"
        :rules="[required]"
        v-model="password"
    />
    <ui-checkbox
        v-model="isStayLogin"
    >
      {{ t('checkboxes.remember') }}
    </ui-checkbox>
    <ui-button
        class="form__button"
        :isDisabled="!isFormValid"
        :isLoading="loading"
    >
      {{ t('buttons.signIn') }}
    </ui-button>
  </form>
</template>

<script setup>
import {useI18n} from "vue-i18n";
import {isEmail, required} from "@/core/rules/textFieldRules.js";
import {computed, ref} from "vue";
import UiInput from "@/components/ui/ui-input.vue";
import UiButton from "@/components/ui/ui-button.vue";
import UiCheckbox from "@/components/ui/ui-checkbox.vue";
import {useLogin} from "@/composables/auth";

const {t} = useI18n()

const email = ref('')
const password = ref('')
const isStayLogin = ref(false)

const isFormValid = computed(() => {
  return (
    isEmail(email.value) === true &&
    required(password.value) === true
  )
})

const { login, loading } = useLogin();

async function handleLogin() {
  await login(email.value, password.value, isStayLogin.value);
}
</script>

<style lang="scss" scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>