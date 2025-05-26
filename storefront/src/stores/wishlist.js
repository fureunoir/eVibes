import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useWishlistStore = defineStore('wishlist', () => {
  const wishlist = ref({})
  const setWishlist = (order) => {
    wishlist.value = order
  }

  return {
    wishlist,
    setWishlist
  }
})
