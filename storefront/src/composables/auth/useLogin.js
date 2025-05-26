import {useMutation} from "@vue/apollo-composable";
import {LOGIN} from "@/graphql/mutations/auth.js";
import {ref} from "vue";
import {ElNotification} from "element-plus";
import {useI18n} from "vue-i18n";
import {useAuthStore} from "@/stores/auth.js";
import translations from "@/core/helpers/translations.js";
import {LOCALE_STORAGE_REFRESH_KEY} from "@/config/index.js";
import { useAuthOrder } from './useAuthOrder';
import { useAuthWishlist } from './useAuthWishlist';

export function useLogin() {
  const loading = ref(false);
  const userData = ref(null);

  const authStore = useAuthStore()
  const {t} = useI18n();

  const { mutate: loginMutation } = useMutation(LOGIN);

  const { getPendingOrder } = useAuthOrder();
  const { getWishlist } = useAuthWishlist();

  async function login(
      email,
      password
  ) {
    loading.value = true;

    try {
      const response = await loginMutation({
          email,
          password
      });

      if (response.data?.obtainJwtToken) {
        authStore.setUser({
          user: response.data.obtainJwtToken.user,
          accessToken: response.data.obtainJwtToken.accessToken
        });

        localStorage.setItem(LOCALE_STORAGE_REFRESH_KEY, response.data.obtainJwtToken.refreshToken)

        ElNotification({
          message: t('popup.login.text'),
          type: 'success'
        })

        if (response.data.obtainJwtToken.user.language !== translations.currentLocale) {
          translations.switchLanguage(response.data.obtainJwtToken.user.language)
        }

        await getPendingOrder(response.data.obtainJwtToken.user.email);
        await getWishlist();
      }
    } catch (error) {
      console.error("Login error:", error);

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
    login,
    loading,
    userData
  };
}