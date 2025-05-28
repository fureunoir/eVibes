import {defineStore} from "pinia";
import {ref} from "vue";

export const useCartStore = defineStore('cart', () => {
  const currentOrder = ref({});
  const setCurrentOrders = (order) => {
    currentOrder.value = order
  };

  return {
    currentOrder,
    setCurrentOrders
  }
})