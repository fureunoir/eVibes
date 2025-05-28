import {useMutation} from "@vue/apollo-composable";
import {RESET_PASSWORD} from "@/graphql/mutations/auth.js";
import {ref} from "vue";
import {ElNotification} from "element-plus";
import {useI18n} from "vue-i18n";

export function usePasswordReset() {
  const {t} = useI18n();

  const { mutate: resetPasswordMutation } = useMutation(RESET_PASSWORD);

  const loading = ref(false);

  async function resetPassword(
      email
  ) {
    loading.value = true;

    try {
      const response = await resetPasswordMutation({
          email
      });

      if (response.data?.resetPassword.success) {
        ElNotification({
          message: t('popup.success.reset'),
          type: 'success'
        })
      }
    } catch (error) {
      console.error("usePasswordReset error:", error);

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
    resetPassword,
    loading
  };
}