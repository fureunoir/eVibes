import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCompanyStore = defineStore('company', () => {
  const companyInfo = ref([])
  const setCompanyInfo = (payload) => {
    companyInfo.value = payload
  }

  return {
    companyInfo,
    setCompanyInfo
  }
})
