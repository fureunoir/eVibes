<template>
  <div class="block">
    <div class="block__inner">
      <input
          :placeholder="placeholder"
          :type="isPasswordVisible"
          :value="modelValue"
          @input="onInput"
          class="block__input"
      >
      <button
        @click.prevent="setPasswordVisible"
        class="block__eyes"
        v-if="type === 'password'"
      >
        <img v-if="isPasswordVisible === 'password'" src="@icons/eyeClosed.svg" alt="eye" loading="lazy">
        <img v-else src="@icons/eyeOpened.svg" alt="eye" loading="lazy">
      </button>
    </div>
    <p v-if="!validate" class="block__error">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import {ref} from "vue";

const $emit = defineEmits()
const props = defineProps({
  type: String,
  placeholder: String,
  isError: Boolean,
  error: String,
  modelValue: [String, Number],
  rules: Array
})

const isPasswordVisible = ref(props.type)
const setPasswordVisible = () => {
  if (isPasswordVisible.value === 'password') {
    isPasswordVisible.value = 'text'
    return
  }
  isPasswordVisible.value = 'password'
}

const validate = ref(true)
const errorMessage = ref('')
const onInput = (e) => {
  let result = true

  props.rules?.forEach((rule) => {
    result = rule((e.target).value)

    if (result !== true) {
      errorMessage.value = String(result)
      result = false
    }
  })

  validate.value = result

  return $emit('update:modelValue', (e.target).value)
}
</script>

<style lang="scss" scoped>
.block {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  position: relative;

  &__inner {
    width: 100%;
    position: relative;
  }

  &__input {
    width: 100%;
    padding: 6px 12px;
    border: 1px solid $black;
    background-color: $white;

    color: #1f1f1f;
    font-size: 12px;
    font-weight: 400;
    line-height: 20px;
    letter-spacing: 0.14px;

    &::placeholder {
      color: #2B2B2B;
    }
  }

  &__eyes {
    cursor: pointer;
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
    background-color: transparent;
    display: grid;
    place-items: center;
  }

  &__error {
    color: $error;
    font-size: 12px;
    font-weight: 500;
    animation: fadeInUp 0.3s ease;

    @keyframes fadeInUp {
      0% {
        opacity: 0;
        transform: translateY(-50%);
      }
      100% {
        opacity: 1;
        transform: translateY(0);
      }
    }
  }
}
</style>