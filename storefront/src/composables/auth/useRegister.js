import {useMutation} from "@vue/apollo-composable";
import {REGISTER} from "@/graphql/mutations/auth.js";
import {h, ref} from "vue";
import {ElNotification} from "element-plus";
import {useI18n} from "vue-i18n";
import {useMailClient} from "@/composables/auth/useMainClient.js";

export function useRegister() {
  const loading = ref(false);
  const mailClient = ref(null)

  const {t} = useI18n();

  const { mutate: registerMutation } = useMutation(REGISTER);

  const { mailClientUrl, detectMailClient, openMailClient } = useMailClient();

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
          title: t('popup.register.title'),
          message: h('div', [
            h('p', t('popup.register.text')),
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
      console.error("Register error:", error);

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
    register,
    loading
  };
}