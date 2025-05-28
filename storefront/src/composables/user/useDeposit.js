import {useMutation} from "@vue/apollo-composable";
import {ref} from "vue";
import {ElNotification} from "element-plus";
import {useI18n} from "vue-i18n";
import {DEPOSIT} from "@/graphql/mutations/deposit.js";

export function useDeposit() {
  const {t} = useI18n();

  const { mutate: depositMutation } = useMutation(DEPOSIT);

  const loading = ref(false);

  async function deposit(
      amount
  ) {
    loading.value = true;

    try {
      const response = await depositMutation(
        amount
      );

      if (response.data?.deposit) {
        window.open(response.data.deposit.transaction.process.url)
      }
    } catch (error) {
      console.error("useDeposit error:", error);

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
    deposit,
    loading
  };
}