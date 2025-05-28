import {useAuthStore} from "@/stores/auth.js";
import {
    DEFAULT_LOCALE,
    LOCALE_STORAGE_LOCALE_KEY,
    LOCALE_STORAGE_REFRESH_KEY,
    LOCALE_STORAGE_STAY_LOGIN_KEY
} from "@/config/index.js";
import {useRouter} from "vue-router";

export function useLogout() {
  const authStore = useAuthStore()
  const router = useRouter()

  async function logout() {
    authStore.setUser({
      user: null,
      accessToken: null
    })

    localStorage.removeItem(LOCALE_STORAGE_REFRESH_KEY)
    localStorage.removeItem(LOCALE_STORAGE_STAY_LOGIN_KEY)

    await router.push({
      name: 'home',
      params: {
        locale: localStorage.getItem(LOCALE_STORAGE_LOCALE_KEY) || DEFAULT_LOCALE
      }
    })
  }

  return {
    logout
  };
}