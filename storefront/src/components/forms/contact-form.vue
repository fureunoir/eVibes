<template>
  <form @submit.prevent="handleContactUs()" class="form">
    <ui-input
        :type="'text'"
        :placeholder="t('fields.name')"
        :rules="[required]"
        v-model="name"
    />
    <ui-input
        :type="'email'"
        :placeholder="t('fields.email')"
        :rules="[required]"
        v-model="email"
    />
    <ui-input
        :type="'text'"
        :placeholder="t('fields.phoneNumber')"
        :rules="[required]"
        v-model="phoneNumber"
    />
    <ui-input
        :type="'text'"
        :placeholder="t('fields.subject')"
        :rules="[required]"
        v-model="subject"
    />
    <ui-textarea
        :placeholder="t('fields.message')"
        :rules="[required]"
        v-model="message"
    />
    <ui-button
        class="form__button"
        :isDisabled="!isFormValid"
        :isLoading="loading"
    >
      {{ t('buttons.send') }}
    </ui-button>
  </form>
</template>

<script setup>
import {useI18n} from "vue-i18n";
import {required} from "@/core/rules/textFieldRules.js";
import {computed, ref} from "vue";
import UiInput from "@/components/ui/ui-input.vue";
import UiButton from "@/components/ui/ui-button.vue";
import UiTextarea from "@/components/ui/ui-textarea.vue";
import {useContactUs} from "@/composables/contact/index.js";

const {t} = useI18n()

const name = ref('')
const email = ref('')
const phoneNumber = ref('')
const subject = ref('')
const message = ref('')

const isFormValid = computed(() => {
  return (
    required(name.value) === true &&
    required(email.value) === true &&
    required(phoneNumber.value) === true &&
    required(subject.value) === true &&
    required(message.value) === true
  )
})

const { contactUs, loading } = useContactUs();

async function handleContactUs() {
  await contactUs(
      name.value,
      email.value,
      phoneNumber.value,
      subject.value,
      message.value,
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