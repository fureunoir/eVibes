<template>
  <form @submit.prevent="handleDeposit()" class="form">
    <div class="form__box">
      <ui-input
          :type="'text'"
          :placeholder="''"
          v-model="amount"
          :numberOnly="true"
      />
      <ui-input
          :type="'text'"
          :placeholder="''"
          v-model="amount"
          :numberOnly="true"
      />
    </div>
    <ui-button
        class="form__button"
        :isDisabled="!isFormValid"
        :isLoading="loading"
    >
      {{ t('buttons.topUp') }}
    </ui-button>
  </form>
</template>

<script setup>
import UiInput from "@/components/ui/ui-input.vue";
import {computed, ref} from "vue";
import UiButton from "@/components/ui/ui-button.vue";
import {useI18n} from "vue-i18n";
import {useDeposit} from "@/composables/user/useDeposit.js";

const {t} = useI18n()

const amount = ref('')

const isFormValid = computed(() => {
  return (
    amount.value >= 5 && amount.value <= 500
  )
})

const onlyNumbersKeypress = (event) => {
  if (!/\d/.test(event.key)) {
    event.preventDefault();
  }
}

const { deposit, loading } = useDeposit();

async function handleDeposit() {
  await deposit(amount.value);
}
</script>

<style lang="scss" scoped>
.form {
  &__box {
    display: flex;
    align-items: flex-start;
    gap: 20px;
  }
}
</style>