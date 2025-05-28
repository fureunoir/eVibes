<template>
  <form @submit.prevent="handleRegister()" class="form">
    <ui-input
        :type="'text'"
        :placeholder="t('fields.firstName')"
        :rules="[required]"
        v-model="firstName"
    />
    <ui-input
        :type="'text'"
        :placeholder="t('fields.lastName')"
        :rules="[required]"
        v-model="lastName"
    />
    <ui-input
        :type="'text'"
        :placeholder="t('fields.phoneNumber')"
        :rules="[required]"
        v-model="phoneNumber"
    />
    <ui-input
        :type="'email'"
        :placeholder="t('fields.email')"
        :rules="[isEmail]"
        v-model="email"
    />
    <ui-input
        :type="'password'"
        :placeholder="t('fields.password')"
        :rules="[isPasswordValid]"
        v-model="password"
    />
    <ui-input
        :type="'password'"
        :placeholder="t('fields.confirmPassword')"
        :rules="[compareStrings]"
        v-model="confirmPassword"
    />
    <ui-button
        class="form__button"
        :isDisabled="!isFormValid"
        :isLoading="loading"
    >
      {{ t('buttons.signUp') }}
    </ui-button>
  </form>
</template>

<script setup>
import {useI18n} from "vue-i18n";
import {isEmail, isPasswordValid, required} from "@/core/rules/textFieldRules.js";
import {computed, ref} from "vue";
import UiInput from "@/components/ui/ui-input.vue";
import UiButton from "@/components/ui/ui-button.vue";
import {useRegister} from "@/composables/auth/index.js";

const {t} = useI18n()

const firstName = ref('')
const lastName = ref('')
const phoneNumber = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')

const compareStrings = (v) => {
  if (v === password.value) return true
  return t('errors.compare')
}

const isFormValid = computed(() => {
  return (
    required(firstName.value) === true &&
    required(lastName.value) === true &&
    required(phoneNumber.value) === true &&
    isEmail(email.value) === true &&
    isPasswordValid(password.value) === true &&
    compareStrings(confirmPassword.value) === true
  )
})

const { register, loading } = useRegister();

async function handleRegister() {
  await register(
      firstName.value,
      lastName.value,
      phoneNumber.value,
      email.value,
      password.value,
      confirmPassword.value
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