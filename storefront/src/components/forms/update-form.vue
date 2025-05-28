<template>
  <form class="form" @submit.prevent="handleUpdate()">
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
        :type="'email'"
        :placeholder="t('fields.email')"
        :rules="[isEmail]"
        v-model="email"
    />
    <ui-input
        :type="'text'"
        :placeholder="t('fields.phoneNumber')"
        :rules="[required]"
        v-model="phoneNumber"
    />
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
        :isLoading="loading"
    >
      {{ t('buttons.save') }}
    </ui-button>
  </form>
</template>

<script setup>
import {useI18n} from "vue-i18n";
import {isEmail, isPasswordValid, required} from "@/core/rules/textFieldRules.js";
import {computed, ref, watchEffect} from "vue";
import UiInput from "@/components/ui/ui-input.vue";
import UiButton from "@/components/ui/ui-button.vue";
import {useAuthStore} from "@/stores/auth.js";
import {useUserUpdating} from "@/composables/user";

const {t} = useI18n()
const authStore = useAuthStore()

const userFirstName = computed(() => authStore.user?.firstName)
const userLastName = computed(() => authStore.user?.lastName)
const userEmail = computed(() => authStore.user?.email)
const userPhoneNumber = computed(() => authStore.user?.phoneNumber)

const firstName = ref('')
const lastName = ref('')
const email = ref('')
const phoneNumber = ref('')
const password = ref('')
const confirmPassword = ref('')

const compareStrings = (v) => {
  if (v === password.value) return true
  return t('errors.compare')
}

const { updateUser, loading } = useUserUpdating();

watchEffect(() => {
  firstName.value = userFirstName.value || ''
  lastName.value = userLastName.value || ''
  email.value = userEmail.value || ''
  phoneNumber.value = userPhoneNumber.value || ''
})

async function handleUpdate() {
  await updateUser(
      firstName.value,
      lastName.value,
      email.value,
      phoneNumber.value,
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