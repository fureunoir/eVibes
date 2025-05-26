<template>
  <button class="button" :disabled="isDisabled" :class="[{active: isLoading}]">
    <ui-loader class="button__loader" v-if="isLoading" />
    <slot v-else />
  </button>
</template>

<script setup>
import UiLoader from "@/components/ui/ui-loader.vue";

const props = defineProps({
  isDisabled: Boolean,
  isLoading: Boolean
})
</script>

<style lang="scss" scoped>
.button {
  position: relative;
  width: 100%;
  cursor: pointer;
  flex-shrink: 0;
  transition: 0.2s;
  border: 1px solid $black;
  background-color: $white;
  padding-block: 5px;
  z-index: 1;

  color: $black;
  text-align: center;
  font-size: 14px;
  font-weight: 700;

  &:hover, &.active {
    background-color: $black;
  }

  &:disabled {
    cursor: not-allowed;
    background-color: rgba($black, 0.5);
  }

  &:disabled:hover, &.active {
    background-color: rgba($black, 0.5);
  }

  &__loader {
    margin-bottom: 10px;
  }
}
</style>