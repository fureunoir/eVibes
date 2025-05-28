<template>
  <div class="block">
    <textarea
        :placeholder="placeholder"
        :value="modelValue"
        @input="onInput"
        class="block__textarea"
    />
    <p v-if="!validate" class="block__error">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import {ref} from "vue";

const $emit = defineEmits()
const props = defineProps({
  placeholder: String,
  isError: Boolean,
  error: String,
  modelValue: [String, Number],
  rules: Array
})

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

  &__textarea {
    width: 100%;
    height: 150px;
    resize: none;
    padding: 6px 12px;
    border: 1px solid $black;
    background-color: $white;

    color: #1f1f1f;
    font-size: 12px;
    font-weight: 400;
    line-height: 20px;

    &::placeholder {
      color: #2B2B2B;
    }
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