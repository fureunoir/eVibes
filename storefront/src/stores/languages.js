import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLanguageStore = defineStore('language', () => {
  const languages = ref([]);
  const setLanguages = (payload) => {
    languages.value = payload
  };

  return {
    languages,
    setLanguages
  }
})
