<template>
  <form @submit.prevent="handleReset()" class="form">
    <ui-input
        :type="'email'"
        :placeholder="t('fields.email')"
        :rules="[isEmail]"
        v-model="email"
    />
    <ui-button
        class="form__button"
        :isDisabled="!isFormValid"
        :isLoading="loading"
    >
      {{ t('buttons.sendLink') }}
    </ui-button>
  </form>
</template>

<script setup>
import {useI18n} from "vue-i18n";
import {isEmail} from "@/core/rules/textFieldRules.js";
import {computed, ref} from "vue";
import UiInput from "@/components/ui/ui-input.vue";
import UiButton from "@/components/ui/ui-button.vue";
import {usePasswordReset} from "@/composables/auth";

const {t} = useI18n()

const email = ref('')

const isFormValid = computed(() => {
  return (
    isEmail(email.value) === true
  )
})

const { resetPassword, loading } = usePasswordReset();

async function handleReset() {
  await resetPassword(email.value);
}
</script>

<style lang="scss" scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>