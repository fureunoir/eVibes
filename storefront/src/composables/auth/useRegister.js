import {useMutation} from "@vue/apollo-composable";
import {REGISTER} from "@/graphql/mutations/auth.js";
import {h, ref} from "vue";
import {ElNotification} from "element-plus";
import {useI18n} from "vue-i18n";
import {useMailClient} from "@/composables/utils";

export function useRegister() {
  const {t} = useI18n();

  const { mutate: registerMutation } = useMutation(REGISTER);

  const { mailClientUrl, detectMailClient, openMailClient } = useMailClient();

  const loading = ref(false);

  async function register(
      firstName,
      lastName,
      phoneNumber,
      email,
      password,
      confirmPassword
  ) {
    loading.value = true;

    try {
      const response = await registerMutation({
          firstName,
          lastName,
          phoneNumber,
          email,
          password,
          confirmPassword
      });

      if (response.data?.createUser?.success) {
        detectMailClient(email);

        ElNotification({
          message: h('div', [
            h('p', t('popup.success.register')),
            mailClientUrl.value ? h(
              'button',
              {
                style: {
                  marginTop: '10px',
                  padding: '6px 12px',
                  backgroundColor: '#000000',
                  color: '#fff',
                  border: 'none',
                  cursor: 'pointer',
                },
                onClick: () => {
                  openMailClient()
                }
              },
              t('buttons.goEmail')
            ) : ''
          ]),
          type: 'success'
        })
      }
    } catch (error) {
      console.error("useRegister error:", error);

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
    register,
    loading
  };
}