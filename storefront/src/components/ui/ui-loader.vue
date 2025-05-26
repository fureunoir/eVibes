<template>
  <div class="loader">
    <li class="loader__dots" id="dot-1"></li>
    <li class="loader__dots" id="dot-2"></li>
    <li class="loader__dots" id="dot-3"></li>
  </div>
</template>

<script setup>

</script>

<style lang="scss" scoped>
.loader {
  display: flex;
  gap: 0.6em;
  list-style: none;

  &__dots {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: $white;
  }
}

#dot-1 {
  animation: loader-1 0.6s infinite ease-in-out;
}

@keyframes loader-1 {
  50% {
    opacity: 0;
    transform: translateY(-0.3em);
  }
}

#dot-2 {
  animation: loader-2 0.6s 0.3s infinite ease-in-out;
}

@keyframes loader-2 {
  50% {
    opacity: 0;
    transform: translateY(-0.3em);
  }
}

#dot-3 {
  animation: loader-3 0.6s 0.6s infinite ease-in-out;
}

@keyframes loader-3 {
  50% {
    opacity: 0;
    transform: translateY(-0.3em);
  }
}
</style>