import {useMutation} from "@vue/apollo-composable";
import {ref} from "vue";
import {ElNotification} from "element-plus";
import {useI18n} from "vue-i18n";
import {CONTACT_US} from "@/graphql/mutations/contact.js";

export function useContactUs() {
  const {t} = useI18n();

  const { mutate: contactUsMutation } = useMutation(CONTACT_US);

  const loading = ref(false);

  async function contactUs(
      name,
      email,
      phoneNumber,
      subject,
      message
  ) {
    loading.value = true;

    try {
      const response = await contactUsMutation({
          name,
          email,
          phoneNumber,
          subject,
          message
      });

      if (response.data?.contactUs.received) {
        ElNotification({
          message: t('popup.success.contactUs'),
          type: 'success'
        })
      }
    } catch (error) {
      console.error("useContactUs error:", error);

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
    contactUs,
    loading
  };
}