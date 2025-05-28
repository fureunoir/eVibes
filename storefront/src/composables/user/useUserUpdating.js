import {useMutation} from "@vue/apollo-composable";
import {computed, ref} from "vue";
import {ElNotification} from "element-plus";
import {useI18n} from "vue-i18n";
import {useAuthStore} from "@/stores/auth.js";
import translations from "@/core/helpers/translations.js";
import {useRoute, useRouter} from "vue-router";
import {useLogout} from "@/composables/auth";
import {UPDATE_USER} from "@/graphql/mutations/user.js";

export function useUserUpdating() {
  const router = useRouter();
  const route = useRoute();
  const authStore = useAuthStore()
  const {t} = useI18n();

  const { mutate: userUpdatingMutation } = useMutation(UPDATE_USER);

  const { logout } = useLogout();

  const accessToken = computed(() => authStore.accessToken)
  const userUuid = computed(() => authStore.user?.uuid)
  const userEmail = computed(() => authStore.user?.email)

  const loading = ref(false);

  async function updateUser(
      firstName,
      lastName,
      email,
      phoneNumber,
      password,
      confirmPassword
  ) {
    loading.value = true;

    try {
      const fields = {
        uuid: userUuid.value,
        firstName,
        lastName,
        email,
        phoneNumber,
        password,
        confirmPassword
      };
      
      const params = Object.fromEntries(
        Object.entries(fields).filter(([_, value]) => 
          value !== undefined && value !== null && value !== ''
        )
      );
      
      // if (('password' in params && !('passwordConfirm' in params)) ||
      //     (!('password' in params) && 'passwordConfirm' in params)) {
      //   ElNotification({
      //     title: t('popup.errors.main'),
      //     message: t('popup.errors.noDataToUpdate'),
      //     type: 'error'
      //   });
      // }
      
      if (Object.keys(params).length === 0) {
        ElNotification({
          title: t('popup.errors.main'),
          message: t('popup.errors.noDataToUpdate'),
          type: 'error'
        });
      }
      
      const response = await userUpdatingMutation(
          params
      );

      if (response.data?.updateUser) {
        if (userEmail.value !== email) {
          await logout()

          ElNotification({
            message: t("popup.success.confirmEmail"),
            type: "success"
          });
        } else {
          authStore.setUser({
            user: response.data.updateUser.user,
            accessToken: accessToken.value
          })

          ElNotification({
            message: t("popup.successUpdate"),
            type: "success"
          });

          if (response.data.updateUser.user.language !== translations.currentLocale) {
            translations.switchLanguage(response.data.updateUser.user.language, router, route)
          }
        }
      }
    } catch (error) {
      console.error("useUserUpdating error:", error);

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
    updateUser,
    loading
  };
}