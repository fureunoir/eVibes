import {useMutation} from "@vue/apollo-composable";
import {computed, ref} from "vue";
import {ElNotification} from "element-plus";
import {useI18n} from "vue-i18n";
import {useAuthStore} from "@/stores/auth.js";
import translations from "@/core/helpers/translations.js";
import {SWITCH_LANGUAGE} from "@/graphql/mutations/languages.js";

export function useLanguageSwitch() {
  const authStore = useAuthStore()
  const {t} = useI18n();

  const { mutate: languageSwitchMutation } = useMutation(SWITCH_LANGUAGE);

  const accessToken = computed(() => authStore.accessToken)
  const userUuid = computed(() => authStore.user?.uuid)

  const loading = ref(false);

  async function switchLanguage(
      locale
  ) {
    loading.value = true;

    try {
      translations.switchLanguage(locale)
      if (accessToken.value) {
        const response = await languageSwitchMutation(
          userUuid.value,
          locale
        );

        if (response.data?.updateUser) {
          authStore.setUser({
            user: response.data.updateUser.user,
            accessToken: accessToken.value
          })
        }
      }
    } catch (error) {
      console.error("useLanguageSet error:", error);

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
    switchLanguage,
    loading
  };
}