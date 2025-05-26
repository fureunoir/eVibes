import {useMutation} from "@vue/apollo-composable";
import {REFRESH} from "@/graphql/mutations/auth.js";
import {computed, ref} from "vue";
import {ElNotification} from "element-plus";
import {useI18n} from "vue-i18n";
import {useAuthStore} from "@/stores/auth.js";
import { useAuthOrder } from './useAuthOrder';
import { useAuthWishlist } from './useAuthWishlist';
import {DEFAULT_LOCALE, LOCALE_STORAGE_LOCALE_KEY, LOCALE_STORAGE_REFRESH_KEY} from "@/config/index.js";
import {useRoute, useRouter} from "vue-router";
import translations from "@/core/helpers/translations.js";

export function useRefresh() {
  const loading = ref(false);
  const userData = ref(null);

  const router = useRouter()
  const route = useRoute()
  const authStore = useAuthStore()
  const {t} = useI18n();

  const { mutate: refreshMutation } = useMutation(REFRESH);

  const { getPendingOrder } = useAuthOrder();
  const { getWishlist } = useAuthWishlist();

  async function refresh() {
    loading.value = true;

    const refreshToken = computed(() => {
      return localStorage.getItem(LOCALE_STORAGE_REFRESH_KEY)
    })

    if (!refreshToken.value) return

    try {
      const response = await refreshMutation({
        refreshToken: refreshToken.value
      });

      if (response.data?.refreshJwtToken) {
        authStore.setUser({
          user: response.data.refreshJwtToken.user,
          accessToken: response.data.refreshJwtToken.accessToken
        })

        if (response.data.refreshJwtToken.user.language !== translations.currentLocale) {
          translations.switchLanguage(response.data.refreshJwtToken.user.language)
          await router.push({
            name: route.name,
            params: {
              locale: localStorage.getItem(LOCALE_STORAGE_LOCALE_KEY) || DEFAULT_LOCALE
            }
          })
        }

        localStorage.setItem(LOCALE_STORAGE_REFRESH_KEY, response.data.refreshJwtToken.refreshToken)

        await getPendingOrder(response.data.refreshJwtToken.user.email);
        await getWishlist();
      }
    } catch (error) {
      console.error("Refresh error:", error);

      const errorMessage = error.graphQLErrors?.[0]?.message ||
          error.message ||
          t('popup.genericError');

      ElNotification({
        title: t('popup.error'),
        message: errorMessage,
        type: 'error'
      });
    } finally {
      loading.value = false;
    }
  }

  return {
    refresh,
    loading,
    userData
  };
}