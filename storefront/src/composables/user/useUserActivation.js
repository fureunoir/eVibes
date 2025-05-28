import {useMutation} from "@vue/apollo-composable";
import {computed, ref} from "vue";
import {ElNotification} from "element-plus";
import {useI18n} from "vue-i18n";
import {useRoute} from "vue-router";
import {ACTIVATE_USER} from "@/graphql/mutations/user.js";

export function useUserActivation() {
  const {t} = useI18n();
  const route = useRoute();

  const { mutate: userActivationMutation } = useMutation(ACTIVATE_USER);

  const token = computed(() =>
    route.query.token ? (route.query.token) : undefined,
  );
  const uid = computed(() =>
    route.query.uid ? (route.query.uid) : undefined,
  );

  const loading = ref(false);

  async function activateUser() {
    loading.value = true;

    try {
      const response = await userActivationMutation({
          token: token.value,
          uid: uid.value
      });

      if (response.data?.activateUser) {
        ElNotification({
          message: t("popup.activationSuccess"),
          type: "success"
        });
      }
    } catch (error) {
      console.error("useUserActivation error:", error);

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
    activateUser,
    loading
  };
}