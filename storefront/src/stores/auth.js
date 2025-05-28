import {defineStore} from "pinia";
import {ref} from "vue";

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null);
  const accessToken = ref(null);

  const setUser = (payload) => {
    user.value = payload.user
    accessToken.value = payload.accessToken
  }

  return { user, accessToken, setUser }
})