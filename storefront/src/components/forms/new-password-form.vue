<template>
  <form @submit.prevent="handleReset()" class="form">
    <ui-input
        :type="'password'"
        :placeholder="t('fields.newPassword')"
        :rules="[isPasswordValid]"
        v-model="password"
    />
    <ui-input
        :type="'password'"
        :placeholder="t('fields.confirmNewPassword')"
        :rules="[compareStrings]"
        v-model="confirmPassword"
    />
    <ui-button
        class="form__button"
        :isDisabled="!isFormValid"
        :isLoading="loading"
    >
      {{ t('buttons.save') }}
    </ui-button>
  </form>
</template>

<script setup>
import {useI18n} from "vue-i18n";
import {isPasswordValid,} from "@/core/rules/textFieldRules.js";
import {computed, ref} from "vue";
import UiInput from "@/components/ui/ui-input.vue";
import UiButton from "@/components/ui/ui-button.vue";
import {useNewPassword} from "@/composables/auth";

const {t} = useI18n()

const password = ref('')
const confirmPassword = ref('')

const compareStrings = (v) => {
  if (v === password.value) return true
  return t('errors.compare')
}

const isFormValid = computed(() => {
  return (
    isPasswordValid(password.value) === true &&
    compareStrings(confirmPassword.value) === true
  )
})

const { newPassword, loading } = useNewPassword();

async function handleReset() {
  await newPassword(
      password.value,
      confirmPassword.value,
  );
}
</script>

<style lang="scss" scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>