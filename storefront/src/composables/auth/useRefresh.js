import {useMutation} from "@vue/apollo-composable";
import {REFRESH} from "@/graphql/mutations/auth.js";
import {computed, ref} from "vue";
import {ElNotification} from "element-plus";
import {useI18n} from "vue-i18n";
import {useAuthStore} from "@/stores/auth.js";
import {LOCALE_STORAGE_REFRESH_KEY} from "@/config/index.js";
import {useRoute, useRouter} from "vue-router";
import translations from "@/core/helpers/translations.js";
import {usePendingOrder} from "@/composables/orders";
import {useWishlist} from "@/composables/wishlist";

export function useRefresh() {
  const router = useRouter()
  const route = useRoute()
  const authStore = useAuthStore()
  const {t} = useI18n();

  const { mutate: refreshMutation } = useMutation(REFRESH);

  const { getPendingOrder } = usePendingOrder();
  const { getWishlist } = useWishlist();

  const loading = ref(false);

  async function refresh() {
    loading.value = true;

    const refreshToken = computed(() => localStorage.getItem(LOCALE_STORAGE_REFRESH_KEY))

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
          translations.switchLanguage(response.data.refreshJwtToken.user.language, router, route)
        }

        localStorage.setItem(LOCALE_STORAGE_REFRESH_KEY, response.data.refreshJwtToken.refreshToken)

        await getPendingOrder(response.data.refreshJwtToken.user.email);
        await getWishlist();
      }
    } catch (error) {
      console.error("useRefresh error:", error);

      const errorMessage = error.graphQLErrors?.[0]?.message ||
          error.message ||
          t('popup.errors.defaultError');

      ElNotification({
        title: t('popup.errors.main'),
        message: errorMessage,
        type: 'error'
      });
    } finally {
      loading.value = false;
    }
  }

  return {
    refresh,
    loading
  };
}