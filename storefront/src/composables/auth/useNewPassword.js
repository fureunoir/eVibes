import {useMutation} from "@vue/apollo-composable";
import {NEW_PASSWORD} from "@/graphql/mutations/auth.js";
import {computed, ref} from "vue";
import {ElNotification} from "element-plus";
import {useI18n} from "vue-i18n";
import {useRoute, useRouter} from "vue-router";
import {DEFAULT_LOCALE, LOCALE_STORAGE_LOCALE_KEY} from "@/config/index.js";

export function useNewPassword() {
  const {t} = useI18n();
  const route = useRoute();
  const router = useRouter();

  const { mutate: newPasswordMutation } = useMutation(NEW_PASSWORD);

  const token = computed(() =>
    route.query.token ? (route.query.token) : undefined,
  );
  const uid = computed(() =>
    route.query.uid ? (route.query.uid) : undefined,
  );

  const loading = ref(false);

  async function newPassword(
      password,
      confirmPassword
  ) {
    loading.value = true;

    try {
      const response = await newPasswordMutation({
          password,
          confirmPassword,
          token: token.value,
          uid: uid.value
      });

      if (response.data?.confirmResetPassword.success) {
        ElNotification({
          message: t('popup.success.newPassword'),
          type: 'success'
        })

        await router.push({
          name: 'home',
          params: {
            locale: localStorage.getItem(LOCALE_STORAGE_LOCALE_KEY) || DEFAULT_LOCALE
          }
        })
      }
    } catch (error) {
      console.error("useNewPassword error:", error);

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
    newPassword,
    loading
  };
}