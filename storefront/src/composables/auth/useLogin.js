import {useMutation} from "@vue/apollo-composable";
import {LOGIN} from "@/graphql/mutations/auth.js";
import {ref} from "vue";
import {ElNotification} from "element-plus";
import {useI18n} from "vue-i18n";
import {useAuthStore} from "@/stores/auth.js";
import translations from "@/core/helpers/translations.js";
import {
  DEFAULT_LOCALE,
  LOCALE_STORAGE_LOCALE_KEY,
  LOCALE_STORAGE_REFRESH_KEY,
  LOCALE_STORAGE_STAY_LOGIN_KEY
} from "@/config/index.js";
import {useRoute, useRouter} from "vue-router";
import {usePendingOrder} from "@/composables/orders";
import {useWishlist} from "@/composables/wishlist";

export function useLogin() {
  const router = useRouter();
  const route = useRoute();
  const authStore = useAuthStore()
  const {t} = useI18n();

  const { mutate: loginMutation } = useMutation(LOGIN);

  const { getPendingOrder } = usePendingOrder();
  const { getWishlist } = useWishlist();

  const loading = ref(false);

  async function login(
      email,
      password,
      isStayLogin
  ) {
    loading.value = true;

    try {
      const response = await loginMutation({
          email,
          password
      });

      if (isStayLogin) {
        localStorage.setItem(LOCALE_STORAGE_STAY_LOGIN_KEY, 'remember')
      }

      if (response.data?.obtainJwtToken) {
        authStore.setUser({
          user: response.data.obtainJwtToken.user,
          accessToken: response.data.obtainJwtToken.accessToken
        });

        localStorage.setItem(LOCALE_STORAGE_REFRESH_KEY, response.data.obtainJwtToken.refreshToken)

        ElNotification({
          message: t('popup.success.login'),
          type: 'success'
        })

        await router.push({
          name: 'home',
          params: {
            locale: localStorage.getItem(LOCALE_STORAGE_LOCALE_KEY) || DEFAULT_LOCALE
          }
        })

        if (response.data.obtainJwtToken.user.language !== translations.currentLocale) {
          translations.switchLanguage(response.data.obtainJwtToken.user.language, router, route)
        }

        await getPendingOrder(response.data.obtainJwtToken.user.email);
        await getWishlist();
      }
    } catch (error) {
      console.error("useLogin error:", error);

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
    login,
    loading
  };
}