<template>
  <div>
    <input
      :id="'checkbox' + id"
      class="checkbox"
      type="checkbox"
      :value="modelValue"
      @input="onInput"
      :checked="modelValue"
    >
    <label :for="'checkbox' + id" class="checkbox__label">
      <slot />
    </label>
  </div>
</template>

<script setup>
const $emit = defineEmits()
const props = defineProps({
  id: [Number, String],
  modelValue: Boolean
})

const onInput = (event) => {
  $emit('update:modelValue', event.target.checked);
};
</script>

<style lang="scss" scoped>
.checkbox {
  display: none;
  opacity: 0;

  &__label {
    color: #2B2B2B;
    font-size: 12px;
    font-weight: 400;
    line-height: 16px;
    letter-spacing: 0.12px;
  }
}

.checkbox + .checkbox__label::before {
  content: '';
  display: inline-block;
  width: 17px;
  height: 17px;
  flex-shrink: 0;
  flex-grow: 0;
  border: 1px solid $black;
  margin-right: 10px;
  background-repeat: no-repeat;
  background-position: center center;
  background-size: 50% 50%;
}

.checkbox:checked + .checkbox__label::before {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 8'%3e%3cpath fill='%2f6b4f' d='M6.564.75l-3.59 3.612-1.538-1.55L0 4.26 2.974 7.25 8 2.193z'/%3e%3c/svg%3e");
}

.checkbox + .checkbox__label {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  user-select: none;
}
</style>